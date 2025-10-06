from app.browser.controller import BrowserController

with BrowserController(run_dir="runs") as bc:
    bc.goto("https://www.flipkart.com")
    bc.screenshot("flipkart_test.png")
    print("✅ Page title:", bc.page.title())
