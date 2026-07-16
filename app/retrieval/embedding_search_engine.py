from dataclasses import dataclass

import numpy as np

from app.ingestion.chunker import TextChunk
from app.retrieval.search_engine import SearchResult


@dataclass
class EmbeddingSearchConfig:
    model_name: str = "sentence-transformers/all-MiniLM-L6-v2"


class EmbeddingSearchEngine:
    def __init__(self, config: EmbeddingSearchConfig | None = None) -> None:
        self.config = config or EmbeddingSearchConfig()
        self.model = None
        self.chunks: list[TextChunk] = []
        self.chunk_embeddings: np.ndarray | None = None

    def build_index(self, chunks: list[TextChunk]) -> None:
        if not chunks:
            raise ValueError("Cannot build index with empty chunks.")

        from sentence_transformers import SentenceTransformer

        self.model = SentenceTransformer(self.config.model_name)
        self.chunks = chunks

        texts = [chunk.text for chunk in chunks]

        self.chunk_embeddings = self.model.encode(
            texts,
            normalize_embeddings=True,
            show_progress_bar=True,
        )

    def search(
        self,
        query: str,
        top_k: int = 5,
        min_score: float = 0.20,
    ) -> list[SearchResult]:
        if self.model is None or self.chunk_embeddings is None:
            raise ValueError("Index has not been built yet.")

        if not query.strip():
            raise ValueError("Query cannot be empty.")

        query_embedding = self.model.encode(
            [query],
            normalize_embeddings=True,
        )[0]

        scores = np.dot(self.chunk_embeddings, query_embedding)

        ranked_indices = scores.argsort()[::-1]

        results: list[SearchResult] = []

        for index in ranked_indices:
            score = float(scores[index])

            if score < min_score:
                continue

            chunk = self.chunks[index]

            results.append(
                SearchResult(
                    document_name=chunk.document_name,
                    chunk_id=chunk.chunk_id,
                    text=chunk.text,
                    score=score,
                )
            )

            if len(results) >= top_k:
                break

        return results