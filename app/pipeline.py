from pathlib import Path
from typing import Literal

from app.generation.qa_engine import ExtractiveQAEngine
from app.ingestion.chunker import chunk_documents
from app.ingestion.pdf_loader import load_pdfs_from_folder
from app.retrieval.search_engine import TfidfSearchEngine


RetrievalMethod = Literal["tfidf", "semantic"]


class ResearchPaperAssistant:
    def __init__(
        self,
        papers_folder: str = "data/papers",
        retrieval_method: RetrievalMethod = "tfidf",
    ) -> None:
        self.papers_folder = Path(papers_folder)
        self.retrieval_method = retrieval_method
        self.search_engine = None
        self.qa_engine = ExtractiveQAEngine()
        self.document_count = 0
        self.chunk_count = 0

    def build(self) -> None:
        documents = load_pdfs_from_folder(self.papers_folder)
        chunks = chunk_documents(documents)

        self.search_engine = self._create_search_engine()
        self.search_engine.build_index(chunks)

        self.document_count = len(documents)
        self.chunk_count = len(chunks)

    def ask(self, question: str) -> str:
        if self.search_engine is None:
            raise ValueError("Assistant has not been built yet.")

        search_results = self.search_engine.search(
            query=question,
            top_k=5,
            min_score=self._minimum_score(),
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

    def _create_search_engine(self):
        if self.retrieval_method == "semantic":
            from app.retrieval.embedding_search_engine import EmbeddingSearchEngine

            return EmbeddingSearchEngine()

        return TfidfSearchEngine()

    def _minimum_score(self) -> float:
        if self.retrieval_method == "semantic":
            return 0.20

        return 0.02