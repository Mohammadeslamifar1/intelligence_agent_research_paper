# Research Paper Intelligence Agent

[![Tests](https://github.com/Mohammadeslamifar1/intelligence_agent_research_paper/actions/workflows/tests.yml/badge.svg)](https://github.com/Mohammadeslamifar1/intelligence_agent_research_paper/actions/workflows/tests.yml)

Research Paper Intelligence Agent is an AI engineering project that helps users analyze academic PDF papers. It extracts text from uploaded research papers, splits the content into searchable chunks, retrieves relevant context for a user question, and generates a grounded answer with source chunks.

The goal of this project is to demonstrate practical AI engineering skills, including document processing, retrieval based question answering, API development, testing, and web app deployment.

## Project Status

Current version: working prototype

Implemented features:

1. PDF text extraction
2. Text chunking with overlap
3. TF IDF based retrieval
4. Extractive question answering
5. Interactive command line assistant
6. Streamlit web demo
7. FastAPI backend
8. Unit tests for core pipeline components

## Demo Questions

Example questions the system can answer:

```text
What is the main contribution of this paper?
What data does this paper use?
What physical quantities are included in the catalog?
What are the limitations mentioned in the paper?

```
## Architecture

```text
PDF Papers
    |
    v
PDF Loader
    |
    v
Text Chunker
    |
    v
TF IDF Retrieval Engine
    |
    v
Extractive QA Engine
    |
    v
CLI App, Streamlit App, FastAPI Backend




```
## Project Structure

```text
research_paper_intelligence_agent
    app
        api
            main.py
        generation
            qa_engine.py
        ingestion
            chunker.py
            pdf_loader.py
        retrieval
            search_engine.py
        ui
            streamlit_app.py
        pipeline.py
    data
        papers
    scripts
        ask.py
        test_chunker.py
        test_pdf_loader.py
        test_qa.py
        test_search.py
    tests
        test_pipeline_components.py
    requirements.txt
    README.md

```
## Setup

Create and activate a virtual environment.

For Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1

Install dependencies:
python -m pip install -r requirements.txt

```
## Add Papers

Place one or more PDF research papers inside:

```text
data\papers
```

The command line assistant and FastAPI backend read papers from this folder.

## Run the Command Line Assistant

```powershell
python scripts\ask.py
```

The assistant will build the index and then allow you to ask questions interactively.

## Run the Streamlit Demo

```powershell
streamlit run app\ui\streamlit_app.py
```

Then upload one or more PDF files, build the assistant, and ask questions in the browser.

## Run the FastAPI Backend

```powershell
uvicorn app.api.main:app
```

Open the API documentation in the browser:

```text
http://127.0.0.1:8000/docs
```

Use the endpoints in this order:

```text
GET /health
POST /build
POST /ask
```

Example request body for POST /ask:

```json
{
  "question": "What is the main contribution of this paper?"
}
```

## Run Tests

```powershell
pytest
```

## Current Retrieval Method

The current version uses TF IDF retrieval. This is simple, fast, local, and does not require an API key.

Planned upgrades:

1. Embedding based retrieval
2. Vector database integration
3. Better answer generation with an LLM
4. Paper comparison mode
5. Citation aware answers
6. Docker support
7. GitHub Actions continuous integration

## Resume Description

Built a full stack research paper intelligence agent that extracts text from academic PDFs, chunks documents, retrieves relevant context, answers user questions with source references, and exposes the system through a command line app, Streamlit interface, and FastAPI backend.

Implemented modular Python components, automated tests, and a clean project structure for maintainable AI engineering development.

## Tech Stack

Python

PyMuPDF

Scikit learn

FastAPI

Streamlit

Pydantic

Pytest