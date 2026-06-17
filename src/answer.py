import sys
from foundry_local_sdk import FoundryLocalManager

from retrieve import get_top_chunks


def get_content_from_chunk(chunk):
    if not chunk.choices:
        return ""

    delta = chunk.choices[0].delta
    content = delta.content

    if content:
        return content

    return ""


def build_context(top_chunks):
    context_parts = []

    for chunk in top_chunks:
        context_parts.append(
            f"Source: {chunk['source']}\n"
            f"Text: {chunk['chunk_text']}"
        )

    return "\n\n---\n\n".join(context_parts)


def answer_question(question):
    top_chunks = get_top_chunks(question, top_k=3)

    if not top_chunks:
        print("No relevant chunks found.")
        return

    best_score = top_chunks[0]["score"]

    if best_score < 0.45:
        print("\nQuestion:", question)
        print("Answer: I could not find this information in the provided documents.")
        return

    context = build_context(top_chunks)

    manager = FoundryLocalManager.instance

    print("\nLoading chat model...")
    chat_model = manager.catalog.get_model("qwen2.5-0.5b")
    chat_model.download(
        lambda p: print(f"\rDownloading chat model: {p:.1f}%", end="", flush=True)
    )
    print()
    chat_model.load()

    chat_client = chat_model.get_chat_client()

    messages = [
        {
            "role": "system",
            "content": (
                "You are a strict RAG assistant. "
                "Answer the question using only the provided context. "
                "Do not add outside information. "
                "If the question asks what something stands for, answer with the expansion directly. "
                "If the answer is not in the context, say: "
                "I could not find this information in the provided documents. "
                "Answer in one short complete sentence."
            ),
            
        },
        {
            "role": "user",
            "content": f"Context:\n{context}\n\nQuestion:\n{question}",
        },
    ]

    print("\nQuestion:", question)
    print("\nRetrieved context:")
    print(context)

    print("\nAnswer: ", end="", flush=True)

    for chunk in chat_client.complete_streaming_chat(messages):
        content = get_content_from_chunk(chunk)
        if content:
            print(content, end="", flush=True)

    print()

    chat_model.unload()
    print("\nChat model unloaded.")


def main():
    if len(sys.argv) > 1:
        question = " ".join(sys.argv[1:])
    else:
        question = input("Ask a question: ").strip()

    if not question:
        print("Please enter a question.")
        return

    answer_question(question)


if __name__ == "__main__":
    main()