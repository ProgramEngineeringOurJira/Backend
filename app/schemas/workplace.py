from enum import StrEnum
from typing import List, Optional
from uuid import UUID, uuid4

from beanie import Document, Link
from beanie.odm.documents import PydanticObjectId
from pydantic import BaseModel, Field

from .issue import Issue
from .sprint import Sprint


class WorkplaceCreation(BaseModel):
    name: str
    description: Optional[str] = None


class Role(StrEnum):
    ADMIN = "ADMIN"
    MEMBER = "MEMBER"
    GUEST = "GUEST"


class UserAssignedWorkplace(Document):
    user_id: PydanticObjectId
    workplace_id: UUID
    role: Role


def states():
    return ["Backlog", "To do", "In Progress", "In Review", "QA", "Done"]


class Workplace(Document, WorkplaceCreation):
    id: UUID = Field(default_factory=uuid4)
    states: List[str] = Field(default_factory=states)
    users: List[Link[UserAssignedWorkplace]] = Field(default_factory=list)
    sprints: List[Link[Sprint]] = Field(default_factory=list)
    issues: List[Link[Issue]] = Field(default_factory=list)
