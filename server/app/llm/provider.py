import os, requests
from typing import List, Dict, Optional, Literal, cast

Provider = Literal["ollama", "openai"]

class LLMClient:
    def __init__(self, provider: Optional[Provider] = None, model: Optional[str] = None):
        # ✅ Explicit cast fixes Pylance warning
        self.provider: Provider = cast(Provider, provider or os.getenv("LLM_PROVIDER", "ollama"))
        self.model = model or os.getenv("LLM_MODEL", "mistral")  # Mistral via Ollama
        self.ollama_host = os.getenv("OLLAMA_HOST", "http://localhost:11434")
        self.openai_key = os.getenv("OPENAI_API_KEY")

    def chat(self, messages: List[Dict[str, str]], temperature: float = 0.1) -> str:
        if self.provider == "ollama":
            url = f"{self.ollama_host}/api/chat"
            payload = {
                "model": self.model,
                "messages": messages,
                "stream": False,
                "options": {"temperature": temperature},
            }
            r = requests.post(url, json=payload, timeout=120)
            r.raise_for_status()
            return r.json()["message"]["content"]

        elif self.provider == "openai":
            import openai
            openai.api_key = self.openai_key or os.getenv("OPENAI_API_KEY")
            client = openai.OpenAI()
            resp = client.chat.completions.create(
                model=self.model or "gpt-4o-mini",
                temperature=temperature,
                messages=messages,
            )
            return resp.choices[0].message.content

        else:
            raise ValueError(f"Unknown LLM provider: {self.provider}")
