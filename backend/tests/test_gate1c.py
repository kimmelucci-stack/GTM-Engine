import json

from gtm_engine.gate1c import NAMES, readiness


def test_missing_configuration_never_claims_access(tmp_path):
    report = readiness(tmp_path, {})
    assert report["missing_settings"] == list(NAMES)
    assert report["gate_status"] == "NOT_TESTED"
    assert report["network_requests"] == 0


def test_configured_does_not_mean_tested_and_does_not_leak_values(tmp_path):
    settings = dict(zip(NAMES, ["synthetic-private-value", "123", "456", "v99.0"]))
    report = readiness(tmp_path, settings)
    assert report["readiness"] == "configuration_present_access_unverified"
    assert set(report["provider_access"].values()) == {"not_tested"}
    assert all(value not in json.dumps(report) for value in settings.values())


def test_unprotected_env_is_not_read(tmp_path, monkeypatch):
    from types import SimpleNamespace

    monkeypatch.setattr("gtm_engine.gate1c.subprocess.run",
                        lambda *a, **kw: SimpleNamespace(returncode=1))
    (tmp_path / ".env").write_text('META_ACCESS_TOKEN="do-not-expose"', encoding="utf-8")
    report = readiness(tmp_path, {})
    assert report["configuration_error"] == "local_env_not_protected"
    assert "META_ACCESS_TOKEN" in report["missing_settings"]
    assert "do-not-expose" not in json.dumps(report)


def test_invalid_identifiers_are_reported_without_values(tmp_path):
    report = readiness(tmp_path, {"META_APP_ID": "private-invalid-input"})
    assert report["invalid_setting_names"] == ["META_APP_ID"]
    assert "private-invalid-input" not in json.dumps(report)
