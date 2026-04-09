"""Processa PDFs e DOCX da pasta data/ e gera o vectorstore FAISS."""

import os
import sys
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.schema import Document
import config


def load_docx(path):
    """Carrega um .docx e retorna lista de Documents."""
    from docx import Document as DocxDoc

    doc = DocxDoc(path)
    text = "\n".join(p.text for p in doc.paragraphs if p.text.strip())

    # Tabelas tambem
    for table in doc.tables:
        for row in table.rows:
            cells = [c.text.strip() for c in row.cells if c.text.strip()]
            if cells:
                text += "\n" + " | ".join(cells)

    return [Document(page_content=text, metadata={"source": os.path.basename(path)})]


def load_pdf(path):
    """Carrega um .pdf e retorna lista de Documents."""
    from langchain_community.document_loaders import PyPDFLoader
    return PyPDFLoader(path).load()


def ingest():
    files = [
        os.path.join(config.DATA_DIR, f)
        for f in os.listdir(config.DATA_DIR)
        if f.lower().endswith((".pdf", ".docx"))
    ]

    if not files:
        print(f"Nenhum PDF/DOCX encontrado em {config.DATA_DIR}/")
        sys.exit(1)

    print(f"Processando {len(files)} arquivo(s)...")

    docs = []
    for fpath in files:
        name = os.path.basename(fpath)
        print(f"  - {name}")
        if fpath.lower().endswith(".docx"):
            docs.extend(load_docx(fpath))
        else:
            docs.extend(load_pdf(fpath))

    print(f"Documentos carregados: {len(docs)}")

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=config.CHUNK_SIZE,
        chunk_overlap=config.CHUNK_OVERLAP,
        separators=["\n\n", "\n", ". ", " "],
    )
    chunks = splitter.split_documents(docs)
    print(f"Chunks gerados: {len(chunks)}")

    print("Gerando embeddings e salvando vectorstore...")
    embeddings = OpenAIEmbeddings(api_key=config.OPENAI_API_KEY)
    vectorstore = FAISS.from_documents(chunks, embeddings)
    vectorstore.save_local(config.VECTORSTORE_DIR)

    print(f"Vectorstore salvo em {config.VECTORSTORE_DIR}/")
    print("Pronto! Rode: python bot_telegram.py  ou  python api.py")


if __name__ == "__main__":
    ingest()
