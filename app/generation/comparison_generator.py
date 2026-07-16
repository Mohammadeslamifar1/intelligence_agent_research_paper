from dataclasses import dataclass

from app.generation.qa_engine import ExtractiveQAEngine
from app.retrieval.search_engine import SearchResult


@dataclass
class ComparisonSection:
    title: str
    question: str
    answer: str
    sources: list[SearchResult]


class PaperComparisonGenerator:
    def __init__(
        self,
        search_engine,
        qa_engine: ExtractiveQAEngine,
        min_score: float,
    ) -> None:
        self.search_engine = search_engine
        self.qa_engine = qa_engine
        self.min_score = min_score

    def generate(self) -> list[ComparisonSection]:
        questions = {
            "Main Contributions": "Compare the main contributions of the papers.",
            "Data Used": "Compare the datasets or data sources used by the papers.",
            "Methodology": "Compare the methodology or approach used by the papers.",
            "Reported Results": "Compare the results, findings, or measured quantities reported by the papers.",
            "Limitations": "Compare the limitations, warnings, or uncertainties mentioned by the papers.",
        }

        sections: list[ComparisonSection] = []

        for title, question in questions.items():
            search_results = self.search_engine.search(
                query=question,
                top_k=8,
                min_score=self.min_score,
            )

            answer = self.qa_engine.answer_question(
                question=question,
                search_results=search_results,
                max_sentences=6,
            )

            sections.append(
                ComparisonSection(
                    title=title,
                    question=question,
                    answer=answer.answer,
                    sources=answer.sources,
                )
            )

        return sections

    def to_markdown(self, sections: list[ComparisonSection]) -> str:
        lines = ["# Paper Comparison Report", ""]

        for section in sections:
            lines.append(f"## {section.title}")
            lines.append("")
            lines.append(section.answer)
            lines.append("")
            lines.append("Sources:")
            lines.append("")

            if not section.sources:
                lines.append("No sources found.")
            else:
                for source in section.sources:
                    lines.append(
                        f"{source.document_name}, chunk {source.chunk_id}, score {source.score:.4f}"
                    )

            lines.append("")

        return "\n".join(lines)