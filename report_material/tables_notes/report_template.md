# Assignment 2 Report Template

## 1. Overview

- Base script analyzed: `part1_base/OllamaSimpleRAG.py`
- Improved Top-K version: `part2_topk/OllamaTopKRAG.py`
- PDF ingestion version: `part3_pdf/OllamaPDFRAG.py`
- Tested PDF:
- Selected prompts:

## 2. Code Changes

### 2.1 Top-K Version

- Replaced single-document retrieval with `Top-K` retrieval.
- Updated the RAG prompt so it includes multiple retrieved contexts.
- Added command-line parameters for `input-file`, `top-k`, embedding model, and LLM model.

### 2.2 PDF Ingestion Version

- Added PDF reading with `PyPDF2` / `pypdf`.
- Added chunk extraction from the PDF.
- Stored chunk metadata such as page and chunk index in ChromaDB.
- Updated retrieval and prompt building to use multiple PDF chunks.

## 3. Part 1: Base Script Comparison

| Prompt | Without RAG | With RAG | Did RAG help? | Notes |
|---|---|---|---|---|
| Prompt 1 |  |  |  |  |
| Prompt 2 |  |  |  |  |
| Prompt 3 |  |  |  |  |

## 4. Part 2: Top-K Comparison

| Prompt | Retrieved context in base script | Retrieved context in Top-K | Base answer | Top-K answer | Improvement? |
|---|---|---|---|---|---|
| Prompt 1 |  |  |  |  |  |
| Prompt 2 |  |  |  |  |  |
| Prompt 3 |  |  |  |  |  |

## 5. Part 3: PDF Experiments

| Prompt | Retrieved chunks appropriate? | Without RAG answer quality | With RAG answer quality | Retrieval error or generation error? | Notes |
|---|---|---|---|---|---|
| PDF Prompt 1 |  |  |  |  |  |
| PDF Prompt 2 |  |  |  |  |  |
| PDF Prompt 3 |  |  |  |  |  |

## 6. Model Comparison

| Embedding Model | LLM Model | Prompt | Retrieval quality | Final answer quality | Notes |
|---|---|---|---|---|---|
| `qwen3-embedding:0.6b` | `deepseek-r1:1.5b` |  |  |  |  |
| `qwen3-embedding:0.6b` | `llama3.1:8b` |  |  |  |  |
| `qwen3-embedding:0.6b` | `qwen3.5:9b` |  |  |  |  |
| `all-minilm:latest` | `deepseek-r1:1.5b` |  |  |  |  |
| `all-minilm:latest` | `llama3.1:8b` |  |  |  |  |
| `all-minilm:latest` | `qwen3.5:9b` |  |  |  |  |

## 7. Conclusions

- When RAG improved the result:
- When RAG did not improve the result:
- Main retrieval issues:
- Main generation issues:
- Best model combination:
