import re
from dataclasses import dataclass

from app.retrieval.search_engine import SearchResult


@dataclass
class Answer:
    question: str
    answer: str
    sources: list[SearchResult]


class ExtractiveQAEngine:
    def answer_question(
        self,
        question: str,
        search_results: list[SearchResult],
        max_sentences: int = 5,
    ) -> Answer:
        if not question.strip():
            raise ValueError("Question cannot be empty.")

        if not search_results:
            return Answer(
                question=question,
                answer="I could not find enough relevant information in the uploaded papers.",
                sources=[],
            )

        candidate_sentences = []

        for result in search_results:
            sentences = self._split_into_sentences(result.text)

            for sentence in sentences:
                score = self._sentence_score(question, sentence)

                if score > 0:
                    candidate_sentences.append(
                        {
                            "sentence": sentence,
                            "score": score + result.score,
                            "source": result,
                        }
                    )

        if not candidate_sentences:
            best_result = search_results[0]
            return Answer(
                question=question,
                answer=best_result.text[:900],
                sources=[best_result],
            )

        ranked_sentences = sorted(
            candidate_sentences,
            key=lambda item: item["score"],
            reverse=True,
        )

        selected_sentences = []
        selected_sources = []

        for item in ranked_sentences:
            sentence = item["sentence"]
            source = item["source"]

            if sentence not in selected_sentences:
                selected_sentences.append(sentence)

            if source not in selected_sources:
                selected_sources.append(source)

            if len(selected_sentences) >= max_sentences:
                break

        final_answer = " ".join(selected_sentences)

        return Answer(
            question=question,
            answer=final_answer,
            sources=selected_sources,
        )

    def _split_into_sentences(self, text: str) -> list[str]:
        cleaned_text = " ".join(text.split())
        sentences = re.split(r"(?<=[.!?])\s+", cleaned_text)
        return [sentence.strip() for sentence in sentences if len(sentence.strip()) > 40]

    def _sentence_score(self, question: str, sentence: str) -> float:
        question_words = self._important_words(question)
        sentence_words = self._important_words(sentence)

        if not question_words or not sentence_words:
            return 0.0

        overlap = question_words.intersection(sentence_words)
        return len(overlap) / len(question_words)

    def _important_words(self, text: str) -> set[str]:
        stop_words = {
            "what",
            "which",
            "where",
            "when",
            "why",
            "how",
            "the",
            "this",
            "that",
            "does",
            "paper",
            "use",
            "uses",
            "are",
            "is",
            "was",
            "were",
            "and",
            "or",
            "of",
            "to",
            "in",
            "for",
            "from",
            "with",
            "a",
            "an",
        }

        words = re.findall(r"[a-zA-Z][a-zA-Z0-9]+", text.lower())
        return {word for word in words if word not in stop_words}