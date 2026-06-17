import math
from pathlib import Path
from foundry_local_sdk import Configuration, FoundryLocalManager


NOTE_PATH = Path("sample_note.txt")


def load_documents_from_file(path):
    text = path.read_text(encoding="utf-8")

    documents = [
        paragraph.strip()
        for paragraph in text.split("\n\n")
        if paragraph.strip()
    ]

    return documents


def cosine_similarity(a, b):
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(x * x for x in b))

    if norm_a == 0 or norm_b == 0:
        return 0.0

    return dot / (norm_a * norm_b)


def main():
    if not NOTE_PATH.exists():
        print("sample_note.txt was not found.")
        return

    documents = load_documents_from_file(NOTE_PATH)

    if not documents:
        print("No documents found in sample_note.txt.")
        return

    question = "Where does SQLite store data?"

    config = Configuration(app_name="file_rag_demo")
    FoundryLocalManager.initialize(config)
    manager = FoundryLocalManager.instance

    print("Loading embedding model...")
    embedding_model = manager.catalog.get_model("qwen3-embedding-0.6b")
    embedding_model.download(
        lambda p: print(f"\rDownloading embedding model: {p:.1f}%", end="", flush=True)
    )
    print()
    embedding_model.load()

    embedding_client = embedding_model.get_embedding_client()

    print("Reading documents from sample_note.txt...")
    print(f"Loaded {len(documents)} document chunks.")

    print("Creating document embeddings...")
    document_response = embedding_client.generate_embeddings(documents)
    document_embeddings = [item.embedding for item in document_response.data]

    print("Creating question embedding...")
    question_response = embedding_client.generate_embedding(question)
    question_embedding = question_response.data[0].embedding

    scores = []

    for index, document_embedding in enumerate(document_embeddings):
        score = cosine_similarity(question_embedding, document_embedding)
        scores.append((index, score))

    scores.sort(key=lambda item: item[1], reverse=True)

    best_index, best_score = scores[0]
    retrieved_context = documents[best_index]

    print("\nQuestion:", question)
    print("Retrieved context:", retrieved_context)
    print(f"Similarity score: {best_score:.4f}")

    print("\nAnswer:", retrieved_context)

    embedding_model.unload()
    print("\nEmbedding model unloaded. Done!")


if __name__ == "__main__":
    main()