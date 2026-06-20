from __future__ import annotations

from pydantic import BaseModel, Field, field_validator

from src.db.repository import safe_identifier


def clean_user_id(value: str | None = None) -> str:
    return safe_identifier(str(value or "default").replace("..", ""), fallback="default")


class ReportGenerateRequest(BaseModel):
    user_id: str = "default"
    strategy_name: str = "trend_default"

    @field_validator("user_id", mode="before")
    @classmethod
    def validate_user_id(cls, value: str | None) -> str:
        return clean_user_id(value)

    @field_validator("strategy_name", mode="before")
    @classmethod
    def validate_strategy_name(cls, value: str | None) -> str:
        return safe_identifier(value or "trend_default", fallback="trend_default")


class ReportListQuery(BaseModel):
    user_id: str = "default"
    page: int = Field(default=1)
    page_size: int = Field(default=20)

    @field_validator("user_id", mode="before")
    @classmethod
    def validate_user_id(cls, value: str | None) -> str:
        return clean_user_id(value)

    @field_validator("page", mode="before")
    @classmethod
    def validate_page(cls, value: int | str | None) -> int:
        try:
            page = int(value or 1)
        except (TypeError, ValueError):
            return 1
        return max(page, 1)

    @field_validator("page_size", mode="before")
    @classmethod
    def validate_page_size(cls, value: int | str | None) -> int:
        try:
            page_size = int(value or 20)
        except (TypeError, ValueError):
            return 20
        return min(max(page_size, 1), 100)


class UserQuery(BaseModel):
    user_id: str = "default"

    @field_validator("user_id", mode="before")
    @classmethod
    def validate_user_id(cls, value: str | None) -> str:
        return clean_user_id(value)
