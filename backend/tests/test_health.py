from fastapi.testclient import TestClient

from gtm_engine.api import app


def test_process_health_does_not_claim_provider_readiness() -> None:
    with TestClient(app) as client:
        response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "gtm-engine-api"}
