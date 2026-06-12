import json
import requests
from typing import Generator
from app.config import settings

class LLMResponder:
    def __init__(self):
        """
        Initializes the Ollama local responder using variables configured in settings.
        """
        self.url = f"{settings.OLLAMA_URL}/api/chat"
        self.model = settings.OLLAMA_MODEL

    def generate_response(self, chat_history: list[dict]) -> str:
        """
        Sends the entire conversation thread history to Ollama and returns the assistant reply.
        
        Args:
            chat_history (list[dict]): A list of messages in Ollama format:
                                       [{"role": "user"|"assistant"|"system", "content": "..."}]
        
        Returns:
            str: The text content of the assistant's response.
        """
        # System instructions to enforce English response
        system_message = {
            "role": "system",
            "content": (
                "You are Vaani, a helpful local voice-activated assistant. "
                "The user will speak to you in Hindi, English, or Gujarati, which will be "
                "transcribed and translated to English. You must ALWAYS reply in clear, concise English."
            )
        }

        # Prepend the system instructions if not already present
        messages_payload = [system_message] + [
            msg for msg in chat_history if msg["role"] != "system"
        ]

        payload = {
            "model": self.model,
            "messages": messages_payload,
            "stream": False  # Disable streaming for synchronous processing
        }

        try:
            # Send POST request to Ollama service
            response = requests.post(self.url, json=payload, timeout=30)
            response.raise_for_status()
            result = response.json()
            
            # Extract content from response
            return result["message"]["content"].strip()

        except requests.exceptions.Timeout:
            raise RuntimeError(
                f"Ollama server timed out. Ensure your computer has enough resources "
                f"to execute the model '{self.model}'."
            )
        except requests.exceptions.RequestException as e:
            raise RuntimeError(
                f"Cannot connect to the local Ollama server at {settings.OLLAMA_URL}. "
                f"Please verify Ollama is installed and running, and that you have pulled "
                f"the model (run: `ollama pull {self.model}`). Error: {e}"
            )

    def generate_response_stream(self, chat_history: list[dict]) -> Generator[str, None, None]:
        """
        Sends the conversation thread to Ollama and yields response chunks in real-time.
        """
        system_message = {
            "role": "system",
            "content": (
                "You are Vaani, a helpful local voice-activated assistant. "
                "The user will speak to you in Hindi, English, or Gujarati, which will be "
                "transcribed and translated to English. You must ALWAYS reply in clear, concise English."
            )
        }

        messages_payload = [system_message] + [
            msg for msg in chat_history if msg["role"] != "system"
        ]

        payload = {
            "model": self.model,
            "messages": messages_payload,
            "stream": True  # Enable streaming
        }

        try:
            # Send POST request to Ollama service with streaming enabled
            response = requests.post(self.url, json=payload, timeout=30, stream=True)
            response.raise_for_status()
            
            for line in response.iter_lines():
                if line:
                    chunk = json.loads(line.decode('utf-8'))
                    if "message" in chunk and "content" in chunk["message"]:
                        yield chunk["message"]["content"]

        except requests.exceptions.Timeout:
            raise RuntimeError(
                f"Ollama server timed out. Ensure your computer has enough resources "
                f"to execute the model '{self.model}'."
            )
        except requests.exceptions.RequestException as e:
            raise RuntimeError(
                f"Cannot connect to the local Ollama server at {settings.OLLAMA_URL}. "
                f"Please verify Ollama is installed and running, and that you have pulled "
                f"the model (run: `ollama pull {self.model}`). Error: {e}"
            )
