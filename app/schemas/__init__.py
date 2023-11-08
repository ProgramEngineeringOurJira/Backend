from .documents import Comment, Issue, Sprint, User, UserAssignedWorkplace, Workplace

__beanie_models__ = [User, Workplace, Sprint, UserAssignedWorkplace, Issue, Comment]


__all__ = [
    "__beanie_models__",
]
