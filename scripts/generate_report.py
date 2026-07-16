from pathlib import Path

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

    report = assistant.generate_report()

    output_folder = Path("results")
    output_folder.mkdir(parents=True, exist_ok=True)

    output_path = output_folder / "paper_report.md"
    output_path.write_text(report, encoding="utf-8")

    print(report)
    print(f"\nSaved report to: {output_path}")


if __name__ == "__main__":
    main()