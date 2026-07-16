from dataclasses import dataclass

from app.generation.qa_engine import ExtractiveQAEngine
from app.retrieval.search_engine import SearchResult


@dataclass
class ReportSection:
    title: str
    question: str
    answer: str
    sources: list[SearchResult]


class PaperReportGenerator:
    def __init__(
        self,
        search_engine,
        qa_engine: ExtractiveQAEngine,
        min_score: float,
    ) -> None:
        self.search_engine = search_engine
        self.qa_engine = qa_engine
        self.min_score = min_score

    def generate(self) -> list[ReportSection]:
        questions = {
            "Main Contribution": "What is the main contribution of this paper?",
            "Data Used": "What data does this paper use?",
            "Methodology": "What methodology or approach does this paper use?",
            "Measured Results": "What quantities, results, or findings are measured or reported?",
            "Limitations": "What limitations, warnings, or uncertainties do the authors mention?",
        }

        sections: list[ReportSection] = []

        for title, question in questions.items():
            search_results = self.search_engine.search(
                query=question,
                top_k=5,
                min_score=self.min_score,
            )

            answer = self.qa_engine.answer_question(
                question=question,
                search_results=search_results,
            )

            sections.append(
                ReportSection(
                    title=title,
                    question=question,
                    answer=answer.answer,
                    sources=answer.sources,
                )
            )

        return sections

    def to_markdown(self, sections: list[ReportSection]) -> str:
        lines = ["# Paper Intelligence Report", ""]

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