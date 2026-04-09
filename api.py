"""API REST — endpoint compartilhado para Telegram, WhatsApp e qualquer client."""

from fastapi import FastAPI, Request
from pydantic import BaseModel
import config
from rag import engine

app = FastAPI(title="Estudio de Oculus - Bot API")


class Question(BaseModel):
    question: str


class Answer(BaseModel):
    answer: str


@app.on_event("startup")
async def startup():
    engine.load()


@app.post("/ask", response_model=Answer)
async def ask(q: Question):
    answer = engine.query(q.question)
    return Answer(answer=answer)


@app.get("/health")
async def health():
    return {"status": "ok"}


# --- WhatsApp Webhook (Meta Business API) ---

@app.get("/webhook")
async def verify_webhook(request: Request):
    """Verificacao do webhook pelo Meta."""
    params = request.query_params
    mode = params.get("hub.mode")
    token = params.get("hub.verify_token")
    challenge = params.get("hub.challenge")

    if mode == "subscribe" and token == config.WHATSAPP_VERIFY_TOKEN:
        return int(challenge)
    return {"error": "verificacao falhou"}, 403


@app.post("/webhook")
async def whatsapp_webhook(request: Request):
    """Recebe mensagens do WhatsApp e responde."""
    import httpx

    body = await request.json()

    try:
        entry = body["entry"][0]
        changes = entry["changes"][0]
        value = changes["value"]
        message = value["messages"][0]
        from_number = message["from"]
        text = message["text"]["body"]
    except (KeyError, IndexError):
        return {"status": "ignored"}

    answer = engine.query(text)

    async with httpx.AsyncClient() as client:
        await client.post(
            f"https://graph.facebook.com/v21.0/{config.WHATSAPP_PHONE_ID}/messages",
            headers={
                "Authorization": f"Bearer {config.WHATSAPP_TOKEN}",
                "Content-Type": "application/json",
            },
            json={
                "messaging_product": "whatsapp",
                "to": from_number,
                "type": "text",
                "text": {"body": answer},
            },
        )

    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=config.API_PORT)
