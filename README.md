# PaisaPilot — your money copilot (simulated Alexa+ experience)

**Hackathon:** Build, Ship, Shape: Amazon Developer Hackathon · **Track:** Alexa+ (simulated experience path)
**Entrant:** Devadi321 (solo) · **Submission deadline:** ~26 Oct 2026

## What it is

A web app that simulates an Alexa+ money-copilot skill: talk (or type) to log
spending, set monthly budgets, and track product prices — and the agent warns
you before you overshoot. No Amazon device needed; the "simulated Alexa+
experience" path only requires the simulation's source code + demo video.

Two tools mashed into one agent:
- **Money Manager** — voice expense logging, category auto-detection, monthly
  budgets with 80%/100% warnings, spending dashboard.
- **Deal Watch** — "Track iPhone 17 below 70000" puts a product on a watchlist;
  price checks alert you (voice + UI) when it drops to target.

## How the "agent" works

`backend/agent.py` — intent pipeline:
1. **Amazon Bedrock** (`backend/llm.py`) for LLM intent extraction when AWS
   credentials are present → this is the documented AWS integration for the
   **AWS Builder mini challenge** (Bedrock runtime `invoke_model` call).
2. **Heuristic fallback parser** — regex intent parsing that works fully
   offline, so the demo never depends on a key.

Voice in/out in the browser via Web Speech API (STT) + speechSynthesis (TTS).

## Run it

```bash
cd paisapilot
python3 -m venv .venv && .venv/bin/pip install -r backend/requirements.txt
PORT=5000 .venv/bin/python -m backend.app
# open http://localhost:5000
```

Optional (enables the Bedrock path + AWS Builder mini-challenge):
```bash
.venv/bin/pip install boto3
export AWS_REGION=ap-south-1 BEDROCK_MODEL_ID=amazon.nova-micro-v1:0
# AWS credentials via env / ~/.aws / instance role; $150 hackathon credits form due Oct 21
```

## Try saying

- "Spent 250 on lunch" / "I spent ₹500 for groceries"
- "Set budget 5000 for food"
- "Track iPhone 17 below 70000" (+ optional product URL)
- "How much did I spend?" / "List my watches"

## Submission checklist

- [x] Registered on Devpost (Devadi321)
- [x] Working web app + agent
- [ ] Claim $150 AWS credits (form due Oct 21) → enable Bedrock path
- [x] Demo video < 3 min (YouTube/Vimeo, public, English) — BUILT 2 Oct 2026: 57s narrated demo at docs/video/paisapilot-demo.mp4 (needs upload to YouTube + link)
- [ ] GitHub repo (public + license, or private shared with testing@devpost.com + Amazon team)
- [ ] Product feedback answers (tools used, what worked, friction)
- [ ] Friction log (docs/friction-log.md) — up to 10% judging bonus
- [ ] Submit on Devpost before deadline
