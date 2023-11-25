from typing import List

from pydantic import BaseModel, Field

from app.schemas.documents import Issue, Sprint
from app.schemas.types import State


class Column(BaseModel):
    name: State
    issues: List[Issue] = Field(default_factory=list)

    @staticmethod
    def group(issues: List[Issue]) -> List["Column"]:
        columns = [Column(name=state) for state in State]
        for issue in issues:
            for column in columns:
                if issue.state == column.name:
                    column.issues.append(issue)
        return columns


class SprintResponse(Sprint):
    workplace_id: None = Field(default=None, exclude=True)
    columns: List[Column] = Field(default_factory=list)
