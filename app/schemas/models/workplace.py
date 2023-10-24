from typing import Optional

from pydantic import BaseModel, Field


class WorkplaceCreation(BaseModel):
    name: str
    description: Optional[str] = None

class FileModelOut(BaseModel):
    URL : str = Field()
