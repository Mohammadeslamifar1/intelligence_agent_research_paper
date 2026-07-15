from dataclasses import dataclass

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from app.ingestion.chunker import TextChunk


@dataclass
class SearchResult:
    document_name: str
    chunk_id: int
    text: str
    score: float


class TfidfSearchEngine:
    def setup(self) -> None:
        self.vectorizer = TfidfVectorizer(
            stop_words="english",
            max_features=20000,
            ngram_range=(1, 2),
        )
        self.chunks: list[TextChunk] = []
        self.chunk_vectors = None

    def build_index(self, chunks: list[TextChunk]) -> None:
        self.setup()

        if not chunks:
            raise ValueError("Cannot build index with empty chunks.")

        self.chunks = chunks
        texts = [chunk.text for chunk in chunks]
        self.chunk_vectors = self.vectorizer.fit_transform(texts)

    def search(
        self,
        query: str,
        top_k: int = 5,
        min_score: float = 0.02,
    ) -> list[SearchResult]:
        if self.chunk_vectors is None:
            raise ValueError("Index has not been built yet.")

        if not query.strip():
            raise ValueError("Query cannot be empty.")

        query_vector = self.vectorizer.transform([query])
        scores = cosine_similarity(query_vector, self.chunk_vectors).flatten()

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