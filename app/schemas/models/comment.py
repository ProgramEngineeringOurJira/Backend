from typing import List, Optional

from pydantic import BaseModel, Field


class CommentCreation(BaseModel):
    text: str
    files: Optional[List[str]] = Field(default=list())


class CommentUpdate(BaseModel):
    text: Optional[str]
    files: Optional[List[str]]
