# app/skills/extractors/web.py
import requests, re
from bs4 import BeautifulSoup
from app.utils.logger import logger

def extract_web_results(query: str, max_results: int = 10) -> list[dict]:
    """
    Fetches organic web search results using DuckDuckGo (no API key needed)
    and extracts titles, snippets, and links for 'learn'/'explore' intents.
    """
    logger.info(f"Searching web for: {query}")
    url = f"https://duckduckgo.com/html/?q={query.replace(' ', '+')}"
    headers = {"User-Agent": "Mozilla/5.0 (compatible; AIWebNavigator/1.0)"}
    res = requests.get(url, headers=headers, timeout=15)
    soup = BeautifulSoup(res.text, "html.parser")

    results = []
    for a in soup.select("a.result__a")[:max_results]:
        link = a["href"]
        title = a.get_text(strip=True)
        desc_tag = a.find_parent("div", class_="result__body")
        snippet = desc_tag.get_text(" ", strip=True) if desc_tag else ""
        results.append({
            "title": title,
            "snippet": snippet[:350],
            "link": link,
            "site": "web"
        })

    if not results:
        logger.warning("No web results found.")
    return results
