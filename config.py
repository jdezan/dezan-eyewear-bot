import os
from dotenv import load_dotenv

load_dotenv()

# ── LLM ───────────────────────────────────────────────────────────────────────
# Provider: "groq" (gratuito) ou "openai"
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "groq")
LLM_MODEL = os.getenv("LLM_MODEL", "llama-3.3-70b-versatile")
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")  # necessário se LLM_PROVIDER=openai

# ── Embeddings ────────────────────────────────────────────────────────────────
# Provider: "huggingface" (gratuito, local) ou "openai"
EMBEDDING_PROVIDER = os.getenv("EMBEDDING_PROVIDER", "huggingface")
EMBEDDING_MODEL = os.getenv(
    "EMBEDDING_MODEL",
    "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
)

# ── Evolution API (WhatsApp) ───────────────────────────────────────────────────
EVOLUTION_API_URL = os.getenv("EVOLUTION_API_URL", "https://evolution-api-evolution-api.rs7gvp.easypanel.host")
EVOLUTION_API_KEY = os.getenv("EVOLUTION_API_KEY", "")
EVOLUTION_INSTANCE = os.getenv("EVOLUTION_INSTANCE", "dezan-eyeware")

# ── Dezan Eyewear — Links ─────────────────────────────────────────────────────
SITE_URL = os.getenv("SITE_URL", "https://dezaneyewear.com.br")
ML_URL = os.getenv("ML_URL", "https://lista.mercadolivre.com.br/_CustId_6112331")

# ── FAQ — Google Sheets ───────────────────────────────────────────────────────
# URL do CSV publicado (Planilha → Arquivo → Publicar na Web → CSV)
GOOGLE_SHEETS_FAQ_URL = os.getenv("GOOGLE_SHEETS_FAQ_URL", "")

# ── Admin ─────────────────────────────────────────────────────────────────────
# Chave para endpoint /admin/faq/reload — defina uma senha forte
ADMIN_KEY = os.getenv("ADMIN_KEY", "troque-esta-chave")

# ── Telegram (opcional) ────────────────────────────────────────────────────────
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")

# ── Paths & servidor ──────────────────────────────────────────────────────────
DATA_DIR = os.getenv("DATA_DIR", "./data")
VECTORSTORE_DIR = "./vectorstore"
API_PORT = int(os.getenv("API_PORT", "8000"))

# ── RAG ───────────────────────────────────────────────────────────────────────
CHUNK_SIZE = 800
CHUNK_OVERLAP = 150

SYSTEM_PROMPT = """Você é o assistente virtual do Dezan Eyewear — marca premium de óculos.

REGRAS OBRIGATÓRIAS:
- Responda SOMENTE com base no catálogo de produtos fornecido como contexto
- Seja cordial, profissional e objetivo
- Escreva em português brasileiro
- Se perguntarem sobre preço, direcione para a loja: {ml_url}
- Se a pergunta não puder ser respondida com o catálogo, diga:
  "Essa informação não consta no nosso catálogo. Acesse dezaneyewear.com.br ou nossa loja no Mercado Livre para mais detalhes."
- Ao recomendar modelos, destaque diferenciais (Blindado Ready, polarizado, armação TR90, etc.)
- Mantenha as respostas concisas para WhatsApp (evite listas muito longas)
- Ao final, quando pertinente, mencione: "Ver todos os modelos em: {site_url}"
""".format(ml_url=ML_URL, site_url=SITE_URL)
