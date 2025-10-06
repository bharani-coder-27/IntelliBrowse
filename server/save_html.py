from browser.controller import BrowserController

if __name__ == "__main__":
    with BrowserController(run_dir="runs") as bc:
        bc.goto("https://www.amazon.in/s?k=laptops+under+50000", timeout=60000)
        bc.save_html("amazon_page.html")
        print("✅ Saved Amazon search HTML to amazon_page.html")
