from __future__ import annotations

from pol.analysis.dedup import dedup_minhash
from pol.types import CorpusDoc


def _doc(i: int, text: str) -> CorpusDoc:
    return CorpusDoc(doc_id=f"d{i}", source="test", text=text, license="public_domain")


def test_dedup_catches_exact_duplicates() -> None:
    docs = [
        _doc(1, "alpha beta gamma delta epsilon zeta eta"),
        _doc(2, "alpha beta gamma delta epsilon zeta eta"),
        _doc(3, "unrelated text about something else entirely random words"),
    ]
    report = dedup_minhash(docs, threshold=0.5)
    assert report.n_duplicates >= 1


def test_dedup_no_false_positives_on_disjoint() -> None:
    docs = [
        _doc(1, "alpha beta gamma delta " * 50),
        _doc(2, "zeta eta theta iota " * 50),
        _doc(3, "omega psi chi phi " * 50),
    ]
    report = dedup_minhash(docs, threshold=0.8)
    assert report.n_duplicates == 0
