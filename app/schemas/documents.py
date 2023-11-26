from datetime import datetime
from typing import List
from uuid import UUID, uuid4

from beanie import BackLink, Delete, Document, Indexed, Link, WriteRules, before_event
from beanie.odm.operators.find.logical import And, Or
from pydantic import Field

from app.core.exceptions import ValidationError

from .models import CommentCreation, IssueBase, SprintCreation, UserRegister, WorkplaceCreation
from .types import Role


class User(Document, UserRegister):
    id: UUID = Field(default_factory=uuid4)
    email: Indexed(str, unique=True)
    password: str = Field(exclude=True)
    name: str = Field()

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
    role: Role
    workplace: BackLink["Workplace"] = Field(original_field="users", exclude=True)
    workplace_id: UUID = Field(exclude=True)

    @before_event(Delete)
    async def delete_refs(self):
        self.user = None

    def __hash__(self):
        return hash(self.id)

    def __eq__(self, other):
        if not isinstance(other, (UserAssignedWorkplace, UUID)):
            return False
        id = other if isinstance(other, UUID) else other.id
        return self.id == id


class Workplace(Document, WorkplaceCreation):
    id: UUID = Field(default_factory=uuid4)
    users: List[Link["UserAssignedWorkplace"]] = Field(default_factory=list, exclude=True)
    sprints: List[Link["Sprint"]] = Field(default_factory=list)

    @before_event(Delete)
    async def delete_refs(self):
        await UserAssignedWorkplace.find(UserAssignedWorkplace.workplace_id == self.id).delete()
        await Comment.find(Comment.workplace_id == self.id).delete()
        await Issue.find(Issue.workplace_id == self.id).delete()
        await Sprint.find(Sprint.workplace_id == self.id).delete()


class Sprint(Document, SprintCreation):
    id: UUID = Field(default_factory=uuid4)
    issues: List[Link["Issue"]] = Field(default_factory=list, exclude=True)
    workplace: BackLink["Workplace"] = Field(original_field="sprints", exclude=True)
    workplace_id: UUID = Field(exclude=True)

    @before_event(Delete)
    async def delete_refs(self):
        self.workplace.sprints.remove(self.id)
        await self.workplace.save(link_rule=WriteRules.WRITE)
        await Comment.find(Comment.sprint_id == self.id).delete()
        await Issue.find(Issue.sprint_id == self.id).delete()

    async def validate_creation(sprint_creation: SprintCreation, workplace_id: UUID, sprint_id: UUID = None):
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
    end_date: datetime = Field(default_factory=datetime.now)
    author: Link["UserAssignedWorkplace"]
    implementers: List[Link["UserAssignedWorkplace"]] = Field(default_factory=list)
    comments: List[Link["Comment"]] = Field(default_factory=list)
    sprint: BackLink["Sprint"] = Field(default=None, original_field="issues", exclude=True)
    workplace_id: UUID = Field(exclude=True)
    sprint_id: UUID = Field(exclude=True)
    files: List[str] = Field(default_factory=list)

    @before_event(Delete)
    async def delete_refs(self):
        self.sprint.issues.remove(self.id)
        await self.sprint.save(link_rule=WriteRules.WRITE)
        await Comment.find(Comment.issue_id == self.id).delete()

    def __eq__(self, other):
        if not isinstance(other, (Issue, UUID)):
            return False
        id = other if isinstance(other, UUID) else other.id
        return self.id == id


class Comment(Document, CommentCreation):
    id: UUID = Field(default_factory=uuid4)
    creation_date: datetime = Field(default_factory=datetime.now)
    author: Link["UserAssignedWorkplace"]
    issue: BackLink["Issue"] = Field(default=None, original_field="comments", exclude=True)
    workplace_id: UUID = Field(exclude=True)
    sprint_id: UUID = Field(exclude=True)
    issue_id: UUID = Field(exclude=True)
    files: List[str] = Field(default_factory=list)

    @before_event(Delete)
    async def delete_refs(self):
        self.issue.comments.remove(self.id)
        await self.issue.save(link_rule=WriteRules.WRITE)

    def __eq__(self, other):
        if not isinstance(other, (Comment, UUID)):
            return False
        id = other if isinstance(other, UUID) else other.id
        return self.id == id
