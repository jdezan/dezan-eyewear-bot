"""
FAQ via Google Sheets (publicado como CSV)
─────────────────────────────────────────
Estrutura esperada da planilha (3 colunas):
  key       | keyword                              | response
  catalogo  | catalogo,coleção,modelos,oculos      | 📚 *Nossas Coleções:* ...
  preco     | preco,valor,quanto custa,custo       | 💰 Para consultar preços ...
  site      | site,loja,comprar,link               | 🌐 Acesse: ...
  atendente | atendente,humano,pessoa,falar        | 👤 Em breve ...

Como publicar como CSV:
  Planilha → Arquivo → Compartilhar → Publicar na Web
  → Selecionar aba → Formato: CSV → Publicar → Copiar URL
"""
import csv
import io
import logging
from datetime import datetime, timedelta
from typing import Optional

import requests

logger = logging.getLogger(__name__)


class GoogleSheetsFAQ:
    def __init__(self, csv_url: str, cache_minutes: int = 5):
        self.csv_url = csv_url
        self.cache_duration = timedelta(minutes=cache_minutes)
        self._rows: list[dict] = []
        self._last_fetch: Optional[datetime] = None

    # ── Internos ──────────────────────────────────────────────────────────
    def _fetch(self) -> None:
        """Baixa e parseia o CSV do Google Sheets."""
        if not self.csv_url:
            logger.warning("GOOGLE_SHEETS_FAQ_URL não configurada — FAQ desabilitado")
            return
        try:
            resp = requests.get(self.csv_url, timeout=8)
            resp.raise_for_status()
            # Força UTF-8 para garantir acentos corretos (Google Sheets exporta em UTF-8)
            content = resp.content.decode("utf-8-sig")  # utf-8-sig remove BOM se houver
            reader = csv.DictReader(io.StringIO(content))
            self._rows = [
                {k.strip().lower(): v.strip() for k, v in row.items()}
                for row in reader
                if any(v.strip() for v in row.values())  # ignora linhas vazias
            ]
            self._last_fetch = datetime.now()
            logger.info(f"FAQ carregado: {len(self._rows)} linhas do Google Sheets")
        except Exception as e:
            logger.error(f"Erro ao carregar Google Sheets FAQ: {e}")

    def _ensure_fresh(self) -> None:
        if not self._last_fetch or datetime.now() - self._last_fetch > self.cache_duration:
            self._fetch()

    # ── API pública ───────────────────────────────────────────────────────
    def match(self, text_lower: str) -> Optional[str]:
        """
        Procura correspondência por keyword no texto recebido.
        Retorna o campo 'response' se encontrar, None caso contrário.
        """
        self._ensure_fresh()
        for row in self._rows:
            keywords = [k.strip() for k in row.get("keyword", "").split(",") if k.strip()]
            if any(kw in text_lower for kw in keywords):
                response = row.get("response", "")
                # Substitui \n literal por quebra de linha real
                return response.replace("\\n", "\n")
        return None

    def get_by_key(self, key: str) -> Optional[str]:
        """Busca resposta pela coluna 'key' (chave exata)."""
        self._ensure_fresh()
        key_lower = key.lower()
        for row in self._rows:
            if row.get("key", "").lower() == key_lower:
                response = row.get("response", "")
                return response.replace("\\n", "\n")
        return None

    def reload(self) -> int:
        """Força recarga do cache. Retorna número de linhas carregadas."""
        self._last_fetch = None
        self._fetch()
        return len(self._rows)


# ── Singleton ─────────────────────────────────────────────────────────────────
import config  # noqa: E402

faq = GoogleSheetsFAQ(
    csv_url=getattr(config, "GOOGLE_SHEETS_FAQ_URL", ""),
    cache_minutes=5,
)
