# meshwary-chatbot 🤖

A lightweight AI chat microservice built with **FastAPI** and **Google Gemini** via LangChain. Designed as a stateless AI component — no database, no auth — just a smart, reliable chat engine with multi-key fallback and streaming support.

---

## Features

- 🔁 **Multi API key fallback** — up to 6 Gemini API keys, auto-switches on failure or quota limit
- ⚡ **Streaming support** — true chunk-by-chunk streaming via SSE
- 🧠 **Chat history** — accepts conversation history from the main backend
- 🔧 **Config via `.env`** — model, temperature, system prompt, server settings
- 📋 **Structured logging** — logs to console and `app.log` file

---

## Project Structure

```
meshwary-chatbot/
├── main.py          # FastAPI app & endpoints
├── config.py        # All settings loaded from .env
├── logger.py        # Console + file logger
├── requirements.txt
├── .env             # Environment variables (never commit this)
└── .gitignore
```

---

## Setup

**1. Clone the repo**
```bash
git clone https://github.com/your-username/meshwary-chatbot.git
cd meshwary-chatbot
```

**2. Install dependencies**
```bash
pip install -r requirements.txt
```

**3. Configure `.env`**
```env
# API Keys (use different Google accounts for independent quotas)
GOOGLE_API_KEY_1=your_key_here
GOOGLE_API_KEY_2=your_key_here
GOOGLE_API_KEY_3=your_key_here
GOOGLE_API_KEY_4=your_key_here
GOOGLE_API_KEY_5=your_key_here
GOOGLE_API_KEY_6=your_key_here

# Model
MODEL_NAME=gemini-2.0-flash-lite
TEMPERATURE=0.7

# System prompt
SYSTEM_PROMPT=You are a helpful assistant.

# Server
HOST=0.0.0.0
PORT=8000
DEBUG=false
```

**4. Run**
```bash
python main.py
```

---

## API Endpoints

### `POST /chat`
Returns a full response at once.

**Request:**
```json
{
  "prompt": "hello",
  "history": [
    {"role": "user", "content": "my name is Badawi"},
    {"role": "assistant", "content": "Nice to meet you Badawi!"}
  ]
}
```

**Response:**
```json
{
  "response": "Hello! How can I help you today?"
}
```

---

### `POST /chat/stream`
Returns a chunk-by-chunk streaming response.

**Request:** same as `/chat`

**Response:** plain text stream

**Test with curl:**
```bash
curl -X POST http://localhost:8000/chat/stream \
  -H "Content-Type: application/json" \
  -d '{"prompt": "tell me about Sinai", "history": []}' \
  --no-buffer
```

---

## Swagger Docs

Visit **http://localhost:8000/docs** after running the server.

---

## Architecture

This service is designed as a **stateless AI component** inside a larger system:

```
[Mobile App] ←→ [Main Backend + DB] ←→ [meshwary-chatbot]
                      ↑
              handles users, auth,
              and chat history
```

The main backend is responsible for auth, storing history, and passing it with every request. This service just receives, processes, and responds.

---

## Get a Gemini API Key

→ [aistudio.google.com/apikey](https://aistudio.google.com/apikey) — free with a Google account

> 💡 Use a **different Google account** for each key to get independent free-tier quotas.