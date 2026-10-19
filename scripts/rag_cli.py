"""
Command-line access to the RAG pipeline. Run from the repository root.

  python scripts/rag_cli.py ingest-file report.pdf --company "Acme Corp" --year 2024
  python scripts/rag_cli.py ingest-report 12          # download a scraped report by id (allowlisted hosts only)
  python scripts/rag_cli.py ask "How is the board overseeing cybersecurity?" --company-id 1
  python scripts/rag_cli.py stats

ingest-file works offline: download a 10-K PDF (or .txt) yourself and point at it.
Author: Osman Yildiz
"""
import argparse
import os
import sys

sys.path.insert(0, os.getcwd())

from backend1.app import create_app, db  # noqa: E402
from backend1.app.models.annual_report import AnnualReport  # noqa: E402
from backend1.app.models.company import Company  # noqa: E402
from backend1.app.models.rag_chunk import RagChunk  # noqa: E402
from backend1.app.services.rag import answer_question  # noqa: E402
from backend1.app.services.rag.ingest import IngestError, ingest_report, store_pages  # noqa: E402
from backend1.app.services.rag.llm import get_llm_client  # noqa: E402
from backend1.app.services.rag.store import get_index  # noqa: E402


def read_pages(path: str):
    if path.lower().endswith('.pdf'):
        import PyPDF2
        reader = PyPDF2.PdfReader(path)
        return [(p.extract_text() or '') for p in reader.pages]
    with open(path, encoding='utf-8', errors='replace') as f:
        return [f.read()]


def cmd_ingest_file(args):
    pages = read_pages(args.path)
    company = Company.query.filter_by(name=args.company).first()
    if not company:
        company = Company(name=args.company, ticker=args.ticker, source_url=f'local-file://{args.company}')
        db.session.add(company)
        db.session.commit()
    report = AnnualReport.query.filter_by(company_id=company.id, year=args.year).first()
    if not report:
        report = AnnualReport(company_id=company.id, year=args.year, report_type='Annual Report',
                              title=f'{args.company} {args.year} (local file)')
        db.session.add(report)
        db.session.commit()
    count = store_pages(report, pages)
    print(f'Indexed {count} passages from {len(pages)} pages -> company_id={company.id}, report_id={report.id}')
    return 0 if count else 1


def cmd_ingest_report(args):
    report = AnnualReport.query.get(args.report_id)
    if not report:
        print(f'No report with id {args.report_id}')
        return 1
    try:
        print(f'Indexed {ingest_report(report)} passages for report {report.id}')
    except IngestError as exc:
        print(f'Ingest failed: {exc}')
        return 1
    return 0


def cmd_ask(args):
    answer = answer_question(args.question, get_index(), get_llm_client(),
                             company_id=args.company_id, top_k=args.top_k)
    print(answer.answer)
    if answer.abstained:
        print(f'\n(abstained: {answer.reason})')
    for c in answer.citations:
        print(f"\n[{c['n']}] {c['company']} {c['year']}, p.{c['page']}\n    {c['snippet']}")
    m = answer.metrics
    print(f"\nprovider={m['provider']} model={m['model'] or 'n/a'} passages={m['num_passages']} "
          f"latency={m['latency_ms']}ms tokens={m['input_tokens']}/{m['output_tokens']}")
    return 0


def cmd_stats(_args):
    print(f"chunks={RagChunk.query.count()}, indexed terms={len(get_index().postings)}")
    return 0


def main():
    p = argparse.ArgumentParser(description=__doc__.split('\n\n')[0])
    sub = p.add_subparsers(dest='cmd', required=True)
    f = sub.add_parser('ingest-file')
    f.add_argument('path')
    f.add_argument('--company', required=True)
    f.add_argument('--year', type=int, required=True)
    f.add_argument('--ticker')
    f.set_defaults(fn=cmd_ingest_file)
    r = sub.add_parser('ingest-report')
    r.add_argument('report_id', type=int)
    r.set_defaults(fn=cmd_ingest_report)
    a = sub.add_parser('ask')
    a.add_argument('question')
    a.add_argument('--company-id', type=int)
    a.add_argument('--top-k', type=int, default=4)
    a.set_defaults(fn=cmd_ask)
    s = sub.add_parser('stats')
    s.set_defaults(fn=cmd_stats)
    args = p.parse_args()
    with create_app().app_context():
        db.create_all()
        sys.exit(args.fn(args))


if __name__ == '__main__':
    main()
