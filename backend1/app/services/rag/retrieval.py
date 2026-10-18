"""BM25 retrieval over report chunks. Pure Python: no model downloads, deterministic."""
import math
import re
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from typing import Dict, Iterable, List, Optional

STOPWORDS = frozenset("""
a an and are as at be been by can do does did for from has have had how i in is it its
of on or our that the their there these this those to was were what when where which
who whom why will with would about into than then they we you your not no any all
""".split())

_TOKEN = re.compile(r'[a-z0-9]+')


def _stem(token: str) -> str:
    """Very light suffix stripping so 'risks' matches 'risk'."""
    if len(token) > 4 and token.endswith('ies'):
        return token[:-3] + 'y'
    if len(token) > 3 and token.endswith('s') and not token.endswith('ss'):
        return token[:-1]
    return token


def tokenize(text: str) -> List[str]:
    return [_stem(t) for t in _TOKEN.findall(text.lower()) if t not in STOPWORDS]


def query_terms(question: str, ignore: Iterable[str] = ()) -> List[str]:
    """Distinct, order-preserving query terms, minus any terms in `ignore`."""
    skip = set(ignore)
    return [t for t in dict.fromkeys(tokenize(question)) if t not in skip]


def coverage(terms: List[str], text: str) -> float:
    """Share of `terms` that appear in `text`."""
    if not terms:
        return 0.0
    present = set(tokenize(text))
    return sum(1 for t in terms if t in present) / len(terms)


@dataclass
class Hit:
    chunk_id: int
    score: float
    coverage: float          # share of distinct query terms present in the chunk
    text: str
    meta: Dict = field(default_factory=dict)


class BM25Index:
    """In-memory BM25 index. docs: iterable of {'id', 'text', 'meta'}."""

    def __init__(self, docs: Iterable[Dict], k1: float = 1.5, b: float = 0.75):
        self.k1, self.b = k1, b
        self.docs: Dict[int, Dict] = {}
        self.tf: Dict[int, Counter] = {}
        self.length: Dict[int, int] = {}
        self.postings: Dict[str, List[int]] = defaultdict(list)
        self.names: Dict[int, set] = {}   # company_id -> tokens of the company name
        for d in docs:
            meta = d.get('meta', {})
            if meta.get('company_id') is not None and meta.get('company') and meta['company_id'] not in self.names:
                self.names[meta['company_id']] = set(tokenize(meta['company']))
            tokens = tokenize(d['text'])
            counts = Counter(tokens)
            self.docs[d['id']] = d
            self.tf[d['id']] = counts
            self.length[d['id']] = len(tokens)
            for term in counts:
                self.postings[term].append(d['id'])
        n = len(self.docs)
        self.avg_len = (sum(self.length.values()) / n) if n else 0.0

    def __len__(self) -> int:
        return len(self.docs)

    def _idf(self, term: str) -> float:
        n, df = len(self.docs), len(self.postings.get(term, ()))
        return math.log(1 + (n - df + 0.5) / (df + 0.5))

    def name_terms(self, company_id: int) -> set:
        """Tokens of a company's name. When a search is already scoped to that company
        the name carries no information, so callers can exclude it from scoring."""
        return set(self.names.get(company_id, ()))

    def search(self, query: str, k: int = 5, filters: Optional[Dict] = None,
               ignore_terms: Iterable[str] = ()) -> List[Hit]:
        terms = query_terms(query, ignore_terms)
        if not terms or not self.docs:
            return []
        candidates = set()
        for t in terms:
            candidates.update(self.postings.get(t, ()))
        scores: Dict[int, float] = {}
        for doc_id in candidates:
            meta = self.docs[doc_id].get('meta', {})
            if filters and any(meta.get(key) != val for key, val in filters.items()):
                continue
            tf, dl = self.tf[doc_id], self.length[doc_id]
            s = 0.0
            for t in terms:
                f = tf.get(t, 0)
                if f:
                    denom = f + self.k1 * (1 - self.b + self.b * dl / (self.avg_len or 1))
                    s += self._idf(t) * f * (self.k1 + 1) / denom
            if s > 0:
                scores[doc_id] = s
        ranked = sorted(scores, key=lambda i: (-scores[i], i))[:k]
        hits = []
        for doc_id in ranked:
            matched = sum(1 for t in terms if self.tf[doc_id].get(t))
            d = self.docs[doc_id]
            hits.append(Hit(doc_id, round(scores[doc_id], 4), matched / len(terms),
                            d['text'], d.get('meta', {})))
        return hits
