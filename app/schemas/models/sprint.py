from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, model_validator

from app.core import ValidationError


class SprintBase(BaseModel):
    name: str
    start_date: datetime
    end_date: datetime


# сделаем отдельный класс для модели, потому что каждый получаемый спринт из базы зачем-то тоже валидировался
class SprintCreation(SprintBase):
    @model_validator(mode="after")
    def validate_date_order(self) -> "SprintCreation":
        if self.start_date > self.end_date:
            raise ValidationError("Дата окончания спринта должна быть позже даты начала.")
        return self


class SprintUpdate(BaseModel):
    name: Optional[str] = Field(default=None)
    start_date: Optional[datetime] = Field(default=None)
    end_date: Optional[datetime] = Field(default=None)
