// PaisaPilot frontend — simulated Alexa+ voice experience.
const $ = (id) => document.getElementById(id);
const chatBox = $("chat"), micBtn = $("mic"), textIn = $("textin"),
      sendBtn = $("send"), micStatus = $("mic-status");

// ---------- chat ----------
function addMsg(text, who) {
  const d = document.createElement("div");
  d.className = "msg " + who;
  d.textContent = text;
  chatBox.appendChild(d);
  chatBox.scrollTop = chatBox.scrollHeight;
}

function speak(text) {
  try {
    if (!("speechSynthesis" in window)) return;
    speechSynthesis.cancel();
    const u = new SpeechSynthesisUtterance(text.slice(0, 280));
    u.rate = 1.02;
    speechSynthesis.speak(u);
  } catch (e) { /* voice is best-effort */ }
}

async function send(text) {
  text = (text || "").trim();
  if (!text) return;
  addMsg(text, "user");
  textIn.value = "";
  try {
    const r = await fetch("/api/chat", {
      method: "POST", headers: {"Content-Type": "application/json"},
      body: JSON.stringify({text}),
    });
    const j = await r.json();
    addMsg(j.reply, "alexa");
    speak(j.speak || j.reply);
    refreshDash(); refreshWatches();
  } catch (e) {
    addMsg("Hmm, I couldn't reach my brain. Is the server running?", "alexa");
  }
}

sendBtn.onclick = () => send(textIn.value);
textIn.addEventListener("keydown", (e) => { if (e.key === "Enter") send(textIn.value); });
document.querySelectorAll(".chip").forEach(c => c.onclick = () => send(c.textContent));

// ---------- voice input ----------
let rec = null;
micBtn.onclick = () => {
  const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
  if (!SR) { micStatus.textContent = "Voice input needs Chrome or Edge — type instead."; return; }
  if (rec) { rec.stop(); rec = null; micBtn.classList.remove("listening"); micStatus.textContent = ""; return; }
  rec = new SR();
  rec.lang = "en-IN";
  rec.interimResults = false;
  micBtn.classList.add("listening");
  micStatus.textContent = "Listening… speak now.";
  rec.onresult = (e) => {
    const t = e.results[0][0].transcript;
    micStatus.textContent = 'Heard: "' + t + '"';
    send(t);
  };
  rec.onerror = () => { micStatus.textContent = "Didn't catch that — try again."; };
  rec.onend = () => { micBtn.classList.remove("listening"); rec = null; setTimeout(()=>micStatus.textContent="", 2500); };
  rec.start();
};

// ---------- tabs ----------
document.querySelectorAll(".tab").forEach(t => t.onclick = () => {
  document.querySelectorAll(".tab").forEach(x => x.classList.remove("active"));
  document.querySelectorAll(".panel").forEach(x => x.classList.remove("active"));
  t.classList.add("active");
  $("tab-" + t.dataset.tab).classList.add("active");
  if (t.dataset.tab === "dash") refreshDash();
  if (t.dataset.tab === "watch") refreshWatches();
});

// ---------- dashboard ----------
let catChart = null;
const inr = (n) => "₹" + Number(n || 0).toLocaleString("en-IN", {maximumFractionDigits: 0});

async function refreshDash() {
  try {
    const s = await (await fetch("/api/summary")).json();
    $("d-total").textContent = inr(s.total);
    $("d-top").textContent = s.by_category.length ? s.by_category[0][0] + " · " + inr(s.by_category[0][1]) : "—";

    // budgets
    const bw = $("d-budgets");
    if (!s.budgets.length) {
      bw.innerHTML = '<p class="muted">No budgets yet — say "Set budget 5000 for food".</p>';
    } else {
      bw.innerHTML = s.budgets.map(b => {
        const over = b.pct >= 100;
        return `<div class="budget-row"><div class="bl"><span>${b.category}</span>
          <span>${inr(b.spent)} / ${inr(b.limit)} (${b.pct}%)</span></div>
          <div class="bar${over ? " over" : ""}"><div style="width:${Math.min(b.pct,100)}%"></div></div></div>`;
      }).join("");
    }

    // recent
    const ex = await (await fetch("/api/expenses?limit=8")).json();
    $("d-recent").innerHTML = ex.length ? ex.slice(0, 8).map(e =>
      `<div class="exp-row"><div>${e.note || e.category}<div class="cat">${e.category}</div></div>
       <div><span class="amt">${inr(e.amount)}</span>
       <button class="del" data-id="${e.id}" title="delete">✕</button></div></div>`).join("")
      : '<p class="muted">No expenses yet.</p>';
    document.querySelectorAll(".del").forEach(b => b.onclick = async () => {
      await fetch("/api/expenses/" + b.dataset.id, {method: "DELETE"});
      refreshDash();
    });

    // chart
    if (window.Chart && s.by_category.length) {
      const ctx = $("ch-cat");
      if (catChart) catChart.destroy();
      catChart = new Chart(ctx, {
        type: "doughnut",
        data: { labels: s.by_category.map(x => x[0]),
                datasets: [{ data: s.by_category.map(x => x[1]),
                  backgroundColor: ["#33c3ff","#7b5cff","#ff5da2","#3ddc84","#ffb020","#ff8a5d","#9d7bff","#5ddcff"] }] },
        options: { plugins: { legend: { labels: { color: "#eef2ff" } } } },
      });
    }
  } catch (e) { /* dashboard is best-effort */ }
}

// ---------- price watch ----------
async function refreshWatches() {
  try {
    const ws = await (await fetch("/api/watchlist")).json();
    const box = $("w-list");
    if (!ws.length) { box.innerHTML = '<p class="muted">Nothing tracked yet.</p>'; return; }
    box.innerHTML = ws.map(w => `
      <div class="watch-row">
        <div><div class="nm">${w.name} ${w.alerted ? '<span class="alert">🔥 DEAL!</span>' : ""}</div>
        <div class="pr">target ${inr(w.target_price)} · now ${w.last_price ? inr(w.last_price) : "unknown"}</div></div>
        <div><button class="check" data-id="${w.id}">Check</button>
        <button class="del" data-id="${w.id}">✕</button></div>
      </div>`).join("");
    box.querySelectorAll(".check").forEach(b => b.onclick = async () => {
      b.textContent = "…";
      const r = await (await fetch("/api/watchlist/" + b.dataset.id + "/check", {method: "POST"})).json();
      if (r.alert) speak(`Deal alert! ${r.name} is now ${inr(r.price)}, below your target of ${inr(r.target)}.`);
      refreshWatches();
    });
    box.querySelectorAll(".del").forEach(b => b.onclick = async () => {
      await fetch("/api/watchlist/" + b.dataset.id, {method: "DELETE"});
      refreshWatches();
    });
  } catch (e) { /* best-effort */ }
}

$("w-add").onclick = async () => {
  const name = $("w-name").value.trim(), target = parseFloat($("w-target").value), url = $("w-url").value.trim();
  if (!name || !target) { alert("Give me a product name and a target price."); return; }
  await send(`Track ${name} below ${target}${url ? " " + url : ""}`);
  $("w-name").value = $("w-target").value = $("w-url").value = "";
  document.querySelector('[data-tab="watch"]').click();
};
$("w-checkall").onclick = async () => {
  const rs = await (await fetch("/api/watchlist/check-all", {method: "POST"})).json();
  const deals = rs.filter(r => r.alert);
  if (deals.length) speak(`Deal alert! ${deals.map(d => d.name + " at " + inr(d.price)).join(", ")}`);
  refreshWatches();
};

// greeting
addMsg("Hi! I'm PaisaPilot, your money copilot. Try: “Spent 250 on lunch”, “Set budget 5000 for food”, or “Track iPhone 17 below 70000”.", "alexa");
refreshDash();
