"""Lightweight topic clustering via TF-IDF + KMeans.

For the synthetic corpus this is enough to recover the planted topics;
for the real Pile of Law you'd want BERTopic or LDA + a real embedder.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.feature_extraction.text import TfidfVectorizer

from ..types import CorpusDoc


@dataclass
class TopicAssignment:
    doc_id: str
    topic: int
    coordinates_2d: tuple[float, float]


@dataclass
class TopicReport:
    n_clusters: int
    assignments: list[TopicAssignment]
    cluster_top_terms: dict[int, list[str]]


def cluster(docs: list[CorpusDoc], n_clusters: int = 6, seed: int = 7) -> TopicReport:
    texts = [d.text for d in docs]
    vec = TfidfVectorizer(max_features=2000, stop_words="english", ngram_range=(1, 2), min_df=2)
    X = vec.fit_transform(texts)
    km = KMeans(n_clusters=n_clusters, n_init=10, random_state=seed)
    labels = km.fit_predict(X)
    # 2-D coords via PCA on the centered TF-IDF (top features only for speed)
    pca = PCA(n_components=2, random_state=seed)
    coords = pca.fit_transform(
        X.toarray() if X.shape[1] < 2000 else km.transform(X)[:, :n_clusters]
    )

    terms = vec.get_feature_names_out()
    centers = km.cluster_centers_
    top: dict[int, list[str]] = {}
    for i in range(n_clusters):
        top_idx = centers[i].argsort()[-8:][::-1]
        top[i] = [terms[j] for j in top_idx]

    assignments = [
        TopicAssignment(
            doc_id=d.doc_id,
            topic=int(labels[i]),
            coordinates_2d=(float(coords[i, 0]), float(coords[i, 1])),
        )
        for i, d in enumerate(docs)
    ]
    return TopicReport(n_clusters=n_clusters, assignments=assignments, cluster_top_terms=top)


def assignment_counts(report: TopicReport) -> dict[int, int]:
    out: dict[int, int] = {}
    for a in report.assignments:
        out[a.topic] = out.get(a.topic, 0) + 1
    return out


def total_assignments(report: TopicReport) -> int:
    return sum(assignment_counts(report).values()) or 1


def cluster_silhouette_approx(report: TopicReport) -> float:
    """Rough cluster-quality proxy: how spread-out are clusters in 2D space."""
    coords = np.array([a.coordinates_2d for a in report.assignments])
    labels = np.array([a.topic for a in report.assignments])
    if len(set(labels)) < 2:
        return 0.0
    centers = np.array([coords[labels == k].mean(axis=0) for k in sorted(set(labels))])
    intra = float(
        np.mean([np.linalg.norm(coords[i] - centers[labels[i]]) for i in range(len(coords))])
    )
    inter = float(
        np.mean(
            [
                np.linalg.norm(centers[a] - centers[b])
                for a in range(len(centers))
                for b in range(a + 1, len(centers))
            ]
        )
    )
    return (inter - intra) / max(inter + intra, 1e-9)
