import json
import os
from datetime import datetime

DATA_FILE = "data/chats.json"


def _load() -> dict:
    if not os.path.exists(DATA_FILE):
        os.makedirs("data", exist_ok=True)
        return {}
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def _save(data: dict):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def list_chats() -> list:
    """Return all chat summaries (id, title, created_at)."""
    data = _load()
    return [
        {"id": cid, "title": c["title"], "created_at": c["created_at"]}
        for cid, c in data.items()
    ]


def get_chat(chat_id: str) -> dict | None:
    """Return a full chat with its messages, or None if not found."""
    data = _load()
    return data.get(chat_id)


def create_chat(chat_id: str, title: str = "New conversation") -> dict:
    """Create a new empty chat and persist it."""
    data = _load()
    chat = {
        "id": chat_id,
        "title": title,
        "created_at": datetime.now().isoformat(),
        "messages": []
    }
    data[chat_id] = chat
    _save(data)
    return chat


def append_message(chat_id: str, role: str, content: str) -> dict:
    """Add a message to a chat. Creates the chat if it doesn't exist."""
    data = _load()
    if chat_id not in data:
        create_chat(chat_id)
        data = _load()
    data[chat_id]["messages"].append({
        "role": role,
        "content": content,
        "time": datetime.now().isoformat()
    })
    _save(data)
    return data[chat_id]


def rename_chat(chat_id: str, title: str):
    """Update a chat's title."""
    data = _load()
    if chat_id in data:
        data[chat_id]["title"] = title
        _save(data)


def delete_chat(chat_id: str):
    """Remove a chat entirely."""
    data = _load()
    data.pop(chat_id, None)
    _save(data)