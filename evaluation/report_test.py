"""Tests for evaluation/report.py — table formatting + edge cases."""

import json
from pathlib import Path

from evaluation.report import (
    format_table,
    generate_full_report,
    generate_model_comparison,
    generate_per_page_breakdown,
    generate_strategy_model_matrix,
    generate_summary_table,
    load_results,
)


def _row(strategy="text", model="m", page=1, similarity=1.0, timing=100.0, error=None):
    return {
        "page_number": page,
        "strategy": strategy,
        "model": model,
        "prompt_variant": "default",
        "metrics": {
            "text_similarity": similarity,
            "heading_structure": similarity,
            "list_structure": similarity,
            "table_structure": similarity,
            "code_block_score": similarity,
            "paragraph_structure": similarity,
            "word_overlap": similarity,
        },
        "timing_ms": timing,
        "token_usage": None,
        "error": error,
    }


# ---------------------------------------------------------------------------
# format_table
# ---------------------------------------------------------------------------

def test_format_table_basic():
    md = format_table(["Header1", "Header2"], [["one", "two"], ["three", "four"]])
    lines = md.split("\n")
    assert lines[0].startswith("|") and "Header1" in lines[0] and "Header2" in lines[0]
    assert "---" in lines[1]
    assert "one" in lines[2] and "two" in lines[2]
    assert "three" in lines[3] and "four" in lines[3]


def test_format_table_alignment_markers():
    md = format_table(["A", "B"], [["1", "2"]], col_alignments=["left", "right"])
    sep = md.split("\n")[1]
    # Right-aligned column ends with ":"
    assert sep.rstrip(" |").endswith(":")


# ---------------------------------------------------------------------------
# generate_summary_table — including the empty-results guard (fix 2.7)
# ---------------------------------------------------------------------------

def test_generate_summary_table_groups_by_strategy():
    results = [_row(strategy="text"), _row(strategy="text"), _row(strategy="image")]
    md = generate_summary_table(results)
    assert "text" in md and "image" in md


def test_generate_summary_table_empty_results_does_not_crash():
    """The bug we fixed in 2.7: list(...).[0] crashed when no successful runs."""
    assert "No successful conversions" in generate_summary_table([])


def test_generate_summary_table_all_errors_does_not_crash():
    md = generate_summary_table([_row(error="boom"), _row(error="boom")])
    assert "No successful conversions" in md


# ---------------------------------------------------------------------------
# generate_model_comparison — same guard
# ---------------------------------------------------------------------------

def test_generate_model_comparison_empty_results():
    assert "No successful conversions" in generate_model_comparison([])


def test_generate_model_comparison_groups_by_model():
    results = [_row(model="m1"), _row(model="m2"), _row(model="m1")]
    md = generate_model_comparison(results)
    assert "m1" in md and "m2" in md


# ---------------------------------------------------------------------------
# generate_strategy_model_matrix
# ---------------------------------------------------------------------------

def test_strategy_model_matrix_includes_all_pairs():
    results = [
        _row(strategy="text", model="m1", similarity=0.9),
        _row(strategy="image", model="m2", similarity=0.4),
    ]
    md = generate_strategy_model_matrix(results)
    assert "text" in md and "image" in md
    assert "m1" in md and "m2" in md


# ---------------------------------------------------------------------------
# generate_per_page_breakdown
# ---------------------------------------------------------------------------

def test_per_page_breakdown_picks_best_per_page():
    results = [
        _row(page=1, strategy="text", similarity=0.3),
        _row(page=1, strategy="image", similarity=0.9),
        _row(page=2, strategy="text", similarity=0.7),
    ]
    md = generate_per_page_breakdown(results)
    # Page 1's best is "image"; page 2's best is "text"
    lines = md.split("\n")
    page1_line = next(l for l in lines if "| 1 " in l or l.startswith("| 1"))
    assert "image" in page1_line


# ---------------------------------------------------------------------------
# generate_full_report
# ---------------------------------------------------------------------------

def test_full_report_includes_all_sections():
    results = [_row()]
    report = generate_full_report(results)
    assert "Strategy Comparison" in report
    assert "Model Comparison" in report
    assert "Strategy × Model Matrix" in report
    assert "Per-Page Breakdown" in report
    assert "Metric Definitions" in report


def test_full_report_writes_to_file(tmp_path: Path):
    out = tmp_path / "report.md"
    generate_full_report([_row()], output_path=str(out))
    assert out.exists()
    assert "Strategy Comparison" in out.read_text(encoding="utf-8")


# ---------------------------------------------------------------------------
# load_results
# ---------------------------------------------------------------------------

def test_load_results_roundtrips_json(tmp_path: Path):
    p = tmp_path / "results.json"
    payload = [_row()]
    p.write_text(json.dumps(payload), encoding="utf-8")
    assert load_results(str(p)) == payload
