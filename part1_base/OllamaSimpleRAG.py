import argparse
import json
import sys

import chromadb
import ollama


DEFAULT_EMBEDDING_MODEL = "qwen3-embedding:0.6b"
DEFAULT_LLM_MODEL = "deepseek-r1:1.5b"
DEFAULT_INPUT_FILE = "rag_input.json"


if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")


def parse_args():
    parser = argparse.ArgumentParser(
        description="Run the base local RAG demo with Ollama and ChromaDB."
    )
    parser.add_argument("--input-file", default=DEFAULT_INPUT_FILE)
    parser.add_argument("--embedding-model", default=DEFAULT_EMBEDDING_MODEL)
    parser.add_argument("--llm-model", default=DEFAULT_LLM_MODEL)
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
        collection.add(
            ids=[str(index)],
            embeddings=response["embeddings"],
            documents=[document],
        )


def retrieve_context(collection, user_query, embedding_model):
    query_embedding = ollama.embed(model=embedding_model, input=user_query)
    results = collection.query(
        query_embeddings=query_embedding["embeddings"],
        n_results=1,
    )
    return results["documents"][0][0]


def build_rag_prompt(user_query, retrieved_doc):
    return (
        "Answer the question using only the following context.\n\n"
        f"Context: {retrieved_doc}\n\n"
        f"Question: {user_query}"
    )


def main():
    args = parse_args()
    data = load_input_file(args.input_file)
    documents = data["documents"]
    user_query = data["user_query"]

    print("=== RAG DEMO START ===\n")

    print("[1/6] Creating vector collection...")
    client = chromadb.Client()
    collection = reset_collection(client, "docs")
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

    # The base version deliberately retrieves only one document so that Part 2
    # can compare this limitation against the improved Top-K approach.
    print("[5/6] Generating query embedding and retrieving context...")
    retrieved_doc = retrieve_context(collection, user_query, args.embedding_model)
    print("[5/6] Retrieval completed.\n")
    print("----- RETRIEVED CONTEXT -----")
    print(retrieved_doc)
    print()

    rag_prompt = build_rag_prompt(user_query, retrieved_doc)

    print("[6/6] Running LLM with RAG...")
    print("----- RAG PROMPT -----")
    print(rag_prompt)
    print()

    output_rag = ollama.generate(model=args.llm_model, prompt=rag_prompt)
    print("[6/6] LLM response with RAG completed.\n")
    print("----- RESPONSE WITH RAG -----")
    print(output_rag["response"])
    print()

    print("=== RAG DEMO END ===")


if __name__ == "__main__":
    main()
