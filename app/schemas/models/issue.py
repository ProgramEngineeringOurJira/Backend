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
    end_date: Optional[datetime] = Field(default=None)
    sprint_id: UUID


class IssueCreation(IssueBase):
    implementers: List[UUID] = Field(default=list())


class IssueUpdate(BaseModel):
    name: Optional[str] = Field(default=None)
    text: Optional[str] = Field(default=None)
    priority: Optional[Priority] = Field(default=None)
    state: Optional[State] = Field(default=None)
    label: Optional[Label] = Field(default=None)
    sprint_id: Optional[UUID] = Field(default=None)
    implementers: Optional[List[UUID]] = Field(default=None)
    end_date: Optional[datetime] = Field(default=None)
