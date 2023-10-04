from typing import List, Optional
from uuid import UUID, uuid4

from beanie import Document, Link
from pydantic import BaseModel, Field

from app.routers.auth.schemas import UserAssignedWorkplace


class WorkplaceCreation(BaseModel):
    name: str
    description: Optional[str] = None


class Workplace(Document, WorkplaceCreation):
    id: UUID = Field(default_factory=uuid4)
    states: List[str] = Field(default=["Backlog", "To do", "In Progress", "In Review", "QA", "Done"])
    users: list[Link[UserAssignedWorkplace]] = Field(default=list())
