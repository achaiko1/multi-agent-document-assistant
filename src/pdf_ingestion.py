
from pathlib import Path
import pymupdf


def extract_pdf_text(file_path: str) -> list[dict]:
    """
    Extract text from a PDF, preserving page numbers.

    Args:
        file_path: Path to a PDF document.

    Returns:
        A list containing page numbers and extracted text.
    """
    path = Path(file_path)

    if not path.is_file():
        raise FileNotFoundError(f"PDF not found: {file_path}")

    if path.suffix.lower() != ".pdf":
        raise ValueError("File must be a PDF")

    pages = []

    with pymupdf.open(path) as document:
        for page_number, page in enumerate(document, start=1):
            text = page.get_text("text").strip()

            if text:
                pages.append({
                    "page_number": page_number,
                    "text": text
                })

    return pages
