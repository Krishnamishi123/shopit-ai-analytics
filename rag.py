
import os
import logging
from functools import lru_cache

from dotenv import load_dotenv

from langchain_community.vectorstores import FAISS

from langchain_google_genai import (
    GoogleGenerativeAIEmbeddings,
    ChatGoogleGenerativeAI,
)

from langchain_core.prompts import ChatPromptTemplate


# =========================================================
# 1. LOAD ENVIRONMENT VARIABLES
# =========================================================

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

load_dotenv(os.path.join(SCRIPT_DIR, ".env"))

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

if not GOOGLE_API_KEY:
    raise ValueError(
        "GOOGLE_API_KEY not found in .env file"
    )

logger = logging.getLogger("shopit")


# =========================================================
# 2. PATHS AND MODELS
# =========================================================

VECTORSTORE_DIR = os.path.join(
    SCRIPT_DIR,
    "vectorstore"
)

EMBEDDING_MODEL = "models/gemini-embedding-001"
CHAT_MODEL = "gemini-3.6-flash"


# =========================================================
# 3. CREATE EMBEDDING CLIENT ONCE
# =========================================================

@lru_cache(maxsize=1)
def get_embeddings():
    return GoogleGenerativeAIEmbeddings(
        model=EMBEDDING_MODEL
    )


# =========================================================
# 4. LOAD EXISTING FAISS STORE ONCE
# =========================================================

@lru_cache(maxsize=1)
def get_vectorstore():

    index_file = os.path.join(
        VECTORSTORE_DIR,
        "index.faiss"
    )

    metadata_file = os.path.join(
        VECTORSTORE_DIR,
        "index.pkl"
    )

    if not (
        os.path.isfile(index_file)
        and os.path.isfile(metadata_file)
    ):
        raise FileNotFoundError(
            "Shopit FAISS vector store is missing. "
            "Run `python INGEST.PY` to build it first."
        )

    print("\n==============================")
    print("LOADING EXISTING VECTOR STORE")
    print("==============================")

    vectorstore = FAISS.load_local(
        VECTORSTORE_DIR,
        get_embeddings(),
        allow_dangerous_deserialization=True,
    )

    print("Existing FAISS vector store loaded.")

    return vectorstore


# =========================================================
# 5. CREATE RETRIEVER
# =========================================================

@lru_cache(maxsize=1)
def get_retriever():
    return get_vectorstore().as_retriever(
        search_kwargs={"k": 4}
    )


# =========================================================
# 6. CREATE GEMINI LLM ONCE
# =========================================================

@lru_cache(maxsize=1)
def get_llm():
    return ChatGoogleGenerativeAI(
        model=CHAT_MODEL,
        temperature=0.2,
    )


# =========================================================
# 7. RAG PROMPT
# =========================================================

prompt = ChatPromptTemplate.from_template(
    """
You are Shopit's AI assistant.

Answer the user's question using ONLY
the provided Shopit policy context.

If the answer cannot be found in the context,
say:

"I could not find this information in
the Shopit policy documents."

Do not invent or assume policy information.

Always give a clear and concise answer.

-------------------------
SHOPIT POLICY CONTEXT
-------------------------

{context}

-------------------------
USER QUESTION
-------------------------

{question}
"""
)


# =========================================================
# 8. HELPER: EXTRACT RESPONSE TEXT
# =========================================================

def extract_response_text(content):

    if isinstance(content, str):
        return content.strip()

    if isinstance(content, list):
        parts = []

        for block in content:
            if isinstance(block, dict):
                if block.get("type") == "text":
                    parts.append(block.get("text", ""))
            elif isinstance(block, str):
                parts.append(block)

        return "".join(parts).strip()

    return str(content).strip()


# =========================================================
# 9. RAG FUNCTION
# =========================================================

def ask_shopit_policy(question):

    question = question.strip()

    if not question:
        return (
            "Please enter a policy question.",
            []
        )

    print("\nSearching policy documents...")

    # Load from disk on first use; reuse afterwards.
    retriever = get_retriever()

    retrieved_docs = retriever.invoke(question)

    print(
        "Retrieved chunks:",
        len(retrieved_docs)
    )

    context = "\n\n".join(
        doc.page_content
        for doc in retrieved_docs
    )

    messages = prompt.format_messages(
        context=context,
        question=question,
    )

    response = get_llm().invoke(messages)

    answer = extract_response_text(
        response.content
    )

    if not answer:
        answer = (
            "I could not generate an answer from "
            "the retrieved Shopit policy documents."
        )

    logger.info(
        "Policy query completed; retrieved %d chunks.",
        len(retrieved_docs),
    )

    # Preserve the original return format.
    return answer, retrieved_docs


# =========================================================
# 10. TEST RAG DIRECTLY
# =========================================================

if __name__ == "__main__":

    question = input(
        "\nAsk Shopit a policy question: "
    )

    answer, sources = ask_shopit_policy(question)

    print("\n==============================")
    print("SHOPIT AI ANSWER")
    print("==============================")

    print(answer)

    print("\n==============================")
    print("SOURCES")
    print("==============================")

    for i, doc in enumerate(sources, 1):

        print(f"\nSource {i}:")

        print(
            "File:",
            doc.metadata.get("file_name")
        )

        print(
            "Page:",
            doc.metadata.get("page")
        )
