from itertools import groupby
from typing import List

from pydantic import BaseModel, Field

from app.schemas.documents import Issue, Sprint


class Column(BaseModel):
    name: str
    issues: List[Issue]

    @staticmethod
    def group(issues: List[Issue]) -> List["Column"]:
        sorted_issues = sorted(issues, key=lambda issue: issue.state)
        grouped_issues = [
            Column(name=key.value, issues=result)
            for key, result in groupby(sorted_issues, key=lambda issue: issue.state)
        ]
        return grouped_issues


class SprintResponse(Sprint):
    workplace_id: None = Field(default=None, exclude=True)
    columns: List[Column] = Field(default_factory=list)
