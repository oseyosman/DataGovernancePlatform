# RAG evaluation report

- Corpus: `fixtures`  |  Provider: `extractive`  |  k = 4
- Questions: 35 (27 answerable, 8 unanswerable)
- Generated: 2026-10-18 16:43 UTC

| Metric | Value |
| --- | --- |
| Retrieval recall@4 | 96% |
| Retrieval MRR | 0.889 |
| Answer accuracy (string check) | 78% |
| False abstentions | 18% |
| Citation precision | 96% |
| Correct abstention on unanswerable | 100% |
| Injection leak rate | 0% |
| Latency avg / p95 (ms) | 0.0 / 0 |
| Tokens in / out | 0 / 0 |

## By category

| Category | n | recall@k | accuracy | abstained |
| --- | --- | --- | --- | --- |
| company_scope | 1 | 100% | 100% | 0 |
| cross_company | 2 | 100% | 100% | 0 |
| injection | 1 | 100% | 100% | 0 |
| lexical | 19 | 100% | 90% | 1 |
| paraphrase | 4 | 75% | 0% | 4 |
| unanswerable | 8 | n/a | n/a | 8 |

## Failures (6)

| id | category | question | outcome |
| --- | --- | --- | --- |
| q09 | lexical | What happened in the 2024 ransomware incident? | wrong answer; relevant rank: 1 |
| q14 | lexical | Which regulator examines the bank? | abstained (no_matching_passages); relevant rank: 1 |
| q24 | paraphrase | How quickly must we tell customers about a data leak? | abstained (weak_evidence); relevant rank: 2 |
| q25 | paraphrase | How many people work at Halvorsen? | abstained (weak_evidence); relevant rank: 1 |
| q26 | paraphrase | Do staff need two-step login for remote access? | abstained (weak_evidence); relevant rank: 1 |
| q27 | paraphrase | Has the bank had any hacking problems this year? | abstained (no_matching_passages); relevant rank: None |
