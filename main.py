from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage

from config import config
from logger import get_logger

logger = get_logger(__name__)

app = FastAPI(title="Gemini Chat API", version="1.0.0")

@app.on_event("startup")
async def startup_event():
    logger.info("========== CONFIG DEBUG ==========")
    logger.info(f"MODEL_NAME={config.MODEL_NAME}")
    logger.info(f"TEMPERATURE={config.TEMPERATURE}")
    logger.info(f"SYSTEM_PROMPT exists={bool(config.SYSTEM_PROMPT)}")
    logger.info(f"SYSTEM_PROMPT length={len(config.SYSTEM_PROMPT) if config.SYSTEM_PROMPT else 0}")
    logger.info(f"API_KEYS count={len(config.API_KEYS)}")

    for i, key in enumerate(config.API_KEYS, start=1):
        logger.info(f"GOOGLE_API_KEY_{i} exists={bool(key)}")

    logger.info("==================================")

# ── Helpers ───────────────────────────────────────────────────────────────────
def get_llm(api_key: str) -> ChatGoogleGenerativeAI:
    return ChatGoogleGenerativeAI(
        model=config.MODEL_NAME,
        google_api_key=api_key,
        temperature=config.TEMPERATURE,
    )


def build_messages(prompt: str, history: list[dict]) -> list:
    messages = [SystemMessage(content=config.SYSTEM_PROMPT)]

    for msg in history:
        if msg["role"] == "user":
            messages.append(HumanMessage(content=msg["content"]))
        elif msg["role"] == "assistant":
            messages.append(AIMessage(content=msg["content"]))

    messages.append(HumanMessage(content=prompt))
    return messages


# ── Schemas ───────────────────────────────────────────────────────────────────
class HistoryMessage(BaseModel):
    role: str
    content: str


class PromptRequest(BaseModel):
    prompt: str
    history: list[HistoryMessage] = []


class ChatResponse(BaseModel):
    response: str


# ── Endpoints ─────────────────────────────────────────────────────────────────

@app.post("/chat", response_model=ChatResponse)
async def chat(request: PromptRequest):
    logger.info(f"/chat | prompt='{request.prompt[:60]}' | history_len={len(request.history)}")
    messages = build_messages(request.prompt, [m.model_dump() for m in request.history])

    for i, key in enumerate(config.API_KEYS):
        try:
            llm = get_llm(key)
            result = llm.invoke(messages)
            logger.info(f"/chat | success with key {i+1}")
            return ChatResponse(response=result.content)
        except Exception as e:
            logger.warning(f"/chat | key {i+1} failed: {e}")

    logger.error("/chat | all API keys failed")
    raise HTTPException(status_code=503, detail="All API keys failed!")


@app.post("/chat/stream")
async def chat_stream(request: PromptRequest):
    logger.info(f"/chat/stream | prompt='{request.prompt[:60]}' | history_len={len(request.history)}")
    messages = build_messages(request.prompt, [m.model_dump() for m in request.history])

    async def stream_generator():
        for i, key in enumerate(config.API_KEYS):
            try:
                llm = get_llm(key)
                async for chunk in llm.astream(messages):
                    if chunk.content:
                        yield chunk.content
                logger.info(f"/chat/stream | success with key {i+1}")
                return
            except Exception as e:
                logger.warning(f"/chat/stream | key {i+1} failed: {e}")

        logger.error("/chat/stream | all API keys failed")
        yield "[ERROR] All API keys failed!"

    return StreamingResponse(stream_generator(), media_type="text/plain")


# ── Run ───────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn
    logger.info(f"Starting server on {config.HOST}:{config.PORT} | model={config.MODEL_NAME} | keys={len(config.API_KEYS)}")
    uvicorn.run("main:app", host=config.HOST, port=config.PORT, reload=config.DEBUG)