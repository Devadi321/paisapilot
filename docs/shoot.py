"""Capture demo screenshots for the PaisaPilot video pipeline validation."""
from playwright.sync_api import sync_playwright

BASE = "http://localhost:5059"
OUT = "docs/demo-shots"

with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={"width": 1280, "height": 800})
    pg.goto(BASE, wait_until="networkidle")
    pg.wait_for_timeout(800)
    pg.screenshot(path=f"{OUT}/01-talk-empty.png")

    # drive the scripted demo conversation
    for msg in ["I spent 250 on lunch", "Set budget 5000 for food",
                "Spent 4500 on biryani party", "Track iPhone 17 below 70000"]:
        pg.fill("#textin", msg)
        pg.click("#send")
        pg.wait_for_timeout(900)
    pg.screenshot(path=f"{OUT}/02-talk-conversation.png")

    # dashboard
    pg.click('[data-tab="dash"]')
    pg.wait_for_timeout(1200)
    pg.screenshot(path=f"{OUT}/03-dashboard.png")

    # price watch
    pg.click('[data-tab="watch"]')
    pg.wait_for_timeout(800)
    pg.screenshot(path=f"{OUT}/04-pricewatch.png")

    b.close()
print("shots done")
