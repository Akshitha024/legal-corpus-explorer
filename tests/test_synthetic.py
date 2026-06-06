from __future__ import annotations

from pol.data.synthetic import generate, known_sources


def test_generate_count() -> None:
    docs = generate(n=30)
    assert len(docs) == 30
    assert all(d.text for d in docs)


def test_generate_has_various_sources() -> None:
    docs = generate(n=200, seed=7)
    sources = {d.source for d in docs}
    assert len(sources) >= 4  # several sources represented


def test_known_sources_list() -> None:
    assert len(list(known_sources())) >= 5


def test_generated_has_some_duplicates() -> None:
    # the synthetic generator injects ~5% near-duplicates; on 200 docs we
    # expect at least a few exact-text matches
    docs = generate(n=200, seed=7)
    texts = [d.text for d in docs]
    assert len(texts) > len(set(texts))
