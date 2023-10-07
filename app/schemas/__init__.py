from .auth import User
from .issue import Issue
from .sprint import Sprint
from .workplace import UserAssignedWorkplace, Workplace

__beanie_models__ = [User, Workplace, Sprint, UserAssignedWorkplace, Issue]


__all__ = [
    "__beanie_models__",
]
