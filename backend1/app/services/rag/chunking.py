"""Split report text into overlapping passages for retrieval."""
import re
from typing import Dict, List

_WS = re.compile(r'[ \t]+')
_SENTENCE_END = re.compile(r'(?<=[.!?])\s+')


def normalize(text: str) -> str:
    """Collapse runs of spaces and excess blank lines (PDF extraction is noisy)."""
    text = text.replace('\x00', ' ')
    text = _WS.sub(' ', text)
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()


def split_sentences(text: str) -> List[str]:
    parts = _SENTENCE_END.split(text.replace('\n', ' '))
    return [p.strip() for p in parts if p.strip()]


def chunk_text(text: str, max_chars: int = 1000, overlap_sentences: int = 1) -> List[str]:
    """
    Pack whole sentences into chunks of roughly max_chars, repeating the last
    `overlap_sentences` sentences at the start of the next chunk so facts that
    straddle a boundary stay retrievable.
    """
    sentences = split_sentences(normalize(text))
    chunks: List[str] = []
    current: List[str] = []
    size = 0
    for sentence in sentences:
        # Hard-wrap pathological sentences (tables, footers) so no chunk explodes.
        while len(sentence) > max_chars:
            head, sentence = sentence[:max_chars], sentence[max_chars:]
            if current:
                chunks.append(' '.join(current))
                current, size = [], 0
            chunks.append(head)
        if size + len(sentence) > max_chars and current:
            chunks.append(' '.join(current))
            current = current[-overlap_sentences:] if overlap_sentences else []
            size = sum(len(s) + 1 for s in current)
        current.append(sentence)
        size += len(sentence) + 1
    if current:
        chunks.append(' '.join(current))
    return [c for c in chunks if len(c) >= 20]


def chunk_pages(pages: List[str], max_chars: int = 1000) -> List[Dict]:
    """Chunk each page separately so every chunk keeps a page number."""
    out: List[Dict] = []
    for page_no, page_text in enumerate(pages, start=1):
        for piece in chunk_text(page_text or '', max_chars=max_chars):
            out.append({'page': page_no, 'text': piece})
    return out
