from pydantic import BaseModel


class SearchModel(BaseModel):
    start_string: str
