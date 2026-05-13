"""
Bot WhatsApp — Dezan Eyewear
Integração: Evolution API + Google Sheets (FAQ) + RAG/Groq (IA)
"""
import logging
import httpx
from datetime import datetime, timedelta
import config

logger = logging.getLogger(__name__)

# ─── Sessões em memória ───────────────────────────────────────────────────────
sessions: dict = {}
SESSION_TIMEOUT = timedelta(minutes=30)

# ─── Textos ───────────────────────────────────────────────────────────────────
MENU_TEXT = (
    "👓 *Olá! Bem-vindo ao Dezan Eyewear!*\n\n"
    "Somos uma marca premium de óculos. Como posso te ajudar?\n\n"
    "1️⃣  Ver catálogo de coleções\n"
    "2️⃣  Visitar nosso site\n"
    "3️⃣  Comprar na Amazon\n"
    "4️⃣  Perguntar sobre modelos (IA)\n"
    "5️⃣  Falar com um atendente\n\n"
    "Responda com o *número* da opção desejada."
)

MENU_OPTIONS = {"1", "2", "3", "4", "5"}
RESET_WORDS = {"menu", "0", "inicio", "início", "voltar", "oi", "ola", "olá", "opa"}


# ─── Helpers ──────────────────────────────────────────────────────────────────
async def send_message(number: str, text: str) -> None:
    """Envia mensagem de texto via Evolution API."""
    url = f"{config.EVOLUTION_API_URL}/message/sendText/{config.EVOLUTION_INSTANCE}"
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(
                url,
                headers={"apikey": config.EVOLUTION_API_KEY, "Content-Type": "application/json"},
                json={"number": number, "text": text},
            )
            if resp.status_code not in (200, 201):
                logger.error(f"Evolution send error {resp.status_code}: {resp.text[:200]}")
    except Exception as e:
        logger.error(f"send_message exception: {e}")


def get_session(number: str) -> dict:
    """Retorna sessão ativa ou cria nova."""
    now = datetime.now()
    if number in sessions:
        s = sessions[number]
        if now - s["last_activity"] > SESSION_TIMEOUT:
            del sessions[number]
        else:
            s["last_activity"] = now
            return s
    sessions[number] = {"state": "MENU", "last_activity": now}
    return sessions[number]


# ─── Dispatcher principal ─────────────────────────────────────────────────────
async def handle_message(number: str, text: str, push_name: str = "") -> None:
    """
    Estados:
      MENU     → aguardando escolha (1-5)
      CHAT_IA  → conversa aberta com RAG/Groq
    """
    from google_sheets_faq import faq  # import aqui para evitar circular no startup
    from rag import engine

    text_stripped = text.strip()
    text_lower = text_stripped.lower()
    session = get_session(number)

    # ── Comandos globais de reset ──────────────────────────────────────────
    if text_lower in RESET_WORDS or text_stripped == "0":
        session["state"] = "MENU"
        await send_message(number, MENU_TEXT)
        return

    state = session["state"]

    # ── Estado MENU ───────────────────────────────────────────────────────
    if state == "MENU":
        if text_stripped in MENU_OPTIONS:
            await handle_menu_option(number, text_stripped, session)
        else:
            # Primeira mensagem qualquer → mostra menu
            greeting = f"Olá{', ' + push_name if push_name else ''}! " if session.get("new_user") is None else ""
            session["new_user"] = False
            await send_message(number, greeting + MENU_TEXT if greeting else MENU_TEXT)
        return

    # ── Estado CHAT_IA ────────────────────────────────────────────────────
    if state == "CHAT_IA":
        if text_stripped in MENU_OPTIONS:
            await handle_menu_option(number, text_stripped, session)
            return

        # 1. Tenta FAQ primeiro (resposta instantânea sem IA)
        faq_response = faq.match(text_lower)
        if faq_response:
            await send_message(number, faq_response)
            await send_message(number, "_Digite *menu* para voltar às opções._")
            return

        # 2. RAG com Groq
        await send_message(number, "🔍 Consultando nosso catálogo...")
        try:
            answer = engine.query(text_stripped)
            await send_message(number, answer)
        except Exception as e:
            logger.error(f"RAG error: {e}")
            await send_message(
                number,
                "Desculpe, tive um problema ao processar sua pergunta. "
                "Tente novamente ou digite *menu* para outras opções.",
            )
        await send_message(number, "_Mais alguma dúvida? Ou digite *menu* para voltar._")
        return

    # Fallback
    session["state"] = "MENU"
    await send_message(number, MENU_TEXT)


# ─── Handlers de opção de menu ────────────────────────────────────────────────
async def handle_menu_option(number: str, option: str, session: dict) -> None:
    from google_sheets_faq import faq

    if option == "1":
        resp = faq.get_by_key("catalogo") or (
            "📚 *Nossas Coleções Premium:*\n\n"
            "🌊 *Atlântico* — Oversized e estilos urbanos, elegância robusta\n"
            "✨ *Aurora* — Design sofisticado, feminino e versátil\n"
            "🌸 *Bella Vita* — Estilo italiano, feminino e contemporâneo\n"
            "🏛️ *Collezione Milano* — Rimless e geométrico, luxo europeu\n"
            "🎨 *Veneto* — Retrô sofisticado, unissex e atemporal\n\n"
            "💰 *Preço único:* R$ 127,00\n"
            f"🌐 Site: {config.SITE_URL}\n\n"
            "Para mais detalhes sobre qualquer modelo, escolha a opção *4* e pergunte!"
        )
        await send_message(number, resp)

    elif option == "2":
        resp = faq.get_by_key("site") or (
            f"🌐 *Acesse nosso site:*\n{config.SITE_URL}\n\n"
            "Explore o catálogo completo, conheça nossa história e entre em contato!"
        )
        await send_message(number, resp)

    elif option == "3":
        resp = faq.get_by_key("amazon") or (
            "🛒 *Compre na Amazon*\n\n"
            "Nossa loja na Amazon estará disponível em breve com todos os modelos.\n\n"
            "Por enquanto, fale com nosso atendente para efetuar sua compra:\n"
            "👉 Digite *5* para falar com um atendente."
        )
        await send_message(number, resp)

    elif option == "4":
        session["state"] = "CHAT_IA"
        await send_message(
            number,
            "🤖 *Assistente Dezan Eyewear — IA*\n\n"
            "Pode me perguntar sobre:\n"
            "• Modelos e coleções\n"
            "• Materiais e lentes\n"
            "• Diferenciais (polarizado, lentes UV400 etc.)\n"
            "• Qualquer dúvida sobre nossos óculos!\n\n"
            "Digite *menu* a qualquer momento para voltar.",
        )

    elif option == "5":
        resp = faq.get_by_key("atendente") or (
            "👤 *Atendimento Humano*\n\n"
            "Um de nossos atendentes entrará em contato em breve.\n\n"
            f"Enquanto isso, explore nosso catálogo em:\n🌐 {config.SITE_URL}"
        )
        await send_message(number, resp)

    # Volta para menu após opções 1/2/3/5
    if option in ("1", "2", "3", "5"):
        await send_message(number, "Digite *menu* para voltar às opções ou *4* para perguntar à IA.")
