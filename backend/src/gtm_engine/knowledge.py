"""Selective, read-only loading of explicitly approved, versioned Markdown playbooks."""

import hashlib
from datetime import datetime
from pathlib import Path, PureWindowsPath
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class KnowledgeError(Exception):
    """Fixed codes only; do not include paths or file contents in errors."""


class Playbook(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    playbook_id: str = Field(min_length=1)
    title: str = Field(min_length=1)
    discipline: str = Field(min_length=1)
    version: str = Field(min_length=1)
    status: Literal["approved", "draft", "deprecated"]
    path: str
    sha256: str = Field(pattern=r"^[a-f0-9]{64}$")
    source_references: tuple[str, ...] = Field(min_length=1)
    last_reviewed_at: datetime

    @field_validator("last_reviewed_at")
    @classmethod
    def aware_review(cls, value):
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("Review timestamp requires timezone")
        return value


class KnowledgeRegistry(BaseModel):
    model_config = ConfigDict(extra="forbid")
    version: str = Field(min_length=1)
    playbooks: list[Playbook]
    phases: dict[str, list[str]]

    @model_validator(mode="after")
    def valid_links(self):
        ids = {p.playbook_id for p in self.playbooks}
        if len(ids) != len(self.playbooks):
            raise ValueError("Duplicate playbook ID")
        for selected in self.phases.values():
            if not set(selected) <= ids or len(set(selected)) != len(selected):
                raise ValueError("Unknown or duplicate phase playbook")
        return self


class LoadedPlaybook(BaseModel):
    model_config = ConfigDict(frozen=True)
    playbook_id: str
    version: str
    sha256: str
    source_references: tuple[str, ...]
    content: str
    nature: Literal["methodology_not_project_evidence"] = "methodology_not_project_evidence"


def load_phase(root: Path, registry: KnowledgeRegistry, phase: str, *,
               max_bytes: int = 100_000, max_total_bytes: int = 300_000) -> tuple[LoadedPlaybook, ...]:
    if max_bytes <= 0 or max_total_bytes <= 0:
        raise KnowledgeError("invalid_size_limit")
    if phase not in registry.phases:
        raise KnowledgeError("unknown_phase")
    base = root.resolve()
    by_id = {p.playbook_id: p for p in registry.playbooks}
    loaded, total = [], 0
    for identifier in registry.phases[phase]:
        entry = by_id[identifier]
        if entry.status != "approved":
            raise KnowledgeError("playbook_not_approved")
        candidate = Path(entry.path)
        windows = PureWindowsPath(entry.path)
        if (candidate.anchor or windows.anchor or ".." in candidate.parts or ".." in windows.parts
                or candidate.suffix.lower() != ".md"):
            raise KnowledgeError("invalid_playbook_path")
        target = (base / candidate).resolve()
        if not target.is_relative_to(base):
            raise KnowledgeError("playbook_outside_knowledge_root")
        try:
            with target.open("rb") as handle:
                raw = handle.read(max_bytes + 1)
        except OSError:
            raise KnowledgeError("playbook_unreadable") from None
        total += len(raw)
        if len(raw) > max_bytes or total > max_total_bytes:
            raise KnowledgeError("knowledge_size_limit")
        digest = hashlib.sha256(raw).hexdigest()
        if digest != entry.sha256:
            raise KnowledgeError("playbook_changed_review_required")
        try:
            text = raw.decode("utf-8-sig")
        except UnicodeError:
            raise KnowledgeError("invalid_markdown_encoding") from None
        if not text.strip():
            raise KnowledgeError("empty_playbook")
        loaded.append(LoadedPlaybook(playbook_id=entry.playbook_id, version=entry.version,
                                     sha256=digest, source_references=entry.source_references,
                                     content=text))
    return tuple(loaded)
