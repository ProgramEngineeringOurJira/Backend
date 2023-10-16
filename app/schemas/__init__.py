from .documents import Issue, Sprint, User, UserAssignedWorkplace, Workplace

__beanie_models__ = [User, Workplace, Sprint, UserAssignedWorkplace, Issue]


__all__ = [
    "__beanie_models__",
]
