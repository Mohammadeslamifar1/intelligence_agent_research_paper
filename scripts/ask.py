from app.pipeline import ResearchPaperAssistant


def choose_retrieval_method() -> str:
    print("Choose retrieval method:")
    print("1. TF IDF keyword search")
    print("2. Semantic embedding search")

    choice = input("Enter 1 or 2: ").strip()

    if choice == "2":
        return "semantic"

    return "tfidf"


def main() -> None:
    retrieval_method = choose_retrieval_method()

    assistant = ResearchPaperAssistant(
        retrieval_method=retrieval_method,
    )

    print("Building research paper assistant...")
    assistant.build()

    print(
        f"Ready. Loaded {assistant.document_count} paper file and created {assistant.chunk_count} chunks."
    )
    print(f"Retrieval method: {retrieval_method}")
    print("Type your question. Type exit to stop.")

    while True:
        question = input("\nYour question: ").strip()

        if question.lower() in {"exit", "quit"}:
            print("Goodbye.")
            break

        if not question:
            print("Please write a question.")
            continue

        answer = assistant.ask(question)
        print(answer)


if __name__ == "__main__":
    main()