from pathlib import Path

from app.generation.qa_engine import ExtractiveQAEngine
from app.ingestion.chunker import chunk_documents
from app.ingestion.pdf_loader import load_pdfs_from_folder
from app.retrieval.search_engine import TfidfSearchEngine


def main() -> None:
    papers_folder = Path("data/papers")

    documents = load_pdfs_from_folder(papers_folder)
    chunks = chunk_documents(documents)

    search_engine = TfidfSearchEngine()
    search_engine.build_index(chunks)

    qa_engine = ExtractiveQAEngine()

    questions = [
        "What is the main contribution of this paper?",
        "What data does the paper use?",
        "What physical quantities are measured?",
        "What are the limitations of the catalog?",
    ]

    for question in questions:
        search_results = search_engine.search(
            query=question,
            top_k=5,
            min_score=0.02,
        )

        answer = qa_engine.answer_question(
            question=question,
            search_results=search_results,
        )

        print("\n" + "=" * 80)
        print(f"Question: {answer.question}")
        print("\nAnswer:")
        print(answer.answer)

        print("\nSources:")
        for source in answer.sources:
            print(
                f"{source.document_name}, chunk {source.chunk_id}, score {source.score:.4f}"
            )


if __name__ == "__main__":
    main()