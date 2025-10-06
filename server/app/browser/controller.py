from __future__ import annotations
import os, random, time
from typing import Optional, cast
from playwright.sync_api import sync_playwright, Page


class BrowserController:
    def __init__(self, run_dir: str):
        self.run_dir = run_dir
        self._pw = None
        self.browser = None
        self.context = None          # ✅ keep reference
        self.page: Page | None = None  # Python 3.10+ syntax


    def __enter__(self):
        os.makedirs(self.run_dir, exist_ok=True)
        self._pw = sync_playwright().start()

        headless = os.getenv("HEADLESS", "false").lower() == "true"
        ua_list = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        ]
        user_agent = random.choice(ua_list)

        # --- Attempt to launch Chromium ---
        try:
            self.browser = self._pw.chromium.launch(
                headless=headless,
                args=[
                    "--no-sandbox",
                    "--disable-blink-features=AutomationControlled",
                    "--disable-dev-shm-usage",
                    "--disable-features=IsolateOrigins,site-per-process",
                ],
            )
        except Exception as e:
            print(f"[BrowserController] Launch failed once: {e}")
            print("[BrowserController] Retrying in headless mode...")
            self.browser = self._pw.chromium.launch(headless=True)

        # --- Create context ---
        vw = random.randint(1280, 1440)
        vh = random.randint(820, 920)
        self.context = self.browser.new_context(
            user_agent=user_agent,
            locale="en-IN",
            timezone_id="Asia/Kolkata",
            viewport={"width": vw, "height": vh},
            extra_http_headers={
                "Accept-Language": "en-IN,en;q=0.9",
                "Sec-CH-UA": '"Chromium";v="124", "Not:A-Brand";v="99"',
                "Sec-CH-UA-Platform": '"Windows"',
            },
        )

        # --- Create and verify page ---
        self.page = self.context.new_page()
        if not self.page:
            raise RuntimeError("BrowserController: Failed to create a Playwright page.")

        # --- Add cookies ---
        try:
            self.context.add_cookies([
                {"name": "lc-main", "value": "en_IN", "domain": ".amazon.in", "path": "/"},
                {"name": "i18n-prefs", "value": "INR", "domain": ".amazon.in", "path": "/"},
            ])
        except Exception as e:
            print(f"[BrowserController] Warning: Cookie set failed: {e}")

        # --- Set timeouts ---
        self.page.set_default_timeout(10_000)
        self.page.set_default_navigation_timeout(20_000)

        print("[BrowserController] ✅ Browser ready. Headless:", headless)
        print(f"[BrowserController] Page object valid: {bool(self.page)}")
        return self

    def __exit__(self, exc_type, exc, tb):
        try:
            if self.context:
                self.context.close()
            if self.browser:
                self.browser.close()
        finally:
            if self._pw:
                try:
                    self._pw.stop()
                except Exception as e:
                    print(f"[BrowserController] Cleanup error: {e}")

    # ---------- Helper Methods ----------
    def _ensure_page(self) -> Page:
        if not self.page and self.browser:
            if not self.context:
                self.context = self.browser.new_context()
            self.page = self.context.new_page()
            print("[BrowserController] ⚠️ Recreated missing page context.")
        if not self.page:
            raise RuntimeError("BrowserController: page not initialized")
        return cast(Page, self.page)  # ✅ tells Pylance it’s non-None


    def goto(self, url: str, timeout: Optional[int] = 60_000, wait_until: str = "domcontentloaded"):
        self._ensure_page()
        print(f"[BrowserController] Navigating to {url}")
        return self.page.goto(url, timeout=timeout, wait_until=wait_until)

    def screenshot(self, filename: Optional[str] = None, full_page: bool = True) -> str:
        self._ensure_page()
        if not filename:
            filename = f"snap_{int(time.time())}.png"
        path = os.path.join(self.run_dir, filename)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        self.page.screenshot(path=path, full_page=full_page)
        return path

    def save_html(self, filename: str) -> str:
        self._ensure_page()
        path = os.path.join(self.run_dir, filename)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(self.page.content())
        return path
