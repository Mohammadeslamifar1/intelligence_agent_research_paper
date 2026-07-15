from pathlib import Path

from app.ingestion.pdf_loader import load_pdfs_from_folder


def main() -> None:
    papers_folder = Path("data/papers")
    documents = load_pdfs_from_folder(papers_folder)

    print(f"Loaded {len(documents)} PDF file(s).")

    for file_name, text in documents.items():
        print("\n" + "=" * 80)
        print(f"File: {file_name}")
        print(f"Characters extracted: {len(text)}")
        print("Preview:")
        print(text[:1000])


if __name__ == "__main__":
    main()