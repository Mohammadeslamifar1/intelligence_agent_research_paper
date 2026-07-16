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
        max_sentences: int = 4,
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
            cleaned_text = self._clean_text(result.text)
            sentences = self._split_into_sentences(cleaned_text)

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
                answer=self._clean_text(best_result.text[:700]),
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

            if self._is_noisy_sentence(sentence):
                continue

            if self._is_duplicate(sentence, selected_sentences):
                continue

            selected_sentences.append(sentence)

            if source not in selected_sources:
                selected_sources.append(source)

            if len(selected_sentences) >= max_sentences:
                break

        if not selected_sentences:
            best_result = search_results[0]
            selected_sentences = [self._clean_text(best_result.text[:700])]
            selected_sources = [best_result]

        final_answer = self._format_answer(selected_sentences)

        return Answer(
            question=question,
            answer=final_answer,
            sources=selected_sources,
        )

    def _clean_text(self, text: str) -> str:
        text = re.sub(r"\[Page\s+\d+\]", " ", text)
        text = re.sub(r"\s+", " ", text)
        text = text.replace("ﬁ", "fi")
        text = text.replace("ﬂ", "fl")
        text = text.replace("in-", "in")
        text = text.replace("comprehen- sive", "comprehensive")
        text = text.replace("lumi- nosities", "luminosities")
        text = text.replace("Ed- dington", "Eddington")
        text = text.replace("re- spectively", "respectively")
        return text.strip()

    def _split_into_sentences(self, text: str) -> list[str]:
        sentences = re.split(r"(?<=[.!?])\s+", text)
        return [
            sentence.strip()
            for sentence in sentences
            if 50 <= len(sentence.strip()) <= 450
        ]

    def _sentence_score(self, question: str, sentence: str) -> float:
        question_words = self._important_words(question)
        sentence_words = self._important_words(sentence)

        if not question_words or not sentence_words:
            return 0.0

        overlap = question_words.intersection(sentence_words)
        score = len(overlap) / len(question_words)

        lower_sentence = sentence.lower()
        lower_question = question.lower()

        if "contribution" in lower_question:
            bonus_terms = ["present", "catalog", "measure", "update", "compile"]
            score += self._bonus_score(lower_sentence, bonus_terms)

        if "data" in lower_question:
            bonus_terms = ["data", "catalog", "sdss", "dr16q", "observed"]
            score += self._bonus_score(lower_sentence, bonus_terms)

        if "physical quantities" in lower_question or "measured" in lower_question:
            bonus_terms = [
                "black hole mass",
                "bolometric",
                "redshift",
                "continuum",
                "emission line",
            ]
            score += self._bonus_score(lower_sentence, bonus_terms)

        if "limitation" in lower_question or "limitations" in lower_question:
            bonus_terms = [
                "uncertainties",
                "unreliable",
                "quality",
                "caution",
                "systematic",
            ]
            score += self._bonus_score(lower_sentence, bonus_terms)

        return score

    def _bonus_score(self, sentence: str, terms: list[str]) -> float:
        bonus = 0.0

        for term in terms:
            if term in sentence:
                bonus += 0.15

        return bonus

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
            "main",
            "mentioned",
            "included",
        }

        words = re.findall(r"[a-zA-Z][a-zA-Z0-9]+", text.lower())
        return {word for word in words if word not in stop_words}

    def _is_noisy_sentence(self, sentence: str) -> bool:
        noisy_terms = [
            "typeset using",
            "department of",
            "keywords",
            "this paper is organized",
            "throughout this paper",
            "references",
        ]

        lower_sentence = sentence.lower()

        return any(term in lower_sentence for term in noisy_terms)

    def _is_duplicate(self, sentence: str, selected_sentences: list[str]) -> bool:
        sentence_words = self._important_words(sentence)

        for selected in selected_sentences:
            selected_words = self._important_words(selected)

            if not sentence_words or not selected_words:
                continue

            overlap = sentence_words.intersection(selected_words)
            similarity = len(overlap) / max(len(sentence_words), len(selected_words))

            if similarity > 0.75:
                return True

        return False

    def _format_answer(self, sentences: list[str]) -> str:
        answer = " ".join(sentences)
        answer = re.sub(r"\s+", " ", answer)
        return answer.strip()