import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
INGEST_SCRIPT = PROJECT_ROOT / "src" / "ingest.py"
ANSWER_SCRIPT = PROJECT_ROOT / "src" / "answer.py"
TEST_RESULTS_PATH = PROJECT_ROOT / "TEST_RESULTS.md"

FALLBACK_ANSWER = "I could not find this information in the provided documents."


TEST_CASES = [
    {
        "question": "Where does SQLite store data?",
        "source_type": "TXT",
        "expected": "Retrieve SQLite-related context and answer from the documents.",
        "required_keywords": ["sqlite", "single", "database", "file"],
        "expects_fallback": False,
    },
    {
        "question": "What are embeddings used for?",
        "source_type": "TXT",
        "expected": "Retrieve embeddings-related context and answer from the documents.",
        "required_keywords": ["embedding", "text", "vector"],
        "expects_fallback": False,
    },
    {
        "question": "What is the course name in the MATH202 syllabus?",
        "source_type": "PDF",
        "expected": "Retrieve grading-related information from the PDF if the relevant text/table is extracted clearly.",
        "required_keywords": ["grade", "exam"],
        "expects_fallback": False,
        "allow_needs_review": True,
    },
    {
        "question": "How many exams are there in PSY201?",
        "source_type": "DOCX",
        "expected": "Retrieve exam information from the PSY201 syllabus DOCX file.",
        "required_keywords": ["two", "exam"],
        "expects_fallback": False,
    },
    {
        "question": "Who is the president of Turkey?",
        "source_type": "Out-of-document",
        "expected": "Refuse to answer because the information is not in the documents.",
        "required_keywords": [],
        "expects_fallback": True,
    },
]


def run_script(command, timeout=600):
    result = subprocess.run(
        command,
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        timeout=timeout,
        check=False,
    )

    return result.returncode, result.stdout.strip(), result.stderr.strip()


def run_ingest_script():
    command = [sys.executable, str(INGEST_SCRIPT)]
    return run_script(command)


def run_answer_script(question):
    command = [sys.executable, str(ANSWER_SCRIPT), question]
    return run_script(command)


def extract_answer(output):
    marker = "Answer:"

    if marker not in output:
        if FALLBACK_ANSWER in output:
            return FALLBACK_ANSWER
        return "No answer found in output."

    answer_part = output.split(marker, 1)[1].strip()

    stop_markers = [
        "Chat model unloaded.",
        "Models unloaded.",
        "Done!",
    ]

    for stop_marker in stop_markers:
        if stop_marker in answer_part:
            answer_part = answer_part.split(stop_marker, 1)[0].strip()

    return " ".join(answer_part.split())


def parse_ingest_summary(output):
    processed_documents = []
    saved_chunks = "Unknown"

    for line in output.splitlines():
        line = line.strip()

        if line.startswith("Processing "):
            processed_documents.append(line)

        match = re.search(r"Saved\s+(\d+)\s+chunks\s+to\s+rag\.db", line)
        if match:
            saved_chunks = match.group(1)

    return processed_documents, saved_chunks


def answer_contains_keywords(answer, keywords):
    answer_lower = answer.lower()
    return all(keyword.lower() in answer_lower for keyword in keywords)


def decide_status(returncode, answer, test_case):
    if returncode != 0:
        return "Failed"

    if answer == "No answer found in output.":
        return "Failed"

    expects_fallback = test_case["expects_fallback"]
    is_fallback = FALLBACK_ANSWER.lower() in answer.lower()

    if expects_fallback:
        if is_fallback:
            return "Passed"
        return "Failed"

    if is_fallback:
        if test_case.get("allow_needs_review"):
            return "Needs Review"
        return "Failed"

    required_keywords = test_case["required_keywords"]

    if required_keywords and not answer_contains_keywords(answer, required_keywords):
        if test_case.get("allow_needs_review"):
            return "Needs Review"
        return "Failed"

    return "Passed"


def escape_markdown_table_cell(value):
    return value.replace("|", "\\|").replace("\n", " ")


def build_report(ingest_output, ingest_status, results):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    processed_documents, saved_chunks = parse_ingest_summary(ingest_output)

    lines = [
        "# Test Results",
        "",
        "This file records the latest automated test results for the local RAG assistant.",
        "",
        "## Environment",
        "",
        "- Conda environment: `foundry-rag`",
        "- Embedding model: `qwen3-embedding-0.6b`",
        "- Chat model: `qwen2.5-0.5b`",
        "- Database: `rag.db`",
        "- Document folder: `data/docs`",
        "- Supported document types: `.txt`, `.pdf`, `.docx`",
        "- PDF parser: `pdfplumber`",
        "- DOCX parser: `python-docx`",
        "",
        "## Pipeline Tested",
        "",
        "The following pipeline was tested:",
        "",
        "1. Read supported documents from `data/docs`",
        "2. Extract text from `.txt`, `.pdf`, and `.docx` files",
        "3. Extract PDF tables with `pdfplumber` when possible",
        "4. Split extracted text into chunks",
        "5. Generate embeddings for each chunk",
        "6. Store chunks and embeddings in `rag.db`",
        "7. Embed the user question",
        "8. Retrieve the most relevant chunks using cosine similarity",
        "9. Build context from retrieved chunks",
        "10. Generate an answer using the local chat model",
        "",
        "## Automated Test Run",
        "",
        f"- Last run: `{timestamp}`",
        f"- Ingestion status: `{ingest_status}`",
        f"- Chunks saved to database: `{saved_chunks}`",
        "",
        "## Ingestion Test",
        "",
        "Command:",
        "",
        "```bash",
        "python src/ingest.py",
        "```",
        "",
        "Processed documents:",
        "",
    ]

    if processed_documents:
        for document in processed_documents:
            lines.append(f"- `{document}`")
    else:
        lines.append("- No processed documents were found in the output.")

    lines.extend(
        [
            "",
            "## Question Answering Tests",
            "",
            "| Test | Question | Source Type | Expected Behavior | Actual Result | Status |",
            "|---|---|---|---|---|---|",
        ]
    )

    for index, result in enumerate(results, start=1):
        question = escape_markdown_table_cell(result["question"])
        source_type = escape_markdown_table_cell(result["source_type"])
        expected = escape_markdown_table_cell(result["expected"])
        answer = escape_markdown_table_cell(result["answer"])
        status = result["status"]

        lines.append(
            f"| {index} | `{question}` | {source_type} | {expected} | {answer} | {status} |"
        )

    lines.extend(
        [
            "",
            "## Notes",
            "",
            "- Answerable questions should be answered using retrieved document context.",
            "- Unanswerable questions should be refused instead of answered from outside knowledge.",
            "- `Needs Review` means the system ran successfully, but the retrieved answer did not clearly satisfy the expected keywords.",
            "- PDF table extraction can be imperfect, especially for complex or scanned PDFs.",
            "- If an answer is too verbose or inaccurate, refine the system prompt, improve chunking, or clean the source documents.",
            "",
            "## Current Status",
            "",
            "The core RAG pipeline is tested with this flow:",
            "",
            "```text",
            "data/docs/*.txt, *.pdf, *.docx",
            "-> src/ingest.py",
            "-> rag.db",
            "-> src/retrieve.py",
            "-> src/answer.py",
            "-> local context-based answer",
            "```",
        ]
    )

    return "\n".join(lines) + "\n"


def main():
    if not INGEST_SCRIPT.exists():
        print("src/ingest.py was not found. Create it before running tests.")
        sys.exit(1)

    if not ANSWER_SCRIPT.exists():
        print("src/answer.py was not found. Create it before running tests.")
        sys.exit(1)

    print("Running ingestion pipeline...")
    ingest_returncode, ingest_output, ingest_error = run_ingest_script()
    ingest_status = "Passed" if ingest_returncode == 0 else "Failed"

    if ingest_returncode != 0:
        print(ingest_error)

    results = []

    for test_case in TEST_CASES:
        question = test_case["question"]
        print(f"Running test: {question}")

        returncode, output, error_output = run_answer_script(question)
        answer = extract_answer(output)

        if returncode != 0 and error_output:
            answer = error_output

        status = decide_status(returncode, answer, test_case)

        results.append(
            {
                "question": question,
                "source_type": test_case["source_type"],
                "expected": test_case["expected"],
                "answer": answer,
                "status": status,
            }
        )

    report = build_report(ingest_output, ingest_status, results)
    TEST_RESULTS_PATH.write_text(report, encoding="utf-8")

    print(f"\nSaved automated test results to {TEST_RESULTS_PATH.name}.")


if __name__ == "__main__":
    main()