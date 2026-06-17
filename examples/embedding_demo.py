import math
from foundry_local_sdk import Configuration, FoundryLocalManager


documents = [
    "Foundry Local runs AI models directly on your device without cloud connectivity.",
    "SQLite stores data in a lightweight local database file.",
    "RAG retrieves relevant documents before generating an answer.",
    "Prompt engineering helps guide the model to answer correctly.",
]


def cosine_similarity(a, b):
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(x * x for x in b))

    if norm_a == 0 or norm_b == 0:
        return 0.0

    return dot / (norm_a * norm_b)


def main():
    config = Configuration(app_name="phase1_embedding_demo")
    FoundryLocalManager.initialize(config)
    manager = FoundryLocalManager.instance

    embedding_model = manager.catalog.get_model("qwen3-embedding-0.6b")

    print("Downloading embedding model if needed...")
    embedding_model.download(
        lambda p: print(f"\rDownloading embedding model: {p:.1f}%", end="", flush=True)
    )
    print()

    print("Loading embedding model...")
    embedding_model.load()
    print("Embedding model loaded.")

    embedding_client = embedding_model.get_embedding_client()

    print("Generating document embeddings...")
    response = embedding_client.generate_embeddings(documents)
    doc_embeddings = [item.embedding for item in response.data]

    query = "Where does SQLite store data?"
    print(f"\nQuery: {query}")

    query_response = embedding_client.generate_embedding(query)
    query_embedding = query_response.data[0].embedding

    scores = []

    for i, doc_embedding in enumerate(doc_embeddings):
        score = cosine_similarity(query_embedding, doc_embedding)
        scores.append((i, score))

    scores.sort(key=lambda x: x[1], reverse=True)

    print("\nMost relevant documents:")
    for index, score in scores:
        print(f"Score: {score:.4f} | Document: {documents[index]}")

    embedding_model.unload()
    print("\nEmbedding model unloaded.")


if __name__ == "__main__":
    main()