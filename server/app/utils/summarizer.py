# app/utils/summarizer.py
from app.llm.provider import LLMClient
from app.llm.compare_prompt import SYSTEM_COMPARE, USER_TEMPLATE_COMPARE

def summarize_comparison(products: list[dict]) -> str:
    """
    Uses the same LLMClient (local or remote) to generate a comparison summary.
    """
    llm = LLMClient()

    # Build a readable list of products
    product_text = "\n".join(
        f"- {p.get('title','N/A')} | Price: {p.get('price','N/A')} | Rating: {p.get('rating','N/A')}"
        for p in products
    )

    user_prompt = USER_TEMPLATE_COMPARE.format(product_text=product_text)

    try:
        summary = llm.chat(
            messages=[
                {"role": "system", "content": SYSTEM_COMPARE},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.3,
        )
        return summary.strip()
    except Exception as e:
        return f"⚠️ Summary unavailable ({e})"
