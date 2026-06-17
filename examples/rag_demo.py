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


def get_content_from_chunk(chunk):
    if not chunk.choices:
        return ""

    content = chunk.choices[0].delta.content
    if content:
        return content

    return ""


def answer_with_context(chat_client, context, question):
    messages = [
        {
            "role": "system",
            "content": (
                "You are a strict RAG assistant. "
                "Answer using only the provided context. "
                "Do not add outside information. "
                "Do not expand acronyms unless the expansion is written in the context. "
                "If the answer is not in the context, say: "
                "I could not find this information in the provided context. "
                "Answer in one complete sentence."
            ),
        },
        {
            "role": "user",
            "content": f"Context:\n{context}\n\nQuestion:\n{question}",
        },
    ]

    print("\nAnswer: ", end="", flush=True)

    for chunk in chat_client.complete_streaming_chat(messages):
        content = get_content_from_chunk(chunk)
        if content:
            print(content, end="", flush=True)

    print()


def main():
    config = Configuration(app_name="mini_rag_demo")
    FoundryLocalManager.initialize(config)
    manager = FoundryLocalManager.instance

    question = "What does RAG do?"

    print("Loading embedding model...")
    embedding_model = manager.catalog.get_model("qwen3-embedding-0.6b")
    embedding_model.download(
        lambda p: print(f"\rDownloading embedding model: {p:.1f}%", end="", flush=True)
    )
    print()
    embedding_model.load()

    embedding_client = embedding_model.get_embedding_client()

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

    embedding_model.unload()

    print("\nAnswer:", retrieved_context)

    print("\nEmbedding model unloaded. Done!")


if __name__ == "__main__":
    main()