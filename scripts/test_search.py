from pathlib import Path

from app.ingestion.pdf_loader import load_pdfs_from_folder
from app.ingestion.chunker import chunk_documents
from app.retrieval.search_engine import TfidfSearchEngine


def main() -> None:
    papers_folder = Path("data/papers")

    documents = load_pdfs_from_folder(papers_folder)
    chunks = chunk_documents(documents)

    search_engine = TfidfSearchEngine()
    search_engine.build_index(chunks)

    queries = [
        "What is the main contribution of this paper?",
        "What data does the paper use?",
        "What physical quantities are measured?",
        "What are the limitations of the catalog?",
    ]

    for query in queries:
        results = search_engine.search(query=query, top_k=3)

        print("\n" + "=" * 80)
        print(f"Query: {query}")
        print(f"Number of useful results: {len(results)}")

        for result in results:
            print("\n" + "." * 80)
            print(f"Document: {result.document_name}")
            print(f"Chunk ID: {result.chunk_id}")
            print(f"Score: {result.score:.4f}")
            print(result.text[:900])


main()