"""Step 1: load The Dish page in a real (headless) browser and save what we find,
so we can see where the menu data lives. Nothing is emailed yet."""
import json, pathlib
from playwright.sync_api import sync_playwright
 
URL = "https://illinitower.mydininghub.com/en/location/the-dish"
out = pathlib.Path("probe_output"); out.mkdir(exist_ok=True)
json_responses = []
 
with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page()
 
    def on_response(resp):
        ct = resp.headers.get("content-type", "")
        if "json" in ct:
            try:
                json_responses.append({"url": resp.url, "status": resp.status, "body": resp.json()})
            except Exception:
                pass
 
    page.on("response", on_response)
    page.goto(URL, wait_until="networkidle", timeout=90000)
    page.wait_for_timeout(5000)
    (out / "rendered.html").write_text(page.content(), encoding="utf-8")
    (out / "visible_text.txt").write_text(page.inner_text("body"), encoding="utf-8")
    page.screenshot(path=str(out / "page.png"), full_page=True)
    browser.close()
 
(out / "json_responses.json").write_text(json.dumps(json_responses, indent=2)[:5_000_000], encoding="utf-8")
print(f"Saved {len(json_responses)} JSON responses. Visible text preview:")
print((out / "visible_text.txt").read_text()[:1500])
