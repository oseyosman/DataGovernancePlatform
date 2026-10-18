"""
RAG pipeline: validate -> retrieve -> sanitize -> generate -> verify citations.

Guardrails
  * question length cap and empty-question check
  * abstain without calling the model when retrieval evidence is weak
  * drop sentences that look like prompt injection before they reach the model
  * require at least one valid [n] citation, otherwise abstain
"""
import os
import re
import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional

from backend1.app.services.rag.chunking import split_sentences
from backend1.app.services.rag.llm import LLMClient
from backend1.app.services.rag.prompts import INSUFFICIENT
from backend1.app.services.rag.retrieval import BM25Index, coverage, query_terms

MAX_QUESTION_CHARS = 500
DEFAULT_TOP_K = 4
SNIPPET_CHARS = 240


def min_coverage() -> float:
    try:
        return float(os.environ.get('RAG_MIN_COVERAGE', '0.5'))
    except ValueError:
        return 0.5


_INJECTION = re.compile(
    r'(ignore|disregard|forget|override)\s+(all\s+|any\s+|the\s+)?(previous|prior|above|earlier|system)\b'
    r'|\bsystem\s+prompt\b|\byou\s+are\s+now\b|\bnew\s+instructions?\b|\bact\s+as\b'
    r'|\breveal\s+(your|the)\s+(rules|instructions|prompt)\b',
    re.IGNORECASE)


def sanitize_text(text: str):
    """Remove sentences that look like instructions aimed at the model. Returns (text, removed_count)."""
    kept, removed = [], 0
    for sentence in split_sentences(text):
        if _INJECTION.search(sentence):
            removed += 1
        else:
            kept.append(sentence)
    return ' '.join(kept), removed


@dataclass
class RagAnswer:
    question: str
    answer: str
    abstained: bool
    reason: Optional[str] = None
    citations: List[Dict] = field(default_factory=list)
    metrics: Dict = field(default_factory=dict)

    def to_dict(self) -> Dict:
        return {'question': self.question, 'answer': self.answer, 'abstained': self.abstained,
                'reason': self.reason, 'citations': self.citations, 'metrics': self.metrics}


def _abstain(question, reason, metrics, start) -> RagAnswer:
    metrics['latency_ms'] = int((time.perf_counter() - start) * 1000)
    return RagAnswer(question, 'I could not find enough supporting evidence in the indexed reports to answer that.',
                     True, reason, [], metrics)


def answer_question(question: str, index: BM25Index, client: LLMClient,
                    company_id: Optional[int] = None, top_k: int = DEFAULT_TOP_K) -> RagAnswer:
    start = time.perf_counter()
    question = (question or '').strip()
    metrics = {'provider': client.provider, 'model': '', 'num_passages': 0, 'filtered_passages': 0,
               'top_score': None, 'coverage': None, 'input_tokens': 0, 'output_tokens': 0, 'latency_ms': 0}
    if not question:
        raise ValueError('question is required')
    if len(question) > MAX_QUESTION_CHARS:
        raise ValueError(f'question must be at most {MAX_QUESTION_CHARS} characters')

    filters = {'company_id': company_id} if company_id is not None else None
    # A company filter already scopes the search, so the company's name adds no evidence.
    ignore = index.name_terms(company_id) if company_id is not None else set()
    terms = query_terms(question, ignore)
    hits = index.search(question, k=top_k, filters=filters, ignore_terms=ignore)
    if not hits:
        return _abstain(question, 'no_matching_passages', metrics, start)
    metrics['top_score'] = hits[0].score

    passages: List[Dict] = []
    for hit in hits:
        clean, removed = sanitize_text(hit.text)
        metrics['filtered_passages'] += removed
        if not clean:
            continue
        passages.append({'n': len(passages) + 1, 'chunk_id': hit.chunk_id, 'text': clean,
                         'coverage': coverage(terms, clean),
                         'company': hit.meta.get('company'), 'year': hit.meta.get('year'),
                         'page': hit.meta.get('page'), 'report_id': hit.meta.get('report_id')})
    metrics['num_passages'] = len(passages)
    if not passages:
        return _abstain(question, 'all_passages_filtered', metrics, start)

    # Judge evidence on the text the model will actually see. Measuring before sanitizing
    # let a question match words inside a planted instruction and pass the gate.
    best_coverage = max(p['coverage'] for p in passages)
    metrics['coverage'] = round(best_coverage, 3)
    if best_coverage < min_coverage():
        return _abstain(question, 'weak_evidence', metrics, start)

    response = client.generate(question, passages)
    metrics.update(model=response.model, input_tokens=response.input_tokens,
                   output_tokens=response.output_tokens)
    text = response.text.strip()
    if not text or INSUFFICIENT in text:
        return _abstain(question, 'model_declined', metrics, start)

    cited = [int(n) for n in re.findall(r'\[(\d+)\]', text)]
    valid = sorted({n for n in cited if 1 <= n <= len(passages)})
    if not valid:
        return _abstain(question, 'no_valid_citation', metrics, start)

    by_n = {p['n']: p for p in passages}
    citations = [{'n': n, 'chunk_id': by_n[n]['chunk_id'], 'company': by_n[n]['company'],
                  'year': by_n[n]['year'], 'page': by_n[n]['page'], 'report_id': by_n[n]['report_id'],
                  'snippet': by_n[n]['text'][:SNIPPET_CHARS]} for n in valid]
    metrics['latency_ms'] = int((time.perf_counter() - start) * 1000)
    return RagAnswer(question, text, False, None, citations, metrics)
