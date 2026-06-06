from __future__ import annotations

from pol.analysis.stats import compute
from pol.types import CorpusDoc


def test_stats_counts() -> None:
    docs = [
        CorpusDoc(doc_id="d1", source="scotus", text="abc", license="public_domain", year=2020),
        CorpusDoc(doc_id="d2", source="scotus", text="def", license="public_domain", year=2021),
        CorpusDoc(doc_id="d3", source="cfr", text="ghi", license="public_domain", year=2020),
    ]
    s = compute(docs)
    assert s.n_docs == 3
    assert s.by_source == {"scotus": 2, "cfr": 1}
    assert s.by_year == {2020: 2, 2021: 1}
    assert s.total_chars == 9
