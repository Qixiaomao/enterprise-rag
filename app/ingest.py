from pathlib import Path

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings


BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data" / "raw"
VECTOR_DB_DIR = str(BASE_DIR / "data" / "vector_db")

def load_documents():
    documents = []
    for pdf_file in DATA_DIR.glob("*.pdf"):
        print(f"Loading PDF: {pdf_file}")
        loader = PyPDFLoader(str(pdf_file))
        docs = loader.load()
        print(f"  Pages loaded: {len(docs)}")
        documents.extend(docs)
    return documents


def split_documents(documents):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=100,
        separators=["\n\n", "\n", "。", ".", " ", ""]
    )
    chunks = splitter.split_documents(documents)

    # 过滤空文本
    valid_chunks = []
    for chunk in chunks:
        text = chunk.page_content.strip()
        if text:
            chunk.page_content = text
            valid_chunks.append(chunk)

    return valid_chunks


def build_vector_db(chunks):
    if not chunks:
        raise ValueError("No valid chunks found. Please check whether the PDF contains extractable text.")

    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=VECTOR_DB_DIR
    )
    return vectorstore


if __name__ == "__main__":
    docs = load_documents()
    print(f"Loaded documents: {len(docs)}")

    if docs:
        print("First page preview:")
        print(repr(docs[0].page_content[:300]))

    chunks = split_documents(docs)
    print(f"Valid chunks after filtering: {len(chunks)}")

    if chunks:
        print("First chunk preview:")
        print(repr(chunks[0].page_content[:300]))

    build_vector_db(chunks)
    print("Vector DB built successfully.")