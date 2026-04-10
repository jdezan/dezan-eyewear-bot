"""
API REST — Dezan Eyewear Bot
Endpoints:
  POST /ask               → consulta RAG direta (testes/integração)
  GET  /health            → healthcheck
  POST /webhook/evolution → recebe mensagens do WhatsApp via Evolution API
  POST /admin/faq/reload  → força recarga do FAQ do Google Sheets
"""
import asyncio
import logging

from fastapi import FastAPI, Request, Header, HTTPException
from pydantic import BaseModel

import config
from rag import engine

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
logger = logging.getLogger(__name__)

app = FastAPI(title="Dezan Eyewear — Bot API", version="2.0.0")


# ── Schemas ───────────────────────────────────────────────────────────────────
class Question(BaseModel):
    question: str

class Answer(BaseModel):
    answer: str


# ── Startup ───────────────────────────────────────────────────────────────────
@app.on_event("startup")
async def startup():
    logger.info("Carregando vectorstore FAISS...")
    engine.load()
    logger.info("RAG pronto.")


# ── Endpoints públicos ────────────────────────────────────────────────────────
@app.get("/health")
async def health():
    return {"status": "ok", "rag_loaded": engine.qa_chain is not None}


@app.post("/ask", response_model=Answer)
async def ask(q: Question):
    """Consulta RAG direta (para testes ou integrações externas)."""
    answer = engine.query(q.question)
    return Answer(answer=answer)


# ── Webhook Evolution API ─────────────────────────────────────────────────────
@app.post("/webhook/evolution")
async def evolution_webhook(request: Request):
    """
    Recebe eventos do WhatsApp via Evolution API.
    Configure no Evolution API:
      URL: https://<seu-bot>.easypanel.host/webhook/evolution
      Eventos: MESSAGES_UPSERT
    """
    from bot_whatsapp import handle_message

    body = await request.json()
    event = body.get("event", "")

    # Só processar mensagens novas recebidas
    if event not in ("MESSAGES_UPSERT", "messages.upsert"):
        return {"status": "ignored", "event": event}

    try:
        data = body.get("data", {})
        key = data.get("key", {})

        # Ignorar mensagens enviadas pelo próprio bot
        if key.get("fromMe", False):
            return {"status": "ignored", "reason": "fromMe"}

        remote_jid: str = key.get("remoteJid", "")

        # Ignorar grupos
        if "@g.us" in remote_jid:
            return {"status": "ignored", "reason": "group"}

        push_name: str = data.get("pushName", "")

        # Extrair texto da mensagem (texto normal ou resposta com texto)
        message = data.get("message", {})
        text: str = (
            message.get("conversation")
            or message.get("extendedTextMessage", {}).get("text")
            or ""
        )

        if not text.strip():
            return {"status": "ignored", "reason": "no_text"}

        logger.info(f"MSG de {push_name} ({remote_jid[:25]}): {text[:80]}")

        # Processa em background (responde ao Evolution imediatamente com 200)
        asyncio.create_task(handle_message(remote_jid, text, push_name))

    except Exception as e:
        logger.error(f"Erro no webhook Evolution: {e}", exc_info=True)
        return {"status": "error", "detail": str(e)}

    return {"status": "ok"}


# ── Admin ─────────────────────────────────────────────────────────────────────
@app.post("/admin/faq/reload")
async def reload_faq(x_admin_key: str = Header(default="")):
    """Força recarga do FAQ do Google Sheets. Header: X-Admin-Key: <ADMIN_KEY>"""
    if x_admin_key != config.ADMIN_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")
    from google_sheets_faq import faq
    count = faq.reload()
    return {"status": "ok", "rows_loaded": count}


# ── Entry point ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=config.API_PORT, log_level="info")
