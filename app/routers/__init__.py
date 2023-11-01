from app.routers.auth import router as register_router
from app.routers.issue import router as issue_router
from app.routers.sprint import router as sprint_router
from app.routers.workplace import router as workplace_router
from app.routers.invitation_workplace import router as invitation_workplace_router

list_of_routes = [
    register_router,
    workplace_router,
    sprint_router,
    issue_router,
    invitation_workplace_router,
]


__all__ = [
    "list_of_routes",
]
