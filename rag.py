"""Motor RAG — carrega FAISS index e responde perguntas com base no catálogo."""

import os
import logging
from langchain_community.vectorstores import FAISS
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
import config

logger = logging.getLogger(__name__)


def _build_embeddings():
    """Cria objeto de embeddings conforme EMBEDDING_PROVIDER."""
    if config.EMBEDDING_PROVIDER == "huggingface":
        from langchain_community.embeddings import HuggingFaceEmbeddings
        return HuggingFaceEmbeddings(
            model_name=config.EMBEDDING_MODEL,
            encode_kwargs={"normalize_embeddings": True},
        )
    # Fallback: OpenAI
    from langchain_openai import OpenAIEmbeddings
    return OpenAIEmbeddings(api_key=config.OPENAI_API_KEY)


def _build_llm():
    """Cria objeto LLM conforme LLM_PROVIDER."""
    if config.LLM_PROVIDER == "groq":
        from langchain_groq import ChatGroq
        return ChatGroq(
            api_key=config.GROQ_API_KEY,
            model_name=config.LLM_MODEL,
            temperature=0.3,
        )
    # Fallback: OpenAI
    from langchain_openai import ChatOpenAI
    return ChatOpenAI(
        api_key=config.OPENAI_API_KEY,
        model=config.LLM_MODEL,
        temperature=0.3,
    )


class RAGEngine:
    def __init__(self):
        self.vectorstore = None
        self.qa_chain = None

    def load(self):
        """Carrega o vectorstore FAISS do disco e monta a chain."""
        if not os.path.exists(config.VECTORSTORE_DIR):
            raise FileNotFoundError(
                f"Vectorstore não encontrado em '{config.VECTORSTORE_DIR}'. "
                "Execute primeiro: python ingest.py"
            )

        logger.info(f"Carregando embeddings ({config.EMBEDDING_PROVIDER}/{config.EMBEDDING_MODEL})...")
        embeddings = _build_embeddings()

        self.vectorstore = FAISS.load_local(
            config.VECTORSTORE_DIR,
            embeddings,
            allow_dangerous_deserialization=True,
        )

        prompt = PromptTemplate(
            template=(
                f"{config.SYSTEM_PROMPT}\n\n"
                "Contexto do catálogo:\n{context}\n\n"
                "Pergunta: {question}\n"
                "Resposta:"
            ),
            input_variables=["context", "question"],
        )

        logger.info(f"Carregando LLM ({config.LLM_PROVIDER}/{config.LLM_MODEL})...")
        llm = _build_llm()

        self.qa_chain = RetrievalQA.from_chain_type(
            llm=llm,
            chain_type="stuff",
            retriever=self.vectorstore.as_retriever(search_kwargs={"k": 4}),
            chain_type_kwargs={"prompt": prompt},
            return_source_documents=False,
        )
        logger.info("RAG engine pronto.")

    def query(self, question: str) -> str:
        """Faz uma pergunta ao RAG e retorna a resposta."""
        if not self.qa_chain:
            self.load()
        result = self.qa_chain.invoke({"query": question})
        return result["result"]


# Singleton
engine = RAGEngine()
