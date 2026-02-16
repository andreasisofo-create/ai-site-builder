"""
Servizio n8n per Ads AI - trigger workflow via webhook.
Ported from Node.js: backend/services/n8n-service.js
"""

import httpx
from datetime import datetime, timezone
from typing import Any, Dict, Optional
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

WEBHOOK_MAP: Dict[str, str] = {
    "campaignCreate": "N8N_WEBHOOK_CAMPAIGN_CREATE",
    "campaignMonitor": "N8N_WEBHOOK_CAMPAIGN_MONITOR",
    "alertPerformance": "N8N_WEBHOOK_ALERT_PERFORMANCE",
    "leadSync": "N8N_WEBHOOK_LEAD_SYNC",
    "reportDaily": "N8N_WEBHOOK_REPORT_DAILY",
    "keywordResearch": "N8N_WEBHOOK_KEYWORD_RESEARCH",
}


class N8nAdsService:
    """Servizio per trigger workflow n8n per campagne ads."""

    async def trigger_workflow(
        self, workflow_name: str, data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Trigger un workflow n8n via webhook."""
        attr_name = WEBHOOK_MAP.get(workflow_name)
        if not attr_name:
            raise ValueError(f"Workflow non configurato: {workflow_name}")

        webhook_path = getattr(settings, attr_name, "")
        if not webhook_path:
            raise ValueError(f"Webhook path non configurato per: {workflow_name}")

        base_url = settings.N8N_BASE_URL
        if not base_url:
            raise ValueError("N8N_BASE_URL non configurato")

        url = f"{base_url.rstrip('/')}/webhook/{webhook_path}"

        payload = {
            **data,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        headers: Dict[str, str] = {"Content-Type": "application/json"}
        if settings.N8N_API_KEY:
            headers["X-N8N-API-KEY"] = settings.N8N_API_KEY

        try:
            logger.info("[n8n] Trigger workflow: %s", workflow_name)
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(url, json=payload, headers=headers)
                response.raise_for_status()

            logger.info("[n8n] Workflow %s triggerato", workflow_name)
            return response.json()
        except httpx.HTTPStatusError as e:
            logger.error("[n8n] HTTP error: %s - %s", e.response.status_code, e.response.text)
            raise
        except Exception as e:
            logger.error("[n8n] Errore: %s", str(e))
            raise

    async def create_campaign(self, campaign_data: Dict[str, Any]) -> Dict[str, Any]:
        return await self.trigger_workflow("campaignCreate", campaign_data)

    async def monitor_campaign(
        self, campaign_id: str, platform: str
    ) -> Dict[str, Any]:
        return await self.trigger_workflow(
            "campaignMonitor", {"campaignId": campaign_id, "platform": platform}
        )

    async def send_alert(self, alert_data: Dict[str, Any]) -> Dict[str, Any]:
        return await self.trigger_workflow("alertPerformance", alert_data)


n8n_ads_service = N8nAdsService()
