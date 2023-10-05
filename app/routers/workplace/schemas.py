from typing import List, Optional
from uuid import UUID, uuid4

from beanie import Document, Link
from pydantic import BaseModel, Field

from app.routers.auth.schemas import UserAssignedWorkplace
from app.routers.sprint import Sprint


class WorkplaceCreation(BaseModel):
    name: str
    description: Optional[str] = None


def states():
    return ["Backlog", "To do", "In Progress", "In Review", "QA", "Done"]


class Workplace(Document, WorkplaceCreation):
    id: UUID = Field(default_factory=uuid4)
    states: List[str] = Field(default_factory=states)
    users: List[Link[UserAssignedWorkplace]] = Field(default_factory=list)
    sprints: List[Link[Sprint]] = Field(default_factory=list)
