from datetime import datetime
from typing import List
from uuid import UUID, uuid4

from beanie import BackLink, Document, Indexed, Link
from beanie.odm.documents import PydanticObjectId
from pydantic import Field

from .models.auth import UserRegister
from .models.models import IssueCreation, SprintCreation, WorkplaceCreation
from .types import Role, states


class User(Document, UserRegister):
    email: Indexed(str, unique=True)
    password: str = Field(exclude=True)

    @property
    def created(self) -> datetime:
        """Datetime user was created from ID"""
        return self.id.generation_time

    @classmethod
    async def by_email(cls, email: str) -> "User":
        """Get a user by email"""
        return await cls.find_one(cls.email == email)


class UserAssignedWorkplace(Document):
    user_id: PydanticObjectId
    workplace_id: UUID
    role: Role


class Workplace(Document, WorkplaceCreation):
    id: UUID = Field(default_factory=uuid4)
    states: List[str] = Field(default_factory=states)
    users: List[Link["UserAssignedWorkplace"]] = Field(default_factory=list, exclude=True)
    sprints: List[Link["Sprint"]] = Field(default_factory=list)
    issues: List[Link["Issue"]] = Field(default_factory=list)


class Sprint(Document, SprintCreation):
    id: UUID = Field(default_factory=uuid4)
    workplace_id: BackLink["Workplace"] = Field(original_field="sprints", exclude=True)
    issues: List[Link["Issue"]] = Field(default_factory=list)


class Issue(Document, IssueCreation):
    id: UUID = Field(default_factory=uuid4)
    creation_date: datetime = Field(default_factory=datetime.now)
    workplace_id: BackLink["Workplace"] = Field(original_field="issues", exclude=True)
    author_id: PydanticObjectId
    implementers: List[PydanticObjectId] = Field(default_factory=list)
    # comments: List[Link["Comment"]]
