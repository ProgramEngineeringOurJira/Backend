from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel,Field
from ..types import Priority


class IssueBase(BaseModel):
    name: str
    text: str
    priority: Priority
    state: str


class IssueCreation(IssueBase):
    sprint_id: Optional[UUID] = None
    implementers: List[UUID] = Field(default=list())

class IssueUpdate(BaseModel):
    name: Optional[str]
    text: Optional[str]
    priority: Optional[Priority]
    state: Optional[str]
    sprint_id: Optional[UUID] = None
    implementers: Optional[List[UUID]] 