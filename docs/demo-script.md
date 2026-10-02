# PaisaPilot — demo video script (target: ~2 min, hard cap 3 min)

Format: screen recording of the web app (http://localhost:5000) with voiceover.
Voice: Alexa-style TTS or recorded narration. Captions on. No copyrighted music.

## Shot list

### 0:00–0:15 — Hook
**Visual:** PaisaPilot landing on the Talk tab, mic glowing.
**VO:** "What if Alexa could stop you from overspending — and hunt deals for you?
Meet PaisaPilot: a money copilot built as a simulated Alexa+ experience."

### 0:15–0:50 — Act 1: voice expense logging
**Visual:** Tap mic, speak: *"Alexa, I spent 250 on lunch."*
Chat shows the message; Alexa replies "Logged ₹250 for food (lunch)."
**VO:** "Just talk. PaisaPilot logs the spend, detects the category, and talks back —
no forms, no spreadsheets."

### 0:50–1:20 — Act 2: budgets that warn you
**Visual:** Speak: *"Set budget 5000 for food."* → "Done — your monthly food budget is ₹5,000."
Then log a big expense; Alexa warns: "Careful — you've used 95% of your ₹5,000 food budget."
Cut to Dashboard tab: budget bar nearly full, category doughnut.
**VO:** "Set monthly budgets by voice. PaisaPilot warns you at 80% — before the money's gone,
not after. The dashboard shows exactly where it all went."

### 1:20–1:50 — Act 3: deal watch
**Visual:** Speak: *"Track iPhone 17 below 70000."* → watch added.
Open Price Watch tab, hit "Check" → price drops below target → 🔥 DEAL banner + voice alert.
**VO:** "And it hunts deals. Name a product and your price — PaisaPilot watches and yells
when it drops. Budgeting and bargain-hunting, one agent."

### 1:50–2:10 — How it's built (credibility, fast)
**Visual:** Quick code pan: `agent.py` intent pipeline, `llm.py` Bedrock hook.
**VO:** "Under the hood: an intent pipeline that parses money commands, with an
Amazon Bedrock hook for LLM understanding — and a full offline fallback, so the demo
never dies. Built for the Alexa+ simulated track, with the AWS Builder challenge in sight."

### 2:10–2:20 — Close
**Visual:** Back on the glowing mic. Tagline on screen.
**VO:** "PaisaPilot — talk money, stay in control. Thanks for watching."

## Recording notes
- Record at 1080p, browser window only. Do 3 takes of the voice lines; pick the cleanest.
- Seed demo data first: a few expenses + one budget + the iPhone watch, so every shot lands.
- Keep the cursor calm; pause 1 beat between acts for clean cuts.
- Export < 3:00, upload unlisted→public on YouTube, link it in the Devpost submission.
