"""
Sentinel SOS - Push Notification Adapter (Firebase Cloud Messaging).
"""

import os
from typing import Any, Dict, Optional
from app.core.config import settings
from app.core.logging import logger

_firebase_initialized = False


def _init_firebase() -> bool:
    global _firebase_initialized
    if _firebase_initialized:
        return True

    credentials_path = settings.PUSH_CREDENTIALS_PATH
    if not credentials_path:
        return False

    # Check relative to backend directory if not absolute
    if not os.path.isabs(credentials_path):
        candidate = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), credentials_path)
        if os.path.exists(candidate):
            credentials_path = candidate

    if not os.path.exists(credentials_path):
        logger.warning(f"Firebase credentials file not found at: {credentials_path}")
        return False

    try:
        import firebase_admin
        from firebase_admin import credentials

        if not firebase_admin._apps:
            cred = credentials.Certificate(credentials_path)
            firebase_admin.initialize_app(cred, {
                "projectId": settings.PUSH_FCM_PROJECT_ID or None,
            })
        _firebase_initialized = True
        logger.info(f"Firebase Admin SDK initialized successfully for project: {settings.PUSH_FCM_PROJECT_ID}")
        return True
    except Exception as e:
        logger.error(f"Failed to initialize Firebase Admin SDK: {e}")
        return False


class PushNotificationClient:
    def __init__(self):
        self.project_id = settings.PUSH_FCM_PROJECT_ID
        self.credentials_path = settings.PUSH_CREDENTIALS_PATH

    async def send_push(
        self,
        target_token: str,
        title: str,
        body: str,
        data: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """Dispatches push notification to responder or citizen device via Firebase FCM."""
        if not self.project_id or not _init_firebase():
            logger.info(f"[MOCK PUSH] Target: {target_token} | Title: {title} | Body: {body}")
            return {
                "status": "DELIVERED",
                "channel": "mock_push",
                "target": target_token,
                "title": title,
            }

        try:
            from firebase_admin import messaging

            message = messaging.Message(
                notification=messaging.Notification(
                    title=title,
                    body=body,
                ),
                data=data or {},
                token=target_token,
            )

            response = messaging.send(message)
            logger.info(f"[FCM PUSH SUCCESS] Sent to {target_token[:10]}... Message ID: {response}")
            return {
                "status": "DELIVERED",
                "channel": "fcm",
                "message_id": response,
                "target": target_token,
            }
        except Exception as e:
            logger.error(f"[FCM PUSH ERROR] Failed to send push notification: {e}")
            return {
                "status": "FAILED",
                "channel": "fcm",
                "error": str(e),
                "target": target_token,
            }


push_client = PushNotificationClient()
