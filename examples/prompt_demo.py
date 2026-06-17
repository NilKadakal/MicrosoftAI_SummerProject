from foundry_local_sdk import Configuration, FoundryLocalManager


def get_content_from_chunk(chunk):
    if not chunk.choices:
        return ""

    delta = chunk.choices[0].delta
    content = delta.content

    if content:
        return content

    return ""


def is_question_supported_by_context(context, question):
    context_lower = context.lower()
    question_lower = question.lower()

    stop_words = ["what", "is", "the", "a", "an", "does", "where", "how"]

    important_terms = [
        term.strip("?.!,")
        for term in question_lower.split()
        if term.strip("?.!,") not in stop_words
    ]

    for term in important_terms:
        if term not in context_lower:
            return False

    return True


def ask_with_context(client, context, question):
    print("\nQuestion:", question)
    print("Answer: ", end="", flush=True)

    if not is_question_supported_by_context(context, question):
        print("I could not find this information in the provided context.")
        return

    messages = [
        {
            "role": "system",
            "content": (
                "You are a careful RAG assistant. "
                "Answer using only the provided context. "
                "Keep the answer short."
            ),
        },
        {
            "role": "user",
            "content": f"Context:\n{context}\n\nQuestion:\n{question}",
        },
    ]

    for chunk in client.complete_streaming_chat(messages):
        content = get_content_from_chunk(chunk)
        if content:
            print(content, end="", flush=True)

    print()


def main():
    config = Configuration(app_name="phase1_prompt_demo")
    FoundryLocalManager.initialize(config)
    manager = FoundryLocalManager.instance

    model = manager.catalog.get_model("qwen2.5-0.5b")

    print("Downloading model if needed...")
    model.download(
        lambda progress: print(
            f"\rDownloading model: {progress:.2f}%",
            end="",
            flush=True,
        )
    )
    print()

    print("Loading model...")
    model.load()
    print("Model loaded and ready.")

    client = model.get_chat_client()

    context = "SQLite is a lightweight local database that stores data in a single file."

    ask_with_context(client, context, "What is SQLite?")
    ask_with_context(client, context, "What is Foundry Local?")

    model.unload()
    print("\nModel unloaded.")


if __name__ == "__main__":
    main()