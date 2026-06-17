# Local RAG Assistant

This project is a local Retrieval-Augmented Generation (RAG) assistant built with Foundry Local, Python, embeddings, SQLite, PDF/DOCX parsing, and a local language model.

The assistant reads local `.txt`, `.pdf`, and `.docx` documents, splits them into chunks, creates embeddings for each chunk, stores the embeddings in a SQLite database, retrieves the most relevant chunks for a user question, and generates an answer using a local chat model.

## Project Goal

The goal of this project is to build a local offline document question-answering assistant.

Instead of relying only on the language model's general knowledge, the assistant retrieves relevant information from local documents and uses that information as context before answering.

## Technologies Used

- Python 3.11
- Foundry Local SDK
- `qwen3-embedding-0.6b` embedding model
- `qwen2.5-0.5b` chat model
- SQLite
- Cosine similarity
- `pdfplumber` for PDF text and table extraction
- `python-docx` for DOCX document reading
- Command-line interface

## Project Structure

```text
local-rag-assistant/
├── data/
│   └── docs/
│       ├── embeddings.txt
│       ├── foundry_local.txt
│       ├── Math202SYL_Spr2026.pdf
│       ├── PSY201_syllabus_SP25-26.docx
│       ├── prompt_engineering.txt
│       ├── rag.txt
│       ├── sample_note.txt
│       └── sqlite.txt
├── examples/
│   ├── embedding_demo.py
│   ├── file_rag_demo.py
│   ├── main.py
│   ├── prompt_demo.py
│   ├── rag_demo.py
│   └── sqlite_demo.py
├── src/
│   ├── ingest.py
│   ├── retrieve.py
│   ├── answer.py
│   └── run_tests.py
├── .gitignore
├── rag.db
├── README.md
├── TEST_RESULTS.md
├── DEMO_SCRIPT.md
├── PRESENTATION_OUTLINE.md
├── requirements.txt
```

The `src/` folder contains the final project code. The `examples/` folder contains Phase 1 learning demos used to test individual concepts such as embeddings, SQLite, prompt engineering, and mini RAG retrieval.

## How It Works

1. Documents are placed inside `data/docs`.
2. `src/ingest.py` reads `.txt`, `.pdf`, and `.docx` documents and splits them into chunks.
3. Each chunk is converted into an embedding using the local embedding model.
4. Chunks and embeddings are stored in `rag.db`.
5. `src/retrieve.py` embeds the user question and finds the most relevant chunks using cosine similarity.
6. `src/answer.py` builds context from the retrieved chunks and asks the local chat model to answer using only that context.

## Setup

Create and activate the conda environment:

```bash
conda create -n foundry-rag python=3.11
conda activate foundry-rag
```

Install the required packages:

```bash
pip install foundry-local-sdk openai numpy pdfplumber python-docx
```

Save installed packages:

```bash
pip freeze > requirements.txt
```

## Running the Project

First, build the local RAG database:

```bash
python src/ingest.py
```

This reads all supported files from `data/docs`:

```text
.txt
.pdf
.docx
```

Then ask a question:

```bash
python src/answer.py "Where does SQLite store data?"
```

Another example:

```bash
python src/answer.py "What does RAG stand for?"
```

## Example Results

### Example 1

Question:

```text
Where does SQLite store data?
```

Answer:

```text
SQLite stores data in a single database file.
```

### Example 2

Question:

```text
Who is the president of Turkey?
```

Answer:

```text
I could not find this information in the provided documents.
```

## Testing

Run the automated test script:

```bash
python src/run_tests.py
```

The script runs sample questions through `src/answer.py` and writes the latest results to:

```text
TEST_RESULTS.md
```

The system was tested with both answerable and unanswerable questions. It correctly answered document-based questions and refused to answer questions that were not supported by the provided documents.

## Limitations

- The current project uses small sample documents.
- The chat model is small, so answers can sometimes be slightly verbose or imperfect.
- PDF text and tables are extracted with `pdfplumber`, but scanned image-based PDFs may still require OCR.
- Complex PDF tables may not always preserve their original layout perfectly.
- The command-line interface is simple and does not yet include a graphical UI.

## Future Work

- Add OCR support for scanned PDFs.
- Improve the chunking strategy.
- Add a Streamlit interface.
- Add more test documents.
- Improve answer formatting and citation display.
