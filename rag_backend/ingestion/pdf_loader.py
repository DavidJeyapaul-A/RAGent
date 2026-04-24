# rag_backend/ingestion/pdf_loader.py

import fitz  # PyMuPDF
from pathlib import Path
from typing import List, Dict

# ---------------- this is for local testing purposes ----------------
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
# --------------------------------------------------------------------

from rag_backend.utils.logger import get_logger

log = get_logger(__name__)


def extract_text_from_pdf(pdf_path: Path) -> List[Dict]:
    """
    Extracts text and metadata from each page of a PDF.

    Args:
        pdf_path (Path): Path to the PDF file.

    Returns:
        List[Dict]: A list of dicts with keys: page_num, text, metadata
    """
    pages_data = []
    try:
        log.info(f"Opening PDF: {pdf_path}")
        with fitz.open(pdf_path) as doc:
            for page_num, page in enumerate(doc, start=1):
                text = page.get_text()
                blocks = page.get_text("blocks")
                print(f"[DEBUG] Page {page_num} text: {text}")
                print(f"[DEBUG] Page {page_num} blocks: {blocks}")
                metadata = {
                    "file_name": pdf_path.name,
                    "page_num": page_num,
                    "total_pages": len(doc)
                }
                pages_data.append({
                    "text": text,
                    "metadata": metadata
                })
                log.debug(f"Extracted page {page_num}/{len(doc)} from {pdf_path.name}")
    except Exception as e:
        log.error(f"Failed to process PDF {pdf_path}: {e}")
        raise

    return pages_data


pdf_path = Path("/home/david/project/RAGent/rag_backend/tests/data/sample.pdf")

try:
    pages = extract_text_from_pdf(pdf_path)
    print("Extracted Pages:")
    for page in pages:
        print(f"--- Page {page['metadata']['page_num']} ---")
        print(page["text"])
except Exception as e:
    print(f"Error reading PDF: {e}")