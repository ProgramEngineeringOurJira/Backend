from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field, model_validator

from app.core import ValidationError

from ..types import Priority


class IssueCreation(BaseModel):
    name: str
    text: str
    priority: Priority
    state: str
    sprint_id: Optional[UUID] = None


class SprintCreation(BaseModel):
    name: str
    start_date: datetime
    end_date: datetime

    @model_validator(mode="after")
    def validate_date_order(self) -> "SprintCreation":
        if self.start_date > self.end_date:
            raise ValidationError("Дата окончания спринта должна быть позже даты начала.")
        return self


class WorkplaceCreation(BaseModel):
    name: str
    description: Optional[str] = None


class SuccessfulResponse(BaseModel):
    details: str = Field("Выполнено", title="Статус операции")
