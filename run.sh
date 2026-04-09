#!/bin/bash
# Estudio de Oculus — Bot Setup Rapido
# Uso: bash run.sh [ingest|telegram|api|docker]

set -u

CMD="${1:-help}"
DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$DIR"

case "$CMD" in
    ingest)
        echo "==> Processando PDFs em data/..."
        python3 ingest.py
        ;;
    telegram)
        echo "==> Iniciando bot Telegram..."
        python3 bot_telegram.py
        ;;
    api)
        echo "==> Iniciando API (Telegram manual + WhatsApp webhook)..."
        python3 api.py
        ;;
    docker)
        echo "==> Subindo com Docker Compose..."
        docker compose up -d --build
        ;;
    stop)
        docker compose down
        ;;
    *)
        echo "Estudio de Oculus - Bot RAG"
        echo ""
        echo "Uso: bash run.sh [comando]"
        echo ""
        echo "Comandos:"
        echo "  ingest    - Processa PDFs e gera vectorstore"
        echo "  telegram  - Inicia bot Telegram (polling)"
        echo "  api       - Inicia API REST + webhook WhatsApp"
        echo "  docker    - Sobe tudo via Docker Compose"
        echo "  stop      - Para containers Docker"
        echo ""
        echo "Setup rapido:"
        echo "  1. Coloque PDFs em data/"
        echo "  2. Copie .env.example para .env e preencha"
        echo "  3. pip install -r requirements.txt"
        echo "  4. bash run.sh ingest"
        echo "  5. bash run.sh telegram  (ou: bash run.sh api)"
        ;;
esac
