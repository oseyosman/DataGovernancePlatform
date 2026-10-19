"""
RAG models - chunked report text for retrieval, and per-query telemetry.
Author: Osman Yildiz
"""
from datetime import datetime
from backend1.app import db


class RagChunk(db.Model):
    """A passage of text extracted from an annual report, used as retrieval context."""
    __tablename__ = 'rag_chunks'

    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False, index=True)
    annual_report_id = db.Column(db.Integer, db.ForeignKey('annual_reports.id'), nullable=False, index=True)
    chunk_index = db.Column(db.Integer, nullable=False)
    page = db.Column(db.Integer, nullable=True)
    text = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<RagChunk {self.id} report={self.annual_report_id} idx={self.chunk_index}>'


class RagQueryLog(db.Model):
    """Operational telemetry for each question asked through the RAG endpoint."""
    __tablename__ = 'rag_query_logs'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    company_id = db.Column(db.Integer, nullable=True)
    question = db.Column(db.String(500), nullable=False)
    abstained = db.Column(db.Boolean, nullable=False, default=False)
    abstain_reason = db.Column(db.String(100), nullable=True)
    num_passages = db.Column(db.Integer, nullable=False, default=0)
    filtered_passages = db.Column(db.Integer, nullable=False, default=0)
    top_score = db.Column(db.Float, nullable=True)
    coverage = db.Column(db.Float, nullable=True)
    latency_ms = db.Column(db.Integer, nullable=False, default=0)
    provider = db.Column(db.String(50), nullable=True)
    model = db.Column(db.String(100), nullable=True)
    input_tokens = db.Column(db.Integer, nullable=False, default=0)
    output_tokens = db.Column(db.Integer, nullable=False, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
