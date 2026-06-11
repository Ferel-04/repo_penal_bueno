from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, field_validator


class SearchInput(BaseModel):
    query: str


class FactInput(BaseModel):
    facts: str
    crime_type: str | None = None


class FamilyViolenceReviewDecision(BaseModel):
    diligence_id: str = Field(min_length=1)
    fingerprint: str = Field(min_length=64, max_length=64)
    status: Literal["pending", "approved", "rejected"]
    observations: str


class FamilyViolenceReviewRecord(BaseModel):
    schema_version: Literal[1]
    crime_type: Literal["violencia_familiar"]
    reviewer_name: str = Field(min_length=1)
    reviewed_at: datetime
    decisions: list[FamilyViolenceReviewDecision]

    @field_validator("reviewer_name")
    @classmethod
    def normalize_reviewer_name(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("El nombre de la persona revisora es obligatorio.")
        return normalized
