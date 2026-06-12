import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # API Keys
    API_KEYS: list[str] = [
        key for i in range(1, 7)
        if (key := os.getenv(f"GOOGLE_API_KEY_{i}"))
    ]

    # Model
    MODEL_NAME: str    = os.getenv("MODEL_NAME", "gemini-2.0-flash-lite")
    TEMPERATURE: float = float(os.getenv("TEMPERATURE", "0.7"))

    # System prompt
    SYSTEM_PROMPT: str = os.getenv("SYSTEM_PROMPT", "You are a helpful assistant.")

    # Server
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"

    def validate(self):
        if not self.API_KEYS:
            raise ValueError("No API keys found in .env file!")
        return self


config = Config().validate()