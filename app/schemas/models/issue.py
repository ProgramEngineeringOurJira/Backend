from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field

from ..types import Label, Priority, State


class IssueBase(BaseModel):
    name: str
    text: str
    priority: Priority
    state: State
    label: Label


class IssueCreation(IssueBase):
    sprint_id: UUID
    implementers: List[UUID] = Field(default=list())
    creation_date: datetime = Field(default_factory=datetime.now)
    end_date: datetime = Field(default_factory=datetime.now)


class IssueUpdate(BaseModel):
    name: Optional[str]
    text: Optional[str]
    priority: Optional[Priority]
    state: Optional[State]
    label: Optional[Label]
    sprint_id: Optional[UUID] = None
    implementers: Optional[List[UUID]]
    end_date: Optional[datetime]
