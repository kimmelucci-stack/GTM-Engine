import hashlib
from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from gtm_engine.knowledge import KnowledgeError, KnowledgeRegistry, Playbook, load_phase


def fixture(tmp_path, **overrides):
    raw = b"# Synthetic methodology\nNot evidence about a client.\n"
    (tmp_path / "approved.md").write_bytes(raw)
    record = Playbook(**({"playbook_id": "synthetic", "title": "Synthetic methodology",
                          "discipline": "buyer_research", "version": "1",
                          "status": "approved", "path": "approved.md",
                          "sha256": hashlib.sha256(raw).hexdigest(),
                          "source_references": ("synthetic:source",),
                          "last_reviewed_at": datetime(2026, 10, 25, tzinfo=UTC)} | overrides))
    return KnowledgeRegistry(version="synthetic-v1", playbooks=[record],
                             phases={"map_buyers": ["synthetic"], "other": []})


def test_selective_load_records_exact_version_and_nature(tmp_path):
    registry = fixture(tmp_path)
    result = load_phase(tmp_path, registry, "map_buyers")
    assert len(result) == 1 and result[0].version == "1"
    assert result[0].sha256 == registry.playbooks[0].sha256
    assert result[0].nature == "methodology_not_project_evidence"
    assert load_phase(tmp_path, registry, "other") == ()


@pytest.mark.parametrize("status", ["draft", "deprecated"])
def test_unapproved_playbooks_never_loaded(tmp_path, status):
    with pytest.raises(KnowledgeError, match="not_approved"):
        load_phase(tmp_path, fixture(tmp_path, status=status), "map_buyers")


def test_changed_content_requires_review_not_silent_update(tmp_path):
    registry = fixture(tmp_path)
    (tmp_path / "approved.md").write_text("Changed synthetic file", encoding="utf-8")
    with pytest.raises(KnowledgeError, match="changed_review"):
        load_phase(tmp_path, registry, "map_buyers")


@pytest.mark.parametrize("path", ["../outside.md", "/absolute.md", "script.py"])
def test_path_escape_and_non_markdown_rejected(tmp_path, path):
    with pytest.raises(KnowledgeError, match="path"):
        load_phase(tmp_path, fixture(tmp_path, path=path), "map_buyers")


def test_size_limit_is_enforced_without_truncating_methodology(tmp_path):
    with pytest.raises(KnowledgeError, match="size_limit"):
        load_phase(tmp_path, fixture(tmp_path), "map_buyers", max_bytes=4)


def test_unknown_phase_and_registry_references_fail_explicitly(tmp_path):
    registry = fixture(tmp_path)
    with pytest.raises(KnowledgeError, match="unknown_phase"):
        load_phase(tmp_path, registry, "unknown")
    with pytest.raises(ValidationError):
        KnowledgeRegistry(version="synthetic", playbooks=registry.playbooks,
                          phases={"map_buyers": ["not_registered"]})
