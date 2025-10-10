import urllib.parse
import time
from bs4 import BeautifulSoup
from app.utils.logger import logger
from app.browser.controller import BrowserController


def extract_web_results(query: str, max_results: int = 5) -> list[dict]:
    """
    🌐 Searches Bing for the given query and extracts readable text from top web results.
    Uses Playwright via BrowserController for dynamic content and BeautifulSoup for parsing.
    """
    logger.info(f"🌍 Searching Bing for: {query}")
    results = []

    # Construct Bing search URL
    search_url = f"https://www.bing.com/search?q={urllib.parse.quote_plus(query)}"
    logger.info(f"🔗 Bing Search URL: {search_url}")

    # Start the Playwright browser session
    with BrowserController(run_dir="runs") as bc:
        page = bc._ensure_page()
        page.goto(search_url, timeout=30000, wait_until="domcontentloaded")
        time.sleep(2)

        html = page.content()
        soup = BeautifulSoup(html, "html.parser")

        # Extract top result links (like <li class="b_algo"><h2><a href="...">)
        anchors = soup.select("li.b_algo h2 a")
        logger.info(f"🔍 Found {len(anchors)} Bing result links.")

        for a in anchors[:max_results]:
            title = a.get_text(strip=True)
            link = a.get("href")
            if not link:
                continue
            results.append({"title": title, "link": link})

        extracted = []
        for r in results:
            try:
                logger.info(f"📖 Visiting: {r['link']}")
                page.goto(r["link"], timeout=15000, wait_until="domcontentloaded")
                time.sleep(2)

                html = page.content()
                soup = BeautifulSoup(html, "html.parser")

                # Combine visible text from <p> and <article> tags
                paragraphs = " ".join(
                    [p.get_text(" ", strip=True) for p in soup.select("p")]
                )
                text = paragraphs[:3000] or "(No readable text found)"
                logger.info(f"🧠 Extracted {len(text)} chars from {r['link']}")

                extracted.append({
                    "title": r["title"],
                    "url": r["link"],
                    "text": text
                })
            except Exception as e:
                logger.error(f"⚠️ Could not extract from {r['link']}: {e}")
                continue

    return extracted
