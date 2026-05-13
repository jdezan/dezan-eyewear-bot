FROM python:3.12-slim

WORKDIR /app

# Dependências do sistema
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Instala torch CPU-only primeiro (evita +2GB de libs CUDA desnecessárias)
RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu

# Instala demais dependências Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia o código
ARG CACHEBUST=2026-05-13c
COPY . .

EXPOSE 8000

# Roda a API (webhook Evolution API incluído)
CMD ["python", "api.py"]
