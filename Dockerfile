FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Porta da API (Telegram + WhatsApp webhook)
EXPOSE 8000

# Default: roda a API (inclui webhook WhatsApp)
# Para rodar so o Telegram: docker run ... python bot_telegram.py
CMD ["python", "api.py"]
