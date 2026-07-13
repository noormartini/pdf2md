"""Tests for the paired sign-flip permutation test."""

import json
from pathlib import Path

from evaluation.significance import paired_permutation_test, load_paired_scores, METRICS


def test_all_zero_diffs_give_p_one():
    assert paired_permutation_test([0.0] * 20) == 1.0


def test_empty_diffs_give_p_one():
    assert paired_permutation_test([]) == 1.0


def test_consistent_diffs_give_small_p():
    p = paired_permutation_test([0.5] * 20, n_resamples=10_000)
    assert p < 0.01


def test_sign_symmetric_diffs_give_large_p():
    p = paired_permutation_test([0.5, -0.5] * 10, n_resamples=10_000)
    assert p > 0.5


def test_zeros_do_not_change_result():
    diffs = [0.5] * 10
    p_plain = paired_permutation_test(diffs, n_resamples=10_000)
    p_padded = paired_permutation_test(diffs + [0.0] * 50, n_resamples=10_000)
    assert p_plain < 0.01 and p_padded < 0.01


def test_load_paired_scores_computes_a_minus_b(tmp_path: Path):
    def entry(strategy, page, value):
        return {
            "pdf_path": "doc.pdf",
            "page_number": page,
            "strategy": strategy,
            "metrics": {m: value for m in METRICS},
        }

    results = [entry("adaptive", 1, 0.9), entry("text", 1, 0.7),
               entry("adaptive", 2, 0.5), entry("text", 2, 0.5)]
    path = tmp_path / "results.json"
    path.write_text(json.dumps(results))

    diffs = load_paired_scores(str(path), "adaptive", "text")
    for m in METRICS:
        assert diffs[m] == [0.9 - 0.7, 0.0]
