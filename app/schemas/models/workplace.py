from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class WorkplaceCreation(BaseModel):
    name: str
    description: Optional[str] = Field(default=None)


class WorkplaceUpdate(BaseModel):
    name: Optional[str] = Field(default=None)
    description: Optional[str] = Field(default=None)


class FileModelOut(BaseModel):
    url: str


class InviteModel(BaseModel):
    email: EmailStr
