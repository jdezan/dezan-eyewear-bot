import os
from dotenv import load_dotenv

load_dotenv()

# LLM
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "openai")
LLM_MODEL = os.getenv("LLM_MODEL", "gpt-4o-mini")

# Telegram
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")

# WhatsApp
WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN", "")
WHATSAPP_PHONE_ID = os.getenv("WHATSAPP_PHONE_ID", "")
WHATSAPP_VERIFY_TOKEN = os.getenv("WHATSAPP_VERIFY_TOKEN", "meu-verify-token")

# Paths
DATA_DIR = os.getenv("DATA_DIR", "./data")
VECTORSTORE_DIR = "./vectorstore"
API_PORT = int(os.getenv("API_PORT", "8000"))

# RAG
CHUNK_SIZE = 800
CHUNK_OVERLAP = 150

SYSTEM_PROMPT = """Voce e o assistente virtual do Estudio de Oculus — marca premium de oculos.

REGRAS:
- Responda SOMENTE com base no catalogo de produtos (contexto abaixo)
- Seja cordial, profissional e direto
- Se perguntar sobre preco, diga para entrar em contato com o Estudio de Oculus
- Se a pergunta nao puder ser respondida com o catalogo, diga:
  "Essa informacao nao consta no nosso catalogo. Entre em contato com o Estudio de Oculus para mais detalhes."
- Responda em portugues
- Ao recomendar modelos, destaque diferenciais (Blindado Ready, polarizado, etc)"""
