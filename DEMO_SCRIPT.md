# Demo Script

This file describes the final demo flow for the Local RAG Assistant project.

## Demo Goal

The goal of the demo is to show that the assistant can:

1. Read local documents from `data/docs`
2. Convert document chunks into embeddings
3. Store chunks and embeddings in `rag.db`
4. Retrieve relevant chunks for a user question
5. Answer using the retrieved context
6. Refuse to answer when the information is not in the documents

## Before the Demo

Make sure the correct environment is active:

```bash
conda activate foundry-rag
```

Make sure the project folder is open:

```bash
cd Desktop/local-rag-assistant
```

## Step 1: Build the Local RAG Database

Run:

```bash
python src/ingest.py
```

Expected behavior:

- The assistant reads supported files from `data/docs`
- Supported file types are `.txt`, `.pdf`, and `.docx`
- The assistant creates chunks
- The assistant generates embeddings
- The assistant saves everything into `rag.db`

Example expected output:

```text
Reading Math202SYL_Spr2026.pdf...
Processing Math202SYL_Spr2026.pdf: 4 chunks

Reading PSY201_syllabus_SP25-26.docx...
Processing PSY201_syllabus_SP25-26.docx: 22 chunks

Saved 33 chunks to rag.db.
```

## Step 2: Ask a TXT-Based Question

Run:

```bash
python src/answer.py "Where does SQLite store data?"
```

Expected behavior:

- The assistant retrieves SQLite-related context from the local documents.
- The assistant answers using the retrieved context.

Example answer:

```text
SQLite stores data in a single database file.
```

## Step 3: Ask a DOCX-Based Question

Run:

```bash
python src/answer.py "How many exams in the PSY201?"
```

Expected behavior:

- The assistant retrieves information from the PSY201 syllabus `.docx` file.
- The assistant answers based on the exam section.

Example answer:

```text
PSY201 consists of two exams.
```

## Step 4: Ask an Out-of-Document Question

Run:

```bash
python src/answer.py "Who is the president of Turkey?"
```

Expected behavior:

- The assistant should not answer from outside knowledge.
- The assistant should refuse because the answer is not in the provided documents.

Expected answer:

```text
I could not find this information in the provided documents.
```

## Step 5: Run Automated Tests

Run:

```bash
python src/run_tests.py
```

Expected behavior:

- The script runs ingestion.
- The script runs the predefined test questions.
- The script updates `TEST_RESULTS.md` automatically.

## What to Explain During the Demo

Use this short explanation while presenting:

```text
This project is a local RAG assistant. It does not rely only on the language model's general knowledge. First, it reads local documents and stores their embeddings in SQLite. When the user asks a question, the system embeds the question, retrieves the most relevant document chunks, and gives those chunks to the local chat model as context. If the information is not found in the documents, the assistant refuses to answer instead of hallucinating.
```

## Key Features to Mention

- Runs locally with Foundry Local
- Uses `qwen3-embedding-0.6b` for embeddings
- Uses `qwen2.5-0.5b` for local answer generation
- Stores chunks and embeddings in SQLite
- Supports `.txt`, `.pdf`, and `.docx` files
- Uses cosine similarity for retrieval
- Includes automated testing with `src/run_tests.py`

## Limitations to Mention

- The chat model is small, so answers may sometimes be slightly imperfect.
- PDF tables can be difficult to extract perfectly.
- Scanned image-based PDFs may require OCR.
- The current interface is command-line based.

## Closing Statement

```text
The final result is a working offline document question-answering assistant. It demonstrates the full RAG pipeline: local document ingestion, embedding generation, SQLite storage, semantic retrieval, and context-grounded local answer generation.
```
