from fastapi.testclient import TestClient

from app import main as backend


def make_client(tmp_path):
    backend.DATABASE_PATH = tmp_path / "board_api.sqlite3"
    backend.init_database()
    return TestClient(backend.app)


def test_get_board_creates_default_board(tmp_path) -> None:
    client = make_client(tmp_path)

    response = client.get("/api/users/user/board")

    assert response.status_code == 200
    data = response.json()
    assert [column["id"] for column in data["columns"]] == [
        "col-backlog",
        "col-discovery",
        "col-progress",
        "col-review",
        "col-done",
    ]
    assert "card-1" in data["cards"]
    assert data["cards"]["card-1"]["title"] == "Align roadmap themes"


def test_create_and_delete_card(tmp_path) -> None:
    client = make_client(tmp_path)

    create_response = client.post(
        "/api/users/user/cards",
        json={"columnId": "col-backlog", "title": "New task", "details": "Add later"},
    )

    assert create_response.status_code == 200
    board = create_response.json()
    assert any(card["title"] == "New task" for card in board["cards"].values())

    created_card_id = next(
        card_id for card_id, card in board["cards"].items() if card["title"] == "New task"
    )

    delete_response = client.delete(f"/api/users/user/cards/{created_card_id}")

    assert delete_response.status_code == 200
    assert all(card["title"] != "New task" for card in delete_response.json()["cards"].values())


def test_patch_column_and_replace_board_state(tmp_path) -> None:
    client = make_client(tmp_path)

    rename_response = client.patch(
        "/api/users/user/columns/col-backlog",
        json={"title": "Priority"},
    )
    assert rename_response.status_code == 200
    renamed_board = rename_response.json()
    assert next(column["title"] for column in renamed_board["columns"] if column["id"] == "col-backlog") == "Priority"

    update_payload = {
        "columns": [
            {"id": "col-backlog", "title": "Priority", "cardIds": ["card-1"]},
            {"id": "col-progress", "title": "In Progress", "cardIds": []},
            {"id": "col-discovery", "title": "Discovery", "cardIds": []},
            {"id": "col-review", "title": "Review", "cardIds": []},
            {"id": "col-done", "title": "Done", "cardIds": []},
        ],
        "cards": {
            "card-1": {"id": "card-1", "title": "Updated task", "details": "Changed details"}
        },
    }

    replace_response = client.put("/api/users/user/board", json=update_payload)

    assert replace_response.status_code == 200
    updated_board = replace_response.json()
    assert updated_board["cards"]["card-1"]["title"] == "Updated task"
    assert updated_board["columns"][0]["cardIds"] == ["card-1"]
