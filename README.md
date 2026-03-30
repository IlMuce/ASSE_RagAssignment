# ASSE_RagAssignment

This repository is organized to mirror the three parts of Assignment 2 from Lesson 06.

## Project Structure

- `part1_base/`: Part 1, original single-document RAG.
- `part2_topk/`: Part 2, improved retrieval with Top-K documents.
- `part3_pdf/`: Part 3, PDF ingestion plus Top-K chunk retrieval.
- `test_inputs/json_cases/`: the three JSON prompts requested by the assignment.
- `test_inputs/pdf/`: place your thesis chapter PDF and its JSON input here.
- `outputs/`: local folder used to store experiment logs generated while running the scripts. It is created and filled during execution and is not part of the final required deliverables.
- `report_material/tables_notes/report_template.md`: draft structure for the 3-4 page report.

The files `rag_input.json` inside `part1_base/` and `part2_topk/`, and `pdf_rag_input.json` inside `part3_pdf/`, are standalone example inputs kept as local defaults for direct script execution. The actual Part 1 and Part 2 experiments for the report use the JSON files in `test_inputs/json_cases/`.

## Setup

Create and use a local virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\python -m pip install --upgrade pip
.\.venv\Scripts\python -m pip install -r requirements.txt
```

You also need Ollama running locally with these models:

```powershell
ollama pull qwen3-embedding:0.6b
ollama pull all-minilm:latest
ollama pull deepseek-r1:1.5b
ollama pull llama3.1:8b
```

`qwen3.5:9b` is optional and should be used only if available on your machine.

Optional:

- To test `gemma-3-27b-it` through the Gemini API, prepare an env file containing `GEMINI_API_KEY=...` and pass it to the Part 3 runner with `-Provider gemini -ApiEnvFile path\to\api_keys.env`.

## Part 1

Run the base script on the three provided JSON cases.

`part1_base` preserves the original single-document retrieval logic of the professor's script: it still retrieves only one document with `n_results=1`.

Recommended:

```powershell
.\scripts\run_part1_base.ps1
```

This saves the logs automatically in `outputs/part1/`.

Manual alternative:

```powershell
cd part1_base
..\.venv\Scripts\python OllamaSimpleRAG.py --input-file ..\test_inputs\json_cases\prompt_1_population.json
..\.venv\Scripts\python OllamaSimpleRAG.py --input-file ..\test_inputs\json_cases\prompt_2_gender.json
..\.venv\Scripts\python OllamaSimpleRAG.py --input-file ..\test_inputs\json_cases\prompt_3_population_gdp.json
```

For each prompt, compare:

- answer without RAG
- retrieved context
- answer with RAG
- whether the improvement comes from better retrieval or whether the base answer was already sufficient

## Part 2

Run the Top-K script on the same three JSON cases.

Recommended:

```powershell
.\scripts\run_part2_topk.ps1
```

This saves the logs automatically in `outputs/part2/`.

Manual alternative:

```powershell
cd part2_topk
..\.venv\Scripts\python OllamaTopKRAG.py --input-file ..\test_inputs\json_cases\prompt_1_population.json --top-k 3
..\.venv\Scripts\python OllamaTopKRAG.py --input-file ..\test_inputs\json_cases\prompt_2_gender.json --top-k 3
..\.venv\Scripts\python OllamaTopKRAG.py --input-file ..\test_inputs\json_cases\prompt_3_population_gdp.json --top-k 3
```

Focus your analysis on:

- when one document is enough
- when the answer requires combining two documents
- whether Top-K retrieves useful extra context or just noise

## Part 3

Place a substantial textual PDF in `test_inputs/pdf/`, then create a JSON input like:

```json
{
  "pdf_path": "C:\\Users\\denis\\Desktop\\ASSE\\ASSE_RagAssignment\\test_inputs\\pdf\\your_chapter.pdf",
  "user_query": "Your detailed question here",
  "top_k": 3,
  "chunk_size": 180,
  "chunk_overlap": 40
}
```

Run the PDF version:

Recommended:

```powershell
.\scripts\run_part3_pdf.ps1
```

This saves the logs automatically in `outputs/part3/`.

For the additional Chapter 5 experiment:

```powershell
.\scripts\run_part3_chapter5.ps1
```

Optional Gemini/Gemma example:

```powershell
.\scripts\run_part3_pdf.ps1 -Provider gemini -ApiEnvFile ..\self_consistency_assignment\api_keys.env -LlmModel gemma-3-27b-it -EmbeddingModel qwen3-embedding:0.6b -ChunkSize 60 -ChunkOverlap 15 -OutputSubdir qwenembed__gemma27__c60
```

Manual alternative:

```powershell
cd part3_pdf
..\.venv\Scripts\python OllamaPDFRAG.py --input-file ..\test_inputs\pdf\your_pdf_prompt.json
```

The local file `part3_pdf/pdf_rag_input.json` is only a placeholder example. For the final assignment runs, use JSON files created for your selected PDF inside `test_inputs/pdf/`.

Prepare 2-3 prompts:

- one asking for a very specific fact
- one requiring information from two distant parts of the PDF
- one that is difficult enough that a model without RAG is likely to guess or hallucinate

## Suggested Workflow For The Report

1. Fill Part 1 tables after testing the base script on all three JSON prompts.
2. Fill Part 2 tables using the same prompts with `part2_topk`.
3. Fill Part 3 tables using your thesis chapter PDF and 2-3 custom prompts.
4. Repeat Part 3 with two embedding models:
   `qwen3-embedding:0.6b` and `all-minilm:latest`
5. Repeat Part 3 with the available LLMs:
   `deepseek-r1:1.5b`, `llama3.1:8b`, optionally `qwen3.5:9b`, and optionally `gemma-3-27b-it` through the Gemini API

Use the report template in `report_material/tables_notes/report_template.md` as the base document.
