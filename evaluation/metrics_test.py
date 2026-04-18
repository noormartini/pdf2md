"""Tests for evaluation/metrics.py — pure functions, no I/O."""

import pytest

from evaluation.metrics import (
    EvaluationResult,
    aggregate_results,
    calculate_word_overlap,
    code_block_score,
    count_code_blocks,
    count_headings,
    count_lists,
    count_paragraphs,
    count_tables,
    evaluate_conversion,
    heading_structure_score,
    list_structure_score,
    paragraph_structure_score,
    table_structure_score,
    text_similarity,
)


# ---------------------------------------------------------------------------
# text_similarity
# ---------------------------------------------------------------------------

def test_text_similarity_identical():
    assert text_similarity("hello world", "hello world") == 1.0


def test_text_similarity_empty_both():
    assert text_similarity("", "") == 1.0


def test_text_similarity_disjoint():
    assert text_similarity("abcdefgh", "xyzwvuts") < 0.1


def test_text_similarity_normalises_whitespace():
    assert text_similarity("a b c", "a  b\nc") == 1.0


# ---------------------------------------------------------------------------
# count_headings + heading_structure_score
# ---------------------------------------------------------------------------

def test_count_headings_per_level():
    text = "# h1\n## h2\n### h3\n## another h2\n"
    assert count_headings(text) == {"h1": 1, "h2": 2, "h3": 1, "h4": 0, "h5": 0, "h6": 0}


def test_count_headings_ignores_seven_hashes():
    assert count_headings("####### too deep")["h6"] == 0


@pytest.mark.parametrize("ref,cand,expected", [
    ("# t", "# t", 1.0),
    ("# a\n# b", "# a", 0.5),
    ("# t", "## t", 0.0),
    ("", "", 1.0),
])
def test_heading_structure_score(ref, cand, expected):
    assert heading_structure_score(ref, cand) == pytest.approx(expected)


def test_heading_structure_no_inflation_from_unused_levels():
    """Pages with only h1+h2 must not score 1.0 on h3-h6 (the bug we fixed in 2.8)."""
    score = heading_structure_score("# x\n## y", "# x")
    # h1 matches (1.0), h2 has ref but not cand (0.0). h3-h6 skipped. Average = 0.5.
    assert score == pytest.approx(0.5)


# ---------------------------------------------------------------------------
# count_lists + list_structure_score
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("text,bullets,numbered", [
    ("- a\n- b\n", 2, 0),
    ("1. a\n2. b\n", 0, 2),
    ("* a\n+ b\n- c\n", 3, 0),
    ("plain text", 0, 0),
    ("  - indented", 1, 0),
])
def test_count_lists(text, bullets, numbered):
    assert count_lists(text) == {"bullets": bullets, "numbered": numbered}


def test_list_structure_score_match():
    assert list_structure_score("- a\n- b", "- x\n- y") == 1.0


def test_list_structure_score_zero_on_only_one_side():
    assert list_structure_score("- a", "no list here") == 0.0


def test_list_structure_score_both_empty():
    assert list_structure_score("", "") == 1.0


# ---------------------------------------------------------------------------
# count_tables + table_structure_score
# ---------------------------------------------------------------------------

def test_count_tables_one():
    text = "| a | b |\n|---|---|\n| 1 | 2 |\n"
    assert count_tables(text) == 1


def test_count_tables_two():
    text = "|a|b|\n|---|---|\n|1|2|\n\n|c|d|\n|---|---|\n|3|4|\n"
    assert count_tables(text) == 2


def test_table_structure_score_both_empty():
    assert table_structure_score("plain", "plain") == 1.0


# ---------------------------------------------------------------------------
# count_code_blocks + code_block_score
# ---------------------------------------------------------------------------

def test_count_code_blocks_counts_fences():
    text = "```python\nx = 1\n```\n```\ny = 2\n```\n"
    assert count_code_blocks(text) == 4


def test_code_block_score_match():
    a = "```\nx\n```"
    assert code_block_score(a, a) == 1.0


# ---------------------------------------------------------------------------
# count_paragraphs + paragraph_structure_score
# ---------------------------------------------------------------------------

def test_count_paragraphs_excludes_headings_and_code():
    text = "# heading\n\nfirst para\n\nsecond para\n\n```\ncode\n```\n\nthird para"
    assert count_paragraphs(text) == 3


@pytest.mark.parametrize("ref_n,cand_n", [
    (5, 5),
    (5, 6),
    (5, 4),
])
def test_paragraph_structure_within_tolerance(ref_n, cand_n):
    ref = "\n\n".join(["p"] * ref_n)
    cand = "\n\n".join(["p"] * cand_n)
    assert paragraph_structure_score(ref, cand) == 1.0


def test_paragraph_structure_outside_tolerance():
    ref = "\n\n".join(["p"] * 10)
    cand = "p"
    assert paragraph_structure_score(ref, cand) < 1.0


# ---------------------------------------------------------------------------
# word_overlap (Jaccard)
# ---------------------------------------------------------------------------

def test_word_overlap_identical():
    assert calculate_word_overlap("a b c", "a b c") == 1.0


def test_word_overlap_disjoint():
    assert calculate_word_overlap("a b", "x y") == 0.0


def test_word_overlap_partial():
    # {a,b,c} vs {b,c,d} → intersection 2, union 4 → 0.5
    assert calculate_word_overlap("a b c", "b c d") == 0.5


def test_word_overlap_case_insensitive():
    assert calculate_word_overlap("Hello World", "hello world") == 1.0


# ---------------------------------------------------------------------------
# evaluate_conversion
# ---------------------------------------------------------------------------

def test_evaluate_conversion_returns_all_metrics_and_token_usage():
    result = evaluate_conversion(
        reference="# t\n\nbody",
        candidate="# t\n\nbody",
        page_number=1,
        strategy="text",
        model="m",
        prompt_variant="default",
        timing_ms=100.0,
        token_usage=42,
    )
    assert isinstance(result, EvaluationResult)
    assert result.token_usage == 42
    assert result.metrics["text_similarity"] == 1.0
    assert result.error is None


def test_evaluate_conversion_with_error_zeroes_metrics():
    result = evaluate_conversion(
        reference="# t",
        candidate="",
        page_number=1,
        strategy="text",
        model="m",
        prompt_variant="default",
        timing_ms=10.0,
        error="HTTP 500",
    )
    assert result.error == "HTTP 500"
    assert all(v == 0.0 for v in result.metrics.values())


# ---------------------------------------------------------------------------
# aggregate_results
# ---------------------------------------------------------------------------

def _mk(strategy="text", model="m", page=1, similarity=0.5, timing=100.0, error=None):
    return EvaluationResult(
        page_number=page,
        strategy=strategy,
        model=model,
        prompt_variant="default",
        metrics={
            "text_similarity": similarity,
            "heading_structure": similarity,
            "list_structure": similarity,
            "table_structure": similarity,
            "code_block_score": similarity,
            "paragraph_structure": similarity,
            "word_overlap": similarity,
        },
        timing_ms=timing,
        error=error,
    )


def test_aggregate_groups_by_strategy_and_model():
    results = [
        _mk(strategy="text", model="m1", similarity=1.0),
        _mk(strategy="image", model="m1", similarity=0.5),
        _mk(strategy="text", model="m2", similarity=0.0),
    ]
    summary = aggregate_results(results)
    assert summary["total_pages"] == 3
    assert set(summary["by_strategy"].keys()) == {"text", "image"}
    assert summary["by_strategy"]["text"]["count"] == 2
    assert set(summary["by_model"].keys()) == {"m1", "m2"}


def test_aggregate_filters_errored_results():
    results = [
        _mk(similarity=1.0),
        _mk(similarity=0.0, error="boom"),
    ]
    summary = aggregate_results(results)
    assert summary["total_pages"] == 1
    assert summary["error_count"] == 1


def test_aggregate_handles_all_errors():
    summary = aggregate_results([_mk(error="boom")])
    assert "error" in summary


def test_aggregate_handles_empty_input():
    summary = aggregate_results([])
    assert "error" in summary
