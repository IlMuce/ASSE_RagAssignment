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

The three experiments in Part 1 and Part 2 were run on the same JSON prompt files provided in `test_inputs/json_cases/`.

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
| `Report the number of people residing in Genoa.` | The base script retrieved only the age-distribution document, which did not contain the population value. | The Top-K version retrieved the age-distribution document, the population/gender document, and the GDP document. | The base script could not report the population because the retrieved context was incomplete. | The Top-K script correctly reported `563,947` residents because the relevant population document was included among the retrieved contexts. | Yes. Top-K improved the answer by recovering the relevant document even if it was not ranked first. |
| `Are there more males than females in Genoa? And what is the distribution?` | The base script retrieved the gender-distribution document. | The Top-K version retrieved the gender-distribution document plus two additional less relevant documents. | The base script already answered correctly using the retrieved gender data. | The Top-K script also answered correctly. | Limited. In this case one document was already sufficient, so Top-K did not provide a substantial advantage. |
| `Report the percentage of minors and pensioners in Genoa and the GDP per capita.` | The base script retrieved only the demographic document with minors and pensioners percentages. | The Top-K version retrieved the demographic document, the GDP document, and one additional population document. | The base script gave only a partial answer because GDP per capita was missing from the retrieved context. | The Top-K script correctly reported minors, pensioners, and GDP per capita. | Yes. Top-K improved the result because the answer required information coming from more than one document. |

### 3.1 Top-K Discussion

- The main advantage of Top-K retrieval appears when the answer depends on more than one source document.
- In Prompt 1, Top-K fixed the failure of the base script by including the correct population document among the retrieved contexts.
- In Prompt 2, Top-K did not significantly improve the result because the base version was already retrieving the correct document with `n_results=1`.
- In Prompt 3, Top-K clearly improved the final answer because it allowed the model to combine demographic information and GDP information from two different documents.
- Therefore, Top-K retrieval is more robust than the base version, especially for questions that require multi-document aggregation.

## 4. Part 3: PDF Experiments

- Tested PDF: `chapter4_acc_totem.pdf` extracted from the thesis `Muceku_Denis_tesi.pdf`
- Selected PDF prompts:
  - `What are the three main components of the ACC Totem architecture, and what is the role of each one?`
  - `How does ACC Totem reduce manual work for operators, from race configuration to simulator auto-join?`
  - `What are the main limitations or critical issues of the ACC Totem system, and which mitigation measures were adopted?`

| Prompt | Retrieved Context Appropriate? | Without RAG | With RAG | Retrieval Error or Generation Error? | Notes |
|---|---|---|---|---|---|
| `What are the three main components of the ACC Totem architecture, and what is the role of each one?` | Yes, mostly. The first retrieved chunk explicitly lists the three components of the architecture. | The model hallucinated a completely unrelated cryptographic architecture. | The model identified the ACC Totem architecture and used the retrieved context, but the answer was still partially imprecise in the role description. | Mainly generation error. Retrieval was good, but the final answer did not fully preserve the exact structure described in the PDF. | RAG strongly improved the answer, even if the final wording was not perfectly faithful to the source. |
| `How does ACC Totem reduce manual work for operators, from race configuration to simulator auto-join?` | Yes. The retrieved chunks covered both operator workflow simplification and the watcher/agent-based auto-join process. | The model produced a generic and incorrect answer unrelated to the thesis content. | The model correctly recognized that ACC Totem reduces manual work, but the final answer remained too generic and did not exploit all the retrieved details. | Mainly generation error. The retrieved context was relevant, but the answer did not summarize it precisely enough. | RAG improved the answer substantially, but the output was still less detailed than the available context. |
| `What are the main limitations or critical issues of the ACC Totem system, and which mitigation measures were adopted?` | No. The retrieved chunks did not focus on the section that describes the limitations and mitigation measures in detail. | The model refused to answer and provided no useful content. | The model produced a generic list of issues and mitigations not supported by the retrieved chunks. | Mainly retrieval error, followed by generation error. The right section was not retrieved, so the answer became speculative. | This prompt is useful because it exposes a clear failure case of the current PDF RAG setup. |

### 4.1 First PDF Run Discussion

- The selected chapter is appropriate for PDF-based RAG because the extracted text is clear, technical, and rich enough to support detailed prompts.
- Prompt 1 shows that a good retrieval step can strongly improve the answer, even if the final generation remains partially imprecise.
- Prompt 2 shows a mixed case: retrieval was relevant, but the model still produced a summary that was too generic compared to the available evidence.
- Prompt 3 highlights the most important failure in this first run: the retrieval step did not surface the most relevant chunk for the limitations section, so the final answer was not well grounded.
- Overall, this first PDF experiment suggests that the chapter is a good test document, but retrieval quality still depends heavily on the phrasing of the prompt and on chunk ranking.

## 5. Model Comparison

For a fairer comparison involving `all-minilm:latest`, the PDF experiments were rerun with smaller chunks (`chunk_size=60`, `chunk_overlap=15`), because the initial chunk configuration exceeded the embedding context length supported by `all-minilm:latest`.

### 5.0 Experimental Setup Summary

- First PDF experiment on Chapter 4:
  - PDF: `chapter4_acc_totem.pdf`
  - chunking: `chunk_size=180`, `chunk_overlap=40`
  - goal: verify that the PDF-based RAG pipeline worked and evaluate the first three prompts with a strong local baseline
- Fair model comparison on Chapter 4:
  - PDF: `chapter4_acc_totem.pdf`
  - chunking: `chunk_size=60`, `chunk_overlap=15`
  - goal: use the same chunking for all comparable runs, including `all-minilm:latest`
- Additional cross-domain experiment on Chapter 5:
  - PDF: `chapter5_network_security_qos.pdf`
  - chunking: `chunk_size=60`, `chunk_overlap=15`
  - goal: verify whether the same model ranking remained stable on a chapter with different content

### 5.0.1 Why Chunking Changed

- Larger chunks (`180/40`) preserved more local context in each retrieved unit.
- This helped the first Chapter 4 run, because prompts such as architecture and workflow benefited from seeing longer contiguous text.
- However, `all-minilm:latest` could not handle the original chunk size in this setup, so a smaller configuration (`60/15`) was required to include it in the comparison.
- Smaller chunks made the comparison fairer across embedding models, but they also made retrieval harder in some cases because important evidence was split across multiple fragments.
- Therefore:
  - `180/40` was better for the initial qualitative evaluation of Chapter 4
  - `60/15` was better for the multi-model comparison, even if it reduced answer quality for some prompts

| Embedding Model | LLM Model | Prompt | Retrieval Quality | Final Answer Quality | Notes |
|---|---|---|---|---|---|
| `qwen3-embedding:0.6b` | `deepseek-r1:1.5b` | All three PDF prompts with smaller chunks | Mixed. Retrieval became weaker on Prompt 1 and Prompt 3 because the top chunk often contained only a fragment of the relevant section. | The model still improved over the no-RAG baseline, but the answers were generic and in some cases speculative. | This combination remained usable, but smaller chunking reduced answer quality compared with the earlier PDF run. |
| `qwen3-embedding:0.6b` | `llama3.1:8b` | All three PDF prompts with smaller chunks | Mixed, but generally interpretable. Retrieval was still imperfect on Prompt 1 and Prompt 3, while Prompt 2 remained reasonably grounded. | More cautious than DeepSeek: when the context was incomplete, the model tended to answer conservatively instead of inventing details. | Among the fully comparable reruns, this was still the most reliable combination. |
| `qwen3-embedding:0.6b` | `gemma-3-27b-it` | All three PDF prompts with smaller chunks | Same retrieval pattern as the other `qwen3-embedding` runs. Prompt 2 was grounded enough, while Prompt 1 and Prompt 3 remained retrieval-limited. | Very conservative: it avoided the strongest hallucinations, but on incomplete context it often answered that the question could not be fully resolved from the retrieved chunks. | Useful as an API-based comparison. Safer than DeepSeek, but less informative than `llama3.1:8b` on this setup. |
| `qwen3-embedding:0.6b` | `qwen3.5:9b` | Prompt 1 and Prompt 2 completed in the earlier run, Prompt 3 incomplete | Retrieval followed the same `qwen3-embedding` ranking pattern. | Mixed and unstable: one good answer, one empty final answer, and one incomplete run. | This combination was not rerun in the fair chunk-size comparison and remains non-conclusive. |
| `all-minilm:latest` | `deepseek-r1:1.5b` | All three PDF prompts with smaller chunks | Completed, but retrieval quality was generally weaker than with `qwen3-embedding:0.6b`; Prompt 1 and Prompt 3 often surfaced partial or off-target chunks. | Prompt 2 was usable, but Prompt 1 and Prompt 3 remained weak and sometimes speculative. | Smaller chunking made the embedding step possible, but did not produce better overall results than `qwen3-embedding:0.6b`. |
| `all-minilm:latest` | `llama3.1:8b` | All three PDF prompts with smaller chunks | Completed, but retrieval remained weak on Prompt 1 and Prompt 3. | The model was cautious and avoided strong hallucinations, but often could not answer completely because the retrieved chunks were not sufficiently informative. | Better behaved than `all-minilm + deepseek`, but still weaker than the `qwen3-embedding` runs. |
| `all-minilm:latest` | `gemma-3-27b-it` | All three PDF prompts with smaller chunks | Completed, but retrieval remained weak and often insufficiently specific on Prompt 1 and Prompt 3. | Very conservative: it usually preferred saying that the context was insufficient rather than inventing details. | Similar in behavior to `all-minilm + llama`, but still clearly limited by weaker retrieval than `qwen3-embedding:0.6b`. |
| `all-minilm:latest` | `qwen3.5:9b` | Not run in the fair comparison | Not evaluated. | Not evaluated. | This combination was skipped after observing unstable behavior from `qwen3.5:9b` and weaker retrieval from `all-minilm:latest`. |

### 5.1 Model Comparison Discussion

- Reducing the chunk size made `all-minilm:latest` usable, but it also changed retrieval behavior for all the rerun combinations. This made the comparison fairer, but also showed the trade-off between chunk compatibility and retrieval quality.
- `qwen3-embedding:0.6b` remained the stronger embedding model on this chapter: even with smaller chunks, it generally retrieved more useful evidence than `all-minilm:latest`.
- `llama3.1:8b` was again the most cautious and faithful LLM among the completed comparisons. When the retrieved chunks were incomplete, it tended to answer conservatively rather than invent unsupported details.
- `deepseek-r1:1.5b` stayed more verbose and more willing to fill gaps, which sometimes made its answers sound useful but less well grounded.
- `gemma-3-27b-it`, accessed through the Gemini API, was also conservative and better grounded than the weaker DeepSeek answers, but on this chapter it was usually less informative than `llama3.1:8b` when the retrieved chunks were only partial.
- With `all-minilm:latest`, `gemma-3-27b-it` behaved much like `llama3.1:8b`: safer than DeepSeek, but still heavily constrained by the weaker retrieval produced by the embedding model.
- `qwen3.5:9b` remained unstable for this assignment setup, so it was not used as the main basis for the final comparison.

### 5.2 Chunk Size Comparison (`60/15` vs `180/40`)

- After the fair comparison at `60/15`, the Chapter 4 and Chapter 5 experiments were rerun with `qwen3-embedding:0.6b` and larger chunks (`180/40`) using `deepseek-r1:1.5b`, `llama3.1:8b`, and `gemma-3-27b-it`.
- The goal was to isolate the effect of chunking without reintroducing `all-minilm:latest`, which required the smaller chunk configuration.

Main observations:

- On Chapter 4, larger chunks clearly improved Prompt 1 and Prompt 2.
  - For the architecture prompt, both `llama3.1:8b` and `gemma-3-27b-it` moved from partial or conservative answers to substantially more complete answers because the retrieved chunk now contained the actual list of the three components and their roles.
  - For the manual-work prompt, larger chunks also improved the answer quality because the retrieved evidence preserved more of the workflow and operator-facing explanation in a single chunk.
- On Chapter 4, Prompt 3 still remained difficult even with larger chunks.
  - This indicates that the main problem was not only chunk length, but also ranking: the system still did not consistently retrieve the most relevant section for limitations and mitigation measures.
- On Chapter 5, larger chunks improved the QoS prompt the most.
  - `llama3.1:8b` and `gemma-3-27b-it` produced better grounded summaries because the methodology and the conclusion about Fortinet QoS policies appeared in the same larger chunk.
- On Chapter 5, larger chunks did not fully solve the vulnerability-and-hardening prompt.
  - This prompt still required combining multiple concrete findings about the Windows endpoint and the Cisco switch, so longer chunks alone were not sufficient to guarantee a complete answer.

Practical interpretation:

- `60/15` is better when the objective is to compare multiple embedding models under the same compatible setting.
- `180/40` is better when the objective is to maximize answer quality for `qwen3-embedding:0.6b`, especially on prompts whose evidence is contained in one coherent section.
- Therefore, larger chunks improved several answers, but they did not improve everything. They help most when the retrieval target is a self-contained paragraph or subsection, and less when the answer depends on several distinct evidence blocks.

## 6. Additional PDF Experiment: Chapter 5

- Additional tested PDF: `chapter5_network_security_qos.pdf` extracted from `Muceku_Denis_tesi.pdf`
- Selected prompts:
  - `What are the three main macro-areas of risk identified in the Esplace gaming network, and why does each one matter?`
  - `What vulnerabilities were found on the Windows endpoint and on the Cisco switch, and what hardening measures were proposed for each?`
  - `How were the QoS tests performed, and what did they show about the Fortinet policies under heavy load?`

### 6.1 Observations on Chapter 5

| Model Combination | Prompt 1: Risks | Prompt 2: Vulnerabilities and Hardening | Prompt 3: QoS Results | Overall Observation |
|---|---|---|---|---|
| `qwen3-embedding:0.6b` + `deepseek-r1:1.5b` | Partial. It recognized the Windows-client risk but did not reconstruct the three macro-areas correctly. | Weak. It produced an incomplete and partly distorted summary of the findings. | Usable but generic. It captured that the policies distributed bandwidth under heavy load. | Better than the no-RAG baseline, but still too loose on the security prompts. |
| `qwen3-embedding:0.6b` + `llama3.1:8b` | Strong. It reconstructed the three macro-areas of risk with the right overall structure. | Partial but cautious. It recovered the Cisco-side issues and the hardening direction, but it still underused the Windows findings. | Strong. It correctly summarized the speed-test methodology and the positive Fortinet QoS result. | Best combination on Chapter 5 as well. |
| `qwen3-embedding:0.6b` + `gemma-3-27b-it` | Good. It recovered the main idea of the three risk areas, though with less precision than `llama3.1:8b`. | Partial. It remained careful, but still lacked the full Windows-side detail. | Good. It summarized the speed-test method and the balanced-bandwidth outcome. | A useful middle ground: safer than DeepSeek, but still not as complete as `llama3.1:8b`. |
| `all-minilm:latest` + `deepseek-r1:1.5b` | Weak. The answer remained broad and not well aligned with the chapter. | Weak. The model added unsupported security details. | Partial. It captured the existence of PowerShell-based stress testing, but the conclusion remained vague. | This chapter confirmed the weaker retrieval quality already seen with `all-minilm:latest`. |
| `all-minilm:latest` + `llama3.1:8b` | Too conservative. It often refused to infer the three macro-areas from the partial chunks. | Too conservative. It correctly avoided hallucinating, but the answer remained incomplete. | Good. It answered the QoS question reasonably well when the right chunk was retrieved. | More faithful than `all-minilm + deepseek`, but still limited by weaker retrieval. |
| `all-minilm:latest` + `gemma-3-27b-it` | Too conservative. It often stated that the context was insufficient to identify the three macro-areas. | Too conservative. It preferred not to report findings that were not explicit in the retrieved fragments. | Good. It correctly summarized the PowerShell speed-test methodology and the balanced-bandwidth result. | Similar to `all-minilm + llama`: safer than DeepSeek, but still constrained by weaker retrieval. |

### 6.2 Discussion of the Second Chapter

- Chapter 5 produced a different error profile from Chapter 4. The QoS prompt was comparatively easy because the relevant evidence was concentrated in a small portion of the chapter and the retrieved chunks were often enough to support the answer.
- The vulnerability and hardening prompt was harder because the answer required combining multiple concrete findings across different chunks. This exposed retrieval limits more clearly than the ACC Totem workflow prompts.
- The second chapter therefore confirms that RAG quality depends not only on the models, but also on the internal structure of the source text. Questions about broad structure or a compact results section were easier than questions requiring a dense mapping between findings and mitigation measures.
- The Chapter 5 experiment also reinforced the chunking trade-off observed earlier: smaller chunks were acceptable for compact result sections such as the QoS paragraph, but less effective for prompts that required multiple related findings to remain in the same retrieved context.
- The additional `all-minilm + gemma` run confirmed the same pattern already visible with `all-minilm + llama`: conservative generation reduced hallucinations, but it did not compensate for weaker retrieval.

## 7. Conclusions

- When RAG improved the result: when the retrieved document or chunk directly contained the required information, especially in Prompt 2 of Part 1 and Prompt 3 of Part 2.
- When RAG did not improve the result: when the top retrieved context was incomplete or not focused on the real answer, as in Prompt 1 of Part 1 and Prompt 3 of the first PDF run.
- Main retrieval issues: single-document retrieval in the base script was often insufficient; in the PDF setup, some prompts still failed because the most relevant chunk was not ranked high enough or because the relevant evidence was split across multiple short chunks.
- Main generation issues: even with good retrieval, some models produced answers that were too generic, partially imprecise, or not fully grounded in the retrieved text.
- Chapter dependence: the additional Chapter 5 experiment showed that results change with the source material. Broad structural questions and compact result sections were easier than detailed security-analysis questions that required matching findings with mitigations.
- Chunking dependence: larger chunks (`180/40`) improved several runs with `qwen3-embedding:0.6b`, especially on prompts where the answer was concentrated in one local section, but they did not eliminate failures caused by poor ranking or by questions requiring multiple distant pieces of evidence.
- Best model combination: among the completed and comparable runs, `qwen3-embedding:0.6b` with `llama3.1:8b` was the most reliable combination.
