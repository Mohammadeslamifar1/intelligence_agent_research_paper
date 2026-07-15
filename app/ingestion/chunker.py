from dataclasses import dataclass


@dataclass
class TextChunk:
    document_name: str
    chunk_id: int
    text: str
    character_count: int


def split_text_into_chunks(
    text: str,
    document_name: str,
    chunk_size: int = 1200,
    overlap: int = 200,
) -> list[TextChunk]:
    if chunk_size <= 0:
        raise ValueError("chunk_size must be greater than zero")

    if overlap < 0:
        raise ValueError("overlap must be zero or greater")

    if overlap >= chunk_size:
        raise ValueError("overlap must be smaller than chunk_size")

    cleaned_text = " ".join(text.split())

    chunks: list[TextChunk] = []
    start = 0
    chunk_id = 1

    while start < len(cleaned_text):
        end = start + chunk_size
        chunk_text = cleaned_text[start:end].strip()

        if chunk_text:
            chunks.append(
                TextChunk(
                    document_name=document_name,
                    chunk_id=chunk_id,
                    text=chunk_text,
                    character_count=len(chunk_text),
                )
            )
            chunk_id += 1

        start = end - overlap

    return chunks


def chunk_documents(
    documents: dict[str, str],
    chunk_size: int = 1200,
    overlap: int = 200,
) -> list[TextChunk]:
    all_chunks: list[TextChunk] = []

    for document_name, text in documents.items():
        document_chunks = split_text_into_chunks(
            text=text,
            document_name=document_name,
            chunk_size=chunk_size,
            overlap=overlap,
        )
        all_chunks.extend(document_chunks)

    return all_chunks