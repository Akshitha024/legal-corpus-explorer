from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path
from typing import Any

from loguru import logger

from .analysis.dedup import dedup_minhash
from .analysis.stats import compute
from .analysis.topics import (
    assignment_counts,
    cluster,
    cluster_silhouette_approx,
)
from .data.synthetic import generate


def analyze(out_dir: Path, n_docs: int = 200) -> dict[str, Any]:
    out_dir.mkdir(parents=True, exist_ok=True)
    docs = generate(n=n_docs)
    stats = compute(docs)
    dedup = dedup_minhash(docs, threshold=0.85)
    topic_report = cluster(docs, n_clusters=6)
    sil = cluster_silhouette_approx(topic_report)

    artifact = {
        "n_docs": len(docs),
        "total_chars": stats.total_chars,
        "by_source": stats.by_source,
        "by_license": stats.by_license,
        "by_jurisdiction": stats.by_jurisdiction,
        "by_year": stats.by_year,
        "length_distribution": stats.length_distribution,
        "dedup": asdict(dedup),
        "topics": {
            "n_clusters": topic_report.n_clusters,
            "cluster_top_terms": topic_report.cluster_top_terms,
            "cluster_counts": assignment_counts(topic_report),
            "silhouette_approx": sil,
            "assignments": [
                {
                    "doc_id": a.doc_id,
                    "topic": a.topic,
                    "x": a.coordinates_2d[0],
                    "y": a.coordinates_2d[1],
                }
                for a in topic_report.assignments
            ],
        },
    }
    (out_dir / "analysis.json").write_text(json.dumps(artifact))
    logger.info("wrote analysis to {}", out_dir / "analysis.json")
    return artifact
