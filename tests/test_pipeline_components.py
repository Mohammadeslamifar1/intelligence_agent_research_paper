from pathlib import Path

import fitz

from app.generation.qa_engine import ExtractiveQAEngine
from app.ingestion.chunker import chunk_documents, split_text_into_chunks
from app.ingestion.pdf_loader import extract_text_from_pdf
from app.retrieval.search_engine import TfidfSearchEngine


def create_sample_pdf(path: Path, text: str) -> None:
    document = fitz.open()
    page = document.new_page()
    page.insert_text((72, 72), text)
    document.save(path)
    document.close()


def test_extract_text_from_pdf(tmp_path: Path) -> None:
    pdf_path = tmp_path / "sample.pdf"
    sample_text = "This paper presents a research paper intelligence agent."

    create_sample_pdf(pdf_path, sample_text)

    extracted_text = extract_text_from_pdf(pdf_path)

    assert "research paper intelligence agent" in extracted_text


def test_split_text_into_chunks() -> None:
    text = "Artificial intelligence research " * 100

    chunks = split_text_into_chunks(
        text=text,
        document_name="sample.pdf",
        chunk_size=200,
        overlap=50,
    )

    assert len(chunks) > 1
    assert chunks[0].document_name == "sample.pdf"
    assert chunks[0].chunk_id == 1
    assert chunks[0].character_count > 0


def test_chunk_documents() -> None:
    documents = {
        "paper_one.pdf": "Machine learning research " * 80,
        "paper_two.pdf": "Natural language processing research " * 80,
    }

    chunks = chunk_documents(documents, chunk_size=200, overlap=50)

    document_names = {chunk.document_name for chunk in chunks}

    assert len(chunks) > 2
    assert "paper_one.pdf" in document_names
    assert "paper_two.pdf" in document_names


def test_search_engine_returns_relevant_result() -> None:
    documents = {
        "sample.pdf": (
            "This paper introduces a research paper intelligence agent. "
            "The system extracts text from academic PDFs and answers questions."
        )
    }

    chunks = chunk_documents(documents, chunk_size=120, overlap=20)

    search_engine = TfidfSearchEngine()
    search_engine.build_index(chunks)

    results = search_engine.search(
        query="What does the system extract from PDFs?",
        top_k=2,
        min_score=0.01,
    )

    assert len(results) > 0
    assert "PDFs" in results[0].text or "academic" in results[0].text


def test_qa_engine_returns_answer() -> None:
    documents = {
        "sample.pdf": (
            "The main contribution of this paper is a research paper intelligence agent. "
            "It extracts text from academic PDFs and answers questions using retrieved context."
        )
    }

    chunks = chunk_documents(documents, chunk_size=200, overlap=50)

    search_engine = TfidfSearchEngine()
    search_engine.build_index(chunks)

    results = search_engine.search(
        query="What is the main contribution of this paper?",
        top_k=3,
        min_score=0.01,
    )

    qa_engine = ExtractiveQAEngine()
    answer = qa_engine.answer_question(
        question="What is the main contribution of this paper?",
        search_results=results,
    )

    assert answer.answer
    assert len(answer.sources) > 0