import hashlib
from pathlib import Path

import chromadb
import ollama
from pypdf import PdfReader


PROJECT_DIR = Path(__file__).resolve().parent
UPLOAD_DIR = PROJECT_DIR / "data" / "uploads"
CHROMA_DIR = PROJECT_DIR / "data" / "chroma_db"

UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
CHROMA_DIR.mkdir(parents=True, exist_ok=True)

client = chromadb.PersistentClient(path=str(CHROMA_DIR))

collection = client.get_or_create_collection(
    name="taskpilot_documents",
    metadata={"hnsw:space": "cosine"},
)


def extract_text(file_path: str) -> str:
    """Extract text from supported PDF or TXT files."""
    path = Path(file_path).resolve()

    if not path.is_file():
        raise FileNotFoundError(f"File not found: {path}")

    suffix = path.suffix.lower()

    if suffix == ".txt":
        text = path.read_text(encoding="utf-8-sig", errors="replace")

    elif suffix == ".pdf":
        reader = PdfReader(str(path))
        text = "\n".join(page.extract_text() or "" for page in reader.pages)

    else:
        raise ValueError("Only PDF and TXT files are supported.")

    if not text.strip():
        raise ValueError(
            "No readable text found. Scanned PDFs may require OCR."
        )

    return text


def split_text(text: str, chunk_size: int = 800, overlap: int = 120):
    """Split text into overlapping character-based chunks."""
    if chunk_size <= 0 or overlap < 0 or overlap >= chunk_size:
        raise ValueError("Invalid chunk size or overlap.")

    chunks = []
    start = 0

    while start < len(text):
        end = min(start + chunk_size, len(text))
        chunk = text[start:end].strip()

        if chunk:
            chunks.append(chunk)

        if end == len(text):
            break

        start = end - overlap

    return chunks


def embed_text(text: str) -> list[float]:
    """Generate a local embedding using Ollama."""
    response = ollama.embeddings(
        model="nomic-embed-text",
        prompt=text,
    )
    return response["embedding"]


def index_document(file_path: str) -> dict:
    """Extract, chunk, embed, and store a document."""
    path = Path(file_path).resolve()
    text = extract_text(str(path))
    chunks = split_text(text)

    document_id = hashlib.sha256(
        str(path).encode("utf-8")
    ).hexdigest()[:24]

    # Replace previous chunks for this document.
    collection.delete(where={"document_id": document_id})

    ids = []
    embeddings = []
    metadatas = []

    for index, chunk in enumerate(chunks):
        ids.append(f"{document_id}_{index}")
        embeddings.append(embed_text(chunk))
        metadatas.append(
            {
                "document_id": document_id,
                "filename": path.name,
                "chunk_index": index,
            }
        )

    collection.add(
        ids=ids,
        documents=chunks,
        embeddings=embeddings,
        metadatas=metadatas,
    )

    return {
        "filename": path.name,
        "chunks_indexed": len(chunks),
        "status": "success",
    }


def search_documents(query: str, top_k: int = 3) -> list[dict]:
    """Find the most relevant indexed document chunks."""
    if not query or not query.strip():
        return []

    if top_k < 1:
        raise ValueError("top_k must be at least 1.")

    if collection.count() == 0:
        return []

    results = collection.query(
        query_embeddings=[embed_text(query)],
        n_results=min(top_k, collection.count()),
        include=["documents", "metadatas", "distances"],
    )

    matches = []

    for document, metadata, distance in zip(
        results["documents"][0],
        results["metadatas"][0],
        results["distances"][0],
    ):
        matches.append(
            {
                "text": document,
                "filename": metadata["filename"],
                "chunk_index": metadata["chunk_index"],
                "distance": distance,
            }
        )

    return matches
