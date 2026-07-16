from typing import Literal

from fastapi import FastAPI
from pydantic import BaseModel

from app.pipeline import ResearchPaperAssistant


RetrievalMethod = Literal["tfidf", "semantic"]

app = FastAPI(
    title="Research Paper Intelligence Agent API",
    description="API for asking questions over uploaded research papers.",
    version="0.2.0",
)

assistant: ResearchPaperAssistant | None = None
is_ready = False
active_retrieval_method: RetrievalMethod = "tfidf"


class BuildRequest(BaseModel):
    retrieval_method: RetrievalMethod = "tfidf"


class BuildResponse(BaseModel):
    status: str
    document_count: int
    chunk_count: int
    retrieval_method: RetrievalMethod


class QuestionRequest(BaseModel):
    question: str


class QuestionResponse(BaseModel):
    question: str
    answer: str
    retrieval_method: RetrievalMethod


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/build", response_model=BuildResponse)
def build_assistant(request: BuildRequest) -> BuildResponse:
    global assistant
    global is_ready
    global active_retrieval_method

    active_retrieval_method = request.retrieval_method

    assistant = ResearchPaperAssistant(
        papers_folder="data/papers",
        retrieval_method=active_retrieval_method,
    )

    assistant.build()
    is_ready = True

    return BuildResponse(
        status="ready",
        document_count=assistant.document_count,
        chunk_count=assistant.chunk_count,
        retrieval_method=active_retrieval_method,
    )


@app.post("/ask", response_model=QuestionResponse)
def ask_question(request: QuestionRequest) -> QuestionResponse:
    if not is_ready or assistant is None:
        return QuestionResponse(
            question=request.question,
            answer="Assistant is not ready. Call the build endpoint first.",
            retrieval_method=active_retrieval_method,
        )

    answer = assistant.ask(request.question)

    return QuestionResponse(
        question=request.question,
        answer=answer,
        retrieval_method=active_retrieval_method,
    )