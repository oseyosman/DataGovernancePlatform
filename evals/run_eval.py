"""
Evaluation harness for the RAG pipeline.

    python -m evals.run_eval                       # synthetic fixture corpus, offline
    python -m evals.run_eval --provider anthropic  # same questions, real model (needs ANTHROPIC_API_KEY)
    python -m evals.run_eval --corpus db --questions my_questions.json   # your ingested reports

What is measured (per question, then aggregated and broken down by category):
  retrieval     recall@k and MRR: did a relevant passage appear in the top-k hits?
  answers       answer_accuracy: required strings present, forbidden strings absent
  citations     citation_precision: every cited passage is a relevant one
  abstention    on unanswerable questions, did the system decline?
  safety        injection_leak_rate: did text from a planted instruction reach the answer?
  operations    latency (avg / p95) and token counts

A question's relevant passages are given by "gold_chunk_ids" (fixture corpus) or by
"relevant_phrases" (any retrieved passage containing one of the phrases; use this for
real data where chunk ids are not known in advance).

Answer correctness is a string check, which is strict for fluent model output and a
poor fit for paraphrased answers. Treat it as a regression signal, not a final grade.
Author: Osman Yildiz
"""
import argparse
import json
import os
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend1.app.services.rag.llm import LLMClient, get_llm_client  # noqa: E402
from backend1.app.services.rag.pipeline import answer_question  # noqa: E402
from backend1.app.services.rag.retrieval import BM25Index  # noqa: E402

FIXTURES = Path(__file__).resolve().parent / 'fixtures'
RESULTS = Path(__file__).resolve().parent / 'results'


def load_fixture_index() -> BM25Index:
    data = json.loads((FIXTURES / 'corpus.json').read_text())
    names = {c['id']: (c['name'], c['year']) for c in data['companies']}
    docs = []
    for p in data['passages']:
        name, year = names[p['company_id']]
        docs.append({'id': p['id'], 'text': p['text'],
                     'meta': {'company_id': p['company_id'], 'company': name, 'year': year,
                              'page': p['page'], 'report_id': p['company_id']}})
    return BM25Index(docs)


def load_db_index() -> BM25Index:
    from backend1.app import create_app
    from backend1.app.services.rag.store import get_index
    app = create_app()
    ctx = app.app_context()
    ctx.push()
    return get_index()


def is_relevant(question: Dict, chunk_id: int, text: str) -> bool:
    if question.get('gold_chunk_ids'):
        return chunk_id in set(question['gold_chunk_ids'])
    phrases = [p.lower() for p in question.get('relevant_phrases', [])]
    return any(p in text.lower() for p in phrases)


def evaluate_question(q: Dict, index: BM25Index, client: LLMClient, k: int) -> Dict:
    company_id = q.get('company_id')
    filters = {'company_id': company_id} if company_id is not None else None
    hits = index.search(q['question'], k=k, filters=filters)
    rank = next((i for i, h in enumerate(hits, 1) if is_relevant(q, h.chunk_id, h.text)), None)

    ans = answer_question(q['question'], index, client, company_id=company_id, top_k=k)
    text_l = ans.answer.lower()
    cited = [c['chunk_id'] for c in ans.citations]
    texts = {h.chunk_id: h.text for h in hits}

    row = {
        'id': q['id'], 'category': q.get('category', 'uncategorized'), 'question': q['question'],
        'should_abstain': bool(q.get('should_abstain')), 'abstained': ans.abstained,
        'abstain_reason': ans.reason, 'retrieved_ids': [h.chunk_id for h in hits],
        'first_relevant_rank': rank, 'cited_ids': cited, 'answer': ans.answer,
        'latency_ms': ans.metrics.get('latency_ms', 0),
        'input_tokens': ans.metrics.get('input_tokens', 0),
        'output_tokens': ans.metrics.get('output_tokens', 0),
        'filtered_passages': ans.metrics.get('filtered_passages', 0),
    }
    if not row['should_abstain']:
        required = [s.lower() for s in q.get('answer_contains', [])]
        forbidden = [s.lower() for s in q.get('answer_must_not_contain', [])]
        row['correct'] = (not ans.abstained and all(s in text_l for s in required)
                          and not any(s in text_l for s in forbidden))
        row['citations_relevant'] = (bool(cited) and all(is_relevant(q, c, texts.get(c, '')) for c in cited)
                                     ) if not ans.abstained else None
    if q.get('answer_must_not_contain'):
        row['leaked'] = any(s.lower() in text_l for s in q['answer_must_not_contain'])
    return row


def _rate(num: int, den: int) -> Optional[float]:
    return round(num / den, 3) if den else None


def aggregate(rows: List[Dict], k: int) -> Dict:
    answerable = [r for r in rows if not r['should_abstain']]
    unanswerable = [r for r in rows if r['should_abstain']]
    answered = [r for r in answerable if not r['abstained']]
    probes = [r for r in rows if 'leaked' in r]
    lat = sorted(r['latency_ms'] for r in rows)

    def block(rs):
        a = [r for r in rs if not r['should_abstain']]
        return {
            'n': len(rs),
            'recall_at_k': _rate(sum(1 for r in a if r['first_relevant_rank']), len(a)),
            'answer_accuracy': _rate(sum(1 for r in a if r['correct']), len(a)),
            'abstained': sum(1 for r in rs if r['abstained']),
        }

    by_cat = defaultdict(list)
    for r in rows:
        by_cat[r['category']].append(r)

    return {
        'k': k,
        'questions': len(rows), 'answerable': len(answerable), 'unanswerable': len(unanswerable),
        'recall_at_k': _rate(sum(1 for r in answerable if r['first_relevant_rank']), len(answerable)),
        'mrr': round(sum(1 / r['first_relevant_rank'] for r in answerable if r['first_relevant_rank'])
                     / len(answerable), 3) if answerable else None,
        'answer_accuracy': _rate(sum(1 for r in answerable if r['correct']), len(answerable)),
        'false_abstain_rate': _rate(sum(1 for r in answerable if r['abstained']), len(answerable)),
        'citation_precision': _rate(sum(1 for r in answered if r['citations_relevant']), len(answered)),
        'correct_abstain_rate': _rate(sum(1 for r in unanswerable if r['abstained']), len(unanswerable)),
        'injection_leak_rate': _rate(sum(1 for r in probes if r['leaked']), len(probes)),
        'injection_passages_filtered': sum(r['filtered_passages'] for r in rows),
        'latency_ms_avg': round(sum(lat) / len(lat), 2) if lat else None,
        'latency_ms_p95': lat[min(len(lat) - 1, int(len(lat) * 0.95))] if lat else None,
        'input_tokens': sum(r['input_tokens'] for r in rows),
        'output_tokens': sum(r['output_tokens'] for r in rows),
        'by_category': {c: block(rs) for c, rs in sorted(by_cat.items())},
    }


def render_markdown(meta: Dict, summary: Dict, rows: List[Dict]) -> str:
    def pct(v):
        return 'n/a' if v is None else f'{v * 100:.0f}%'
    lines = [
        '# RAG evaluation report', '',
        f"- Corpus: `{meta['corpus']}`  |  Provider: `{meta['provider']}`  |  k = {summary['k']}",
        f"- Questions: {summary['questions']} ({summary['answerable']} answerable, {summary['unanswerable']} unanswerable)",
        f"- Generated: {meta['generated_at']}", '',
        '| Metric | Value |', '| --- | --- |',
        f"| Retrieval recall@{summary['k']} | {pct(summary['recall_at_k'])} |",
        f"| Retrieval MRR | {summary['mrr']} |",
        f"| Answer accuracy (string check) | {pct(summary['answer_accuracy'])} |",
        f"| False abstentions | {pct(summary['false_abstain_rate'])} |",
        f"| Citation precision | {pct(summary['citation_precision'])} |",
        f"| Correct abstention on unanswerable | {pct(summary['correct_abstain_rate'])} |",
        f"| Injection leak rate | {pct(summary['injection_leak_rate'])} |",
        f"| Latency avg / p95 (ms) | {summary['latency_ms_avg']} / {summary['latency_ms_p95']} |",
        f"| Tokens in / out | {summary['input_tokens']} / {summary['output_tokens']} |", '',
        '## By category', '', '| Category | n | recall@k | accuracy | abstained |', '| --- | --- | --- | --- | --- |']
    for cat, b in summary['by_category'].items():
        lines.append(f"| {cat} | {b['n']} | {pct(b['recall_at_k'])} | {pct(b['answer_accuracy'])} | {b['abstained']} |")
    failures = [r for r in rows if (not r['should_abstain'] and not r['correct'])
                or (r['should_abstain'] and not r['abstained'])]
    lines += ['', f'## Failures ({len(failures)})', '']
    if failures:
        lines += ['| id | category | question | outcome |', '| --- | --- | --- | --- |']
        for r in failures:
            if r['should_abstain']:
                outcome = 'should have abstained'
            elif r['abstained']:
                outcome = f"abstained ({r['abstain_reason']}); relevant rank: {r['first_relevant_rank']}"
            else:
                outcome = f"wrong answer; relevant rank: {r['first_relevant_rank']}"
            lines.append(f"| {r['id']} | {r['category']} | {r['question']} | {outcome} |")
    else:
        lines.append('None.')
    return '\n'.join(lines) + '\n'


THRESHOLD_ARGS = {
    'min_recall': ('recall_at_k', '>='), 'min_accuracy': ('answer_accuracy', '>='),
    'min_abstain': ('correct_abstain_rate', '>='), 'max_leak': ('injection_leak_rate', '<='),
    'min_citation_precision': ('citation_precision', '>='),
}


def check_thresholds(summary: Dict, args) -> List[str]:
    failed = []
    for arg, (metric, op) in THRESHOLD_ARGS.items():
        limit = getattr(args, arg)
        value = summary.get(metric)
        if limit is None:
            continue
        if value is None or (op == '>=' and value < limit) or (op == '<=' and value > limit):
            failed.append(f'{metric} = {value} (required {op} {limit})')
    return failed


def run(args) -> int:
    if args.provider:
        os.environ['RAG_LLM_PROVIDER'] = args.provider
    if args.model:
        os.environ['RAG_LLM_MODEL'] = args.model
    client = get_llm_client()
    index = load_fixture_index() if args.corpus == 'fixtures' else load_db_index()
    qpath = Path(args.questions) if args.questions else FIXTURES / 'questions.json'
    questions = json.loads(qpath.read_text())['questions']

    rows = [evaluate_question(q, index, client, args.k) for q in questions]
    summary = aggregate(rows, args.k)
    meta = {'corpus': args.corpus, 'questions_file': str(qpath), 'provider': client.provider,
            'model': getattr(client, 'model', '') or 'n/a',
            'generated_at': datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}

    RESULTS.mkdir(exist_ok=True)
    (RESULTS / f'{args.name}.json').write_text(json.dumps({'meta': meta, 'summary': summary, 'rows': rows}, indent=2))
    report = render_markdown(meta, summary, rows)
    (RESULTS / f'{args.name}.md').write_text(report)
    print(report)

    failed = check_thresholds(summary, args)
    if failed:
        print('THRESHOLD FAILURES:\n  ' + '\n  '.join(failed))
        return 1
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description=__doc__.split('\n\n')[0])
    p.add_argument('--corpus', choices=['fixtures', 'db'], default='fixtures')
    p.add_argument('--questions', help='Path to a questions JSON file (default: bundled fixture questions)')
    p.add_argument('--provider', choices=['extractive', 'anthropic'], help='Overrides RAG_LLM_PROVIDER')
    p.add_argument('--model', help='Overrides RAG_LLM_MODEL')
    p.add_argument('-k', type=int, default=4, help='Passages retrieved per question')
    p.add_argument('--name', default='latest', help='Output file stem under evals/results/')
    p.add_argument('--min-recall', type=float)
    p.add_argument('--min-accuracy', type=float)
    p.add_argument('--min-abstain', type=float)
    p.add_argument('--min-citation-precision', type=float)
    p.add_argument('--max-leak', type=float)
    return p


if __name__ == '__main__':
    sys.exit(run(build_parser().parse_args()))
