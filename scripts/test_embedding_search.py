from pathlib import Path

from app.ingestion.chunker import chunk_documents
from app.ingestion.pdf_loader import load_pdfs_from_folder
from app.retrieval.embedding_search_engine import EmbeddingSearchEngine


def main() -> None:
    papers_folder = Path("data/papers")

    documents = load_pdfs_from_folder(papers_folder)
    chunks = chunk_documents(documents)

    search_engine = EmbeddingSearchEngine()
    search_engine.build_index(chunks)

    queries = [
        "What is the main contribution of this paper?",
        "What dataset is used in this work?",
        "What scientific measurements are reported?",
        "What warnings or limitations do the authors mention?",
    ]

    for query in queries:
        results = search_engine.search(
            query=query,
            top_k=3,
            min_score=0.20,
        )

        print("\n" + "=" * 80)
        print(f"Query: {query}")
        print(f"Number of useful results: {len(results)}")

        for result in results:
            print("\n" + "." * 80)
            print(f"Document: {result.document_name}")
            print(f"Chunk ID: {result.chunk_id}")
            print(f"Score: {result.score:.4f}")
            print(result.text[:900])


if __name__ == "__main__":
    main()