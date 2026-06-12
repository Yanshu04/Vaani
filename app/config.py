import os
from dataclasses import dataclass, field
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file at the project root
env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

@dataclass
class Settings:
    WHISPER_MODEL: str = os.getenv("VAANI_WHISPER_MODEL", "medium")
    SAMPLE_RATE: int = int(os.getenv("VAANI_SAMPLE_RATE", "16000"))
    VAD_AGGRESSIVENESS: int = int(os.getenv("VAANI_VAD_AGGRESSIVENESS", "2"))
    SILENCE_MS: int = int(os.getenv("VAANI_SILENCE_MS", "600"))
    MAX_RECORD_SECONDS: int = int(os.getenv("VAANI_MAX_RECORD_SECONDS", "15"))
    SUPPORTED_LANGUAGES: list[str] = field(default_factory=lambda: ["hi", "en", "gu"])
    MODELS_DIR: str = os.getenv("VAANI_MODELS_DIR", "./models")
    CONFIDENCE_THRESHOLD: float = float(os.getenv("VAANI_TRANSLATION_CONFIDENCE_THRESHOLD", "0.6"))
    OLLAMA_URL: str = os.getenv("VAANI_OLLAMA_URL", "http://localhost:11434")
    OLLAMA_MODEL: str = os.getenv("VAANI_OLLAMA_MODEL", "qwen2.5:1.5b")

# Export a single global instance of Settings
settings = Settings()
