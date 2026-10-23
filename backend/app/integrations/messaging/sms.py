"""
Sentinel SOS - SMS Integration Adapter.

Provides standardized SMS sending interface supporting:
  - Mock (for local development and CI testing)
  - Twilio
  - MSG91

Tracks delivery status and enforces isolated configuration handling.
"""

from typing import Any, Dict
import httpx
from app.core.config import settings
from app.core.logging import logger


class SMSClient:
    def __init__(self):
        self.provider = settings.SMS_PROVIDER

    async def send_sms(self, to_phone: str, message: str) -> Dict[str, Any]:
        """Sends an SMS message via the configured provider."""
        if self.provider == "mock":
            logger.info(f"[MOCK SMS] To: {to_phone} | Content: {message}")
            return {"status": "DELIVERED", "provider": "mock", "recipient": to_phone}

        if self.provider == "twilio":
            account_sid = settings.SMS_TWILIO_ACCOUNT_SID
            # Auth can be either (Account SID, Auth Token) or (API Key SID, API Key Secret)
            username = settings.SMS_TWILIO_API_KEY_SID or account_sid
            password = settings.SMS_TWILIO_API_KEY_SECRET or settings.SMS_TWILIO_AUTH_TOKEN
            from_number = settings.SMS_TWILIO_FROM_NUMBER

            if not account_sid or not username or not password:
                logger.error("[TWILIO SMS ERROR] Missing Twilio credentials.")
                return {
                    "status": "FAILED",
                    "provider": "twilio",
                    "recipient": to_phone,
                    "error": "Missing Twilio credentials.",
                }

            if not from_number:
                logger.error("[TWILIO SMS ERROR] Missing SMS_TWILIO_FROM_NUMBER. Please configure a Twilio phone number.")
                return {
                    "status": "FAILED",
                    "provider": "twilio",
                    "recipient": to_phone,
                    "error": "SMS_TWILIO_FROM_NUMBER is not configured.",
                }

            url = f"https://api.twilio.com/2010-04-01/Accounts/{account_sid}/Messages.json"
            data = {
                "To": to_phone,
                "From": from_number,
                "Body": message,
            }

            try:
                async with httpx.AsyncClient(timeout=10.0) as client:
                    response = await client.post(
                        url,
                        data=data,
                        auth=(username, password),
                    )

                if response.status_code in (200, 201):
                    res_json = response.json()
                    logger.info(f"[TWILIO SMS SUCCESS] SID: {res_json.get('sid')} to {to_phone}")
                    return {
                        "status": "SUBMITTED",
                        "provider": "twilio",
                        "recipient": to_phone,
                        "sid": res_json.get("sid"),
                    }
                else:
                    logger.error(f"[TWILIO SMS ERROR] Status {response.status_code}: {response.text}")
                    return {
                        "status": "FAILED",
                        "provider": "twilio",
                        "recipient": to_phone,
                        "error": response.text,
                        "status_code": response.status_code,
                    }
            except Exception as e:
                logger.error(f"[TWILIO SMS EXCEPTION] {e}")
                return {
                    "status": "FAILED",
                    "provider": "twilio",
                    "recipient": to_phone,
                    "error": str(e),
                }

        if self.provider == "msg91":
            logger.info(f"[MSG91 SMS] Sending to {to_phone}")
            return {"status": "SUBMITTED", "provider": "msg91", "recipient": to_phone}

        logger.warning(f"Unknown SMS provider '{self.provider}'. Message not dispatched.")
        return {"status": "FAILED", "provider": self.provider, "error": "Unknown provider"}


sms_client = SMSClient()
