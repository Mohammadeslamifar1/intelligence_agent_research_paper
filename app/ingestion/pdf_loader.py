from pathlib import Path
import fitz


def extract_text_from_pdf(pdf_path: str | Path) -> str:
    path = Path(pdf_path)

    if not path.exists():
        raise FileNotFoundError(f"PDF file not found: {path}")

    if path.suffix.lower() != ".pdf":
        raise ValueError(f"Expected a PDF file, got: {path.suffix}")

    pages_text: list[str] = []

    with fitz.open(path) as document:
        for page_number, page in enumerate(document, start=1):
            text = page.get_text("text").strip()

            if text:
                pages_text.append(
                    f"\n\n[Page {page_number}]\n{text}"
                )

    return "\n".join(pages_text)


def load_pdfs_from_folder(folder_path: str | Path) -> dict[str, str]:
    folder = Path(folder_path)

    if not folder.exists():
        raise FileNotFoundError(f"Folder not found: {folder}")

    pdf_files = sorted(folder.glob("*.pdf"))

    if not pdf_files:
        raise FileNotFoundError(
            f"No PDF files found in: {folder}. Add at least one PDF first."
        )

    extracted_documents: dict[str, str] = {}

    for pdf_file in pdf_files:
        extracted_documents[pdf_file.name] = extract_text_from_pdf(pdf_file)

    return extracted_documents