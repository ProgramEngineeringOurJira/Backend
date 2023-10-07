from datetime import datetime
from enum import StrEnum
from typing import Optional

from pydantic import BaseModel, EmailStr


class Token(BaseModel):
    access_token: str
    refresh_token: str


class TokenType(StrEnum):
    ACCESS = "ACCESS"
    REFRESH = "REFRESH"


class TokenData(BaseModel):
    email: Optional[str] = None
    exp: Optional[datetime] = None


class UserRegister(BaseModel):
    email: EmailStr
    password: str
