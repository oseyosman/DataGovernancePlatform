"""
LLM client abstraction.

  RAG_LLM_PROVIDER = extractive (default) | anthropic
  RAG_LLM_MODEL    = model id for the anthropic provider
  ANTHROPIC_API_KEY

The 'extractive' provider needs no network or key: it quotes the best-matching
sentences from the retrieved passages. It keeps tests, CI and evals runnable
offline and gives a baseline to compare a real model against.
"""
import os
import re
from dataclasses import dataclass
from typing import List

from backend1.app.services.rag.chunking import split_sentences
from backend1.app.services.rag.prompts import INSUFFICIENT, SYSTEM_PROMPT, build_user_prompt
from backend1.app.services.rag.retrieval import tokenize

DEFAULT_ANTHROPIC_MODEL = 'claude-sonnet-5-5'


class RagConfigError(RuntimeError):
    """Raised when the configured provider cannot be used."""


@dataclass
class LLMResponse:
    text: str
    provider: str
    model: str = ''
    input_tokens: int = 0
    output_tokens: int = 0


class LLMClient:
    provider = 'base'

    def generate(self, question: str, passages: List[dict]) -> LLMResponse:
        raise NotImplementedError


class ExtractiveClient(LLMClient):
    """Offline baseline: returns the most question-relevant sentences with citations."""
    provider = 'extractive'

    def __init__(self, max_sentences: int = 2):
        self.max_sentences = max_sentences

    def generate(self, question: str, passages: List[dict]) -> LLMResponse:
        q_terms = set(tokenize(question))
        scored = []
        for p in passages:
            for sentence in split_sentences(p['text']):
                overlap = len(q_terms & set(tokenize(sentence)))
                if overlap:
                    scored.append((overlap, -p['n'], sentence, p['n']))
        if not scored:
            return LLMResponse(INSUFFICIENT, self.provider, 'extractive-v1')
        scored.sort(reverse=True)
        top_overlap = scored[0][0]
        seen, parts = set(), []
        for overlap, _, sentence, n in scored:
            if sentence in seen:
                continue
            # After the best sentence, add another only if it is nearly as relevant;
            # otherwise a stray shared word pulls in an unrelated, wrongly cited sentence.
            if parts and (overlap < 2 or overlap < 0.75 * top_overlap):
                break
            seen.add(sentence)
            parts.append(f'{sentence} [{n}]')
            if len(parts) == self.max_sentences:
                break
        return LLMResponse(' '.join(parts), self.provider, 'extractive-v1')


class AnthropicClient(LLMClient):
    provider = 'anthropic'

    def __init__(self, model: str = None, api_key: str = None, max_tokens: int = 500, timeout: float = 30.0):
        api_key = api_key or os.environ.get('ANTHROPIC_API_KEY')
        if not api_key:
            raise RagConfigError('RAG_LLM_PROVIDER=anthropic requires ANTHROPIC_API_KEY')
        try:
            import anthropic
        except ImportError as exc:  # pragma: no cover - depends on environment
            raise RagConfigError('Install the "anthropic" package to use the anthropic provider') from exc
        self._client = anthropic.Anthropic(api_key=api_key, timeout=timeout)
        self.model = model or os.environ.get('RAG_LLM_MODEL') or DEFAULT_ANTHROPIC_MODEL
        self.max_tokens = max_tokens

    def generate(self, question: str, passages: List[dict]) -> LLMResponse:
        resp = self._client.messages.create(
            model=self.model,
            max_tokens=self.max_tokens,
            temperature=0,
            system=SYSTEM_PROMPT,
            messages=[{'role': 'user', 'content': build_user_prompt(question, passages)}],
        )
        text = ''.join(b.text for b in resp.content if getattr(b, 'type', '') == 'text').strip()
        usage = getattr(resp, 'usage', None)
        return LLMResponse(text, self.provider, self.model,
                           getattr(usage, 'input_tokens', 0), getattr(usage, 'output_tokens', 0))


def get_llm_client() -> LLMClient:
    provider = (os.environ.get('RAG_LLM_PROVIDER') or 'extractive').lower()
    if provider == 'extractive':
        return ExtractiveClient()
    if provider == 'anthropic':
        return AnthropicClient()
    raise RagConfigError(f'Unknown RAG_LLM_PROVIDER: {provider!r}')
