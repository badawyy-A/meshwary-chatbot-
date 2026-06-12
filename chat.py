import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage

# ── Config ──────────────────────────────────────────────────────────────────
load_dotenv()

API_KEYS = [
    os.getenv(f"GOOGLE_API_KEY_{i}") for i in range(1, 7)
]
API_KEYS = [k for k in API_KEYS if k]  # remove empty/missing keys

if not API_KEYS:
    raise ValueError("No API keys found in .env file!")


def get_llm(api_key: str) -> ChatGoogleGenerativeAI:
    return ChatGoogleGenerativeAI(
        model="gemini-2.0-flash",        
        google_api_key=api_key,
        temperature=0.7,
    )


def invoke_with_fallback(history: list) -> str:
    """Try each API key in order, move to next if one fails."""
    for i, key in enumerate(API_KEYS):
        try:
            llm = get_llm(key)
            response = llm.invoke(history)
            return response.content
        except Exception as e:
            print(f"[Key {i+1} failed: {e}] trying next key...")

    raise RuntimeError("All API keys failed!")


# Keep conversation history so Gemini remembers context
history: list = [
    SystemMessage(content="You are a helpful assistant.")
]

# ── Chat loop ────────────────────────────────────────────────────────────────
print(f"Gemini Chat — {len(API_KEYS)} API keys loaded | type 'exit' to quit\n")

while True:
    user_input = input("You: ").strip()
    if not user_input:
        continue
    if user_input.lower() in ("exit", "quit"):
        print("Bye!")
        break

    history.append(HumanMessage(content=user_input))

    reply = invoke_with_fallback(history)

    history.append(AIMessage(content=reply))

    print(f"\nGemini: {reply}\n")