from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class WorkplaceCreation(BaseModel):
    name: str
    description: Optional[str] = None


class FileModelOut(BaseModel):
    url: str


class InviteModel(BaseModel):
    email: EmailStr
