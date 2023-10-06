from app.routers.auth import User, UserAssignedWorkplace
from app.routers.auth.router import router as register_router
from app.routers.issue import Issue
from app.routers.issue.router import router as issue_router
from app.routers.sprint import Sprint
from app.routers.sprint.router import router as sprint_router
from app.routers.workplace import Workplace
from app.routers.workplace.router import router as workplace_router

list_of_routes = [
    register_router,
    sprint_router,
    workplace_router,
    issue_router,
]
__beanie_models__ = [User, Workplace, Sprint, UserAssignedWorkplace, Issue]


__all__ = [
    "list_of_routes",
    "__beanie_models__",
]
