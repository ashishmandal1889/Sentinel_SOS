"""
Sentinel SOS - Email Notification Adapter (Resend).
"""

from typing import Any, Dict, Optional
import httpx
from app.core.config import settings
from app.core.logging import logger


class EmailClient:
    RESEND_API_URL = "https://api.resend.com/emails"

    async def send_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        from_email: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Dispatches email notification via Resend API or logs mock if not configured.
        """
        sender = from_email or settings.RESEND_FROM_EMAIL
        api_key = settings.RESEND_API_KEY

        if not api_key:
            logger.info(f"[MOCK EMAIL] To: {to_email} | Subject: {subject}")
            return {
                "status": "DELIVERED",
                "channel": "email",
                "recipient": to_email,
                "provider": "mock",
            }

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "from": sender,
            "to": [to_email],
            "subject": subject,
            "html": html_content,
        }

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(
                    self.RESEND_API_URL,
                    json=payload,
                    headers=headers,
                )

            if response.status_code in (200, 201):
                res_data = response.json()
                logger.info(f"[RESEND EMAIL SUCCESS] Sent to {to_email}, id={res_data.get('id')}")
                return {
                    "status": "DELIVERED",
                    "channel": "email",
                    "provider": "resend",
                    "recipient": to_email,
                    "resend_id": res_data.get("id"),
                }
            else:
                logger.error(f"[RESEND EMAIL ERROR] Status: {response.status_code}, Body: {response.text}")
                return {
                    "status": "FAILED",
                    "channel": "email",
                    "provider": "resend",
                    "recipient": to_email,
                    "error": response.text,
                    "status_code": response.status_code,
                }
        except Exception as e:
            logger.error(f"[RESEND EMAIL EXCEPTION] {e}")
            return {
                "status": "FAILED",
                "channel": "email",
                "provider": "resend",
                "recipient": to_email,
                "error": str(e),
            }


email_client = EmailClient()
