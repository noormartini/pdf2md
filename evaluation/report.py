"""Report generator for PDF-to-Markdown conversion experiments."""

import json
import os
from pathlib import Path
from typing import Optional


def load_results(results_path: str) -> list[dict]:
    """Load evaluation results from JSON file."""
    with open(results_path, "r") as f:
        return json.load(f)


def format_table(headers: list[str], rows: list[list[str]], col_alignments: Optional[list[str]] = None) -> str:
    """
    Format a markdown table.

    Args:
        headers: List of column headers
        rows: List of rows (each row is a list of cell values)
        col_alignments: Optional list of 'left', 'right', or 'center' for each column
    """
    if col_alignments is None:
        col_alignments = ["left"] * len(headers)

    # Calculate column widths
    widths = [len(h) for h in headers]
    for row in rows:
        for i, cell in enumerate(row):
            if i < len(widths):
                widths[i] = max(widths[i], len(str(cell)))

    # Build table
    lines = []

    # Header row
    header_parts = []
    for i, h in enumerate(headers):
        align = col_alignments[i] if i < len(col_alignments) else "left"
        if align == "right":
            header_parts.append(h.rjust(widths[i]))
        elif align == "center":
            header_parts.append(h.center(widths[i]))
        else:
            header_parts.append(h.ljust(widths[i]))
    lines.append("| " + " | ".join(header_parts) + " |")

    # Separator row
    sep_parts = []
    for i, w in enumerate(widths):
        align = col_alignments[i] if i < len(col_alignments) else "left"
        if align == "right":
            sep_parts.append("-" * (w - 1) + ":")
        elif align == "center":
            sep_parts.append(":" + "-" * (w - 2) + ":")
        else:
            sep_parts.append("-" * w)
    lines.append("| " + " | ".join(sep_parts) + " |")

    # Data rows
    for row in rows:
        row_parts = []
        for i, cell in enumerate(row):
            if i < len(widths):
                align = col_alignments[i] if i < len(col_alignments) else "left"
                cell_str = str(cell)
                if align == "right":
                    row_parts.append(cell_str.rjust(widths[i]))
                elif align == "center":
                    row_parts.append(cell_str.center(widths[i]))
                else:
                    row_parts.append(cell_str.ljust(widths[i]))
        lines.append("| " + " | ".join(row_parts) + " |")

    return "\n".join(lines)


def generate_summary_table(results: list[dict]) -> str:
    """Generate summary table comparing strategies."""
    # Aggregate by strategy
    strategy_data = {}
    for r in results:
        if r.get("error"):
            continue

        strategy = r["strategy"]
        if strategy not in strategy_data:
            strategy_data[strategy] = {
                "pages": 0,
                "total_time_ms": 0,
                "metrics_sum": {k: 0 for k in r["metrics"].keys()},
            }

        strategy_data[strategy]["pages"] += 1
        strategy_data[strategy]["total_time_ms"] += r["timing_ms"]
        for k, v in r["metrics"].items():
            strategy_data[strategy]["metrics_sum"][k] += v

    if not strategy_data:
        return "*No successful conversions to summarise.*"

    # Build rows
    headers = ["Strategy", "Pages", "Avg Time (ms)"] + list(list(strategy_data.values())[0]["metrics_sum"].keys())
    rows = []

    for strategy, data in sorted(strategy_data.items()):
        avg_time = data["total_time_ms"] / data["pages"] if data["pages"] > 0 else 0
        row = [
            strategy,
            str(data["pages"]),
            f"{avg_time:.1f}",
        ]
        for metric in data["metrics_sum"].keys():
            avg = data["metrics_sum"][metric] / data["pages"] if data["pages"] > 0 else 0
            row.append(f"{avg:.3f}")
        rows.append(row)

    return format_table(headers, rows)


def generate_model_comparison(results: list[dict]) -> str:
    """Generate table comparing models."""
    # Aggregate by model
    model_data = {}
    for r in results:
        if r.get("error"):
            continue

        model = r["model"]
        if model not in model_data:
            model_data[model] = {
                "pages": 0,
                "total_time_ms": 0,
                "metrics_sum": {k: 0 for k in r["metrics"].keys()},
            }

        model_data[model]["pages"] += 1
        model_data[model]["total_time_ms"] += r["timing_ms"]
        for k, v in r["metrics"].items():
            model_data[model]["metrics_sum"][k] += v

    if not model_data:
        return "*No successful conversions to summarise.*"

    # Build rows
    headers = ["Model", "Pages", "Avg Time (ms)"] + list(list(model_data.values())[0]["metrics_sum"].keys())
    rows = []

    for model, data in sorted(model_data.items()):
        avg_time = data["total_time_ms"] / data["pages"] if data["pages"] > 0 else 0
        row = [
            model,
            str(data["pages"]),
            f"{avg_time:.1f}",
        ]
        for metric in data["metrics_sum"].keys():
            avg = data["metrics_sum"][metric] / data["pages"] if data["pages"] > 0 else 0
            row.append(f"{avg:.3f}")
        rows.append(row)

    return format_table(headers, rows)


def generate_strategy_model_matrix(results: list[dict]) -> str:
    """Generate matrix table of strategy x model with text similarity scores."""
    # Aggregate by (strategy, model)
    matrix = {}
    for r in results:
        if r.get("error"):
            continue

        key = (r["strategy"], r["model"])
        if key not in matrix:
            matrix[key] = {"pages": 0, "similarity_sum": 0}

        matrix[key]["pages"] += 1
        matrix[key]["similarity_sum"] += r["metrics"]["text_similarity"]

    # Get unique strategies and models
    strategies = sorted(set(k[0] for k in matrix.keys()))
    models = sorted(set(k[1] for k in matrix.keys()))

    # Build table with models as columns, strategies as rows
    headers = ["Strategy"] + models
    rows = []

    for strategy in strategies:
        row = [strategy]
        for model in models:
            key = (strategy, model)
            if key in matrix and matrix[key]["pages"] > 0:
                avg = matrix[key]["similarity_sum"] / matrix[key]["pages"]
                row.append(f"{avg:.3f} (n={matrix[key]['pages']})")
            else:
                row.append("-")
        rows.append(row)

    return format_table(headers, rows, col_alignments=["left"] + ["center"] * len(models))


def generate_per_page_breakdown(results: list[dict]) -> str:
    """Generate per-page breakdown table."""
    # Aggregate by page
    page_data = {}
    for r in results:
        page = r["page_number"]
        if page not in page_data:
            page_data[page] = []
        page_data[page].append(r)

    # Build rows
    headers = ["Page", "Best Strategy", "Best Model", "Best Similarity", "Worst Error"]
    rows = []

    for page in sorted(page_data.keys()):
        page_results = page_data[page]

        # Find best (highest text_similarity)
        valid_results = [r for r in page_results if not r.get("error")]
        error_results = [r for r in page_results if r.get("error")]

        if valid_results:
            best = max(valid_results, key=lambda r: r["metrics"]["text_similarity"])
            best_strategy = best["strategy"]
            best_model = best["model"]
            best_similarity = f"{best['metrics']['text_similarity']:.3f}"
        else:
            best_strategy = "-"
            best_model = "-"
            best_similarity = "-"

        worst_error = error_results[0]["error"][:30] + "..." if error_results else "-"

        rows.append([
            str(page),
            best_strategy,
            best_model,
            best_similarity,
            worst_error,
        ])

    return format_table(headers, rows)


def generate_temperature_comparison(results: list[dict]) -> str:
    """Generate table comparing different temperatures."""
    # Aggregate by temperature
    temp_data = {}
    for r in results:
        if r.get("error"):
            continue

        # Temperature not directly stored, derive from prompt_variant or skip
        # For now, we'll need to add temperature to results
        pass

    if not temp_data:
        return "*Temperature comparison not available (temperature not tracked in results)*"

    headers = ["Temperature", "Pages", "Avg Similarity", "Avg Time (ms)"]
    rows = []

    for temp, data in sorted(temp_data.items()):
        avg_sim = data["similarity_sum"] / data["pages"] if data["pages"] > 0 else 0
        avg_time = data["total_time_ms"] / data["pages"] if data["pages"] > 0 else 0
        rows.append([
            f"{temp}",
            str(data["pages"]),
            f"{avg_sim:.3f}",
            f"{avg_time:.1f}",
        ])

    return format_table(headers, rows)


def generate_full_report(results: list[dict], output_path: Optional[str] = None) -> str:
    """
    Generate a complete markdown report from evaluation results.
    """
    lines = []

    # Title
    lines.append("# PDF-to-Markdown Conversion Experiment Report\n")

    # Overview
    total = len(results)
    errors = sum(1 for r in results if r.get("error"))
    lines.append(f"**Total evaluations:** {total}")
    lines.append(f"**Errors:** {errors} ({100*errors/total:.1f}%)" if total > 0 else "")
    lines.append("")

    # Strategy Comparison
    lines.append("## Strategy Comparison\n")
    lines.append(generate_summary_table(results))
    lines.append("")

    # Model Comparison
    lines.append("## Model Comparison\n")
    model_table = generate_model_comparison(results)
    if model_table:
        lines.append(model_table)
        lines.append("")

    # Strategy x Model Matrix
    lines.append("## Strategy × Model Matrix (Text Similarity)\n")
    lines.append(generate_strategy_model_matrix(results))
    lines.append("")

    # Per-Page Breakdown
    lines.append("## Per-Page Breakdown\n")
    lines.append(generate_per_page_breakdown(results))
    lines.append("")

    # Metric definitions
    lines.append("## Metric Definitions\n")
    lines.append("""
| Metric | Description |
|--------|-------------|
| text_similarity | SequenceMatcher ratio (0-1) comparing normalized text |
| heading_structure | Similarity of heading counts by level (H1-H6) |
| list_structure | Similarity of bullet and numbered list counts |
| table_structure | Similarity of table separator counts |
| code_block_score | Similarity of fenced code block counts |
| paragraph_structure | Similarity of paragraph counts (with 20% tolerance) |
| word_overlap | Jaccard similarity of word sets |
""")

    report = "\n".join(lines)

    if output_path:
        parent = os.path.dirname(output_path)
        if parent:
            os.makedirs(parent, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(report)
        print(f"Report saved to {output_path}")

    return report


def main():
    """CLI entry point for generating reports."""
    import argparse

    parser = argparse.ArgumentParser(description="Generate report from evaluation results")
    parser.add_argument(
        "-i", "--input",
        default="output/results.json",
        help="Path to results JSON file (default: output/results.json)",
    )
    parser.add_argument(
        "-o", "--output",
        default="output/report.md",
        help="Path to save markdown report (default: output/report.md)",
    )

    args = parser.parse_args()

    results = load_results(args.input)
    generate_full_report(results, args.output)


if __name__ == "__main__":
    main()
