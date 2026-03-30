import json
import ollama
import chromadb

EMBEDDING_MODEL = "qwen3-embedding:0.6b"
LLM_MODEL = "deepseek-r1:1.5b"
# LLM_MODEL = "llama3.1:8b"
# LLM_MODEL = "qwen3.5:9b"
INPUT_FILE = "rag_input.json"

with open(INPUT_FILE, "r", encoding="utf-8") as f:
    data = json.load(f)

documents = data["documents"]
user_query = data["user_query"]

print("=== RAG DEMO START ===\n")

# ----------------------------
# 1. Create / reset collection
# ----------------------------
print("[1/6] Creating vector collection...")
client = chromadb.Client()
collection = client.get_or_create_collection(name="docs")

existing = collection.get()
if existing["ids"]:
    collection.delete(ids=existing["ids"])

print("[1/6] Collection ready.\n")

# ----------------------------
# 2. Embed and store documents
# ----------------------------
print("[2/6] Embedding and indexing documents...")

for i, d in enumerate(documents):
    response = ollama.embed(
        model=EMBEDDING_MODEL,
        input=d
    )

    collection.add(
        ids=[str(i)],
        embeddings=response["embeddings"],
        documents=[d]
    )

print("[2/6] Documents indexed.\n")

# ----------------------------
# 3. Print original prompt
# ----------------------------
print("[3/6] Original prompt ready.")
print("----- ORIGINAL PROMPT -----")
print(user_query)
print()

# ----------------------------
# 4. Run WITHOUT RAG
# ----------------------------
print("[4/6] Running LLM without RAG...")

output_no_rag = ollama.generate(
    model=LLM_MODEL,
    prompt=user_query
)

print("[4/6] LLM response without RAG completed.\n")
print("----- RESPONSE WITHOUT RAG -----")
print(output_no_rag["response"])
print()

# ----------------------------
# 5. Retrieve context with RAG
# ----------------------------
print("[5/6] Generating query embedding and retrieving context...")

response = ollama.embed(
    model=EMBEDDING_MODEL,
    input=user_query
)

results = collection.query(
    query_embeddings=response["embeddings"],
    n_results=1
)

retrieved_doc = results["documents"][0][0]

print("[5/6] Retrieval completed.\n")
print("----- RETRIEVED CONTEXT -----")
print(retrieved_doc)
print()

# ----------------------------
# 6. Run WITH RAG
# ----------------------------
rag_prompt = (
    "Answer the question using only the following context.\n\n"
    f"Context: {retrieved_doc}\n\n"
    f"Question: {user_query}"
)

print("[6/6] Running LLM with RAG...")
print("----- RAG PROMPT -----")
print(rag_prompt)
print()

output_rag = ollama.generate(
    model=LLM_MODEL,
    prompt=rag_prompt
)

print("[6/6] LLM response with RAG completed.\n")
print("----- RESPONSE WITH RAG -----")
print(output_rag["response"])
print()

print("=== RAG DEMO END ===")