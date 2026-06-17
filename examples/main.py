from foundry_local_sdk import Configuration, FoundryLocalManager


def main():
    # Initialize the Foundry Local SDK
    config = Configuration(app_name="foundry_local_phase1_test")
    FoundryLocalManager.initialize(config)
    manager = FoundryLocalManager.instance

    # Download and register execution providers
    current_ep = ""

    def ep_progress(ep_name: str, percent: float):
        nonlocal current_ep
        if ep_name != current_ep:
            if current_ep:
                print()
            current_ep = ep_name
        print(f"\r  {ep_name:<30}  {percent:5.1f}%", end="", flush=True)

    print("Preparing execution providers...")
    manager.download_and_register_eps(progress_callback=ep_progress)
    if current_ep:
        print()

    # Select and load a small local model
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

    # Get chat client
    client = model.get_chat_client()

    messages = [
        {
            "role": "system",
            "content": "You are a helpful assistant. Keep your answer short.",
        },
        {
            "role": "user",
            "content": "In AI, RAG means Retrieval-Augmented Generation. Explain it in one short sentence.",
        },
    ]

    print("\nAssistant: ", end="", flush=True)

    for chunk in client.complete_streaming_chat(messages):
        if not chunk.choices:
            continue

        delta = chunk.choices[0].delta
        content = delta.content

        if content:
            print(content, end="", flush=True)

    print("\n")

    model.unload()
    print("Model unloaded.")


if __name__ == "__main__":
    main()