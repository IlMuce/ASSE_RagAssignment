import argparse
import json

import chromadb
import ollama


DEFAULT_EMBEDDING_MODEL = "qwen3-embedding:0.6b"
DEFAULT_LLM_MODEL = "deepseek-r1:1.5b"
DEFAULT_INPUT_FILE = "rag_input.json"
DEFAULT_TOP_K = 3


def parse_args():
    parser = argparse.ArgumentParser(
        description="Run a Top-K local RAG demo with Ollama and ChromaDB."
    )
    parser.add_argument("--input-file", default=DEFAULT_INPUT_FILE)
    parser.add_argument("--embedding-model", default=DEFAULT_EMBEDDING_MODEL)
    parser.add_argument("--llm-model", default=DEFAULT_LLM_MODEL)
    parser.add_argument("--top-k", type=int, default=DEFAULT_TOP_K)
    return parser.parse_args()


def load_input_file(path):
    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


def reset_collection(client, name):
    collection = client.get_or_create_collection(name=name)
    existing = collection.get()
    if existing["ids"]:
        collection.delete(ids=existing["ids"])
    return collection


def embed_and_store_documents(collection, documents, embedding_model):
    for index, document in enumerate(documents):
        response = ollama.embed(model=embedding_model, input=document)

        # Each document gets a stable string id so Chroma can retrieve it later.
        collection.add(
            ids=[str(index)],
            embeddings=response["embeddings"],
            documents=[document],
        )


def retrieve_context(collection, user_query, embedding_model, top_k):
    query_embedding = ollama.embed(model=embedding_model, input=user_query)
    results = collection.query(
        query_embeddings=query_embedding["embeddings"],
        n_results=top_k,
    )
    return results["documents"][0]


def build_rag_prompt(user_query, retrieved_docs):
    # The model now receives multiple relevant documents instead of only one.
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

    documents = data["documents"]
    user_query = data["user_query"]
    top_k = max(1, min(args.top_k, len(documents)))

    print("=== TOP-K RAG DEMO START ===\n")

    print("[1/6] Creating vector collection...")
    client = chromadb.Client()
    collection = reset_collection(client, "docs_top_k")
    print("[1/6] Collection ready.\n")

    print("[2/6] Embedding and indexing documents...")
    embed_and_store_documents(collection, documents, args.embedding_model)
    print("[2/6] Documents indexed.\n")

    print("[3/6] Original prompt ready.")
    print("----- ORIGINAL PROMPT -----")
    print(user_query)
    print()

    print("[4/6] Running LLM without RAG...")
    output_no_rag = ollama.generate(model=args.llm_model, prompt=user_query)
    print("[4/6] LLM response without RAG completed.\n")
    print("----- RESPONSE WITHOUT RAG -----")
    print(output_no_rag["response"])
    print()

    print("[5/6] Retrieving Top-K context...")
    retrieved_docs = retrieve_context(collection, user_query, args.embedding_model, top_k)
    print("[5/6] Retrieval completed.\n")
    print("----- RETRIEVED CONTEXT -----")
    for index, document in enumerate(retrieved_docs, start=1):
        print(f"[Context {index}] {document}\n")

    rag_prompt = build_rag_prompt(user_query, retrieved_docs)

    print("[6/6] Running LLM with RAG...")
    print("----- RAG PROMPT -----")
    print(rag_prompt)
    print()

    output_rag = ollama.generate(model=args.llm_model, prompt=rag_prompt)
    print("[6/6] LLM response with RAG completed.\n")
    print("----- RESPONSE WITH RAG -----")
    print(output_rag["response"])
    print()

    print("=== TOP-K RAG DEMO END ===")


if __name__ == "__main__":
    main()
