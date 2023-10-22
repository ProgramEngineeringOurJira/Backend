from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class CommentBase(BaseModel):
    name: str
    text: str


class CommentCreation(CommentBase):
    files: List[UUID] = Field(default=list())


class CommentUpdate(BaseModel):
    name: Optional[str]
    text: Optional[str]
    files: Optional[List[UUID]]
