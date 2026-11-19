
import sys
from pathlib import Path

sys.path.insert(
    0,
    str(Path(__file__).resolve().parents[1] / "src")
)

from retrieval import SimulatedRetriever


def test_retriever_starts_empty():
    retriever = SimulatedRetriever(load_samples=False)

    assert len(retriever.documents) == 0


def test_pdf_registration():
    retriever = SimulatedRetriever(load_samples=False)

    pdf_path = Path(__file__).resolve().parents[1] / "docs" / "test.pdf"

    doc_id = retriever.add_pdf(str(pdf_path))

    assert doc_id == "PDF-test"
    assert doc_id in retriever.documents
    assert retriever.documents[doc_id].title == "test.pdf"
    assert "Alder Creek Research LLC" in retriever.documents[doc_id].content



def test_document_removal():
    retriever = SimulatedRetriever(load_samples=False)

    pdf_path = Path(__file__).resolve().parents[1] / "docs" / "test.pdf"

    doc_id = retriever.add_pdf(str(pdf_path))

    assert doc_id in retriever.documents

    del retriever.documents[doc_id]

    assert doc_id not in retriever.documents
    assert len(retriever.documents) == 0

