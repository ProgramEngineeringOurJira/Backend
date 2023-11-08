from typing import List, Optional

from pydantic import BaseModel, Field


class CommentCreation(BaseModel):
    name: str
    text: str
    files: List[str] = Field(default=list())


class CommentUpdate(BaseModel):
    name: Optional[str]
    text: Optional[str]
    files: Optional[List[str]]
