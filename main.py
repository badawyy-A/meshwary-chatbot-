import os
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage

# ── Config ───────────────────────────────────────────────────────────────────
load_dotenv()

API_KEYS = [os.getenv(f"GOOGLE_API_KEY_{i}") for i in range(1, 7)]
API_KEYS = [k for k in API_KEYS if k]

MODEL_NAME     = os.getenv("MODEL_NAME", "gemini-2.0-flash-lite")
SYSTEM_PROMPT  = os.getenv("SYSTEM_PROMPT", "You are a helpful assistant.")

if not API_KEYS:
    raise ValueError("No API keys found in .env file!")

app = FastAPI(title="Gemini Chat API", version="1.0.0")


# ── Helpers ───────────────────────────────────────────────────────────────────
def get_llm(api_key: str) -> ChatGoogleGenerativeAI:
    return ChatGoogleGenerativeAI(
        model=MODEL_NAME,
        google_api_key=api_key,
        temperature=0.7,
    )


def build_messages(prompt: str, history: list[dict]) -> list:
    messages = [SystemMessage(content=SYSTEM_PROMPT)]

    for msg in history:
        if msg["role"] == "user":
            messages.append(HumanMessage(content=msg["content"]))
        elif msg["role"] == "assistant":
            messages.append(AIMessage(content=msg["content"]))

    messages.append(HumanMessage(content=prompt))
    return messages


# ── Schemas ───────────────────────────────────────────────────────────────────
class HistoryMessage(BaseModel):
    role: str       # "user" or "assistant"
    content: str


class PromptRequest(BaseModel):
    prompt: str
    history: list[HistoryMessage] = []


class ChatResponse(BaseModel):
    response: str


# ── Endpoints ─────────────────────────────────────────────────────────────────

@app.post("/chat", response_model=ChatResponse)
async def chat(request: PromptRequest):
    """Send a prompt and get a full response."""
    messages = build_messages(request.prompt, [m.model_dump() for m in request.history])

    for i, key in enumerate(API_KEYS):
        try:
            llm = get_llm(key)
            result = llm.invoke(messages)
            return ChatResponse(response=result.content)
        except Exception as e:
            print(f"[Key {i+1} failed] {e}")

    raise HTTPException(status_code=503, detail="All API keys failed!")


@app.post("/chat/stream")
async def chat_stream(request: PromptRequest):
    """Send a prompt and get a true chunk-by-chunk streaming response."""
    messages = build_messages(request.prompt, [m.model_dump() for m in request.history])

    async def stream_generator():
        for i, key in enumerate(API_KEYS):
            try:
                llm = get_llm(key)
                async for chunk in llm.astream(messages):
                    if chunk.content:
                        yield chunk.content
                return
            except Exception as e:
                print(f"[Key {i+1} failed] {e}")

        yield "[ERROR] All API keys failed!"

    return StreamingResponse(stream_generator(), media_type="text/plain")


# ── Run ───────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)