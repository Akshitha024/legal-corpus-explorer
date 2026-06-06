"""MinHash-based near-duplicate detection.

Uses datasketch for the LSH index; falls back to exact-hash comparison if
datasketch is not installed. The synthetic corpus deliberately injects ~5%
near-duplicates so this catches a meaningful number.
"""

from __future__ import annotations

from dataclasses import dataclass

from ..types import CorpusDoc


@dataclass
class DedupReport:
    n_docs: int
    n_duplicates: int
    n_clusters: int
    duplicate_pairs: list[tuple[str, str]]


def _shingle(text: str, k: int = 5) -> set[str]:
    tokens = text.lower().split()
    if len(tokens) < k:
        return set(tokens)
    return {" ".join(tokens[i : i + k]) for i in range(len(tokens) - k + 1)}


def dedup_minhash(
    docs: list[CorpusDoc], threshold: float = 0.9, num_perm: int = 128
) -> DedupReport:
    try:
        from datasketch import MinHash, MinHashLSH
    except ImportError:
        return _dedup_exact_hash(docs)

    lsh = MinHashLSH(threshold=threshold, num_perm=num_perm)
    minhashes: dict[str, MinHash] = {}
    for d in docs:
        m = MinHash(num_perm=num_perm)
        for sh in _shingle(d.text):
            m.update(sh.encode("utf-8"))
        minhashes[d.doc_id] = m
        lsh.insert(d.doc_id, m)

    seen: set[str] = set()
    pairs: list[tuple[str, str]] = []
    clusters: set[frozenset[str]] = set()
    for d in docs:
        if d.doc_id in seen:
            continue
        candidates = list(lsh.query(minhashes[d.doc_id]))
        if len(candidates) > 1:
            cluster = frozenset(candidates)
            clusters.add(cluster)
            for c in candidates:
                if c != d.doc_id:
                    pairs.append((d.doc_id, c))
                seen.add(c)
    return DedupReport(
        n_docs=len(docs),
        n_duplicates=sum(len(c) - 1 for c in clusters),
        n_clusters=len(clusters),
        duplicate_pairs=pairs,
    )


def _dedup_exact_hash(docs: list[CorpusDoc]) -> DedupReport:
    seen: dict[str, str] = {}
    pairs: list[tuple[str, str]] = []
    clusters: dict[str, list[str]] = {}
    for d in docs:
        h = hash(d.text)
        key = str(h)
        if key in seen:
            pairs.append((seen[key], d.doc_id))
            clusters.setdefault(key, [seen[key]]).append(d.doc_id)
        else:
            seen[key] = d.doc_id
    return DedupReport(
        n_docs=len(docs),
        n_duplicates=len(pairs),
        n_clusters=len(clusters),
        duplicate_pairs=pairs,
    )
