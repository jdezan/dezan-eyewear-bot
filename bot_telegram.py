"""Bot Telegram — responde no grupo usando RAG dos PDFs."""

import logging
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
)
import config
from rag import engine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Ola! Sou o assistente do Estudio de Oculus.\n"
        "Me faca uma pergunta e respondo com base nas informacoes do estudio."
    )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Processa mensagens — em grupo so responde se mencionado."""
    message = update.message
    if not message or not message.text:
        return

    text = message.text.strip()

    # Em grupo: responde se mencionado (@bot) ou se for reply ao bot
    if message.chat.type in ("group", "supergroup"):
        bot_username = context.bot.username
        mentioned = f"@{bot_username}" in text
        is_reply_to_bot = (
            message.reply_to_message
            and message.reply_to_message.from_user
            and message.reply_to_message.from_user.id == context.bot.id
        )
        if not mentioned and not is_reply_to_bot:
            return
        text = text.replace(f"@{bot_username}", "").strip()

    if not text:
        return

    logger.info(f"Pergunta de {message.from_user.first_name}: {text[:80]}")

    try:
        answer = engine.query(text)
        await message.reply_text(answer)
    except Exception as e:
        logger.error(f"Erro RAG: {e}")
        await message.reply_text(
            "Desculpe, tive um problema ao processar sua pergunta. Tente novamente."
        )


def main():
    engine.load()

    app = Application.builder().token(config.TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    logger.info("Bot Telegram iniciado. Ctrl+C para parar.")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
