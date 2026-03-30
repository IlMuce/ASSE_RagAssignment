# Assignment 2 Report

## 1. Modifications Introduced

### 1.1 Original Base Script

- The original retrieval logic was kept unchanged: the script still retrieves only one document with `n_results=1`.
- Small structural changes were introduced to make the experiments easier to reproduce:
  - command-line parameters for input file, embedding model, and LLM model
  - helper functions for loading input, resetting the collection, retrieval, and prompt construction
- These changes do not modify the behavior of the original RAG pipeline and were introduced only to support clearer testing and comparison.

### 1.2 Top-K Version

- The retrieval step was changed from one document to `Top-K` documents.
- The RAG prompt was updated to include multiple retrieved contexts instead of one single context.
- The script was adapted so that the final answer can use information coming from more than one retrieved document.

### 1.3 PDF Ingestion Version

- The script was extended to read a complete PDF file.
- The extracted PDF text was split into chunks before indexing.
- Each chunk was embedded and stored in ChromaDB with page metadata.
- The retrieved Top-K chunks were used to build the final RAG prompt.

## 2. Part 1: Base Script Analysis

### 2.1 Step-by-Step Description of the Base Script

The base script works in six main steps:

1. It creates or resets a local ChromaDB collection.
2. It generates embeddings for each document contained in the JSON input file.
3. It stores the embedded documents in the vector database.
4. It sends the user query directly to the LLM and produces the answer without RAG.
5. It embeds the user query and retrieves the single most similar document with `n_results=1`.
6. It builds a new prompt containing the retrieved context and generates the final answer with RAG.

### 2.2 Comparison on the Three Default Prompts

| Prompt | Without RAG | With RAG | Did RAG help? | Analysis |
|---|---|---|---|---|
| `Report the number of people residing in Genoa.` | The model guessed an approximate population value without support. | The model answered that the population could not be determined from the provided context. | No | RAG did not help because retrieval selected the wrong document. The retrieved document contained age-distribution data, not the total population value. |
| `Are there more males than females in Genoa? And what is the distribution?` | The model incorrectly claimed that males are more numerous. | The model correctly answered that females are slightly more numerous and reported the distribution. | Yes | RAG improved the result because retrieval selected the document containing the gender percentages. |
| `Report the percentage of minors and pensioners in Genoa and the GDP per capita.` | The model produced incorrect demographic and GDP estimates. | The model correctly reported minors and pensioners percentages, but it could not provide GDP per capita. | Partially | RAG helped only partially because the retrieved document contained demographic data but not GDP data. The answer required more than one document. |

### 2.3 When RAG Improves the Answer and When It Does Not

- RAG improves the answer when the retrieval step selects the document that directly contains the requested information.
- RAG does not improve the answer when retrieval selects an irrelevant or incomplete document.
- The main limitation of the base script is that it retrieves only one document, so questions requiring information from multiple documents may remain incomplete.

## 3. Part 2: Top-K Comparison

| Prompt | Retrieved Context in Base Script | Retrieved Context in Top-K Script | Base Script Answer | Top-K Script Answer | Improvement |
|---|---|---|---|---|---|
| Prompt 1 |  |  |  |  |  |
| Prompt 2 |  |  |  |  |  |
| Prompt 3 |  |  |  |  |  |

## 4. Part 3: PDF Experiments

- Tested PDF:
- Selected PDF prompts:

| Prompt | Retrieved Context Appropriate? | Without RAG | With RAG | Retrieval Error or Generation Error? | Notes |
|---|---|---|---|---|---|
| PDF Prompt 1 |  |  |  |  |  |
| PDF Prompt 2 |  |  |  |  |  |
| PDF Prompt 3 |  |  |  |  |  |

## 5. Model Comparison

| Embedding Model | LLM Model | Prompt | Retrieval Quality | Final Answer Quality | Notes |
|---|---|---|---|---|---|
| `qwen3-embedding:0.6b` | `deepseek-r1:1.5b` |  |  |  |  |
| `qwen3-embedding:0.6b` | `llama3.1:8b` |  |  |  |  |
| `qwen3-embedding:0.6b` | `qwen3.5:9b` |  |  |  |  |
| `all-minilm:latest` | `deepseek-r1:1.5b` |  |  |  |  |
| `all-minilm:latest` | `llama3.1:8b` |  |  |  |  |
| `all-minilm:latest` | `qwen3.5:9b` |  |  |  |  |

## 6. Conclusions

- When RAG improved the result:
- When RAG did not improve the result:
- Main retrieval issues:
- Main generation issues:
- Best model combination:
