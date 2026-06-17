import json
import math
import sqlite3
from pathlib import Path

from foundry_local_sdk import Configuration, FoundryLocalManager


DB_PATH = Path("rag.db")


def cosine_similarity(a, b):
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(x * x for x in b))

    if norm_a == 0 or norm_b == 0:
        return 0.0

    return dot / (norm_a * norm_b)


def load_chunks():
    connection = sqlite3.connect(DB_PATH)
    cursor = connection.cursor()

    cursor.execute("""
        SELECT id, source, chunk_index, chunk_text, embedding
        FROM chunks
    """)

    rows = cursor.fetchall()
    connection.close()

    chunks = []

    for row in rows:
        chunk_id = row[0]
        source = row[1]
        chunk_index = row[2]
        chunk_text = row[3]
        embedding = json.loads(row[4])

        chunks.append({
            "id": chunk_id,
            "source": source,
            "chunk_index": chunk_index,
            "chunk_text": chunk_text,
            "embedding": embedding,
        })

    return chunks


def get_top_chunks(query, top_k=3):
    if not DB_PATH.exists():
        print("rag.db was not found. Run python src/ingest.py first.")
        return []

    chunks = load_chunks()

    config = Configuration(app_name="rag_retrieval")
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

    print("Creating query embedding...")
    query_response = embedding_client.generate_embedding(query)
    query_embedding = query_response.data[0].embedding

    scored_chunks = []

    for chunk in chunks:
        score = cosine_similarity(query_embedding, chunk["embedding"])

        scored_chunks.append({
            "id": chunk["id"],
            "source": chunk["source"],
            "chunk_index": chunk["chunk_index"],
            "chunk_text": chunk["chunk_text"],
            "score": score,
        })

    scored_chunks.sort(key=lambda item: item["score"], reverse=True)

    embedding_model.unload()

    return scored_chunks[:top_k]


def main():
    query = "Where does SQLite store data?"

    top_chunks = get_top_chunks(query, top_k=3)

    print("\nQuery:", query)
    print("\nTop chunks:")

    for chunk in top_chunks:
        print("-" * 60)
        print("ID:", chunk["id"])
        print("Source:", chunk["source"])
        print("Chunk index:", chunk["chunk_index"])
        print(f"Score: {chunk['score']:.4f}")
        print("Text:", chunk["chunk_text"])


if __name__ == "__main__":
    main()