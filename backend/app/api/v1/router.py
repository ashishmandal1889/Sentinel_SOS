"""
Sentinel SOS - API v1 Master Router.

Combines all sub-routers under the /api/v1 namespace.
"""

from fastapi import APIRouter
from app.api.v1.endpoints import (
    admin,
    auth,
    contacts,
    dispatch,
    health,
    incidents,
    notifications,
    responders,
    sos,
    users,
)

api_router = APIRouter()

api_router.include_router(health.router, tags=["Health"])
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(sos.router, prefix="/sos", tags=["SOS Emergency"])
api_router.include_router(responders.router, prefix="/responders", tags=["Responders"])
api_router.include_router(dispatch.router, prefix="/dispatch", tags=["Dispatch"])
api_router.include_router(contacts.router, prefix="/contacts", tags=["Emergency Contacts"])
api_router.include_router(notifications.router, prefix="/notifications", tags=["Notifications"])
api_router.include_router(incidents.router, prefix="/incidents", tags=["Incidents History"])
api_router.include_router(admin.router, prefix="/admin", tags=["Administration"])
