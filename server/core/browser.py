from playwright.sync_api import sync_playwright
import json

# ------------------ Helpers ------------------

def close_flipkart_popup(page):
    """Close Flipkart login popup if it appears repeatedly"""
    try:
        while True:
            popup = page.query_selector("button._2KpZ6l._2doB4z")
            if popup:
                popup.click()
                page.wait_for_timeout(500)
            else:
                break
    except:
        pass


def scroll_page(page, steps=5, delay=1000):
    """Scroll down to load lazy-loaded content"""
    for _ in range(steps):
        page.mouse.wheel(0, 2000)
        page.wait_for_timeout(delay)


# ------------------ Amazon Debug Scraper ------------------

def scrape_amazon_products(page, query):
    page.goto(f"https://www.amazon.in/s?k={query.replace(' ', '+')}")
    page.wait_for_selector("div.s-result-item.s-asin", timeout=15000)

    results = []
    product_cards = page.query_selector_all("div.s-result-item.s-asin[data-asin]")
    print(f"DEBUG: Found {len(product_cards)} Amazon product containers")

    for card in product_cards[:10]:
        title_el = card.query_selector("h2 a span")
        link_el = card.query_selector("h2 a")
        price_el = card.query_selector("span.a-price-whole")
        price_frac_el = card.query_selector("span.a-price-fraction")
        rating_el = card.query_selector("span.a-icon-alt")

        if not title_el or not link_el:
            continue

        title = title_el.inner_text().strip()
        link = link_el.get_attribute("href")
        if link and not link.startswith("http"):
            link = "https://www.amazon.in" + link

        price = "N/A"
        if price_el:
            price = price_el.inner_text().strip()
            if price_frac_el:
                price += "." + price_frac_el.inner_text().strip()
            price = f"₹{price}"

        rating = rating_el.inner_text().strip() if rating_el else "N/A"

        # skip accessories/plans
        if "plan" in title.lower() or "cover" in title.lower() or "warranty" in title.lower():
            continue

        results.append({
            "site": "Amazon",
            "title": title,
            "price": price,
            "rating": rating,
            "link": link
        })

    return results


# ------------------ Flipkart Debug Scraper ------------------

def scrape_flipkart_products(page, query):
    page.goto("https://www.flipkart.com/")
    close_flipkart_popup(page)

    page.wait_for_selector("input[name=q]", timeout=10000)
    page.fill("input[name=q]", query)
    page.keyboard.press("Enter")

    page.wait_for_timeout(5000)
    scroll_page(page, steps=6, delay=1200)

    items = page.query_selector_all("div._2kHMtA")
    print(f"DEBUG: Found {len(items)} Flipkart product containers")

    products = []
    for item in items[:10]:
        title_el = item.query_selector("div._4rR01T") or item.query_selector("a.s1Q9rs")
        price_el = item.query_selector("div._30jeq3")
        rating_el = item.query_selector("div._3LWZlK")
        link_el = item.query_selector("a")

        if not title_el or not link_el:
            continue

        title = title_el.inner_text().strip()
        price = price_el.inner_text().strip() if price_el else "N/A"
        rating = rating_el.inner_text().strip() if rating_el else "N/A"

        link = link_el.get_attribute("href")
        if link and not link.startswith("http"):
            link = "https://www.flipkart.com" + link

        products.append({
            "site": "Flipkart",
            "title": title,
            "price": price,
            "rating": rating,
            "link": link
        })

    return products



# ------------------ DuckDuckGo Fallback ------------------

def search_duckduckgo(page, query):
    page.goto("https://duckduckgo.com/")
    page.wait_for_selector("input[name=q]")
    page.fill("input[name=q]", query)
    page.keyboard.press("Enter")

    page.wait_for_timeout(4000)

    html = page.content()
    with open("debug_duckduckgo.html", "w", encoding="utf-8") as f:
        f.write(html)
    print("📂 Saved debug_duckduckgo.html for inspection")

    items = page.query_selector_all("a.result__a, a[data-testid='result-title-a'], h2 a")
    results = []
    for item in items[:5]:
        title = item.inner_text().strip()
        link = item.get_attribute("href")
        if link and link.startswith("http"):
            results.append({
                "site": "Web",
                "title": title,
                "price": "N/A",
                "rating": "N/A",
                "link": link
            })
    return results


# ------------------ Orchestrator ------------------

def run_browser(query: str, product_mode=False):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)  # Debug mode ON
        page = browser.new_page()

        results = []

        if product_mode:
            try:
                amazon_products = scrape_amazon_products(page, query)
                print(f"✅ Amazon returned {len(amazon_products)} results")
                results += amazon_products
            except Exception as e:
                print("❌ Amazon scrape failed:", e)

            try:
                flipkart_products = scrape_flipkart_products(page, query)
                print(f"✅ Flipkart returned {len(flipkart_products)} results")
                results += flipkart_products
            except Exception as e:
                print("❌ Flipkart scrape failed:", e)

        if not results:
            try:
                print("⚠️ Falling back to DuckDuckGo...")
                results += search_duckduckgo(page, query)
            except Exception as e:
                print("❌ DuckDuckGo scrape failed:", e)

        browser.close()
        return results[:20] if results else [{"site": "N/A", "title": "No results found", "price": "N/A", "rating": "N/A", "link": ""}]
