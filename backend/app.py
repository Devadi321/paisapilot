"""PaisaPilot backend — Flask API serving the simulated Alexa+ web experience."""
import os

from flask import Flask, jsonify, request, send_from_directory

from . import agent, db, prices

FRONTEND_DIR = os.path.join(os.path.dirname(__file__), "..", "frontend")

app = Flask(__name__)
db.init_db()


@app.get("/")
def index():
    return send_from_directory(FRONTEND_DIR, "index.html")


@app.get("/<path:filename>")
def static_files(filename):
    return send_from_directory(FRONTEND_DIR, filename)


@app.post("/api/chat")
def chat():
    data = request.get_json(force=True, silent=True) or {}
    text = (data.get("text") or "").strip()
    if not text:
        return jsonify({"reply": "Say something like 'Spent 250 on lunch'.", "speak": "", "data": {}})
    result = agent.handle(text)
    return jsonify(result)


@app.get("/api/expenses")
def get_expenses():
    month = request.args.get("month")
    return jsonify(db.list_expenses(month=month))


@app.delete("/api/expenses/<int:eid>")
def del_expense(eid):
    db.delete_expense(eid)
    return jsonify({"ok": True})


@app.get("/api/budgets")
def get_budgets():
    return jsonify(db.list_budgets())


@app.delete("/api/budgets/<category>")
def del_budget(category):
    db.delete_budget(category)
    return jsonify({"ok": True})


@app.get("/api/watchlist")
def get_watchlist():
    return jsonify(db.list_watches())


@app.delete("/api/watchlist/<int:wid>")
def del_watch(wid):
    db.delete_watch(wid)
    return jsonify({"ok": True})


@app.post("/api/watchlist/<int:wid>/check")
def check_watch(wid):
    watches = {w["id"]: w for w in db.list_watches()}
    w = watches.get(wid)
    if not w:
        return jsonify({"error": "watch not found"}), 404
    price, err = prices.check_price(w["url"]) if w["url"] else (None, "no URL saved")
    alerted = bool(price and price <= w["target_price"])
    if price:
        db.update_watch_price(wid, price, alerted)
    return jsonify({"price": price, "error": err, "alert": alerted,
                    "target": w["target_price"], "name": w["name"]})


@app.post("/api/watchlist/check-all")
def check_all():
    results = []
    for w in db.list_watches():
        price, err = prices.check_price(w["url"]) if w["url"] else (None, "no URL saved")
        alerted = bool(price and price <= w["target_price"])
        if price:
            db.update_watch_price(w["id"], price, alerted)
        results.append({"id": w["id"], "name": w["name"], "price": price,
                        "error": err, "alert": alerted, "target": w["target_price"]})
    return jsonify(results)


@app.get("/api/summary")
def summary():
    res = agent.handle_summary({})
    return jsonify(res["data"])


@app.get("/api/health")
def health():
    from . import llm
    ok, why = llm.bedrock_available()
    return jsonify({"status": "ok", "bedrock": {"available": ok, "detail": why}})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
