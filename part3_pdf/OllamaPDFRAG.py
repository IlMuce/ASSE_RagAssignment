import argparse
import json
import sys
from pathlib import Path

import chromadb
import ollama

try:
    from pypdf import PdfReader
except ImportError:
    from PyPDF2 import PdfReader


DEFAULT_EMBEDDING_MODEL = "qwen3-embedding:0.6b"
DEFAULT_LLM_MODEL = "deepseek-r1:1.5b"
DEFAULT_INPUT_FILE = "pdf_rag_input.json"
DEFAULT_TOP_K = 3
DEFAULT_CHUNK_SIZE = 180
DEFAULT_CHUNK_OVERLAP = 40


if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")


def parse_args():
    parser = argparse.ArgumentParser(
        description="Run a PDF-based Top-K local RAG demo with Ollama and ChromaDB."
    )
    parser.add_argument("--input-file", default=DEFAULT_INPUT_FILE)
    parser.add_argument("--embedding-model", default=DEFAULT_EMBEDDING_MODEL)
    parser.add_argument("--llm-model", default=DEFAULT_LLM_MODEL)
    parser.add_argument("--top-k", type=int, default=None)
    parser.add_argument("--chunk-size", type=int, default=None)
    parser.add_argument("--chunk-overlap", type=int, default=None)
    return parser.parse_args()


def load_input_file(path):
    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


def normalize_whitespace(text):
    return " ".join(text.split())


def extract_pdf_chunks(pdf_path, chunk_size, chunk_overlap):
    reader = PdfReader(str(pdf_path))
    chunks = []
    step = max(1, chunk_size - chunk_overlap)

    for page_number, page in enumerate(reader.pages, start=1):
        page_text = normalize_whitespace(page.extract_text() or "")
        if not page_text:
            continue

        words = page_text.split()
        chunk_index = 1

        # Chunking by words keeps the implementation simple and works well enough
        # for a course assignment where we want transparent, explainable behavior.
        for start in range(0, len(words), step):
            slice_words = words[start : start + chunk_size]
            if not slice_words:
                continue

            chunk_text = " ".join(slice_words)
            chunks.append(
                {
                    "id": f"page_{page_number}_chunk_{chunk_index}",
                    "text": f"[Page {page_number}] {chunk_text}",
                    "page": page_number,
                    "chunk_index": chunk_index,
                }
            )
            chunk_index += 1

            if start + chunk_size >= len(words):
                break

    return chunks


def reset_collection(client, name):
    collection = client.get_or_create_collection(name=name)
    existing = collection.get()
    if existing["ids"]:
        collection.delete(ids=existing["ids"])
    return collection


def embed_and_store_chunks(collection, chunks, embedding_model):
    for chunk in chunks:
        response = ollama.embed(model=embedding_model, input=chunk["text"])
        collection.add(
            ids=[chunk["id"]],
            embeddings=response["embeddings"],
            documents=[chunk["text"]],
            metadatas=[
                {
                    "page": chunk["page"],
                    "chunk_index": chunk["chunk_index"],
                }
            ],
        )


def retrieve_context(collection, user_query, embedding_model, top_k):
    query_embedding = ollama.embed(model=embedding_model, input=user_query)
    return collection.query(
        query_embeddings=query_embedding["embeddings"],
        n_results=top_k,
    )


def build_rag_prompt(user_query, retrieved_docs):
    formatted_context = "\n\n".join(
        f"[Context {index}] {document}"
        for index, document in enumerate(retrieved_docs, start=1)
    )
    return (
        "Answer the question using only the following context.\n\n"
        f"{formatted_context}\n\n"
        f"Question: {user_query}"
    )


def main():
    args = parse_args()
    data = load_input_file(args.input_file)

    pdf_path = Path(data["pdf_path"])
    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    user_query = data["user_query"]
    chunk_size = args.chunk_size or data.get("chunk_size", DEFAULT_CHUNK_SIZE)
    chunk_overlap = args.chunk_overlap or data.get("chunk_overlap", DEFAULT_CHUNK_OVERLAP)
    top_k = args.top_k or data.get("top_k", DEFAULT_TOP_K)

    if chunk_overlap >= chunk_size:
        raise ValueError("chunk_overlap must be smaller than chunk_size.")

    print("=== PDF RAG DEMO START ===\n")

    print("[1/7] Reading PDF and creating chunks...")
    chunks = extract_pdf_chunks(pdf_path, chunk_size, chunk_overlap)
    if not chunks:
        raise ValueError("No text chunks were extracted from the PDF.")
    print(f"[1/7] Extracted {len(chunks)} chunks from {pdf_path.name}.\n")

    print("[2/7] Creating vector collection...")
    client = chromadb.Client()
    collection_name = f"pdf_{pdf_path.stem[:40]}".replace(" ", "_")
    collection = reset_collection(client, collection_name)
    print("[2/7] Collection ready.\n")

    print("[3/7] Embedding and indexing PDF chunks...")
    embed_and_store_chunks(collection, chunks, args.embedding_model)
    print("[3/7] PDF chunks indexed.\n")

    print("[4/7] Original prompt ready.")
    print("----- ORIGINAL PROMPT -----")
    print(user_query)
    print()

    print("[5/7] Running LLM without RAG...")
    output_no_rag = ollama.generate(model=args.llm_model, prompt=user_query)
    print("[5/7] LLM response without RAG completed.\n")
    print("----- RESPONSE WITHOUT RAG -----")
    print(output_no_rag["response"])
    print()

    print("[6/7] Retrieving Top-K PDF context...")
    results = retrieve_context(collection, user_query, args.embedding_model, top_k)
    retrieved_docs = results["documents"][0]
    retrieved_metadatas = results["metadatas"][0]
    print("[6/7] Retrieval completed.\n")
    print("----- RETRIEVED CONTEXT -----")
    for index, (document, metadata) in enumerate(
        zip(retrieved_docs, retrieved_metadatas), start=1
    ):
        print(
            f"[Context {index}] Page {metadata['page']}, chunk {metadata['chunk_index']}"
        )
        print(document)
        print()

    rag_prompt = build_rag_prompt(user_query, retrieved_docs)

    print("[7/7] Running LLM with RAG...")
    print("----- RAG PROMPT -----")
    print(rag_prompt)
    print()

    output_rag = ollama.generate(model=args.llm_model, prompt=rag_prompt)
    print("[7/7] LLM response with RAG completed.\n")
    print("----- RESPONSE WITH RAG -----")
    print(output_rag["response"])
    print()

    print("=== PDF RAG DEMO END ===")


if __name__ == "__main__":
    main()
