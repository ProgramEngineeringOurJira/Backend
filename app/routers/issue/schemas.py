from datetime import datetime
from enum import StrEnum
from typing import List, Optional
from uuid import UUID, uuid4

from beanie import Document
from beanie.odm.documents import PydanticObjectId
from pydantic import BaseModel, Field


class Priority(StrEnum):
    LOW = "LOW"
    NORMAL = "NORMAL"
    HIGH = "HIGH"
    URGENT = "URGRENT"


class IssueCreation(BaseModel):
    name: str
    text: str
    priority: Priority
    state: str
    sprint_id: Optional[UUID] = None


class Issue(Document, IssueCreation):
    id: UUID = Field(default_factory=uuid4)
    creation_date: datetime = Field(default_factory=datetime.now)
    workplace_id: UUID
    author_id: PydanticObjectId
    implementers: List[PydanticObjectId]
    # comments: List[Link[Comment]]
