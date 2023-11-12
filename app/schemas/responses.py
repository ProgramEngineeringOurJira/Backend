from uuid import UUID

from pydantic import Field

from app.schemas.documents import (
    CommentNoBackLinks,
    IssueNoBackLinks,
    SprintNoBackLinks,
    UAWNoBackLinks,
    User,
    Workplace,
)


class UserResponse(User):
    id: UUID = Field(alias="id")


class WorkplaceResponse(Workplace):
    id: UUID = Field(alias="id")


class SprintResponse(SprintNoBackLinks):
    id: UUID = Field(alias="id")


class IssueResponse(IssueNoBackLinks):
    id: UUID = Field(alias="id")


class UserAssignedWorkplaceResponse(UAWNoBackLinks):
    id: UUID = Field(alias="id")


class CommentResponse(CommentNoBackLinks):
    id: UUID = Field(alias="id")
