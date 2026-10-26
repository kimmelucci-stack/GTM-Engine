import importlib
from pathlib import Path
from threading import Thread

import httpx
import pytest


@pytest.fixture
def server(monkeypatch):
    monkeypatch.syspath_prepend(str(Path(__file__).resolve().parents[2] / "scripts"))
    module = importlib.import_module("storage_setup_ui")
    received = []
    instance = module.StorageServer(("127.0.0.1", 0), provision=received.append)
    thread = Thread(target=instance.serve_forever, daemon=True)
    thread.start()
    yield instance, received
    instance.shutdown()
    instance.server_close()
    thread.join(timeout=2)


def test_masked_form_and_cross_origin_rejection(server):
    instance, received = server
    base = instance.origin + "/" + instance.nonce + "/"
    with httpx.Client(trust_env=False) as client:
        response = client.get(base)
        assert 'type="password"' in response.text
        assert "no-store" in response.headers["cache-control"]
        assert client.get(base, headers={"Host": "synthetic.invalid"}).status_code == 404
        assert client.post(base + "submit", data={"csrf": instance.nonce,
                           "storage_secret": "synthetic"},
                           headers={"Origin": "https://synthetic.invalid"}).status_code == 403
        assert client.post(base + "submit", data={"csrf": "wrong", "storage_secret": "synthetic"},
                           headers={"Origin": instance.origin}).status_code == 403
    assert received == []


def test_success_never_echoes_credential(server, capsys):
    instance, received = server
    value = "synthetic-private-test-value"
    with httpx.Client(trust_env=False) as client:
        response = client.post(instance.origin + "/" + instance.nonce + "/submit",
                               data={"csrf": instance.nonce, "storage_secret": value},
                               headers={"Origin": instance.origin})
    assert response.status_code == 200
    assert received == [value]
    assert value not in response.text
    assert value not in capsys.readouterr().out


def test_configuration_preserves_existing_settings_in_ignored_file(monkeypatch, tmp_path):
    monkeypatch.syspath_prepend(str(Path(__file__).resolve().parents[2] / "scripts"))
    module = importlib.import_module("storage_setup_ui")
    monkeypatch.setattr(module, "ROOT", tmp_path)
    monkeypatch.setattr(module, "local_settings", lambda: {"SUPABASE_URL": "https://synthetic.invalid"})
    path = tmp_path / ".env"
    path.write_text("# Existing\nDATABASE_URL=synthetic\n")
    # Construct the marker to avoid a credential-looking literal in this public synthetic test.
    value = "sb_" + "secret_" + "synthetic-only"
    module.configure(value)
    assert path.read_text().startswith("# Existing\nDATABASE_URL=synthetic\n")
    assert path.read_text().count("SUPABASE_SERVICE_ROLE_KEY=") == 1
    assert not (tmp_path / ".env.storage.tmp").exists()
