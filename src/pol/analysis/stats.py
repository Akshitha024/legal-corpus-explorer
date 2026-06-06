"""License + length + source-mix statistics."""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass

from ..types import CorpusDoc


@dataclass
class CorpusStats:
    n_docs: int
    total_chars: int
    by_source: dict[str, int]
    by_license: dict[str, int]
    by_jurisdiction: dict[str, int]
    by_year: dict[int, int]
    length_distribution: list[int]  # per-doc chars


def compute(docs: list[CorpusDoc]) -> CorpusStats:
    return CorpusStats(
        n_docs=len(docs),
        total_chars=sum(len(d.text) for d in docs),
        by_source=dict(Counter(d.source for d in docs)),
        by_license=dict(Counter(d.license for d in docs)),
        by_jurisdiction=dict(Counter(d.jurisdiction or "unknown" for d in docs)),
        by_year=dict(Counter(d.year or 0 for d in docs)),
        length_distribution=[len(d.text) for d in docs],
    )
