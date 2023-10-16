from typing import Optional

from pydantic import BaseModel


class WorkplaceCreation(BaseModel):
    name: str
    description: Optional[str] = None
