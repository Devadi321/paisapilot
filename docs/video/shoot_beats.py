"""Per-beat screenshots for the PaisaPilot demo video."""
from playwright.sync_api import sync_playwright

BASE = "http://localhost:5059"
OUT = "docs/video/shots"

with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={"width": 1280, "height": 800})
    pg.goto(BASE, wait_until="networkidle")
    pg.wait_for_timeout(800)
    pg.screenshot(path=f"{OUT}/b1-hook.png")          # beat 1: hook, empty talk UI

    pg.fill("#textin", "I spent 250 on lunch")
    pg.click("#send"); pg.wait_for_timeout(900)
    pg.screenshot(path=f"{OUT}/b2-expense.png")       # beat 2: expense logged

    pg.fill("#textin", "Set budget 5000 for food")
    pg.click("#send"); pg.wait_for_timeout(900)
    pg.fill("#textin", "Spent 4500 on biryani party")
    pg.click("#send"); pg.wait_for_timeout(900)
    pg.screenshot(path=f"{OUT}/b3-budget.png")        # beat 3: budget + 95% warning

    pg.fill("#textin", "Track iPhone 17 below 70000")
    pg.click("#send"); pg.wait_for_timeout(900)
    pg.click('[data-tab="watch"]'); pg.wait_for_timeout(800)
    pg.screenshot(path=f"{OUT}/b4-dealwatch.png")      # beat 4: price watch tab

    pg.click('[data-tab="dash"]'); pg.wait_for_timeout(1200)
    pg.screenshot(path=f"{OUT}/b5-tech.png")          # beat 5: dashboard (product)

    pg.click('[data-tab="chat"]'); pg.wait_for_timeout(600)
    pg.screenshot(path=f"{OUT}/b6-close.png")         # beat 6: close on talk UI

    b.close()
print("beat shots done")
