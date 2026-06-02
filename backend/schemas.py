from pydantic import BaseModel


class SearchInput(BaseModel):
    query: str


class FactInput(BaseModel):
    facts: str
    crime_type: str | None = None
