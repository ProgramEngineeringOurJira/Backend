from datetime import datetime
from typing import List
from uuid import UUID, uuid4

from beanie import Document, Link
from pydantic import BaseModel, Field, model_validator

from app.core.exceptions import ValidationError

from .issue import Issue

# from .workplace import Workplace


class SprintCreation(BaseModel):
    name: str
    start_date: datetime
    end_date: datetime

    @model_validator(mode="after")
    def validate_date_order(self) -> "SprintCreation":
        if self.start_date > self.end_date:
            raise ValidationError("Дата окончания спринта должна быть позже даты начала.")
        return self


class Sprint(Document, SprintCreation):
    # workplace_id: BackLink[Workplace]
    workplace_id: UUID
    id: UUID = Field(default_factory=uuid4)
    issues: List[Link[Issue]] = Field(default_factory=list)
