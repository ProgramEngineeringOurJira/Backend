from app.routers.auth import router as register_router
from app.routers.comment import router as comment_router
from app.routers.issue import router as issue_router
from app.routers.sprint import router as sprint_router
from app.routers.workplace import router as workplace_router

list_of_routes = [
    register_router,
    workplace_router,
    sprint_router,
    issue_router,
    comment_router,
]


__all__ = [
    "list_of_routes",
]
