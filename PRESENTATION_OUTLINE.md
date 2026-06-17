# Presentation Outline

## 1. Project Title

**Local RAG Assistant with Microsoft Foundry Local**

Short description:

```text
This project is a local offline document question-answering assistant. It uses Retrieval-Augmented Generation, embeddings, SQLite, and a local language model through Microsoft Foundry Local.
```

## 2. Problem Statement

Many language models answer using only their general training knowledge. This can be a problem when the user asks questions about specific local documents, such as course syllabi, notes, manuals, or FAQs.

This project solves that problem by building an assistant that:

- reads local documents,
- retrieves relevant information from those documents,
- uses the retrieved information as context,
- answers locally without depending on a cloud model,
- refuses to answer when the information is not available in the documents.

## 3. What Is RAG?

RAG means **Retrieval-Augmented Generation**.

The process has three main steps:

1. **Retrieve:** Find relevant chunks from local documents.
2. **Augment:** Add those chunks to the model prompt as context.
3. **Generate:** Ask the local language model to generate an answer using only that context.

In this project, RAG helps reduce hallucination because the model is guided by local document content.

## 4. System Architecture

The project has four main layers:

1. **Document layer:** Files inside `data/docs`
2. **Database layer:** SQLite database stored as `rag.db`
3. **Retrieval layer:** Embedding generation and cosine similarity search
4. **Generation layer:** Local chat model answering with retrieved context

Pipeline:

```text
Local documents
-> chunking
-> embeddings
-> SQLite storage
-> query embedding
-> top chunk retrieval
-> context-based local answer
```

## 5. Technologies Used

- Python 3.11
- Microsoft Foundry Local SDK
- `qwen3-embedding-0.6b` for embeddings
- `qwen2.5-0.5b` for local answer generation
- SQLite for local storage
- Cosine similarity for retrieval
- `pdfplumber` for PDF text and table extraction
- `python-docx` for DOCX reading
- Command-line interface

## 6. Implementation Steps

### Phase 1: Foundations

- Installed and tested Foundry Local
- Ran a local chat model
- Generated embeddings
- Tested cosine similarity
- Created a simple SQLite database
- Tested prompt engineering and context-based answering

### Phase 2: RAG Pipeline

- Created `src/ingest.py` for document ingestion
- Created `src/retrieve.py` for similarity-based retrieval
- Created `src/answer.py` for local answer generation
- Stored chunks and embeddings in `rag.db`
- Added support for `.txt`, `.pdf`, and `.docx` files

### Phase 3: Testing and Documentation

- Created `TEST_RESULTS.md`
- Created automated tests with `src/run_tests.py`
- Created `README.md`
- Created `DEMO_SCRIPT.md`

## 7. Live Demo Flow

During the demo, run:

```bash
python src/ingest.py
```

Then ask a TXT-based question:

```bash
python src/answer.py "Where does SQLite store data?"
```

Then ask a DOCX-based question:

```bash
python src/answer.py "How many exams in the PSY201?"
```

Then ask an out-of-document question:

```bash
python src/answer.py "Who is the president of Turkey?"
```

Finally, run automated tests:

```bash
python src/run_tests.py
```

## 8. Test Results

The system was tested with:

- answerable questions from `.txt` documents,
- answerable questions from `.docx` documents,
- PDF ingestion,
- unanswerable questions.

Current status:

- TXT retrieval and answering works.
- DOCX retrieval and answering works.
- PDF ingestion works.
- Out-of-document refusal works.
- PDF table-based questions may need review depending on table extraction quality.

## 9. Limitations

- The chat model is small, so some answers may be imperfect.
- PDF tables may not always be extracted cleanly.
- Scanned PDFs may require OCR.
- The current interface is command-line based.
- Retrieval quality depends on chunking quality.

## 10. Future Work

- Add OCR support for scanned PDFs.
- Improve chunking strategy.
- Add source citation display.
- Add a Streamlit interface.
- Improve answer formatting.
- Add more documents and more test cases.

## 11. Lessons Learned

Main lessons from the project:

- RAG helps make answers more grounded in local documents.
- Embeddings make semantic search possible.
- Chunking quality strongly affects retrieval quality.
- SQLite is useful for simple local storage.
- Prompt engineering alone is not always enough; guard logic and retrieval checks are also important.
- PDF and DOCX support make the assistant more useful, but document parsing introduces new challenges.

## 12. Closing Statement

```text
This project demonstrates a complete local RAG pipeline. The assistant reads local documents, stores their embeddings in SQLite, retrieves relevant chunks for a question, and generates a context-based answer using a local model through Foundry Local.
```
