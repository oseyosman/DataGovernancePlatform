"""Database-backed corpus: build the in-memory BM25 index from stored chunks."""
import threading
from typing import Optional, Tuple

from sqlalchemy import func

from backend1.app import db
from backend1.app.models.annual_report import AnnualReport
from backend1.app.models.company import Company
from backend1.app.models.rag_chunk import RagChunk
from backend1.app.services.rag.retrieval import BM25Index

_lock = threading.Lock()
_cache = {'key': None, 'index': None}


def _fingerprint() -> Tuple[int, int]:
    count, max_id = db.session.query(func.count(RagChunk.id), func.max(RagChunk.id)).one()
    return int(count or 0), int(max_id or 0)


def invalidate_index() -> None:
    with _lock:
        _cache['key'], _cache['index'] = None, None


def get_index() -> BM25Index:
    """Return a cached index, rebuilding only when the chunk table has changed."""
    key = _fingerprint()
    with _lock:
        if _cache['key'] == key and _cache['index'] is not None:
            return _cache['index']
    rows = (db.session.query(RagChunk, AnnualReport.year, Company.name)
            .join(AnnualReport, RagChunk.annual_report_id == AnnualReport.id)
            .join(Company, RagChunk.company_id == Company.id).all())
    docs = [{'id': c.id, 'text': c.text,
             'meta': {'company_id': c.company_id, 'company': name, 'year': year,
                      'page': c.page, 'report_id': c.annual_report_id}}
            for c, year, name in rows]
    index = BM25Index(docs)
    with _lock:
        _cache['key'], _cache['index'] = key, index
    return index
