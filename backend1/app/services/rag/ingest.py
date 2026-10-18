"""Ingest an annual report PDF into retrieval chunks."""
import io
import logging
import os
from typing import List
from urllib.parse import urlparse

import requests

from backend1.app import db
from backend1.app.models.annual_report import AnnualReport
from backend1.app.models.rag_chunk import RagChunk
from backend1.app.services.rag.chunking import chunk_pages
from backend1.app.services.rag.store import invalidate_index

logger = logging.getLogger(__name__)

MAX_PDF_BYTES = 40 * 1024 * 1024
MAX_PAGES = 150


class IngestError(Exception):
    pass


def allowed_hosts() -> List[str]:
    raw = os.environ.get('RAG_ALLOWED_HOSTS', 'annualreports.com')
    return [h.strip().lower() for h in raw.split(',') if h.strip()]


def check_url(url: str) -> None:
    """Only fetch https URLs on an allowlisted host (prevents server-side request forgery)."""
    parsed = urlparse(url or '')
    host = (parsed.hostname or '').lower()
    if parsed.scheme != 'https' or not any(host == h or host.endswith('.' + h) for h in allowed_hosts()):
        raise IngestError('Report URL is not on an allowed host')


def fetch_pdf_pages(url: str) -> List[str]:
    import PyPDF2
    check_url(url)
    resp = requests.get(url, timeout=30, stream=True, allow_redirects=False,
                        headers={'User-Agent': 'DataGovernancePlatform/1.0'})
    resp.raise_for_status()
    content = resp.raw.read(MAX_PDF_BYTES + 1, decode_content=True)
    if len(content) > MAX_PDF_BYTES:
        raise IngestError('PDF is too large to ingest')
    reader = PyPDF2.PdfReader(io.BytesIO(content))
    return [(reader.pages[i].extract_text() or '') for i in range(min(len(reader.pages), MAX_PAGES))]


def store_pages(report: AnnualReport, pages: List[str]) -> int:
    """Replace the report's chunks with freshly chunked pages (idempotent)."""
    RagChunk.query.filter_by(annual_report_id=report.id).delete()
    chunks = chunk_pages(pages)
    for i, c in enumerate(chunks):
        db.session.add(RagChunk(company_id=report.company_id, annual_report_id=report.id,
                                chunk_index=i, page=c['page'], text=c['text']))
    db.session.commit()
    invalidate_index()
    return len(chunks)


def ingest_report(report: AnnualReport) -> int:
    if not report.pdf_url:
        raise IngestError('Report has no PDF URL')
    try:
        pages = fetch_pdf_pages(report.pdf_url)
    except IngestError:
        raise
    except Exception as exc:
        logger.error('Ingest failed for report %s: %s', report.id, exc)
        raise IngestError('Could not download or read the PDF') from exc
    count = store_pages(report, pages)
    if count == 0:
        raise IngestError('No extractable text found (the PDF may be scanned images)')
    return count
