from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage

# ── Config ──────────────────────────────────────────────────────────────────
GOOGLE_API_KEY = "YOUR_GEMINI_API_KEY"   # 👈 replace this

llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",            # or "gemini-1.5-pro"
    google_api_key=GOOGLE_API_KEY,
    temperature=0.7,
)

# Keep conversation history so Gemini remembers context
history: list = [
    SystemMessage(content="You are a helpful assistant.")
]

# ── Chat loop ────────────────────────────────────────────────────────────────
print("Gemini Chat — type 'exit' to quit\n")

while True:
    user_input = input("You: ").strip()
    if not user_input:
        continue
    if user_input.lower() in ("exit", "quit"):
        print("Bye!")
        break

    history.append(HumanMessage(content=user_input))

    response = llm.invoke(history)

    history.append(AIMessage(content=response.content))

    print(f"\nGemini: {response.content}\n")