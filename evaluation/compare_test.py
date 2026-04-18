"""Tests for evaluation/compare.py — focuses on run_combinations with a fake runner.

The runner injection means we can exercise the orchestration loop without
touching fitz, the LLM, or the filesystem (apart from reference loading,
which we point at a tmp dir).
"""

import json
from pathlib import Path

import pytest

from evaluation.compare import (
    ExperimentConfig,
    load_experiment_config,
    load_reference,
    run_combinations,
    save_results,
)
from strategies.result import ConversionResult


def _cfg(reference_dir: str, **overrides) -> ExperimentConfig:
    base = dict(
        name="test",
        input_pdf="unused",
        reference_dir=reference_dir,
        strategies=["text"],
        models=["m1"],
        prompt_variants=["default"],
        temperatures=[0.0],
        max_pages=2,
    )
    base.update(overrides)
    return ExperimentConfig(**base)


def _write_refs(reference_dir: Path, n: int) -> None:
    reference_dir.mkdir(parents=True, exist_ok=True)
    for i in range(1, n + 1):
        (reference_dir / f"page_{i:03d}.md").write_text(f"# Reference page {i}\n", encoding="utf-8")


# ---------------------------------------------------------------------------
# load_reference
# ---------------------------------------------------------------------------

def test_load_reference_zero_padded(tmp_path: Path):
    _write_refs(tmp_path, 1)
    assert "Reference page 1" in load_reference(str(tmp_path), 1)


def test_load_reference_unpadded_fallback(tmp_path: Path):
    (tmp_path / "page_42.md").write_text("# unpadded", encoding="utf-8")
    assert "unpadded" in load_reference(str(tmp_path), 42)


def test_load_reference_missing_returns_none(tmp_path: Path):
    assert load_reference(str(tmp_path), 99) is None


# ---------------------------------------------------------------------------
# load_experiment_config
# ---------------------------------------------------------------------------

def test_load_experiment_config_applies_defaults(tmp_path: Path):
    p = tmp_path / "exp.json"
    p.write_text(json.dumps({"input_pdf": "x.pdf", "reference_dir": "refs"}), encoding="utf-8")
    cfg = load_experiment_config(str(p))
    assert cfg.input_pdf == "x.pdf"
    assert cfg.strategies == ["text"]
    assert cfg.prompt_variants == ["default"]
    assert cfg.temperatures == [0.0]
    assert cfg.max_pages is None


# ---------------------------------------------------------------------------
# run_combinations — combinatorics with a fake runner
# ---------------------------------------------------------------------------

def _make_fake_runner(record: list):
    def fake(**kwargs):
        record.append(kwargs)
        return ConversionResult(
            markdown=f"# {kwargs['strategy']} page",
            timing_ms=1.5,
            token_usage=10,
        ), None
    return fake


def test_run_combinations_invokes_runner_for_every_combination(tmp_path: Path):
    _write_refs(tmp_path, 2)
    cfg = _cfg(
        str(tmp_path),
        strategies=["text", "image"],
        models=["m1", "m2"],
        prompt_variants=["default"],
        temperatures=[0.0, 0.5],
    )
    record: list = []
    results = run_combinations(
        pages=["page text 1", "page text 2"],
        images=["img1", "img2"],
        config=cfg,
        runner=_make_fake_runner(record),
    )
    # 2 strategies × 2 models × 1 prompt × 2 temps × 2 pages = 16
    assert len(record) == 16
    assert len(results) == 16


def test_run_combinations_records_token_usage_and_timing(tmp_path: Path):
    _write_refs(tmp_path, 1)
    cfg = _cfg(str(tmp_path), max_pages=1)

    def fake(**kwargs):
        return ConversionResult(markdown="ok", timing_ms=42.0, token_usage=99), None

    results = run_combinations(["t"], ["i"], cfg, runner=fake)
    assert results[0].token_usage == 99
    assert results[0].timing_ms == 42.0


def test_run_combinations_skips_pages_with_no_reference(tmp_path: Path):
    _write_refs(tmp_path, 1)  # only page 1 has a reference
    cfg = _cfg(str(tmp_path), max_pages=2)
    record: list = []
    results = run_combinations(["t1", "t2"], ["i1", "i2"], cfg, runner=_make_fake_runner(record))
    # Page 2 reference missing → skipped before runner is called
    assert len(record) == 1
    assert len(results) == 1
    assert results[0].page_number == 1


def test_run_combinations_records_runner_errors(tmp_path: Path):
    _write_refs(tmp_path, 1)
    cfg = _cfg(str(tmp_path), max_pages=1)

    def failing(**kwargs):
        return None, "HTTP 500"

    results = run_combinations(["t"], ["i"], cfg, runner=failing)
    assert results[0].error == "HTTP 500"
    # Errored runs zero out metrics
    assert all(v == 0.0 for v in results[0].metrics.values())


def test_run_combinations_passes_correct_args_to_runner(tmp_path: Path):
    _write_refs(tmp_path, 1)
    cfg = _cfg(
        str(tmp_path),
        strategies=["hybrid"],
        models=["mymodel"],
        prompt_variants=["default"],
        temperatures=[0.7],
        base_url="http://example.test",
        max_pages=1,
    )
    record: list = []
    run_combinations(["my page text"], ["my image"], cfg, runner=_make_fake_runner(record))
    call = record[0]
    assert call["strategy"] == "hybrid"
    assert call["model"] == "mymodel"
    assert call["temperature"] == 0.7
    assert call["base_url"] == "http://example.test"
    assert call["page_text"] == "my page text"
    assert call["page_image"] == "my image"


# ---------------------------------------------------------------------------
# save_results
# ---------------------------------------------------------------------------

def test_save_results_writes_serializable_json(tmp_path: Path):
    from evaluation.metrics import EvaluationResult

    results = [EvaluationResult(
        page_number=1,
        strategy="text",
        model="m",
        prompt_variant="default",
        metrics={"text_similarity": 0.5},
        timing_ms=10.0,
        token_usage=42,
    )]
    out = tmp_path / "r.json"
    save_results(results, str(out))
    loaded = json.loads(out.read_text(encoding="utf-8"))
    assert loaded[0]["page_number"] == 1
    assert loaded[0]["token_usage"] == 42
