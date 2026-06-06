"""Core types: a CorpusDoc is one legal document from the Pile."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class CorpusDoc:
    doc_id: str
    source: str  # e.g. "scotus", "courtlistener", "us_code"
    text: str
    license: str  # "public_domain", "cc_by", "cc_by_sa", "unknown"
    jurisdiction: str | None = None
    year: int | None = None
