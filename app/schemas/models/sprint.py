from datetime import datetime

from pydantic import BaseModel, model_validator

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
