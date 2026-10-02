"""Pluggable LLM layer for PaisaPilot's agent.

Priority order:
1. AWS Bedrock (boto3) — when AWS credentials are available. This is the
   documented AWS integration used for the hackathon's AWS Builder mini
   challenge (Amazon Bedrock runtime call).
2. Heuristic fallback — the built-in intent parser in agent.py always works
   offline, so the demo never depends on a key.

Env vars:
    AWS_REGION        (default: ap-south-1)
    BEDROCK_MODEL_ID  (default: amazon.nova-micro-v1:0)
"""
import json
import os

AWS_REGION = os.environ.get("AWS_REGION", "ap-south-1")
BEDROCK_MODEL_ID = os.environ.get("BEDROCK_MODEL_ID", "amazon.nova-micro-v1:0")


def bedrock_available():
    try:
        import boto3  # noqa: F401
    except ImportError:
        return False, "boto3 not installed (pip install boto3)"
    # Credentials present? (env vars, shared file, or instance role)
    try:
        import boto3
        sess = boto3.Session()
        creds = sess.get_credentials()
        if creds is None:
            return False, "no AWS credentials found"
        return True, "ok"
    except Exception as e:  # noqa: BLE001
        return False, str(e)


def bedrock_generate(prompt, max_tokens=400):
    """Call an Amazon Bedrock model. Returns (text | None, error | None)."""
    ok, why = bedrock_available()
    if not ok:
        return None, why
    try:
        import boto3
        client = boto3.client("bedrock-runtime", region_name=AWS_REGION)
        body = {
            "messages": [{"role": "user", "content": [{"text": prompt}]}],
            "inferenceConfig": {"maxTokens": max_tokens, "temperature": 0.2},
        }
        resp = client.invoke_model(modelId=BEDROCK_MODEL_ID, body=json.dumps(body))
        payload = json.loads(resp["body"].read())
        text = payload["output"]["message"]["content"][0]["text"]
        return text.strip(), None
    except Exception as e:  # noqa: BLE001
        return None, str(e)


EXTRACTION_PROMPT = """You are a money-assistant intent parser. Read the user's message and reply with ONLY a JSON object, no other text.
Intents: log_expense, set_budget, add_watch, remove_watch, summary, list_watches, help.
Fields: amount (number), category (food|transport|shopping|bills|entertainment|health|education|travel|other), note, monthly_limit, name, target_price, url, watch_id.
User message: "{text}"
JSON:"""


def llm_parse_intent(text):
    """Try Bedrock for intent extraction. Returns dict | None."""
    prompt = EXTRACTION_PROMPT.format(text=text[:500])
    out, err = bedrock_generate(prompt)
    if out is None:
        return None
    try:
        start = out.find("{")
        end = out.rfind("}") + 1
        data = json.loads(out[start:end])
        if isinstance(data, dict) and "intent" in data:
            return data
    except (json.JSONDecodeError, ValueError):
        return None
    except Exception:  # noqa: BLE001
        pass
    return None
