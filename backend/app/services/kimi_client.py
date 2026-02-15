"""
Provider-agnostic AI client for Site Builder.

Supports multiple backends via a single OpenAI-compatible interface:
  - OpenRouter (unified gateway — recommended, default when key is set)
  - Kimi K2.5 (Moonshot — legacy)
  - GLM-5 (Z.ai / Zhipu — direct)
  - DeepSeek V3 (direct)

The provider is selected via AI_PROVIDER env var or auto-detected from
available API keys (see config.active_ai_provider).
"""

import asyncio
import httpx
import json
import logging
import re
from typing import Dict, Any, Optional, List

from app.core.config import settings

logger = logging.getLogger(__name__)

# Pricing per provider (USD per 1M tokens)
# For OpenRouter the price depends on the model — these are approximate defaults.
PRICING: Dict[str, Dict[str, float]] = {
    "kimi":       {"input": 0.60, "output": 2.50},
    "openrouter": {"input": 0.07, "output": 0.30},   # Qwen3 Coder Next default
    "glm5":       {"input": 0.80, "output": 2.56},
    "deepseek":   {"input": 0.27, "output": 1.10},
}

# Pricing for known OpenRouter models (for accurate cost tracking)
_OPENROUTER_MODEL_PRICING: Dict[str, Dict[str, float]] = {
    "qwen/qwen3-coder-next":         {"input": 0.07,  "output": 0.30},
    "deepseek/deepseek-v3.2":        {"input": 0.24,  "output": 0.38},
    "deepseek/deepseek-chat-v3-0324": {"input": 0.14, "output": 0.28},
    "anthropic/claude-sonnet-4.5":   {"input": 3.00,  "output": 15.00},
    "anthropic/claude-haiku-4.5":    {"input": 0.80,  "output": 4.00},
    "z-ai/glm-5":                    {"input": 0.75,  "output": 2.55},
}

# Providers that support the Kimi-specific "thinking" parameter
_THINKING_PROVIDERS = {"kimi"}


def _resolve_provider_config() -> Dict[str, str]:
    """Resolve API URL, model, and API key based on active provider."""
    provider = settings.active_ai_provider

    if provider == "openrouter":
        return {
            "provider": "openrouter",
            "api_url": settings.OPENROUTER_API_URL or "https://openrouter.ai/api/v1",
            "model": settings.OPENROUTER_MODEL or "deepseek/deepseek-chat-v3-0324",
            "api_key": settings.OPENROUTER_API_KEY,
        }
    elif provider == "glm5":
        return {
            "provider": "glm5",
            "api_url": settings.GLM5_API_URL or "https://api.z.ai/api/paas/v4",
            "model": settings.GLM5_MODEL or "glm-5",
            "api_key": settings.GLM5_API_KEY,
        }
    elif provider == "deepseek":
        return {
            "provider": "deepseek",
            "api_url": settings.DEEPSEEK_API_URL or "https://api.deepseek.com",
            "model": settings.DEEPSEEK_MODEL or "deepseek-chat",
            "api_key": settings.DEEPSEEK_API_KEY,
        }
    else:
        # Kimi (legacy default)
        return {
            "provider": "kimi",
            "api_url": settings.KIMI_API_URL or "https://api.moonshot.ai/v1",
            "model": settings.KIMI_MODEL or "kimi-k2.5",
            "api_key": settings.MOONSHOT_API_KEY or settings.KIMI_API_KEY,
        }


class KimiClient:
    """Provider-agnostic async AI client. Drop-in replacement for the old Kimi-only client."""

    def __init__(self, model_override: Optional[str] = None):
        cfg = _resolve_provider_config()
        self.provider = cfg["provider"]
        self.api_url = cfg["api_url"]
        self.model = model_override or cfg["model"]
        self._api_key = cfg["api_key"]
        self._client: Optional[httpx.AsyncClient] = None

        logger.info(
            f"AI client initialized: provider={self.provider}, "
            f"model={self.model}, url={self.api_url}"
        )

    @property
    def _is_kimi(self) -> bool:
        return self.provider in _THINKING_PROVIDERS

    @property
    def _headers(self) -> Dict[str, str]:
        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
        }
        if self.provider == "openrouter":
            headers["HTTP-Referer"] = "https://e-quipe.app"
            headers["X-Title"] = "Site Builder"
        return headers

    async def _get_client(self) -> httpx.AsyncClient:
        """Lazy-init del client httpx persistente."""
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                timeout=httpx.Timeout(300.0, connect=15.0),
                headers=self._headers,
                limits=httpx.Limits(max_connections=10, max_keepalive_connections=5),
            )
        return self._client

    def _build_payload(
        self,
        messages: List[Dict[str, Any]],
        max_tokens: int,
        thinking: bool,
        temperature: Optional[float] = None,
        top_p: Optional[float] = None,
        stream: bool = False,
    ) -> Dict[str, Any]:
        """Build the request payload, only adding provider-specific fields where needed."""
        if temperature is None:
            temperature = 1.0 if (thinking and self._is_kimi) else 0.6

        payload: Dict[str, Any] = {
            "model": self.model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
        }

        if top_p is not None:
            payload["top_p"] = top_p

        if stream:
            payload["stream"] = True

        # Kimi-specific: thinking mode toggle
        if self._is_kimi and not thinking:
            payload["thinking"] = {"type": "disabled"}

        return payload

    async def call(
        self,
        messages: List[Dict[str, Any]],
        max_tokens: int = 8000,
        thinking: bool = True,
        timeout: float = 180.0,
        _retries: int = 2,
        temperature: Optional[float] = None,
        top_p: Optional[float] = None,
    ) -> Dict[str, Any]:
        """
        Chiamata base all'AI provider con retry su 429 rate limit.

        Args:
            messages: Lista messaggi OpenAI-format
            max_tokens: Max token in output
            thinking: True = Thinking mode (Kimi only, ignored for other providers)
            timeout: Timeout in secondi
            _retries: Numero di retry su 429 (default 2)
            temperature: Override temperature
            top_p: Optional top_p for nucleus sampling diversity

        Returns:
            {"success": True, "content": str, "tokens_input": int, "tokens_output": int}
            oppure {"success": False, "error": str}
        """
        payload = self._build_payload(
            messages=messages,
            max_tokens=max_tokens,
            thinking=thinking,
            temperature=temperature,
            top_p=top_p,
        )

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
                if e.response.status_code == 429 and attempt < _retries:
                    wait = 2 ** attempt + 1
                    logger.warning(f"{self.provider} 429 rate limit, retrying in {wait}s (attempt {attempt + 1}/{_retries})")
                    await asyncio.sleep(wait)
                    continue
                return {"success": False, "error": last_error}
            except httpx.TimeoutException:
                logger.error(f"Timeout calling {self.provider} API")
                return {"success": False, "error": "Timeout: la richiesta ha impiegato troppo tempo"}
            except Exception as e:
                logger.exception(f"Errore chiamata {self.provider} API")
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

        Returns:
            {"success": True, "content": str, "tokens_input": int, "tokens_output": int}
            oppure {"success": False, "error": str}
        """
        payload = self._build_payload(
            messages=messages,
            max_tokens=max_tokens,
            thinking=thinking,
            stream=True,
        )

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
                if response.status_code >= 400:
                    await response.aread()
                    response.raise_for_status()
                async for line in response.aiter_lines():
                    if not line.startswith("data: "):
                        continue
                    data_str = line[6:]
                    if data_str.strip() == "[DONE]":
                        break
                    try:
                        chunk = json.loads(data_str)
                        delta = chunk.get("choices", [{}])[0].get("delta", {})
                        if delta.get("content"):
                            collected_content.append(delta["content"])
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
            logger.error(f"Timeout calling {self.provider} API (stream)")
            return {"success": False, "error": "Timeout: la richiesta ha impiegato troppo tempo"}
        except Exception as e:
            logger.exception(f"Errore chiamata {self.provider} API (stream)")
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
        Chiamata multimodal con immagine (OpenAI vision format).
        Works with Kimi, OpenRouter, and any provider supporting vision.
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

        provider_name = self.provider.upper()
        if status == 401:
            msg = f"API Key {provider_name} non valida o scaduta"
        elif status == 429:
            msg = f"Rate limit {provider_name} raggiunto. Riprova tra qualche secondo."
        elif status == 402:
            msg = f"Credito {provider_name} esaurito. Ricarica il tuo account."
        elif "token limit" in detail.lower() or "exceeded model token limit" in detail.lower():
            msg = f"Token limit exceeded: {detail}"
        elif status >= 500:
            msg = f"Errore server {provider_name}. Riprova piu' tardi."
        else:
            msg = f"Errore {provider_name} API ({status}): {detail}"

        logger.error(f"{provider_name} API HTTP {status}: {detail}")
        return msg

    @staticmethod
    def extract_html(content: str) -> str:
        """Estrae HTML dal markdown se il modello wrappa in code blocks."""
        html_match = re.search(r'```html\n(.*?)\n```', content, re.DOTALL)
        if html_match:
            return html_match.group(1).strip()

        code_match = re.search(r'```\n(.*?)\n```', content, re.DOTALL)
        if code_match:
            return code_match.group(1).strip()

        truncated_match = re.search(r'```html?\n(.*)', content, re.DOTALL)
        if truncated_match:
            return truncated_match.group(1).strip()

        return content.strip()

    def calculate_cost(self, tokens_input: int, tokens_output: int) -> float:
        """Calcola costo stimato in USD basato sul provider e modello attivo."""
        # For OpenRouter, use model-specific pricing if available
        if self.provider == "openrouter" and self.model in _OPENROUTER_MODEL_PRICING:
            pricing = _OPENROUTER_MODEL_PRICING[self.model]
        else:
            pricing = PRICING.get(self.provider, PRICING["kimi"])
        input_cost = (tokens_input / 1_000_000) * pricing["input"]
        output_cost = (tokens_output / 1_000_000) * pricing["output"]
        return round(input_cost + output_cost, 6)

    async def close(self):
        """Chiude il client httpx."""
        if self._client and not self._client.is_closed:
            await self._client.aclose()


# Singleton — default client (Qwen3 for generation)
kimi = KimiClient()

# Refine client — uses a separate model (Claude) for higher quality chat refinement.
# If OPENROUTER_REFINE_MODEL is set and provider is openrouter, creates a dedicated
# client with Claude. Otherwise falls back to the same default client.
_refine_model = getattr(settings, "OPENROUTER_REFINE_MODEL", "")
if _refine_model and settings.active_ai_provider == "openrouter" and _refine_model != kimi.model:
    kimi_refine = KimiClient(model_override=_refine_model)
    logger.info(f"Refine client initialized with model: {_refine_model}")
else:
    kimi_refine = kimi
    logger.info("Refine client: using same model as generation")
