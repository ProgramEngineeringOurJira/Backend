from datetime import datetime
from uuid import UUID, uuid4

from beanie import Document
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel, Field, model_validator


class SprintCreation(BaseModel):
    name: str
    start_date: datetime
    end_date: datetime

    @model_validator(mode="after")
    def validate_date_order(self) -> "SprintCreation":
        if self.start_date > self.end_date:
            raise RequestValidationError("Дата окончания спринта должна быть позже даты начала.")
        return self


class Sprint(Document, SprintCreation):
    workplace_id: UUID
    id: UUID = Field(default_factory=uuid4)

    # Валидатор не может быть асинхронным, поэтому это функция
    async def validate_date_no_intersection(self):
        find_sprint = await Sprint.find(
            Sprint.start_date >= self.start_date, Sprint.start_date < self.end_date, Sprint.id != self.id
        ).first_or_none()
        if find_sprint is not None:
            raise RequestValidationError("Спринты не должны пересекаться по дате.")
        find_sprint = await Sprint.find(
            Sprint.end_date > self.start_date, Sprint.end_date <= self.end_date, Sprint.id != self.id
        ).first_or_none()
        if find_sprint is not None:
            raise RequestValidationError("Спринты не должны пересекаться по дате.")
        find_sprint = await Sprint.find(
            Sprint.start_date <= self.start_date, Sprint.end_date >= self.end_date, Sprint.id != self.id
        ).first_or_none()
        if find_sprint is not None:
            raise RequestValidationError("Спринты не должны пересекаться по дате.")
