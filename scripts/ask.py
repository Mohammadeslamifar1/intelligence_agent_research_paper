from app.pipeline import ResearchPaperAssistant


def main() -> None:
    assistant = ResearchPaperAssistant()

    print("Building research paper assistant...")
    assistant.build()

    print(
        f"Ready. Loaded {assistant.document_count} paper file and created {assistant.chunk_count} chunks."
    )
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


main()