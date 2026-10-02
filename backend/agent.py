"""PaisaPilot agent: understands money commands, acts on them, replies like Alexa+.

Pipeline: try Bedrock LLM intent extraction (llm.py) -> fall back to the
built-in heuristic parser below, which needs no keys and works offline.
"""
import re
from datetime import datetime

from . import db
from . import llm
from . import prices

CATEGORIES = {
    "food": ["food", "lunch", "dinner", "breakfast", "meal", "restaurant", "pizza", "burger",
             "cafe", "coffee", "tea", "chai", "snack", "swiggy", "zomato", "eating", "biryani", "dosa",
             "groceries", "grocery", "kirana", "supermarket", "vegetables", "fruits"],
    "transport": ["transport", "cab", "taxi", "uber", "ola", "auto", "rickshaw", "bus", "train",
                  "metro", "fuel", "petrol", "diesel", "parking", "toll"],
    "shopping": ["shopping", "clothes", "shirt", "t-shirt", "jeans", "shoes", "dress", "amazon",
                 "flipkart", "myntra", "gadget", "earphones", "mobile cover"],
    "bills": ["bill", "electricity", "water", "rent", "recharge", "mobile bill", "internet", "wifi",
              "broadband", "emi", "insurance", "gas cylinder"],
    "entertainment": ["movie", "cinema", "pvr", "game", "concert", "netflix", "spotify", "prime video",
                      "hotstar", "jiocinema", "party"],
    "health": ["health", "doctor", "medicine", "medical", "pharmacy", "gym", "hospital", "clinic"],
    "education": ["book", "course", "exam", "tuition", "college", "fee", "udemy", "coursera"],
    "travel": ["travel", "flight", "hotel", "trip", "vacation", "holiday", "train ticket"],
}

AMOUNT_RE = r"(?:₹|rs\.?|inr)?\s*([\d,]+(?:\.\d{1,2})?)"


def inr(n):
    try:
        return f"₹{float(n):,.0f}"
    except (TypeError, ValueError):
        return "₹0"


def detect_category(text):
    t = text.lower()
    for cat, keywords in CATEGORIES.items():
        for kw in keywords:
            if kw in t:
                return cat
    return "other"


def _num(s):
    return float(s.replace(",", ""))


# ---------- heuristic intent parsing ----------

def heuristic_parse(text):
    t = text.lower().strip()

    # help
    if re.search(r"\b(help|what can you do|commands)\b", t):
        return {"intent": "help"}

    # monthly summary / spending report
    if re.search(r"\b(summary|report|how much.*(spend|spent)|total.*(spend|spent)|spending|my expenses)\b", t):
        return {"intent": "summary"}

    # list price watches
    if re.search(r"\b(list|show).*(watch|track)|my.*(watchlist|tracked)\b", t):
        return {"intent": "list_watches"}

    # remove a watch
    m = re.search(r"(?:stop (?:tracking|watching)|remove|delete).{0,40}?watch\s*(?:#|id\s*)?(\d+)", t)
    if m:
        return {"intent": "remove_watch", "watch_id": int(m.group(1))}

    # add a price watch: "track iphone 17 below 70000", "watch <name> under <price> [url]"
    m = re.search(r"(?:track|watch|alert me (?:on|about|for))\s+(.+?)\s+(?:below|under|less than|<)\s*" + AMOUNT_RE, t)
    if m:
        name = m.group(1).strip()
        url = ""
        um = re.search(r"(https?://\S+)", text)
        if um:
            url = um.group(1)
            name = name.replace(um.group(1), "").strip()
        return {"intent": "add_watch", "name": name[:80], "target_price": _num(m.group(2)), "url": url}

    # set budget: "set budget 5000 for food", "monthly budget 10000 shopping"
    m = re.search(r"budget[^\d]{0,20}" + AMOUNT_RE + r"(?:\s*(?:for|on)\s+(\w+))?", t)
    if m:
        cat = (m.group(2) or "other").lower()
        if cat not in CATEGORIES:
            cat = detect_category(cat) if detect_category(cat) != "other" else "other"
        return {"intent": "set_budget", "category": cat, "monthly_limit": _num(m.group(1))}

    # log expense: "spent 250 on lunch", "paid ₹500 for groceries", "120 auto"
    m = re.search(r"(?:spent|paid|spend|cost|bought|purchased)[^\d₹]{0,15}" + AMOUNT_RE + r"(?:\s*(?:on|for|at)\s+(.+))?", t)
    if m:
        rest = (m.group(2) or "").strip()
        return {"intent": "log_expense", "amount": _num(m.group(1)),
                "category": detect_category(rest), "note": rest[:120]}

    # bare "<amount> <note>": "250 lunch"
    m = re.match(r"^" + AMOUNT_RE + r"\s+(.+)$", t)
    if m and _num(m.group(1)) < 10_000_000:
        rest = m.group(2).strip()
        return {"intent": "log_expense", "amount": _num(m.group(1)),
                "category": detect_category(rest), "note": rest[:120]}

    return {"intent": "unknown"}


def parse_intent(text):
    """LLM first (Bedrock), heuristic fallback."""
    data = llm.llm_parse_intent(text)
    if data:
        return data
    return heuristic_parse(text)


# ---------- handlers ----------

def current_month():
    return datetime.now().strftime("%Y-%m")


def handle_log_expense(p):
    amount = p.get("amount")
    if not amount:
        return reply("How much did you spend? Try: 'Spent 250 on lunch'.")
    category = p.get("category") or detect_category(p.get("note", ""))
    note = p.get("note", "")
    db.add_expense(amount, category, note)
    month = current_month()
    spent = db.category_spend(category, month)
    msg = f"Logged {inr(amount)} for {category}"
    msg += f" ({note})." if note else "."
    for b in db.list_budgets():
        if b["category"] == category:
            pct = (spent / b["monthly_limit"] * 100) if b["monthly_limit"] else 0
            if pct >= 100:
                msg += f" Heads up — you've blown past your {inr(b['monthly_limit'])} {category} budget ({pct:.0f}% used)."
            elif pct >= 80:
                msg += f" Careful — you've used {pct:.0f}% of your {inr(b['monthly_limit'])} {category} budget."
            else:
                msg += f" That's {pct:.0f}% of your {inr(b['monthly_limit'])} {category} budget."
            break
    return reply(msg)


def handle_set_budget(p):
    limit = p.get("monthly_limit")
    category = (p.get("category") or "other").lower()
    if not limit:
        return reply("What should the monthly budget be? Try: 'Set budget 5000 for food'.")
    db.set_budget(category, limit)
    return reply(f"Done — your monthly {category} budget is {inr(limit)}. I'll warn you at 80%.")


def handle_add_watch(p):
    name = (p.get("name") or "").strip()
    target = p.get("target_price")
    url = p.get("url") or ""
    if not name or not target:
        return reply("Tell me what to track and your target price. Try: 'Track iPhone 17 below 70000'.")
    wid = db.add_watch(name, target, url)
    price, err = prices.check_price(url) if url else (None, "no URL given")
    extra = ""
    if price:
        db.update_watch_price(wid, price, price <= target)
        extra = f" Current price I see is {inr(price)}."
        if price <= target:
            extra += " It's already at or below your target — deal alert!"
    elif url:
        extra = f" I couldn't read the price yet ({err}); I'll keep trying."
    return reply(f"Watching '{name}' — I'll alert you when it drops to {inr(target)}.{extra}")


def handle_remove_watch(p):
    wid = p.get("watch_id")
    if not wid:
        return reply("Which watch should I remove? Say 'remove watch 2'. (See 'list my watches'.)")
    db.delete_watch(wid)
    return reply(f"Removed watch #{wid}.")


def handle_list_watches(_p):
    watches = db.list_watches()
    if not watches:
        return reply("Your watchlist is empty. Try: 'Track iPhone 17 below 70000'.")
    lines = []
    for w in watches:
        cur = inr(w["last_price"]) if w["last_price"] else "price unknown"
        lines.append(f"#{w['id']} {w['name']}: target {inr(w['target_price'])}, now {cur}")
    return reply("Here's your watchlist: " + " | ".join(lines), data={"watches": watches})


def handle_summary(_p):
    month = current_month()
    rows = db.spend_by_category(month)
    total = sum(v for _, v in rows)
    if total == 0:
        return reply("No spending logged this month yet. Say 'Spent 250 on lunch' to start.")
    top = rows[0]
    parts = [f"{cat}: {inr(v)}" for cat, v in rows[:5]]
    msg = f"This month you've spent {inr(total)}. Breakdown — " + ", ".join(parts) + "."
    msg += f" Biggest category is {top[0]} at {inr(top[1])}."
    budgets = []
    for b in db.list_budgets():
        spent = db.category_spend(b["category"], month)
        pct = (spent / b["monthly_limit"] * 100) if b["monthly_limit"] else 0
        budgets.append({"category": b["category"], "limit": b["monthly_limit"], "spent": spent, "pct": round(pct, 1)})
        if pct >= 80:
            msg += f" Watch out: {b['category']} is at {pct:.0f}% of budget."
    return reply(msg, data={"by_category": rows, "total": total, "budgets": budgets, "month": month})


def handle_help(_p):
    return reply(
        "Here's what I can do: log spending ('Spent 250 on lunch'), set budgets "
        "('Set budget 5000 for food'), track prices ('Track iPhone 17 below 70000'), "
        "show a summary ('How much did I spend?'), or list watches ('List my watches')."
    )


def reply(text, data=None, speak=None):
    return {"reply": text, "speak": speak or text, "data": data or {}}


HANDLERS = {
    "log_expense": handle_log_expense,
    "set_budget": handle_set_budget,
    "add_watch": handle_add_watch,
    "remove_watch": handle_remove_watch,
    "list_watches": handle_list_watches,
    "summary": handle_summary,
    "help": handle_help,
}


def handle(text):
    parsed = parse_intent(text)
    intent = parsed.get("intent", "unknown")
    fn = HANDLERS.get(intent)
    if not fn:
        return reply(
            "I didn't catch that. Try 'Spent 250 on lunch', 'Set budget 5000 for food', "
            "'Track iPhone 17 below 70000', or 'How much did I spend?'."
        )
    try:
        return fn(parsed)
    except Exception as e:  # noqa: BLE001
        return reply(f"Something went wrong on my end ({e}). Please try again.")
