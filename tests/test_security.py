import importlib

from fastapi.testclient import TestClient

from odin_rag_mcp.auth import create_access_token


def _reload_app(monkeypatch, **env):
    for key, value in env.items():
        monkeypatch.setenv(key, value)

    import api.main as api_main
    import odin_rag_mcp.config as config_module

    importlib.reload(config_module)
    importlib.reload(api_main)
    return TestClient(api_main.app)


def test_api_key_is_required_when_configured(monkeypatch):
    client = _reload_app(monkeypatch, ODIN_API_KEY="super-secret-key")

    response = client.get("/health")
    assert response.status_code == 401

    response = client.get("/health", headers={"X-API-Key": "super-secret-key"})
    assert response.status_code == 200


def test_invalid_provider_is_rejected(monkeypatch):
    client = _reload_app(monkeypatch, ODIN_API_KEY="super-secret-key")

    response = client.post(
        "/chat",
        json={"question": "hello", "provider": "malicious"},
        headers={"X-API-Key": "super-secret-key"},
    )

    assert response.status_code == 422


def test_question_length_is_limited(monkeypatch):
    client = _reload_app(monkeypatch, ODIN_API_KEY="super-secret-key")

    large_question = "A" * 5000
    response = client.post(
        "/chat",
        json={"question": large_question},
        headers={"X-API-Key": "super-secret-key"},
    )

    assert response.status_code == 422


def test_rate_limit_is_enforced(monkeypatch):
    client = _reload_app(
        monkeypatch,
        ODIN_API_KEY="super-secret-key",
        RATE_LIMIT_PER_MINUTE="2",
        RATE_LIMIT_WINDOW_SECONDS="60",
    )

    headers = {"X-API-Key": "super-secret-key"}

    assert client.get("/health", headers=headers).status_code == 200
    assert client.get("/health", headers=headers).status_code == 200

    response = client.get("/health", headers=headers)
    assert response.status_code == 429
    assert response.json()["detail"] == "Rate limit exceeded."


def test_jwt_auth_is_enforced_when_secret_is_configured(monkeypatch):
    client = _reload_app(monkeypatch, JWT_SECRET="this-is-a-long-jwt-secret-1234567890")

    missing_token = client.get("/health")
    assert missing_token.status_code == 401

    token = create_access_token({"sub": "user-123"})
    authorized = client.get("/health", headers={"Authorization": f"Bearer {token}"})
    assert authorized.status_code == 200


def test_audit_log_records_recent_request(monkeypatch):
    client = _reload_app(monkeypatch, JWT_SECRET="this-is-a-long-jwt-secret-1234567890")
    token = create_access_token({"sub": "auditor"})

    response = client.get("/health", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200

    audit_response = client.get("/audit", headers={"Authorization": f"Bearer {token}"})
    assert audit_response.status_code == 200
    payload = audit_response.json()
    assert payload["count"] >= 1


def test_langsmith_settings_are_loaded_when_enabled(monkeypatch):
    monkeypatch.setenv("LANGSMITH_API_KEY", "ls_test_key")
    monkeypatch.setenv("LANGCHAIN_TRACING_V2", "true")
    monkeypatch.setenv("LANGCHAIN_PROJECT", "odin-rag-mcp-tests")

    import odin_rag_mcp.config as config_module

    importlib.reload(config_module)

    assert config_module.settings.langsmith_enabled is True
    assert config_module.settings.langchain_project == "odin-rag-mcp-tests"


def test_request_tracing_and_metrics_are_available(monkeypatch):
    client = _reload_app(monkeypatch, JWT_SECRET="this-is-a-long-jwt-secret-1234567890")
    token = create_access_token({"sub": "metrics-user"})

    response = client.get("/health", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert "X-Trace-Id" in response.headers

    metrics_response = client.get("/metrics", headers={"Authorization": f"Bearer {token}"})
    assert metrics_response.status_code == 200
    payload = metrics_response.json()
    assert payload["total_requests"] >= 1
    assert payload["average_latency_ms"] >= 0
