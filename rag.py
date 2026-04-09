"""Motor RAG — carrega FAISS index e responde perguntas com contexto dos PDFs."""

import os
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import FAISS
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
import config


def _build_llm():
    if config.LLM_PROVIDER == "groq":
        from langchain_community.chat_models import ChatGroq
        return ChatGroq(
            api_key=config.GROQ_API_KEY,
            model_name=config.LLM_MODEL,
            temperature=0.3,
        )
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
        """Carrega o vectorstore FAISS do disco."""
        if not os.path.exists(config.VECTORSTORE_DIR):
            raise FileNotFoundError(
                f"Vectorstore nao encontrado em {config.VECTORSTORE_DIR}. "
                "Rode primeiro: python ingest.py"
            )

        embeddings = OpenAIEmbeddings(api_key=config.OPENAI_API_KEY)
        self.vectorstore = FAISS.load_local(
            config.VECTORSTORE_DIR,
            embeddings,
            allow_dangerous_deserialization=True,
        )

        prompt = PromptTemplate(
            template=(
                f"{config.SYSTEM_PROMPT}\n\n"
                "Contexto:\n{context}\n\n"
                "Pergunta: {question}\n"
                "Resposta:"
            ),
            input_variables=["context", "question"],
        )

        llm = _build_llm()
        self.qa_chain = RetrievalQA.from_chain_type(
            llm=llm,
            chain_type="stuff",
            retriever=self.vectorstore.as_retriever(search_kwargs={"k": 4}),
            chain_type_kwargs={"prompt": prompt},
            return_source_documents=False,
        )

    def query(self, question: str) -> str:
        """Faz uma pergunta ao RAG e retorna a resposta."""
        if not self.qa_chain:
            self.load()
        result = self.qa_chain.invoke({"query": question})
        return result["result"]


# Singleton
engine = RAGEngine()
