# Test Results

This file records the latest automated test results for the local RAG assistant.

## Environment

- Conda environment: `foundry-rag`
- Embedding model: `qwen3-embedding-0.6b`
- Chat model: `qwen2.5-0.5b`
- Database: `rag.db`
- Document folder: `data/docs`
- Supported document types: `.txt`, `.pdf`, `.docx`
- PDF parser: `pdfplumber`
- DOCX parser: `python-docx`

## Pipeline Tested

The following pipeline was tested:

1. Read supported documents from `data/docs`
2. Extract text from `.txt`, `.pdf`, and `.docx` files
3. Extract PDF tables with `pdfplumber` when possible
4. Split extracted text into chunks
5. Generate embeddings for each chunk
6. Store chunks and embeddings in `rag.db`
7. Embed the user question
8. Retrieve the most relevant chunks using cosine similarity
9. Build context from retrieved chunks
10. Generate an answer using the local chat model

## Automated Test Run

- Last run: `2026-06-15 13:42:37`
- Ingestion status: `Passed`
- Chunks saved to database: `33`

## Ingestion Test

Command:

```bash
python src/ingest.py
```

Processed documents:

- `Processing Math202SYL_Spr2026.pdf: 4 chunks`
- `Processing PSY201_syllabus_SP25-26.docx: 22 chunks`
- `Processing embeddings.txt: 1 chunks`
- `Processing foundry_local.txt: 1 chunks`
- `Processing prompt_engineering.txt: 1 chunks`
- `Processing rag.txt: 1 chunks`
- `Processing sample_note.txt: 2 chunks`
- `Processing sqlite.txt: 1 chunks`

## Question Answering Tests

| Test | Question | Source Type | Expected Behavior | Actual Result | Status |
|---|---|---|---|---|---|
| 1 | `Where does SQLite store data?` | TXT | Retrieve SQLite-related context and answer from the documents. | SQLite stores data in a single database file. | Passed |
| 2 | `What are embeddings used for?` | TXT | Retrieve embeddings-related context and answer from the documents. | Embeddings are used to convert text into numerical vectors. | Passed |
| 3 | `What is the course name in the MATH202 syllabus?` | PDF | Retrieve grading-related information from the PDF if the relevant text/table is extracted clearly. | To determine the course name from the Syllabus provided: 1. Look for the course title mentioned explicitly. 2. Check if it mentions the course name at the beginning or end. By searching: - I found "MATH 202" as the course title, which matches exactly the course name being asked for. - It appears at the beginning of the document where the course number is presented. Therefore, the correct course name according to the provided document is **Mathematics** (with the syllabus prefix omitted). | Needs Review |
| 4 | `How many exams are there in PSY201?` | DOCX | Retrieve exam information from the PSY201 syllabus DOCX file. | There are two exams in PSY201. | Passed |
| 5 | `Who is the president of Turkey?` | Out-of-document | Refuse to answer because the information is not in the documents. | I could not find this information in the provided documents. | Passed |

## Notes

- Answerable questions should be answered using retrieved document context.
- Unanswerable questions should be refused instead of answered from outside knowledge.
- `Needs Review` means the system ran successfully, but the retrieved answer did not clearly satisfy the expected keywords.
- PDF table extraction can be imperfect, especially for complex or scanned PDFs.
- If an answer is too verbose or inaccurate, refine the system prompt, improve chunking, or clean the source documents.

## Current Status

The core RAG pipeline is tested with this flow:

```text
data/docs/*.txt, *.pdf, *.docx
-> src/ingest.py
-> rag.db
-> src/retrieve.py
-> src/answer.py
-> local context-based answer
```
