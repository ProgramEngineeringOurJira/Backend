from datetime import datetime
from typing import List, Optional
from uuid import UUID, uuid4

from beanie import BackLink, Document, Indexed, Link
from beanie.odm.operators.find.logical import And, Or
from pydantic import Field

from app.core.exceptions import ValidationError

from .models.auth import UserRegister
from .models.models import IssueBase, SprintCreation, WorkplaceCreation
from .types import Role, states


class User(Document, UserRegister):
    id: UUID = Field(default_factory=uuid4)
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

    def __eq__(self, other):
        if not isinstance(other, (User, UUID)):
            return False
        id = other if isinstance(other, UUID) else other.id
        return self.id == id


class UserAssignedWorkplace(Document):
    id: UUID = Field(default_factory=uuid4)
    user: Link["User"]
    workplace_id: UUID
    role: Role

    def __eq__(self, other):
        if not isinstance(other, (UserAssignedWorkplace, UUID)):
            return False
        id = other if isinstance(other, UUID) else other.id
        return self.id == id


class Workplace(Document, WorkplaceCreation):
    id: UUID = Field(default_factory=uuid4)
    states: List[str] = Field(default_factory=states)
    users: List[Link["UserAssignedWorkplace"]] = Field(default_factory=list, exclude=True)
    sprints: List[Link["Sprint"]] = Field(default_factory=list)
    issues: List[Link["Issue"]] = Field(default_factory=list)


class Sprint(Document, SprintCreation):
    id: UUID = Field(default_factory=uuid4)
    workplace: BackLink["Workplace"] = Field(original_field="sprints", exclude=True)
    issues: List[Link["Issue"]] = Field(default_factory=list)

    async def validate_creation(
        sprint_creation: SprintCreation, workplace_id: UUID, sprint_id: UUID = None, check_self=False
    ):
        find_sprint = await Sprint.find_one(
            Sprint.workplace.id == workplace_id,
            Or(
                And(Sprint.start_date >= sprint_creation.start_date, Sprint.start_date < sprint_creation.end_date),
                And(Sprint.end_date > sprint_creation.start_date, Sprint.end_date <= sprint_creation.end_date),
                And(Sprint.start_date <= sprint_creation.start_date, Sprint.end_date >= sprint_creation.end_date),
            ),
            Sprint.id != sprint_id,
            fetch_links=True,
        )
        if find_sprint is not None:
            raise ValidationError("Спринты не должны пересекаться по дате.")

    def __eq__(self, other):
        if not isinstance(other, (Sprint, UUID)):
            return False
        id = other if isinstance(other, UUID) else other.id
        return self.id == id


class Issue(Document, IssueBase):
    id: UUID = Field(default_factory=uuid4)
    creation_date: datetime = Field(default_factory=datetime.now)
    workplace: BackLink["Workplace"] = Field(original_field="issues", exclude=True)
    author: Link["UserAssignedWorkplace"]
    sprint: Optional[BackLink["Sprint"]] = Field(original_field="issues", exclude=True)
    implementers: List[Link["UserAssignedWorkplace"]] = Field(default_factory=list)
    # comments: List[Link["Comment"]]

    def __eq__(self, other):
        if not isinstance(other, (Issue, UUID)):
            return False
        id = other if isinstance(other, UUID) else other.id
        return self.id == id
