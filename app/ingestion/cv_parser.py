"""CV parser using pypdfium2."""
from __future__ import annotations

import asyncio
import uuid
from concurrent.futures import ThreadPoolExecutor

import pypdfium2 as pdfium

__all__ = ["parse_cv_pdf", "parse_cv_text"]

def _extract_text_sync(pdf_bytes: bytes) -> str:
    """Extract text from PDF synchronously."""
    pdf = pdfium.PdfDocument(pdf_bytes)
    text_pages = []
    for page in pdf:
        text_page = page.get_textpage()
        text_pages.append(text_page.get_text_range())
    return "\n".join(text_pages)

async def parse_cv_pdf(pdf_bytes: bytes) -> tuple[str, uuid.UUID]:
    """Extract text from a PDF CV."""
    loop = asyncio.get_running_loop()
    with ThreadPoolExecutor() as pool:
        raw_text = await loop.run_in_executor(pool, _extract_text_sync, pdf_bytes)
    
    text = " ".join(raw_text.split())
    document_id = uuid.uuid4()
    return text, document_id

async def parse_cv_text(text: str) -> tuple[str, uuid.UUID]:
    """Parse plain text CV."""
    cleaned_text = " ".join(text.split())
    document_id = uuid.uuid4()
    return cleaned_text, document_id