FROM python:3.12-slim

WORKDIR /app

# Dependências do sistema
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Instala dependências Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Pré-baixa o modelo de embeddings HuggingFace durante o build
# (evita delay de cold start no primeiro uso)
RUN python -c "\
from sentence_transformers import SentenceTransformer; \
SentenceTransformer('sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2'); \
print('Modelo de embeddings pré-carregado com sucesso.')"

# Copia o código
COPY . .

EXPOSE 8000

# Roda a API (webhook Evolution API incluído)
CMD ["python", "api.py"]
