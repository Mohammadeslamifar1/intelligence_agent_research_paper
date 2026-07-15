from pathlib import Path

from app.ingestion.pdf_loader import load_pdfs_from_folder
from app.ingestion.chunker import chunk_documents


def main() -> None:
    papers_folder = Path("data/papers")

    documents = load_pdfs_from_folder(papers_folder)
    chunks = chunk_documents(documents)

    print(f"Loaded {len(documents)} PDF file(s).")
    print(f"Created {len(chunks)} text chunks.")

    print("\nFirst chunk preview:")
    print("=" * 80)
    print(f"Document: {chunks[0].document_name}")
    print(f"Chunk ID: {chunks[0].chunk_id}")
    print(f"Characters: {chunks[0].character_count}")
    print(chunks[0].text[:1000])


main()