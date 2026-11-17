
import os
import glob
import logging
import pandas as pd

from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS

load_dotenv()

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(SCRIPT_DIR, "DATA")
VECTORSTORE_DIR = os.path.join(SCRIPT_DIR, "vectorstore")

EMBEDDING_MODEL = "models/gemini-embedding-001"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("shopit.ingestion")


def load_structured_data():
    """Load CSV datasets for inspection and preprocessing."""

    print("\n==============================")
    print("LOADING STRUCTURED DATA")
    print("==============================")

    csv_files = glob.glob(os.path.join(DATA_DIR, "*.csv"))
    data_frames = {}

    for file_path in csv_files:
        file_name = os.path.splitext(
            os.path.basename(file_path)
        )[0]

        data_frames[file_name] = pd.read_csv(file_path)

        print(
            f"Loaded CSV: {file_name}.csv "
            f"-> {data_frames[file_name].shape}"
        )

    sections = [
        ("PRODUCTS", "products"),
        ("CUSTOMERS", "customers"),
        ("SALES", "sales_orders"),
        ("CUSTOMER SUMMARY", "customer_summary"),
        ("PRODUCT PERFORMANCE", "product_performance"),
    ]

    for title, key in sections:
        print(f"\n===== {title} =====")
        print(data_frames.get(key, pd.DataFrame()).head())

    print("\n==============================")
    print("DATASET SIZES")
    print("==============================")

    for name, df in data_frames.items():
        print(f"{name}: {df.shape}")

    return data_frames


def load_policy_documents():
    """Read all policy PDFs and preserve their source metadata."""

    print("\n==============================")
    print("LOADING POLICY DOCUMENTS")
    print("==============================")

    pdf_files = sorted(glob.glob(os.path.join(DATA_DIR, "*.pdf")))

    if not pdf_files:
        raise FileNotFoundError(
            f"No policy PDFs found in {DATA_DIR}"
        )

    policy_documents = []

    for pdf_path in pdf_files:
        print(f"\nLoading PDF: {os.path.basename(pdf_path)}")

        loader = PyPDFLoader(pdf_path)
        documents = loader.load()

        for doc in documents:
            doc.metadata["source_type"] = "policy"
            doc.metadata["file_name"] = os.path.basename(pdf_path)

        policy_documents.extend(documents)

    print("\n==============================")
    print("POLICY DOCUMENT SUMMARY")
    print("==============================")

    print("Total PDF pages loaded:", len(policy_documents))

    for doc in policy_documents:
        print("\n--------------------------------")
        print("File:", doc.metadata.get("file_name"))
        print("Page:", doc.metadata.get("page"))
        print("Content preview:", doc.page_content[:300])

    return policy_documents


def build_vectorstore(policy_documents):
    """Chunk policy pages and save the FAISS index to disk."""

    print("\n==============================")
    print("CHUNKING DOCUMENTS")
    print("==============================")

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
    )

    chunks = splitter.split_documents(policy_documents)

    if not chunks:
        raise ValueError(
            "No text chunks were extracted from the policy PDFs."
        )

    print("Total chunks created:", len(chunks))

    print("\n==============================")
    print("CREATING EMBEDDINGS")
    print("==============================")

    embeddings = GoogleGenerativeAIEmbeddings(
        model=EMBEDDING_MODEL
    )

    print("\n==============================")
    print("CREATING VECTOR STORE")
    print("==============================")

    vectorstore = FAISS.from_documents(
        documents=chunks,
        embedding=embeddings,
    )

    os.makedirs(VECTORSTORE_DIR, exist_ok=True)
    vectorstore.save_local(VECTORSTORE_DIR)

    print("\nVector store saved at:", VECTORSTORE_DIR)
    print("Ingestion completed successfully.")

    return len(chunks)


def main():
    # Preserve the original CSV-loading functionality.
    data_frames = load_structured_data()

    # Load policy documents and create the vector store.
    policy_documents = load_policy_documents()
    chunk_count = build_vectorstore(policy_documents)

    print("\n==============================")
    print("INGESTION COMPLETE")
    print("==============================")
    print("CSV datasets loaded:", len(data_frames))
    print("PDF pages loaded:", len(policy_documents))
    print("Vector chunks created:", chunk_count)


if __name__ == "__main__":
    main()
