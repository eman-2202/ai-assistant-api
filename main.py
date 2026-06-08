from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from openai import OpenAI
from dotenv import load_dotenv
import os, uuid

from history import (
    list_chats, get_chat, create_chat,
    append_message, rename_chat, delete_chat
)

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")


# ── REQUEST MODELS ────────────────────────────────────────────

class ChatRequest(BaseModel):
    chat_id: str | None = None   # if None, a new chat is created
    message: str                 # the new user message
    system: str = "You are a helpful AI assistant."


class RenameRequest(BaseModel):
    title: str


# ── CHAT HISTORY ENDPOINTS ────────────────────────────────────

@app.get("/chats")
def get_chats():
    """List all saved conversations."""
    return list_chats()


@app.get("/chats/{chat_id}")
def get_single_chat(chat_id: str):
    """Get a full chat with all messages."""
    chat = get_chat(chat_id)
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")
    return chat


@app.delete("/chats/{chat_id}")
def remove_chat(chat_id: str):
    """Delete a conversation."""
    delete_chat(chat_id)
    return {"deleted": chat_id}


@app.patch("/chats/{chat_id}")
def update_chat_title(chat_id: str, req: RenameRequest):
    """Rename a conversation."""
    rename_chat(chat_id, req.title)
    return {"renamed": chat_id, "title": req.title}


# ── MAIN CHAT ENDPOINT ────────────────────────────────────────

@app.post("/chat")
def chat(req: ChatRequest):
    # Create a new chat if no ID provided
    chat_id = req.chat_id or str(uuid.uuid4())
    chat = get_chat(chat_id)

    if not chat:
        create_chat(chat_id)
        chat = get_chat(chat_id)

    # Save the user message
    append_message(chat_id, "user", req.message)

    # Auto-title the chat from the first message
    if len(chat["messages"]) == 0:
        title = req.message[:50] + ("…" if len(req.message) > 50 else "")
        rename_chat(chat_id, title)

    # Build the message history for OpenAI
    history = get_chat(chat_id)["messages"]
    openai_messages = [
        {"role": "system", "content": req.system},
        *[{"role": m["role"], "content": m["content"]} for m in history]
    ]

    # Call OpenAI
    response = client.chat.completions.create(
        model=MODEL,
        messages=openai_messages
    )
    reply = response.choices[0].message.content

    # Save assistant reply
    append_message(chat_id, "assistant", reply)

    return {
        "chat_id": chat_id,
        "reply": reply
    }


@app.get("/health")
def health():
    return {"status": "ok", "model": MODEL}

@app.post("/chat/stream")
def chat_stream(req: ChatRequest):
    # Create chat if needed
    chat_id = req.chat_id or str(uuid.uuid4())
    if not get_chat(chat_id):
        create_chat(chat_id)

    # Save user message
    append_message(chat_id, "user", req.message)

    # Auto-title
    chat = get_chat(chat_id)
    if len(chat["messages"]) == 1:
        title = req.message[:50] + ("…" if len(req.message) > 50 else "")
        rename_chat(chat_id, title)

    # Build history for OpenAI
    history = get_chat(chat_id)["messages"]
    openai_messages = [
        {"role": "system", "content": req.system},
        *[{"role": m["role"], "content": m["content"]} for m in history]
    ]

    # Generator that streams chunks and saves the full reply at the end
    def generate():
        full_reply = ""

        # First chunk sends the chat_id so the frontend can save it
        yield f"data: [CHAT_ID:{chat_id}]\n\n"

        stream = client.chat.completions.create(
            model=MODEL,
            messages=openai_messages,
            stream=True
        )

        for chunk in stream:
            delta = chunk.choices[0].delta.content
            if delta:
                full_reply += delta
                # Send each token as a Server-Sent Event
                yield f"data: {delta}\n\n"

        # Save full reply to history
        append_message(chat_id, "assistant", full_reply)

        # Signal the end
        yield "data: [DONE]\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")