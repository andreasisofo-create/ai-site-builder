"""
Client dedicato per Kimi K2.5 API (Moonshot).
Supporta Thinking mode e Instant mode.
Usa httpx.AsyncClient persistente per evitare overhead di connessione.
Supporta streaming SSE per chiamate lunghe (evita timeout).
"""

import asyncio
import httpx
import json
import logging
import re
from typing import Dict, Any, Optional, List

from app.core.config import settings

logger = logging.getLogger(__name__)

# Kimi K2.5 pricing (USD per 1M tokens)
PRICE_INPUT = 0.60
PRICE_OUTPUT = 2.50


class KimiClient:
    """Client async per Kimi K2.5 API."""

    def __init__(self):
        self.api_url = settings.KIMI_API_URL or "https://api.moonshot.ai/v1"
        self.model = settings.KIMI_MODEL or "kimi-k2.5"
        self._client: Optional[httpx.AsyncClient] = None

    @property
    def _headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {settings.active_api_key}",
            "Content-Type": "application/json",
        }

    async def _get_client(self) -> httpx.AsyncClient:
        """Lazy-init del client httpx persistente."""
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                timeout=httpx.Timeout(300.0, connect=15.0),
                headers=self._headers,
                limits=httpx.Limits(max_connections=10, max_keepalive_connections=5),
            )
        return self._client

    async def call(
        self,
        messages: List[Dict[str, Any]],
        max_tokens: int = 8000,
        thinking: bool = True,
        timeout: float = 180.0,
        _retries: int = 2,
    ) -> Dict[str, Any]:
        """
        Chiamata base a Kimi API con retry su 429 rate limit.

        Args:
            messages: Lista messaggi OpenAI-format
            max_tokens: Max token in output
            thinking: True = Thinking mode (temp 1.0, deep reasoning),
                      False = Instant mode (temp 0.6, faster)
            timeout: Timeout in secondi
            _retries: Numero di retry su 429 (default 2)

        Returns:
            {"success": True, "content": str, "tokens_input": int, "tokens_output": int}
            oppure {"success": False, "error": str}
        """
        temperature = 1.0 if thinking else 0.6

        payload: Dict[str, Any] = {
            "model": self.model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
        }

        # Kimi K2.5: per disabilitare Thinking (Instant mode)
        if not thinking:
            payload["thinking"] = {"type": "disabled"}

        last_error = ""
        for attempt in range(_retries + 1):
            try:
                client = await self._get_client()
                response = await client.post(
                    f"{self.api_url}/chat/completions",
                    json=payload,
                    timeout=timeout,
                )
                response.raise_for_status()
                data = response.json()

                content = data["choices"][0]["message"]["content"]
                usage = data.get("usage", {})
                tokens_in = usage.get("prompt_tokens", 0)
                tokens_out = usage.get("completion_tokens", 0)

                return {
                    "success": True,
                    "content": content,
                    "tokens_input": tokens_in,
                    "tokens_output": tokens_out,
                }

            except httpx.HTTPStatusError as e:
                last_error = self._handle_http_error(e)
                # Retry on 429 rate limit
                if e.response.status_code == 429 and attempt < _retries:
                    wait = 2 ** attempt + 1  # 2s, 3s
                    logger.warning(f"Kimi 429 rate limit, retrying in {wait}s (attempt {attempt + 1}/{_retries})")
                    await asyncio.sleep(wait)
                    continue
                return {"success": False, "error": last_error}
            except httpx.TimeoutException:
                logger.error("Timeout calling Kimi API")
                return {"success": False, "error": "Timeout: la richiesta ha impiegato troppo tempo"}
            except Exception as e:
                logger.exception("Errore chiamata Kimi API")
                return {"success": False, "error": str(e)}

        return {"success": False, "error": last_error}

    async def call_stream(
        self,
        messages: List[Dict[str, Any]],
        max_tokens: int = 6000,
        thinking: bool = False,
        timeout: float = 300.0,
    ) -> Dict[str, Any]:
        """
        Chiamata con streaming SSE. Evita timeout per generazioni lunghe.
        I token arrivano incrementalmente, il read timeout si resetta ad ogni chunk.

        Returns:
            {"success": True, "content": str, "tokens_input": int, "tokens_output": int}
            oppure {"success": False, "error": str}
        """
        temperature = 1.0 if thinking else 0.6

        payload: Dict[str, Any] = {
            "model": self.model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "stream": True,
        }

        if not thinking:
            payload["thinking"] = {"type": "disabled"}

        try:
            client = await self._get_client()
            collected_content = []
            tokens_in = 0
            tokens_out = 0

            async with client.stream(
                "POST",
                f"{self.api_url}/chat/completions",
                json=payload,
                timeout=timeout,
            ) as response:
                # Read the body before raise_for_status so the error handler
                # can access .text/.json() on the response (httpx requires
                # streaming responses to be read before content access).
                if response.status_code >= 400:
                    await response.aread()
                    response.raise_for_status()
                async for line in response.aiter_lines():
                    if not line.startswith("data: "):
                        continue
                    data_str = line[6:]  # Remove "data: " prefix
                    if data_str.strip() == "[DONE]":
                        break
                    try:
                        chunk = json.loads(data_str)
                        delta = chunk.get("choices", [{}])[0].get("delta", {})
                        if delta.get("content"):
                            collected_content.append(delta["content"])
                        # Usage info in last chunk
                        usage = chunk.get("usage")
                        if usage:
                            tokens_in = usage.get("prompt_tokens", 0)
                            tokens_out = usage.get("completion_tokens", 0)
                    except json.JSONDecodeError:
                        continue

            content = "".join(collected_content)
            if not content:
                return {"success": False, "error": "Nessun contenuto ricevuto dallo streaming"}

            return {
                "success": True,
                "content": content,
                "tokens_input": tokens_in,
                "tokens_output": tokens_out,
            }

        except httpx.HTTPStatusError as e:
            error_msg = self._handle_http_error(e)
            return {"success": False, "error": error_msg}
        except httpx.TimeoutException:
            logger.error("Timeout calling Kimi API (stream)")
            return {"success": False, "error": "Timeout: la richiesta ha impiegato troppo tempo"}
        except Exception as e:
            logger.exception("Errore chiamata Kimi API (stream)")
            return {"success": False, "error": str(e)}

    async def call_with_image(
        self,
        prompt: str,
        image_url: str,
        max_tokens: int = 1500,
        thinking: bool = True,
        timeout: float = 90.0,
    ) -> Dict[str, Any]:
        """
        Chiamata a Kimi con immagine (multimodal).

        Args:
            prompt: Testo della richiesta
            image_url: URL dell'immagine da analizzare
            max_tokens: Max token output
            thinking: Thinking mode on/off
            timeout: Timeout in secondi
        """
        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": image_url}},
                ],
            }
        ]

        return await self.call(
            messages=messages,
            max_tokens=max_tokens,
            thinking=thinking,
            timeout=timeout,
        )

    def _handle_http_error(self, e: httpx.HTTPStatusError) -> str:
        """Gestisce errori HTTP con messaggi user-friendly."""
        status = e.response.status_code
        try:
            body = e.response.json()
            detail = body.get("error", {}).get("message", "")
        except Exception:
            try:
                detail = e.response.text[:200]
            except Exception:
                detail = f"HTTP {status}"

        if status == 401:
            msg = "API Key Kimi non valida o scaduta"
        elif status == 429:
            msg = "Rate limit Kimi raggiunto. Riprova tra qualche secondo."
        elif status == 402:
            msg = "Credito Kimi esaurito. Ricarica il tuo account Moonshot."
        elif status >= 500:
            msg = "Errore server Kimi. Riprova piu' tardi."
        else:
            msg = f"Errore Kimi API ({status}): {detail}"

        logger.error(f"Kimi API HTTP {status}: {detail}")
        return msg

    @staticmethod
    def extract_html(content: str) -> str:
        """Estrae HTML dal markdown se il modello wrappa in code blocks.
        Gestisce anche output troncato (senza closing ```)."""
        # Caso 1: code block completo ```html ... ```
        html_match = re.search(r'```html\n(.*?)\n```', content, re.DOTALL)
        if html_match:
            return html_match.group(1).strip()

        # Caso 2: code block generico completo ``` ... ```
        code_match = re.search(r'```\n(.*?)\n```', content, re.DOTALL)
        if code_match:
            return code_match.group(1).strip()

        # Caso 3: output troncato - code block aperto ma mai chiuso
        truncated_match = re.search(r'```html?\n(.*)', content, re.DOTALL)
        if truncated_match:
            return truncated_match.group(1).strip()

        return content.strip()

    @staticmethod
    def calculate_cost(tokens_input: int, tokens_output: int) -> float:
        """Calcola costo stimato in USD."""
        input_cost = (tokens_input / 1_000_000) * PRICE_INPUT
        output_cost = (tokens_output / 1_000_000) * PRICE_OUTPUT
        return round(input_cost + output_cost, 6)

    async def close(self):
        """Chiude il client httpx."""
        if self._client and not self._client.is_closed:
            await self._client.aclose()


# Singleton
kimi = KimiClient()
