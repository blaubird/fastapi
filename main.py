from fastapi import FastAPI, Request, HTTPException, Response, Query
from fastapi.responses import HTMLResponse
import os, httpx, hmac, hashlib, json

app = FastAPI()
# ---------- static landing ----------
landing = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8" />
<title>Luminiteq – Digital Solutions</title>
<style>
    body{margin:0;font-family:Arial,Helvetica,sans-serif;
         background:#0f172a;color:#f8fafc;display:flex;
         align-items:center;justify-content:center;height:100vh;}
    .card{text-align:center;padding:2rem 3rem;border-radius:1rem;
          background:#1e293b;box-shadow:0 8px 24px #0004;}
    h1{margin:0;font-size:2rem;}
    p{opacity:.8;margin:.5rem 0 1.5rem}
    a{color:#38bdf8;text-decoration:none;font-weight:600}
</style>
</head>
<body>
<div class="card">
  <h1>макс иди нахуй</h1>
  <p>AI Agents · Chatbots · Websites · Automation</p>
  <a href="mailto:hello@luminiteq.eu">Contact us → hello@luminiteq.eu</a>
</div>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse, include_in_schema=False)
async def index():
    return HTMLResponse(content=landing, status_code=200)
# --- env ---
OPENAI_KEY   = os.getenv("OPENAI_API_KEY")
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")
WH_TOKEN     = os.getenv("WH_TOKEN")
WH_PHONE_ID  = os.getenv("WH_PHONE_ID")

# --- health ---
@app.get("/health", include_in_schema=False)
@app.head("/health", include_in_schema=False)
async def health():
    return {"ok": True}

# ----- Meta VERIFY -----
@app.get("/webhook", include_in_schema=False)
async def verify_webhook(
        hub_mode: str        = Query(None, alias="hub.mode"),
        hub_token: str       = Query(None, alias="hub.verify_token"),
        hub_challenge: str   = Query(None, alias="hub.challenge")
):
    if hub_mode == "subscribe" and hub_token == VERIFY_TOKEN:
        # Meta ждёт plain-text
        return Response(content=hub_challenge, media_type="text/plain")
    raise HTTPException(status_code=403, detail="Forbidden")

# --- incoming messages ---
@app.post("/webhook", include_in_schema=False)
async def webhook(req: Request):
    body = await req.json()
    # 1. пробегаем по входящим сообщениям
    for entry in body.get("entry", []):
        for change in entry.get("changes", []):
            value = change.get("value", {})
            for msg in value.get("messages", []):
                from_id = msg["from"]        # телефон клиента
                text    = msg["text"]["body"]
                # 2. простой авто-ответ
                await send_whatsapp(from_id, f"👋 Вы написали: '{text}'. Скоро подключим ИИ!")
    return {"status": "ok"}

# --- helper to send message back ---
async def send_whatsapp(to, text):
    url = f"https://graph.facebook.com/v18.0/{WH_PHONE_ID}/messages"
    payload = {"messaging_product":"whatsapp",
               "to": to,
               "type":"text",
               "text": {"body": text}}
    headers = {"Authorization": f"Bearer {WH_TOKEN}",
               "Content-Type": "application/json"}
    async with httpx.AsyncClient(timeout=10) as cli:
        r = await cli.post(url, json=payload, headers=headers)
        r.raise_for_status()
