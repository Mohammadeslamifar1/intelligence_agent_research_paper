import sys
from pathlib import Path
import tempfile


import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[2]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.generation.comparison_generator import PaperComparisonGenerator
from app.generation.qa_engine import ExtractiveQAEngine
from app.generation.report_generator import PaperReportGenerator
from app.ingestion.chunker import chunk_documents
from app.ingestion.pdf_loader import extract_text_from_pdf
from app.retrieval.search_engine import TfidfSearchEngine
from app.retrieval.embedding_search_engine import EmbeddingSearchEngine


st.set_page_config(
    page_title="Research Paper Intelligence Agent",
    page_icon="📄",
    layout="wide",
)

st.title("Research Paper Intelligence Agent")
st.write(
    "Upload research papers, build a searchable index, and ask questions grounded in the paper content."
)

if "search_engine" not in st.session_state:
    st.session_state.search_engine = None

if "qa_engine" not in st.session_state:
    st.session_state.qa_engine = None

if "document_count" not in st.session_state:
    st.session_state.document_count = 0

if "chunk_count" not in st.session_state:
    st.session_state.chunk_count = 0
    
if "retrieval_method" not in st.session_state:
    st.session_state.retrieval_method = "TF IDF keyword search"


uploaded_files = st.file_uploader(
    "Upload PDF research papers",
    type=["pdf"],
    accept_multiple_files=True,
)

retrieval_method = st.selectbox(
    "Choose retrieval method",
    options=[
        "TF IDF keyword search",
        "Semantic embedding search",
    ],
)

build_button = st.button("Build assistant")

if build_button:
    if not uploaded_files:
        st.warning("Please upload at least one PDF file.")
    else:
        with st.spinner("Reading papers and building the search index..."):
            documents = {}

            with tempfile.TemporaryDirectory() as temporary_folder:
                temporary_path = Path(temporary_folder)

                for uploaded_file in uploaded_files:
                    pdf_path = temporary_path / uploaded_file.name
                    pdf_path.write_bytes(uploaded_file.getbuffer())

                    documents[uploaded_file.name] = extract_text_from_pdf(pdf_path)

            chunks = chunk_documents(documents)

            if retrieval_method == "Semantic embedding search":
                search_engine = EmbeddingSearchEngine()
            else:
                search_engine = TfidfSearchEngine()

            search_engine.build_index(chunks)
            

            st.session_state.search_engine = search_engine
            st.session_state.qa_engine = ExtractiveQAEngine()
            st.session_state.document_count = len(documents)
            st.session_state.chunk_count = len(chunks)
            st.session_state.retrieval_method = retrieval_method

        st.success(
            f"Assistant ready using {retrieval_method}. Loaded {st.session_state.document_count} paper file and created {st.session_state.chunk_count} chunks."
        )


st.divider()

st.subheader("Ask a question")

question = st.text_input(
    "Question",
    placeholder="What is the main contribution of this paper?",
)

ask_button = st.button("Ask")

if ask_button:
    if st.session_state.search_engine is None:
        st.warning("Build the assistant first.")
    elif not question.strip():
        st.warning("Please enter a question.")
    else:
        search_results = st.session_state.search_engine.search(
            query=question,
            top_k=5,
            min_score=0.02,
        )

        answer = st.session_state.qa_engine.answer_question(
            question=question,
            search_results=search_results,
        )

        st.subheader("Answer")
        st.write(answer.answer)

        st.subheader("Sources")

        if not answer.sources:
            st.write("No sources found.")
        else:
            for source in answer.sources:
                st.write(
                    f"{source.document_name} | chunk {source.chunk_id} | score {source.score:.4f}"
                )
                
st.divider()

st.subheader("Generate Paper Report")

report_button = st.button("Generate Report")

if report_button:
    if st.session_state.search_engine is None:
        st.warning("Build the assistant first.")
    else:
        if st.session_state.retrieval_method == "Semantic embedding search":
            min_score = 0.20
        else:
            min_score = 0.02

        report_generator = PaperReportGenerator(
            search_engine=st.session_state.search_engine,
            qa_engine=st.session_state.qa_engine,
            min_score=min_score,
        )

        with st.spinner("Generating paper report..."):
            sections = report_generator.generate()
            markdown_report = report_generator.to_markdown(sections)

        st.subheader("Paper Intelligence Report")
        st.markdown(markdown_report)

        st.download_button(
            label="Download Report",
            data=markdown_report,
            file_name="paper_report.md",
            mime="text/markdown",
        )
        
st.divider()

st.subheader("Compare Uploaded Papers")

comparison_button = st.button("Generate Comparison Report")

if comparison_button:
    if st.session_state.search_engine is None:
        st.warning("Build the assistant first.")
    elif st.session_state.document_count < 2:
        st.warning("Upload at least two papers to generate a comparison report.")
    else:
        if st.session_state.retrieval_method == "Semantic embedding search":
            min_score = 0.20
        else:
            min_score = 0.02

        comparison_generator = PaperComparisonGenerator(
            search_engine=st.session_state.search_engine,
            qa_engine=st.session_state.qa_engine,
            min_score=min_score,
        )

        with st.spinner("Generating paper comparison report..."):
            sections = comparison_generator.generate()
            markdown_comparison = comparison_generator.to_markdown(sections)

        st.subheader("Paper Comparison Report")
        st.markdown(markdown_comparison)

        st.download_button(
            label="Download Comparison Report",
            data=markdown_comparison,
            file_name="paper_comparison_report.md",
            mime="text/markdown",
        )