from app.llm.provider import LLMClient
from app.llm.summarize_prompt import SYSTEM_SUMMARIZE, USER_TEMPLATE_SUMMARIZE

def summarize_text_llm(text: str) -> str:
    """
    Summarizes a long article or paragraph using the LLMClient (Ollama/Mistral).
    """
    if not text or len(text.strip()) == 0:
        return "(No text provided)"

    snippet = text[:6000]  # Limit input for local model

    llm = LLMClient()
    user_prompt = USER_TEMPLATE_SUMMARIZE.format(text=snippet)

    try:
        response = llm.chat(
            messages=[
                {"role": "system", "content": SYSTEM_SUMMARIZE},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.3,
        )
        return response.strip()
    except Exception as e:
        return f"(⚠️ Summarization failed: {e})"
