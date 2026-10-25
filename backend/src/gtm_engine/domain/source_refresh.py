"""KB-001 source calendar and records; never changes playbook content."""

from datetime import UTC, date, datetime, timedelta
from typing import Literal
from urllib.parse import urlsplit

from pydantic import BaseModel, ConfigDict, Field, field_validator

INTERVAL = timedelta(days=45)


class SourceRecord(BaseModel):
    model_config = ConfigDict(extra="forbid")
    source_id: str = Field(min_length=1)
    title: str = Field(min_length=1)
    publisher: str = Field(min_length=1)
    url: str
    publication_date: date | None = None
    methodology_notes: str = Field(min_length=1)
    applicability: str = Field(min_length=1)
    status: Literal["draft", "approved", "deprecated"] = "draft"
    last_checked_at: datetime | None = None
    last_attempted_at: datetime | None = None
    last_error: str | None = None
    etag: str | None = None
    last_modified: str | None = None
    sha256: str | None = None

    @field_validator("url")
    @classmethod
    def public_url_shape(cls, value):
        parts = urlsplit(value)
        if (parts.scheme != "https" or not parts.hostname or parts.username or parts.password
                or parts.query or parts.fragment or parts.port not in (None, 443)):
            raise ValueError("Only credential-free HTTPS source URLs without query are allowed")
        return value

    @field_validator("last_checked_at", "last_attempted_at")
    @classmethod
    def aware_utc(cls, value):
        if value is not None:
            if value.tzinfo is None or value.utcoffset() is None:
                raise ValueError("Source timestamps require timezone")
            return value.astimezone(UTC)
        return value

    @field_validator("sha256")
    @classmethod
    def valid_hash(cls, value):
        if value is not None and (len(value) != 64 or any(c not in "0123456789abcdef" for c in value)):
            raise ValueError("Expected SHA-256 digest")
        return value


def due(source: SourceRecord, now: datetime) -> bool:
    if now.tzinfo is None or now.utcoffset() is None:
        raise ValueError("Calendar clock requires timezone")
    return source.status == "approved" and (
        source.last_checked_at is None or now - source.last_checked_at >= INTERVAL)
