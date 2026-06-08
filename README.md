# AI Assistant Web App

A minimal, responsive, and full-stack AI Assistant application featuring a real-time streaming chat interface, persistence of conversation histories, and an intuitive sidebar manager. 

Built with a fast asynchronous **FastAPI** backend, the **OpenAI API** (supporting streaming), and a clean **vanilla HTML/CSS/JS** frontend.

## 🚀 Features

- **Real-Time Streaming:** Responses stream token-by-token using Server-Sent Events (SSE) for a smooth UI experience.
- **Session Persistence:** Chat history is automatically managed and saved locally to a JSON file format structure.
- **Chat Management:** Dynamic sidebar allowing users to create new sessions, auto-title threads based on the first prompt, and delete old conversations.
- **Responsive Layout:** Beautiful, modern UI inspired by chat interfaces, supporting code block formatting (`single line` and multi-line syntax highlighting wrappers).

---

## 🛠️ Tech Stack

- **Backend:** Python, FastAPI, Uvicorn, OpenAI SDK, Pydantic, Python-Dotenv
- **Frontend:** Vanilla HTML5, CSS3 (Flexbox, custom animations), Vanilla JavaScript (Fetch API / ReadableStreams)

---

## 📦 Project Structure

```text
├── data/               # Local JSON chat database (Auto-generated, git-ignored)
├── .env                # Local environment variables (Git-ignored)
├── .gitignore          # Git exclusion rules
├── history.py          # Chat session CRUD mechanics 
├── index.py            # Main frontend web page
├── main.py             # FastAPI server application & OpenAI orchestrator
└── requirements.txt    # Python dependencies
