# Friction log — PaisaPilot

Kept during the build for the hackathon's product-feedback requirement.
(Friction logs can earn up to a 10% judging bonus.)

## 2026-10-02 — Day 1: scaffold + agent + UI

| # | Task attempted | Steps taken | Expected vs actual | Severity | Workaround / suggestion |
|---|---------------|-------------|-------------------|----------|------------------------|
| 1 | `pip install flask` on the VM | Ran `pip install flask` | Expected install; got PEP 668 "externally managed environment" error | Low | Used `python3 -m venv .venv` in the project dir. Suggestion: Devpost/Amazon docs could mention venvs for Linux beginners. |
| 2 | Heuristic intent parsing for money commands | Wrote regex parser for spend/budget/watch/summary intents | Worked first try for canonical phrasings; "groceries" initially mapped to `other` | Low | Added grocery/kirana/supermarket keywords. Voice input will produce messier phrasings — the Bedrock LLM parser path exists as the upgrade. |
| 3 | Price extraction from product pages | urllib + regex over JSON-LD/meta/₹ patterns | Works on pages with JSON-LD; JS-rendered stores (most big retailers) return "no price found" | Medium | For the demo, manual price entry + "Check" button; a real deployment would need a headless-browser fetcher. |
| 4 | Devpost registration checkbox | ~20 automation attempts on the "agree to Official Rules" checkbox | Clicks landed but never toggled (label contains embedded links, likely breaking the handler) | Medium | User completed it manually via browser takeover. Devpost: the checkbox label's nested links seem to swallow click events. |
| 5 | Headless video-pipeline screenshots (Playwright) | Installed playwright, scripted the demo conversation, captured 4 screenshots | Worked first try; UI renders exactly as designed | Low | Pipeline validated for the final video assembly (ffmpeg + TTS next). |
| 6 | Killing the Flask server with `pkill -f "backend.app"` | Ran pkill with a pattern matching the app module | pkill matched the shell's own command line and SIGTERM'd my own exec session | Low | Lesson: never pkill with a pattern that appears in the invoking command; match on port (`-f "5059"`) or store the PID and `kill` it directly. |
