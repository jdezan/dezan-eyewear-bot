FROM python:3.12-slim

WORKDIR /app

# Dependências do sistema
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Instala dependências Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia o código
# O modelo HuggingFace será baixado automaticamente no primeiro startup
ARG CACHEBUST=2026-05-13b
COPY . .

EXPOSE 8000

# Roda a API (webhook Evolution API incluído)
CMD ["python", "api.py"]
