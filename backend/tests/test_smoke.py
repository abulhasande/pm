from fastapi.testclient import TestClient

from app import main as backend
from app.main import app

client = TestClient(app)


def test_root_serves_html() -> None:
    response = client.get("/")

    assert response.status_code == 200
    assert response.text.strip()
    assert (
        "Hello world" in response.text
        or "Kanban Studio" in response.text
        or "Project board" in response.text
    )


def test_api_hello() -> None:
    response = client.get("/api/hello")

    assert response.status_code == 200
    assert response.json()["message"] == "Hello from the Project Management backend"


def test_health_check() -> None:
    response = client.get("/api/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_ai_test_success(monkeypatch) -> None:
    def fake_call_openrouter(prompt: str, *, system_prompt=None, response_format=None):
        assert prompt == "Compute 2 + 2 and respond with just the number."
        return "4"

    monkeypatch.setenv("OPENROUTER_API_KEY", "demo-key")
    monkeypatch.setattr(backend, "call_openrouter", fake_call_openrouter)

    response = client.get("/api/ai/test")

    assert response.status_code == 200
    assert response.json()["ok"] is True
    assert response.json()["answer"] == "4"


def test_ai_test_missing_key(monkeypatch) -> None:
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)

    response = client.get("/api/ai/test")

    assert response.status_code == 200
    payload = response.json()
    assert payload["ok"] is False
    assert "OPENROUTER_API_KEY" in payload["error"]


def test_ai_chat_accepts_structured_board_update(monkeypatch, tmp_path) -> None:
    backend.DATABASE_PATH = tmp_path / "structured-ai.sqlite3"
    backend.init_database()

    def fake_call_openrouter(prompt: str, *, system_prompt=None, response_format=None):
        return '{"answer": "Updated the task title.", "board_update": {"columns": [{"id": "col-backlog", "title": "Backlog", "cardIds": ["card-1"]}], "cards": {"card-1": {"id": "card-1", "title": "Renamed task", "details": "Updated details"}}}}'

    monkeypatch.setenv("OPENROUTER_API_KEY", "demo-key")
    monkeypatch.setattr(backend, "call_openrouter", fake_call_openrouter)

    response = client.post(
        "/api/users/user/ai",
        json={"question": "Rename the first task to Renamed task.", "history": []},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["answer"] == "Updated the task title."
    assert payload["board"]["cards"]["card-1"]["title"] == "Renamed task"


def test_ai_chat_rejects_invalid_json(monkeypatch, tmp_path) -> None:
    backend.DATABASE_PATH = tmp_path / "structured-ai-invalid.sqlite3"
    backend.init_database()

    def fake_call_openrouter(prompt: str, *, system_prompt=None, response_format=None):
        return "not valid json"

    monkeypatch.setenv("OPENROUTER_API_KEY", "demo-key")
    monkeypatch.setattr(backend, "call_openrouter", fake_call_openrouter)

    response = client.post(
        "/api/users/user/ai",
        json={"question": "Do something.", "history": []},
    )

    assert response.status_code == 400
    assert "Invalid AI response" in response.json()["detail"]
