from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer
from tabulate import tabulate

from ..runner import analyze
from ..viz.charts import (
    plot_dedup_funnel,
    plot_length_by_source,
    plot_license_pie,
    plot_source_counts,
    plot_topic_scatter,
)

app = typer.Typer(add_completion=False, help="pol: Pile of Law analytics")


@app.command("analyze")
def cmd_analyze(
    out_dir: Annotated[Path, typer.Option(help="results dir")] = Path("results"),
    n_docs: Annotated[int, typer.Option(help="synthetic doc count")] = 200,
) -> None:
    a = analyze(out_dir, n_docs=n_docs)
    table = [
        ("n_docs", a["n_docs"]),
        ("total_chars", a["total_chars"]),
        ("n_duplicates", a["dedup"]["n_duplicates"]),
        ("n_clusters", a["dedup"]["n_clusters"]),
        ("n_topic_clusters", a["topics"]["n_clusters"]),
        ("silhouette_approx", f"{a['topics']['silhouette_approx']:.3f}"),
    ]
    print(tabulate(table, headers=["metric", "value"], tablefmt="github"))


@app.command("plots")
def cmd_plots(
    analysis_path: Annotated[Path, typer.Option(help="analysis json")] = Path(
        "results/analysis.json"
    ),
    out_dir: Annotated[Path, typer.Option(help="figures dir")] = Path("results/figures"),
) -> None:
    plot_source_counts(analysis_path, out_dir / "source_counts.png")
    plot_length_by_source(analysis_path, out_dir / "length_distribution.png")
    plot_license_pie(analysis_path, out_dir / "license_pie.png")
    plot_topic_scatter(analysis_path, out_dir / "topic_scatter.png")
    plot_dedup_funnel(analysis_path, out_dir / "dedup_funnel.png")
    typer.echo(f"wrote 5 figures to {out_dir}")


if __name__ == "__main__":
    app()
