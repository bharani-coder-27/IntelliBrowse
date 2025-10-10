""" from app.browser.controller import BrowserController
from app.skills.extractors.amazon import _extract_amazon_details

url = "https://www.amazon.in/Acer-i5-1334U-39-62cm-Windows-AL15-53/dp/B0DPXBHF8H/ref=sr_1_1_sspa?sr=8-1-spons&sp_csd=d2lkZ2V0TmFtZT1zcF9hdGY"
with BrowserController("runs/test") as bc:
    specs = _extract_amazon_details(bc, url)
    print(specs or "❌ No specs found")
 """

from app.skills.extractors.web import extract_web_results

res = extract_web_results("Last 20 years movies information", 5)
print(len(res), "Wikipedia pages scraped")
for r in res:
    print(r["title"], "→", r["url"])
    print(r["text"][:300], "\n")







