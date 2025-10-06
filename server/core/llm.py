import subprocess

def ask_llm(prompt: str) -> str:
    strict_prompt = f"""
    Instruction: {prompt}
    Convert this into a short plain web search query.
    Rules:
    - Only use simple keywords
    - No site:, quotes, operators, or symbols
    - Keep it short and clear
    Output only the query, nothing else.
    """
    result = subprocess.run(
        ["ollama", "run", "mistral"],
        input=strict_prompt.encode(),
        capture_output=True
    )
    query = result.stdout.decode().strip()

    # ✅ Remove wrapping quotes if LLM still outputs them
    if query.startswith('"') and query.endswith('"'):
        query = query[1:-1]

    return query

