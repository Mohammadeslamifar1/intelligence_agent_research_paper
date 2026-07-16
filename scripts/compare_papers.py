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

    comparison = assistant.compare_papers()

    output_folder = Path("results")
    output_folder.mkdir(parents=True, exist_ok=True)

    output_path = output_folder / "paper_comparison_report.md"
    output_path.write_text(comparison, encoding="utf-8")

    print(comparison)
    print(f"\nSaved comparison report to: {output_path}")


if __name__ == "__main__":
    main()