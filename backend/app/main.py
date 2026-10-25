import json
import os
import sqlite3
import time
from pathlib import Path
from typing import Any

import httpx
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field, ValidationError

app = FastAPI(title="Project Management MVP Backend")

REPO_ROOT = Path(__file__).resolve().parents[2]
FRONTEND_BUILD_DIR = REPO_ROOT / "frontend" / "out"
DEFAULT_DATABASE_PATH = REPO_ROOT / "backend" / "data" / "pm.db"
DATABASE_PATH = Path(os.getenv("PM_DATABASE_PATH", str(DEFAULT_DATABASE_PATH)))
OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL", "openai/gpt-oss-120b")


def call_openrouter(
    prompt: str,
    *,
    system_prompt: str | None = None,
    response_format: dict[str, Any] | None = None,
) -> str:
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        raise RuntimeError("OPENROUTER_API_KEY is not configured.")

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost:8000",
        "X-Title": "Project Management MVP",
    }
    messages: list[dict[str, str]] = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})

    request_body: dict[str, Any] = {
        "model": OPENROUTER_MODEL,
        "messages": messages,
    }
    if response_format is not None:
        request_body["response_format"] = response_format

    response = httpx.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers=headers,
        json=request_body,
        timeout=30.0,
    )
    response.raise_for_status()

    payload = response.json()
    return payload["choices"][0]["message"]["content"]


class BoardAiUpdate(BaseModel):
    columns: list[dict[str, Any]] = Field(...)
    cards: dict[str, dict[str, Any]] = Field(...)


class BoardAiResponse(BaseModel):
    answer: str = Field(..., min_length=1)
    board_update: BoardAiUpdate | None = None


AI_OUTPUT_SCHEMA = {
    "type": "object",
    "properties": {
        "answer": {"type": "string"},
        "board_update": {
            "type": "object",
            "properties": {
                "columns": {"type": "array", "items": {"type": "object"}},
                "cards": {"type": "object", "additionalProperties": {"type": "object"}},
            },
            "required": ["columns", "cards"],
            "additionalProperties": True,
        },
    },
    "required": ["answer"],
    "additionalProperties": False,
}

DEFAULT_COLUMNS = [
    {"id": "col-backlog", "title": "Backlog"},
    {"id": "col-discovery", "title": "Discovery"},
    {"id": "col-progress", "title": "In Progress"},
    {"id": "col-review", "title": "Review"},
    {"id": "col-done", "title": "Done"},
]

DEFAULT_CARDS = [
    {"id": "card-1", "columnId": "col-backlog", "title": "Align roadmap themes", "details": "Draft quarterly themes with impact statements and metrics."},
    {"id": "card-2", "columnId": "col-backlog", "title": "Gather customer signals", "details": "Review support tags, sales notes, and churn feedback."},
    {"id": "card-3", "columnId": "col-discovery", "title": "Prototype analytics view", "details": "Sketch initial dashboard layout and key drill-downs."},
    {"id": "card-4", "columnId": "col-progress", "title": "Refine status language", "details": "Standardize column labels and tone across the board."},
    {"id": "card-5", "columnId": "col-progress", "title": "Design card layout", "details": "Add hierarchy and spacing for scanning dense lists."},
    {"id": "card-6", "columnId": "col-review", "title": "QA micro-interactions", "details": "Verify hover, focus, and loading states."},
    {"id": "card-7", "columnId": "col-done", "title": "Ship marketing page", "details": "Final copy approved and asset pack delivered."},
    {"id": "card-8", "columnId": "col-done", "title": "Close onboarding sprint", "details": "Document release notes and share internally."},
]


def get_connection() -> sqlite3.Connection:
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def init_database() -> None:
    DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)
    with get_connection() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS boards (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL UNIQUE,
                name TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(user_id) REFERENCES users(id)
            )
            """
        )
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS columns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                board_id INTEGER NOT NULL,
                external_id TEXT NOT NULL,
                title TEXT NOT NULL,
                position INTEGER NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(board_id, external_id),
                FOREIGN KEY(board_id) REFERENCES boards(id)
            )
            """
        )
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS cards (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                board_id INTEGER NOT NULL,
                column_id INTEGER NOT NULL,
                external_id TEXT NOT NULL,
                title TEXT NOT NULL,
                details TEXT NOT NULL DEFAULT '',
                position INTEGER NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(board_id, external_id),
                FOREIGN KEY(board_id) REFERENCES boards(id),
                FOREIGN KEY(column_id) REFERENCES columns(id)
            )
            """
        )


def ensure_user_and_board(username: str) -> int:
    with get_connection() as connection:
        user_row = connection.execute(
            "SELECT id FROM users WHERE username = ?",
            (username,),
        ).fetchone()

        if user_row is None:
            connection.execute(
                "INSERT INTO users (username, password_hash) VALUES (?, ?)",
                (username, "demo-password-hash"),
            )
            user_id = connection.execute(
                "SELECT id FROM users WHERE username = ?",
                (username,),
            ).fetchone()["id"]
        else:
            user_id = user_row["id"]

        board_row = connection.execute(
            "SELECT id FROM boards WHERE user_id = ?",
            (user_id,),
        ).fetchone()

        if board_row is None:
            connection.execute(
                "INSERT INTO boards (user_id, name) VALUES (?, ?)",
                (user_id, f"{username}'s board"),
            )
            board_id = connection.execute(
                "SELECT id FROM boards WHERE user_id = ?",
                (user_id,),
            ).fetchone()["id"]

            for index, column in enumerate(DEFAULT_COLUMNS):
                connection.execute(
                    "INSERT INTO columns (board_id, external_id, title, position) VALUES (?, ?, ?, ?)",
                    (board_id, column["id"], column["title"], index),
                )

            column_lookup = {
                row["external_id"]: row["id"]
                for row in connection.execute(
                    "SELECT id, external_id FROM columns WHERE board_id = ?",
                    (board_id,),
                ).fetchall()
            }

            for card in DEFAULT_CARDS:
                connection.execute(
                    "INSERT INTO cards (board_id, column_id, external_id, title, details, position) VALUES (?, ?, ?, ?, ?, ?)",
                    (
                        board_id,
                        column_lookup[card["columnId"]],
                        card["id"],
                        card["title"],
                        card["details"],
                        0,
                    ),
                )

            return board_id

        return board_row["id"]


def serialize_board(board_id: int) -> dict[str, Any]:
    with get_connection() as connection:
        columns = connection.execute(
            "SELECT id, external_id, title FROM columns WHERE board_id = ? ORDER BY position ASC",
            (board_id,),
        ).fetchall()
        cards = connection.execute(
            "SELECT id, column_id, external_id, title, details FROM cards WHERE board_id = ? ORDER BY position ASC",
            (board_id,),
        ).fetchall()

    card_map: dict[str, dict[str, Any]] = {}
    for card in cards:
        card_map[card["external_id"]] = {
            "id": card["external_id"],
            "title": card["title"],
            "details": card["details"],
        }

    columns_payload: list[dict[str, Any]] = []
    cards_by_column: dict[int, list[str]] = {}
    for card in cards:
        cards_by_column.setdefault(card["column_id"], []).append(card["external_id"])

    for column in columns:
        columns_payload.append(
            {
                "id": column["external_id"],
                "title": column["title"],
                "cardIds": cards_by_column.get(column["id"], []),
            }
        )

    return {"columns": columns_payload, "cards": card_map}


def update_board_for_user(username: str, payload: dict[str, Any]) -> dict[str, Any]:
    board_id = ensure_user_and_board(username)
    columns = payload.get("columns")
    cards = payload.get("cards")

    if not isinstance(columns, list):
        raise HTTPException(status_code=400, detail="columns must be a list")
    if not isinstance(cards, dict):
        raise HTTPException(status_code=400, detail="cards must be an object")

    with get_connection() as connection:
        connection.execute("DELETE FROM cards WHERE board_id = ?", (board_id,))
        connection.execute("DELETE FROM columns WHERE board_id = ?", (board_id,))

        column_lookup: dict[str, int] = {}
        for position, column in enumerate(columns):
            if not isinstance(column, dict):
                raise HTTPException(status_code=400, detail="each column must be an object")
            external_id = column.get("id")
            title = column.get("title", "Untitled")
            if not external_id:
                raise HTTPException(status_code=400, detail="column id is required")
            cursor = connection.execute(
                "INSERT INTO columns (board_id, external_id, title, position) VALUES (?, ?, ?, ?)",
                (board_id, external_id, title, position),
            )
            column_lookup[external_id] = cursor.lastrowid

        for column in columns:
            column_id = column_lookup.get(column.get("id"))
            if column_id is None:
                continue
            for position, card_id in enumerate(column.get("cardIds", [])):
                card = cards.get(card_id)
                if not isinstance(card, dict):
                    continue
                connection.execute(
                    "INSERT INTO cards (board_id, column_id, external_id, title, details, position) VALUES (?, ?, ?, ?, ?, ?)",
                    (
                        board_id,
                        column_id,
                        card.get("id", f"card-{time.time_ns()}"),
                        card.get("title", "Untitled card"),
                        card.get("details", ""),
                        position,
                    ),
                )

    return serialize_board(board_id)


@app.on_event("startup")
async def startup_event() -> None:
    init_database()


@app.get("/api/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "service": "project-management-api"}


@app.get("/api/hello")
async def hello() -> dict[str, str]:
    return {"message": "Hello from the Project Management backend", "status": "ok"}


@app.get("/api/ai/test")
async def ai_test() -> dict[str, Any]:
    try:
        answer = call_openrouter("Compute 2 + 2 and respond with just the number.")
        return {"ok": True, "model": OPENROUTER_MODEL, "answer": answer.strip()}
    except Exception as exc:  # pragma: no cover - runtime guard for missing API key
        return {"ok": False, "model": OPENROUTER_MODEL, "answer": "", "error": str(exc)}


@app.post("/api/users/{username}/ai")
async def ask_ai(username: str, payload: dict[str, Any]) -> dict[str, Any]:
    question = payload.get("question")
    history = payload.get("history", [])

    if not isinstance(question, str) or not question.strip():
        raise HTTPException(status_code=400, detail="question is required")
    if not isinstance(history, list):
        raise HTTPException(status_code=400, detail="history must be a list")

    board = serialize_board(ensure_user_and_board(username))
    prompt = json.dumps(
        {
            "board": board,
            "question": question,
            "history": history,
        },
        ensure_ascii=False,
    )
    system_prompt = (
        "You are a PM assistant for a Kanban board. Answer the user clearly and keep the response concise. "
        "If the user asks for a board update, return a board_update object containing the full updated board state "
        "with columns and cards. Only include board_update when needed."
    )

    try:
        raw_response = call_openrouter(
            prompt,
            system_prompt=system_prompt,
            response_format={
                "type": "json_schema",
                "json_schema": {"name": "board_ai_response", "schema": AI_OUTPUT_SCHEMA},
            },
        )
        parsed = json.loads(raw_response)
        ai_response = BoardAiResponse.model_validate(parsed)
    except (json.JSONDecodeError, ValidationError, TypeError, ValueError) as exc:
        raise HTTPException(status_code=400, detail=f"Invalid AI response: {exc}") from exc

    result: dict[str, Any] = {"answer": ai_response.answer}
    if ai_response.board_update is not None:
        result["board"] = update_board_for_user(username, ai_response.board_update.model_dump())

    return result


@app.get("/api/users/{username}/board")
async def get_board(username: str) -> dict[str, Any]:
    board_id = ensure_user_and_board(username)
    return serialize_board(board_id)


@app.put("/api/users/{username}/board")
async def save_board(username: str, payload: dict[str, Any]) -> dict[str, Any]:
    return update_board_for_user(username, payload)


@app.post("/api/users/{username}/cards")
async def create_card(username: str, payload: dict[str, Any]) -> dict[str, Any]:
    board_id = ensure_user_and_board(username)
    column_id = payload.get("columnId")
    title = payload.get("title")
    details = payload.get("details", "")

    if not column_id or not title:
        raise HTTPException(status_code=400, detail="columnId and title are required")

    with get_connection() as connection:
        column_row = connection.execute(
            "SELECT id FROM columns WHERE board_id = ? AND external_id = ?",
            (board_id, column_id),
        ).fetchone()
        if column_row is None:
            raise HTTPException(status_code=404, detail="column not found")

        card_id = f"card-{time.time_ns()}"
        next_position = connection.execute(
            "SELECT COALESCE(MAX(position), -1) + 1 FROM cards WHERE board_id = ? AND column_id = ?",
            (board_id, column_row["id"]),
        ).fetchone()[0]

        connection.execute(
            "INSERT INTO cards (board_id, column_id, external_id, title, details, position) VALUES (?, ?, ?, ?, ?, ?)",
            (board_id, column_row["id"], card_id, title, details, next_position),
        )

    return serialize_board(board_id)


@app.patch("/api/users/{username}/columns/{column_id}")
async def rename_column(username: str, column_id: str, payload: dict[str, str]) -> dict[str, Any]:
    board_id = ensure_user_and_board(username)
    title = payload.get("title")
    if not title:
        raise HTTPException(status_code=400, detail="title is required")

    with get_connection() as connection:
        cursor = connection.execute(
            "UPDATE columns SET title = ? WHERE board_id = ? AND external_id = ?",
            (title, board_id, column_id),
        )
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="column not found")

    return serialize_board(board_id)


@app.delete("/api/users/{username}/cards/{card_id}")
async def delete_card(username: str, card_id: str) -> dict[str, Any]:
    board_id = ensure_user_and_board(username)

    with get_connection() as connection:
        cursor = connection.execute(
            "DELETE FROM cards WHERE board_id = ? AND external_id = ?",
            (board_id, card_id),
        )
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="card not found")

    return serialize_board(board_id)


@app.post("/api/users/{username}/cards/{card_id}/move")
async def move_card(username: str, card_id: str, payload: dict[str, Any]) -> dict[str, Any]:
    board_id = ensure_user_and_board(username)
    target_column_id = payload.get("toColumnId")
    target_index = payload.get("toIndex", 0)

    if not target_column_id:
        raise HTTPException(status_code=400, detail="toColumnId is required")

    with get_connection() as connection:
        target_column = connection.execute(
            "SELECT id FROM columns WHERE board_id = ? AND external_id = ?",
            (board_id, target_column_id),
        ).fetchone()
        if target_column is None:
            raise HTTPException(status_code=404, detail="column not found")

        row = connection.execute(
            "SELECT id, column_id, position FROM cards WHERE board_id = ? AND external_id = ?",
            (board_id, card_id),
        ).fetchone()
        if row is None:
            raise HTTPException(status_code=404, detail="card not found")

        connection.execute(
            "UPDATE cards SET column_id = ?, position = ? WHERE id = ?",
            (target_column["id"], int(target_index), row["id"]),
        )

    return serialize_board(board_id)


if FRONTEND_BUILD_DIR.exists() and (FRONTEND_BUILD_DIR / "index.html").exists():
    next_dir = FRONTEND_BUILD_DIR / "_next"
    assets_dir = FRONTEND_BUILD_DIR / "assets"

    if next_dir.exists():
        app.mount("/_next", StaticFiles(directory=str(next_dir)), name="frontend_next")
    if assets_dir.exists():
        app.mount("/assets", StaticFiles(directory=str(assets_dir)), name="frontend_assets")

    @app.get("/", response_class=HTMLResponse)
    async def root() -> FileResponse:
        return FileResponse(FRONTEND_BUILD_DIR / "index.html")
else:
    @app.get("/", response_class=HTMLResponse)
    async def root() -> str:
        return """
        <!doctype html>
        <html lang="en">
          <head>
            <meta charset="utf-8" />
            <meta name="viewport" content="width=device-width, initial-scale=1" />
            <title>PM Backend</title>
            <style>
              body {
                font-family: Arial, sans-serif;
                display: grid;
                place-items: center;
                min-height: 100vh;
                margin: 0;
                background: #f5f7fb;
                color: #032147;
              }
              .card {
                background: white;
                border-radius: 16px;
                padding: 32px 48px;
                box-shadow: 0 20px 50px rgba(3, 33, 71, 0.08);
                text-align: center;
              }
              button {
                margin-top: 16px;
                padding: 10px 16px;
                background: #753991;
                color: white;
                border: none;
                border-radius: 10px;
                cursor: pointer;
                font-weight: 600;
              }
            </style>
          </head>
          <body>
            <div class="card">
              <h1>Hello world</h1>
              <p>The PM backend is running locally.</p>
              <button type="button" onclick="fetch('/api/hello').then(r => r.json()).then(d => alert(d.message))">
                Test API call
              </button>
            </div>
          </body>
        </html>
        """
