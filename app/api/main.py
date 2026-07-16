from pathlib import Path

from fastapi import FastAPI
from pydantic import BaseModel

from app.pipeline import ResearchPaperAssistant


app = FastAPI(
    title="Research Paper Intelligence Agent API",
    description="API for asking questions over uploaded research papers.",
    version="0.1.0",
)

assistant = ResearchPaperAssistant(papers_folder="data/papers")
is_ready = False


class QuestionRequest(BaseModel):
    question: str


class QuestionResponse(BaseModel):
    question: str
    answer: str


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/build")
def build_assistant() -> dict[str, int | str]:
    global is_ready

    assistant.build()
    is_ready = True

    return {
        "status": "ready",
        "document_count": assistant.document_count,
        "chunk_count": assistant.chunk_count,
    }


@app.post("/ask", response_model=QuestionResponse)
def ask_question(request: QuestionRequest) -> QuestionResponse:
    if not is_ready:
        return QuestionResponse(
            question=request.question,
            answer="Assistant is not ready. Call the build endpoint first.",
        )

    answer = assistant.ask(request.question)

    return QuestionResponse(
        question=request.question,
        answer=answer,
    )