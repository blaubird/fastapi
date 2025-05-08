from fastapi import FastAPI, Request, HTTPException, Response
import os, httpx, hmac, hashlib, json

app = FastAPI()

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

# --- Meta webhook verification ---
@app.get("/webhook", include_in_schema=False)
async def verify(mode: str = "", challenge: str = "", verify_token: str = ""):
    if mode == "subscribe" and verify_token == VERIFY_TOKEN:
        return Response(content=challenge, media_type="text/plain")
    raise HTTPException(403, "Verification failed")

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
