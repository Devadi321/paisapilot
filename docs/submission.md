# Devpost submission draft — PaisaPilot

## Basics
- **Title:** PaisaPilot — your money copilot
- **Tagline (≤140 chars):** A voice-first money copilot for Alexa+: log spending, set budgets, and hunt deals just by talking.
- **Track:** Alexa+ (simulated experience path)
- **Mini challenge:** AWS Builder (Bedrock integration — pending credits; heuristic fallback ships regardless)

## Text description (features & functionality)
PaisaPilot is a simulated Alexa+ experience: a money copilot you talk to instead of
typing into. Say "Alexa, I spent 250 on lunch" and the agent logs the expense,
auto-detects the category (food, transport, shopping, bills, entertainment, health,
education, travel), and talks back. Say "Set budget 5000 for food" and it tracks the
month — warning you at 80% and 100%, before the money is gone, not after. A dashboard
shows spending by category, budget bars, and recent expenses. And it hunts deals:
"Track iPhone 17 below 70000" puts a product on a watchlist; PaisaPilot checks the
price and fires a voice + visual alert when it drops to target.

## How it's built
- **Frontend:** single-page web app with an Alexa-style voice UI (Web Speech API
  for speech-to-text, speechSynthesis for replies), dashboard (Chart.js), price-watch tab.
- **Backend:** Python Flask + SQLite. `agent.py` runs the intent pipeline:
  1) Amazon Bedrock (`llm.py`, `invoke_model`) for LLM intent extraction when AWS
     credentials are present;
  2) a built-in heuristic parser fallback that works fully offline, so the demo never
     depends on a key.
- **Price checks:** best-effort extraction from JSON-LD/meta/₹ patterns; manual
  refresh + "check all" supported.
- **Repo:** (GitHub URL to add) — public, MIT license, README with run instructions.

## Demo video
- **URL:** https://www.youtube.com/watch?v=qLEERiTbOMY (uploaded 2 Oct 2026, Public, English)
- Public, English, under 3 minutes. Shows: voice expense logging → budget warnings →
  deal watch → dashboard → tech overview.

## Product feedback (required)
- **Tools/APIs/SDKs used and for what:**
  - Flask (Python web backend + REST API) — served the app and agent endpoints.
  - Web Speech API (browser) — voice input; speechSynthesis — voice replies.
  - Chart.js (vendored locally) — spending doughnut chart.
  - Amazon Bedrock (planned, via `llm.py`) — LLM intent parsing for the AWS Builder
    mini challenge; $150 credits requested 2 Oct 2026.
  - Playwright + ffmpeg — headless demo capture and video assembly.
- **What worked well:** Flask got the API up in minutes; Web Speech API needed no
  keys and worked in Chrome; Playwright drove the whole demo script deterministically
  for screenshots.
- **What needs work:** Web Speech API only works in Chromium browsers and struggles
  with Indian-accented English on some phrases; price extraction fails on
  JS-rendered retailer pages (needs a headless fetcher in production).
- **Onboarding:** Flask/Python docs got us from zero to running server in ~10 minutes.
  Bedrock onboarding is still pending credits.
- **Would you build with these again?** Yes for Flask + Web Speech API for rapid
  voice prototypes; Bedrock TBD after credits land.

## Friction log
`docs/friction-log.md` — 6 entries and counting (PEP 668 venv fix, Devpost checkbox
automation failure, pkill footgun, Playwright pipeline validation, Chart.js vendoring).

## If the project existed before the window
N/A — built from scratch on 2 Oct 2026, inside the submission window.
