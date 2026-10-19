"""
RAG Routes - grounded question answering over ingested annual reports
Author: Osman Yildiz
"""
import logging
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import func

from backend1.app import db
from backend1.app.models.activity import Activity
from backend1.app.models.annual_report import AnnualReport
from backend1.app.models.rag_chunk import RagChunk, RagQueryLog
from backend1.app.models.user import User
from backend1.app.routes.admin import admin_required
from backend1.app.services.rag import answer_question
from backend1.app.services.rag.ingest import IngestError, ingest_report
from backend1.app.services.rag.llm import RagConfigError, get_llm_client
from backend1.app.services.rag.store import get_index

logger = logging.getLogger(__name__)
bp = Blueprint('rag', __name__, url_prefix='/api/rag')

MAX_TOP_K = 8


def _is_int(value) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def _log_query(user_id, company_id, answer) -> None:
    """Persist per-query telemetry. Never let logging break the response."""
    m = answer.metrics
    try:
        db.session.add(RagQueryLog(
            user_id=user_id, company_id=company_id, question=answer.question[:500],
            abstained=answer.abstained, abstain_reason=answer.reason,
            num_passages=m.get('num_passages', 0), filtered_passages=m.get('filtered_passages', 0),
            top_score=m.get('top_score'), coverage=m.get('coverage'),
            latency_ms=m.get('latency_ms', 0), provider=m.get('provider'), model=m.get('model'),
            input_tokens=m.get('input_tokens', 0), output_tokens=m.get('output_tokens', 0)))
        db.session.commit()
    except Exception:
        db.session.rollback()
        logger.exception('Could not write RAG query log')


@bp.route('/ask', methods=['POST'])
@jwt_required()
def ask():
    """Answer a question using only passages retrieved from ingested reports."""
    data = request.get_json(silent=True) or {}
    question = data.get('question')
    company_id = data.get('company_id')
    top_k = data.get('top_k', 4)

    if not isinstance(question, str) or not question.strip():
        return jsonify({'error': 'question is required'}), 400
    if company_id is not None and not _is_int(company_id):
        return jsonify({'error': 'company_id must be an integer'}), 400
    if not _is_int(top_k) or not 1 <= top_k <= MAX_TOP_K:
        return jsonify({'error': f'top_k must be an integer between 1 and {MAX_TOP_K}'}), 400

    user = User.query.get(get_jwt_identity())
    if not user:
        return jsonify({'error': 'User not found'}), 404

    try:
        client = get_llm_client()
        answer = answer_question(question, get_index(), client, company_id=company_id, top_k=top_k)
    except ValueError as exc:  # validation messages come from our own code
        return jsonify({'error': str(exc)}), 400
    except RagConfigError:
        logger.exception('RAG provider misconfigured')
        return jsonify({'error': 'Question answering is not configured on this server'}), 503
    except Exception:
        logger.exception('RAG answer failed')
        return jsonify({'error': 'The answer service is temporarily unavailable'}), 502

    _log_query(user.id, company_id, answer)
    return jsonify(answer.to_dict()), 200


@bp.route('/ingest/<int:report_id>', methods=['POST'])
@admin_required
def ingest(report_id):
    """Download, chunk and index one annual report (admin only)."""
    report = AnnualReport.query.get(report_id)
    if not report:
        return jsonify({'error': 'Report not found'}), 404
    try:
        count = ingest_report(report)
    except IngestError as exc:
        return jsonify({'error': str(exc)}), 400
    except Exception:
        logger.exception('Unexpected ingest failure for report %s', report_id)
        return jsonify({'error': 'Ingest failed'}), 500

    try:
        db.session.add(Activity(user_id=int(get_jwt_identity()), action='rag_ingest',
                                table_name='annual_reports', record_id=report.id,
                                description=f'Indexed {count} passages', ip_address=request.remote_addr))
        db.session.commit()
    except Exception:
        db.session.rollback()
    return jsonify({'report_id': report.id, 'chunks': count}), 200


@bp.route('/stats', methods=['GET'])
@admin_required
def stats():
    """Corpus size and recent query telemetry (admin only)."""
    recent = (RagQueryLog.query.order_by(RagQueryLog.created_at.desc()).limit(500).all())
    latencies = sorted(r.latency_ms for r in recent)
    n = len(recent)
    p95 = latencies[min(n - 1, int(n * 0.95))] if n else None
    return jsonify({
        'corpus': {'chunks': RagChunk.query.count(),
                   'reports': db.session.query(func.count(func.distinct(RagChunk.annual_report_id))).scalar() or 0},
        'recent_queries': {
            'count': n,
            'abstain_rate': round(sum(1 for r in recent if r.abstained) / n, 3) if n else None,
            'avg_latency_ms': round(sum(latencies) / n) if n else None,
            'p95_latency_ms': p95,
            'input_tokens': sum(r.input_tokens for r in recent),
            'output_tokens': sum(r.output_tokens for r in recent),
        },
    }), 200
