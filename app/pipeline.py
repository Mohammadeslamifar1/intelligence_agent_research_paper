from pathlib import Path

from app.generation.qa_engine import ExtractiveQAEngine
from app.ingestion.chunker import chunk_documents
from app.ingestion.pdf_loader import load_pdfs_from_folder
from app.retrieval.search_engine import TfidfSearchEngine


class ResearchPaperAssistant:
    def __init__(self, papers_folder: str = "data/papers") -> None:
        self.papers_folder = Path(papers_folder)
        self.search_engine = TfidfSearchEngine()
        self.qa_engine = ExtractiveQAEngine()
        self.document_count = 0
        self.chunk_count = 0

    def build(self) -> None:
        documents = load_pdfs_from_folder(self.papers_folder)
        chunks = chunk_documents(documents)

        self.search_engine.build_index(chunks)

        self.document_count = len(documents)
        self.chunk_count = len(chunks)

    def ask(self, question: str) -> str:
        search_results = self.search_engine.search(
            query=question,
            top_k=5,
            min_score=0.02,
        )

        answer = self.qa_engine.answer_question(
            question=question,
            search_results=search_results,
        )

        output_lines = [
            "",
            "Question:",
            answer.question,
            "",
            "Answer:",
            answer.answer,
            "",
            "Sources:",
        ]

        if not answer.sources:
            output_lines.append("No sources found.")
        else:
            for source in answer.sources:
                output_lines.append(
                    f"{source.document_name}, chunk {source.chunk_id}, score {source.score:.4f}"
                )

        return "\n".join(output_lines)