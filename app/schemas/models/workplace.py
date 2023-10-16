from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field



class WorkplaceCreation(BaseModel):
    name: str
    description: Optional[str] = None