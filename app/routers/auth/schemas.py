from datetime import datetime
from enum import StrEnum
from typing import Optional
from uuid import UUID

from beanie import Document, Indexed
from beanie.odm.documents import PydanticObjectId
from pydantic import BaseModel, EmailStr, Field



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

class User(Document, UserRegister):
    email: Indexed(str, unique=True)

    @property
    def created(self) -> datetime:
        """Datetime user was created from ID"""
        return self.id.generation_time

    @classmethod
    async def by_email(cls, email: str) -> "User":
        """Get a user by email"""
        return await cls.find_one(cls.email == email)


class SuccessfulResponse(BaseModel):
    details: str = Field("Выполнено", title="Статус операции")


# Role и UserAssignedWorkplace лежат тут чтобы избежать зацикливания импортов, поскольку эти классы используются в oauth


class Role(StrEnum):
    ADMIN = "ADMIN"
    MEMBER = "MEMBER"
    GUEST = "GUEST"


class UserAssignedWorkplace(Document):
    user_id: PydanticObjectId
    workplace_id: UUID
    role: Role
