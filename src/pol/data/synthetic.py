"""Synthetic corpus generator that produces a Pile-of-Law-shaped sample.

Mimics the real Pile-of-Law in source mix, license distribution, document
length distribution, and topic mix; small enough that CI runs in under a
second.
"""

from __future__ import annotations

import random
from collections.abc import Iterable

from ..types import CorpusDoc

_SOURCE_PROFILE = {
    # source -> (weight, typical_length_chars, license)
    "scotus": (0.15, 12000, "public_domain"),
    "courtlistener": (0.30, 5000, "public_domain"),
    "us_code": (0.10, 8000, "public_domain"),
    "cfr": (0.10, 6000, "public_domain"),
    "state_codes": (0.10, 9000, "public_domain"),
    "edgar_8k": (0.10, 3500, "public_domain"),
    "patents": (0.10, 7000, "public_domain"),
    "law_review": (0.05, 18000, "cc_by"),
}

_TOPIC_VOCAB = {
    "civil_rights": [
        "plaintiff",
        "discrimination",
        "fourteenth",
        "amendment",
        "equal",
        "protection",
    ],
    "tax": ["taxable", "deduction", "irs", "income", "section", "credit"],
    "contracts": ["consideration", "breach", "damages", "performance", "warranty", "term"],
    "criminal": ["defendant", "felony", "sentencing", "miranda", "evidence", "guilt"],
    "patents": ["claim", "novelty", "obvious", "prior", "art", "infringement"],
    "regulatory": ["agency", "rulemaking", "comment", "compliance", "enforcement", "filing"],
}


def _make_text(topic: str, source: str, length_chars: int, seed: int) -> str:
    rng = random.Random(seed)
    vocab = _TOPIC_VOCAB[topic]
    filler = (
        "the parties hereto ",
        "in the matter of ",
        "the court finds that ",
        "pursuant to ",
        "notwithstanding any ",
        "the petitioner ",
    )
    out = [f"[{source.upper()}] "]
    while sum(len(w) for w in out) < length_chars:
        out.append(rng.choice(vocab) + " ")
        out.append(rng.choice(filler))
    return "".join(out)[:length_chars]


def generate(n: int = 200, seed: int = 7) -> list[CorpusDoc]:
    rng = random.Random(seed)
    sources = list(_SOURCE_PROFILE.keys())
    weights = [_SOURCE_PROFILE[s][0] for s in sources]
    topics = list(_TOPIC_VOCAB.keys())
    docs: list[CorpusDoc] = []
    for i in range(n):
        source = rng.choices(sources, weights=weights, k=1)[0]
        _, typical_len, license_ = _SOURCE_PROFILE[source]
        length = max(500, int(rng.lognormvariate(0, 0.6) * typical_len))
        topic = rng.choice(topics)
        # 5% near-duplicate rate: with that probability emit the same text twice
        if i > 0 and rng.random() < 0.05:
            prev = docs[rng.randint(0, len(docs) - 1)]
            docs.append(
                CorpusDoc(
                    doc_id=f"d_{i:04d}",
                    source=prev.source,
                    text=prev.text,
                    license=prev.license,
                    jurisdiction=prev.jurisdiction,
                    year=prev.year,
                )
            )
            continue
        text = _make_text(topic, source, length, seed=i)
        year = rng.randint(1990, 2024)
        jurisdiction = rng.choice(["federal", "ny", "ca", "tx", "fl", None])
        docs.append(
            CorpusDoc(
                doc_id=f"d_{i:04d}",
                source=source,
                text=text,
                license=license_,
                jurisdiction=jurisdiction,
                year=year,
            )
        )
    return docs


def known_sources() -> Iterable[str]:
    return iter(_SOURCE_PROFILE.keys())
