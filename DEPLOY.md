# 🚀 Guia de Deploy — Dezan Eyewear Bot WhatsApp

> Stack: Python 3.12 · FastAPI · LangChain · FAISS · Groq (LLM gratuito) · HuggingFace Embeddings · Evolution API · Google Sheets FAQ

---

## 📐 Arquitetura

```
Cliente WhatsApp
      │
      ▼
Evolution API  ◄─── já rodando no EasyPanel
(dezan-eyeware)
      │  webhook POST
      ▼
Bot FastAPI  ◄─── novo serviço no EasyPanel
  ├── FAQ Google Sheets  (respostas instantâneas)
  └── RAG Groq + FAISS  (IA para perguntas abertas)
      │
      ▼
Cliente WhatsApp recebe resposta
```

**Fluxo do cliente:**
```
1ª mensagem → Menu (1-5)
  1 → Catálogo das coleções
  2 → Link do site
  3 → Link Mercado Livre
  4 → Chat com IA (RAG) ──► perguntas livres sobre os óculos
  5 → Atendente humano
```

---

## 1️⃣  Pré-requisitos

| Item | Onde obter | Custo |
|------|-----------|-------|
| Conta Groq | https://console.groq.com | **Gratuito** |
| API Key da Evolution API | EasyPanel → Evolution API → Configurações | Já tem |
| Conta Google (para Sheets) | google.com | Gratuito |
| GitHub (para o código) | github.com | Gratuito |

---

## 2️⃣  Obter a API Key da Evolution API

1. Acesse: https://evolution-api-evolution-api.rs7gvp.easypanel.host/manager
2. Faça login com as credenciais do Evolution API
3. Vá em **Settings → Global Settings → API Key**
4. Copie a chave — você vai usar como `EVOLUTION_API_KEY`

---

## 3️⃣  Obter Chave Groq (IA gratuita)

1. Acesse https://console.groq.com
2. Crie conta gratuita
3. Vá em **API Keys → Create API Key**
4. Copie a chave — começa com `gsk_...`

---

## 4️⃣  Configurar Google Sheets FAQ

### Criar a planilha

1. Acesse https://sheets.google.com → crie nova planilha
2. Nomeie como **"Dezan Eyewear - FAQ"**
3. Adicione exatamente estes cabeçalhos na linha 1:

| A | B | C |
|---|---|---|
| key | keyword | response |

4. Adicione as respostas prontas (exemplos abaixo):

| key | keyword | response |
|-----|---------|----------|
| catalogo | catalogo,colecao,modelos,oculos,armacao | 📚 *Nossas Coleções Premium:*\n\n👓 *Atlântico Premium* — Elegância e resistência\n✨ *Aurora Premium* — Design moderno\n🏛️ *Veneto Premium* — Clássico atemporal\n\nVeja em: https://dezaneyewear.com.br |
| preco | preco,valor,quanto,custa,custo,pagar | 💰 Para ver preços acesse nossa loja:\nhttps://lista.mercadolivre.com.br/_CustId_6112331 |
| entrega | entrega,frete,prazo,envio,demora | 🚚 Informações de entrega disponíveis na loja do Mercado Livre:\nhttps://lista.mercadolivre.com.br/_CustId_6112331 |
| garantia | garantia,defeito,troca,problema | 🛡️ Nossos óculos têm garantia contra defeitos de fabricação. Entre em contato para mais detalhes. |
| site | site,loja,onde,comprar | 🌐 https://dezaneyewear.com.br\n🛒 https://lista.mercadolivre.com.br/_CustId_6112331 |
| atendente | atendente,humano,pessoa,falar,ajuda | 👤 Ótimo! Um atendente entrará em contato em breve. Obrigado pela preferência! |

> ⚠️ Use `\n` para quebra de linha dentro da célula do Google Sheets.

### Publicar como CSV

1. Na planilha: **Arquivo → Compartilhar → Publicar na Web**
2. Selecione a aba → Formato: **Valores separados por vírgula (.csv)**
3. Clique **Publicar** → Copie a URL
4. A URL terá o formato:
   ```
   https://docs.google.com/spreadsheets/d/SEU_ID/pub?gid=0&single=true&output=csv
   ```
5. Guarde essa URL — vai no `.env` como `GOOGLE_SHEETS_FAQ_URL`

---

## 5️⃣  Preparar o código no GitHub

```bash
# No seu computador (dentro da pasta estudio-oculus-export):
git init            # se ainda não for um repo
git add .
git commit -m "feat: bot WhatsApp Evolution API + Groq + Google Sheets"

# Crie um repo no github.com e faça push:
git remote add origin https://github.com/SEU_USUARIO/dezan-eyewear-bot.git
git push -u origin main
```

> ⚠️ Certifique-se de que `.gitignore` contém `.env` — nunca suba tokens/chaves!

---

## 6️⃣  Deploy no EasyPanel

### 6.1 — Criar o serviço do Bot

1. Acesse seu EasyPanel
2. Clique em **+ Create** → **App**
3. Preencha:
   - **Name:** `dezan-bot` (ou o nome que preferir)
   - **Source:** GitHub → selecione seu repositório
   - **Branch:** `main`
   - **Build:** Dockerfile (detecta automaticamente)
4. Clique **Create**

### 6.2 — Rodar o ingest.py ANTES de iniciar

> **Importante:** O bot precisa do vectorstore FAISS gerado antes de iniciar.
> Você precisa rodar `ingest.py` uma vez — existem duas formas:

**Opção A — Rodar no terminal do EasyPanel:**
1. No serviço criado → aba **Terminal**
2. Execute: `python ingest.py`
3. Aguarde "Vectorstore salvo em ./vectorstore/"

**Opção B — Volume persistente + rodar localmente:**
1. Configure um volume persistente no EasyPanel para `/app/vectorstore`
2. Rode `ingest.py` localmente com o mesmo modelo de embedding
3. Suba a pasta `vectorstore/` gerada junto com o código

### 6.3 — Configurar variáveis de ambiente

No EasyPanel → serviço `dezan-bot` → **Environment**:

```env
LLM_PROVIDER=groq
LLM_MODEL=llama-3.3-70b-versatile
GROQ_API_KEY=gsk_SUA_CHAVE_AQUI

EMBEDDING_PROVIDER=huggingface
EMBEDDING_MODEL=sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2

EVOLUTION_API_URL=https://evolution-api-evolution-api.rs7gvp.easypanel.host
EVOLUTION_API_KEY=SUA_KEY_DO_EVOLUTION
EVOLUTION_INSTANCE=dezan-eyeware

SITE_URL=https://dezaneyewear.com.br
ML_URL=https://lista.mercadolivre.com.br/_CustId_6112331

GOOGLE_SHEETS_FAQ_URL=https://docs.google.com/spreadsheets/d/SEU_ID/pub?...

ADMIN_KEY=coloque-uma-senha-forte-aqui

API_PORT=8000
```

### 6.4 — Configurar porta e domínio

1. Na aba **Domains** do serviço:
   - **Port:** 8000
   - Ative o domínio automático do EasyPanel
   - Anote a URL gerada, ex: `https://dezan-bot.rs7gvp.easypanel.host`

### 6.5 — Deploy

1. Clique **Deploy** → aguarde o build (pode levar 3-5 min por conta do modelo HuggingFace)
2. Verifique os logs — deve aparecer:
   ```
   Carregando vectorstore FAISS...
   RAG pronto.
   ```
3. Teste o health: `https://dezan-bot.rs7gvp.easypanel.host/health`
   - Resposta esperada: `{"status":"ok","rag_loaded":true}`

---

## 7️⃣  Configurar Webhook no Evolution API

Após o bot estar rodando, configure o webhook para receber mensagens:

### Via painel (Evolution API Manager)

1. Acesse: `https://evolution-api-evolution-api.rs7gvp.easypanel.host/manager`
2. Clique na instância **dezan-eyeware**
3. Vá em **Webhook**
4. Preencha:
   - **Webhook URL:** `https://dezan-bot.rs7gvp.easypanel.host/webhook/evolution`
   - **Events:** ✅ `MESSAGES_UPSERT`
5. Salve

### Via API (alternativa)

```bash
curl -X POST \
  https://evolution-api-evolution-api.rs7gvp.easypanel.host/webhook/set/dezan-eyeware \
  -H "apikey: SUA_EVOLUTION_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "webhook": {
      "enabled": true,
      "url": "https://dezan-bot.rs7gvp.easypanel.host/webhook/evolution",
      "events": ["MESSAGES_UPSERT"]
    }
  }'
```

---

## 8️⃣  Testar

### Teste 1 — Health check
```
GET https://dezan-bot.rs7gvp.easypanel.host/health
Esperado: {"status":"ok","rag_loaded":true}
```

### Teste 2 — RAG direto
```bash
curl -X POST https://dezan-bot.rs7gvp.easypanel.host/ask \
  -H "Content-Type: application/json" \
  -d '{"question":"Quais são os modelos da coleção Aurora?"}'
```

### Teste 3 — WhatsApp
1. Envie "oi" para o número conectado no Evolution API
2. O bot deve responder com o menu de opções
3. Responda "4" e faça uma pergunta sobre óculos

---

## 9️⃣  Atualizar FAQ sem reimplantar

Sempre que atualizar a planilha, o bot atualiza automaticamente em até 5 minutos.

Para forçar atualização imediata:
```bash
curl -X POST https://dezan-bot.rs7gvp.easypanel.host/admin/faq/reload \
  -H "X-Admin-Key: SUA_ADMIN_KEY"
```

---

## 🔄 Atualizar catálogos (novos .docx)

1. Adicione os novos arquivos em `data/`
2. Execute `ingest.py` novamente no terminal do EasyPanel
3. Reinicie o serviço (ou aguarda o próximo deploy)

---

## 🛠️ Troubleshooting

| Problema | Causa provável | Solução |
|----------|---------------|---------|
| `rag_loaded: false` | ingest.py não foi rodado | Execute `python ingest.py` no terminal |
| Bot não responde no WhatsApp | Webhook não configurado | Verifique passo 7 |
| Erro 401 no webhook | API Key incorreta | Verifique `EVOLUTION_API_KEY` |
| FAQ não carrega | URL do Sheets incorreta | Verifique se está publicado como CSV |
| Timeout na IA | Groq indisponível | Aguarde, é gratuito e pode ter fila |

---

## 💡 Evoluções sugeridas

- **Redis** para sessões persistentes (sobrevive a reinicialização)
- **Typebot** integrado ao Evolution para fluxos visuais mais complexos
- **Chatwoot** para visualizar conversas e assumir atendimento humano
- Adicionar mais catálogos `.docx` em `data/` e rodar `ingest.py`
