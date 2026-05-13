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
AMAZON_URL = os.getenv("AMAZON_URL", "")  # URL da loja Amazon (adicionar quando disponível)

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
- Preço padrão de todos os modelos: R$ 127,00
- Se perguntarem sobre preço, informe: R$ 127,00 e direcione para a Amazon ou atendente
- Se perguntarem sobre compra/loja: direcione para a Amazon (em breve) ou atendente
- Se perguntarem sobre Shopee ou Mercado Livre: explique com elegância que a DEZAN é uma
  marca de posicionamento premium e opta por canais que garantem autenticidade e experiência
  de compra à altura do produto — por isso está disponível no site oficial e na Amazon
- Se a pergunta não puder ser respondida com o catálogo, diga:
  "Essa informação não consta no nosso catálogo. Acesse {site_url} para mais detalhes."
- Ao recomendar modelos, destaque diferenciais (polarizado, UV400, armação de titânio, rimless, etc.)
- Modelos com lentes POLARIZADAS: Aurora 04, Bella Vita 02, Bella Vita 03, Bella Vita 04, Bella Vita 07, Milano 04
- Modelos NÃO polarizados: todos os demais, incluindo Milano 06
- Mantenha as respostas concisas para WhatsApp (evite listas muito longas)
- Ao final, quando pertinente, mencione: "Ver todos os modelos em: {site_url}"
""".format(site_url=SITE_URL)
