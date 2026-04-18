"""Evaluation metrics for comparing PDF-to-Markdown conversion results."""

import difflib
import re
from dataclasses import dataclass
from typing import Optional


@dataclass
class MetricResult:
    """Result of a single metric evaluation."""
    name: str
    value: float
    unit: str = ""
    description: str = ""


@dataclass
class EvaluationResult:
    """Complete evaluation result for one conversion."""
    page_number: int
    strategy: str
    model: str
    prompt_variant: str
    metrics: dict[str, float]
    timing_ms: float
    token_usage: Optional[int] = None
    error: Optional[str] = None


def text_similarity(reference: str, candidate: str) -> float:
    """
    Calculate text similarity using difflib SequenceMatcher.
    Returns a score between 0.0 (completely different) and 1.0 (identical).
    """
    # Normalize whitespace for fair comparison
    ref_normalized = " ".join(reference.split())
    cand_normalized = " ".join(candidate.split())

    return difflib.SequenceMatcher(
        None, ref_normalized, cand_normalized
    ).ratio()


def count_headings(text: str) -> dict[str, int]:
    """Count headings by level in markdown text."""
    counts = {"h1": 0, "h2": 0, "h3": 0, "h4": 0, "h5": 0, "h6": 0}

    for line in text.split("\n"):
        stripped = line.lstrip()
        if stripped.startswith("#"):
            level = len(stripped) - len(stripped.lstrip("#"))
            if 1 <= level <= 6:
                counts[f"h{level}"] += 1

    return counts


def heading_structure_score(reference: str, candidate: str) -> float:
    """
    Compare heading structure between reference and candidate.
    Returns similarity score based on heading counts per level.

    Only levels used by either side contribute to the score, so a page that
    only has H1+H2 is not artificially inflated by perfect H3-H6 matches.
    """
    ref_counts = count_headings(reference)
    cand_counts = count_headings(candidate)

    similarities = []
    for level in ref_counts.keys():
        ref_val = ref_counts[level]
        cand_val = cand_counts[level]

        if ref_val == 0 and cand_val == 0:
            continue
        if ref_val == 0 or cand_val == 0:
            similarities.append(0.0)
        else:
            similarities.append(min(ref_val / cand_val, cand_val / ref_val))

    return sum(similarities) / len(similarities) if similarities else 1.0


def count_lists(text: str) -> dict[str, int]:
    """Count bulleted and numbered lists in markdown text."""
    bullet_pattern = re.compile(r"^\s*[-*+]\s+")
    number_pattern = re.compile(r"^\s*\d+\.\s+")

    bullets = 0
    numbers = 0

    for line in text.split("\n"):
        if bullet_pattern.match(line):
            bullets += 1
        elif number_pattern.match(line):
            numbers += 1

    return {"bullets": bullets, "numbered": numbers}


def list_structure_score(reference: str, candidate: str) -> float:
    """Compare list structure between reference and candidate."""
    ref_counts = count_lists(reference)
    cand_counts = count_lists(candidate)

    total_ref = ref_counts["bullets"] + ref_counts["numbered"]
    total_cand = cand_counts["bullets"] + cand_counts["numbered"]

    if total_ref == 0 and total_cand == 0:
        return 1.0
    if total_ref == 0 or total_cand == 0:
        return 0.0

    return min(total_ref / total_cand, total_cand / total_ref)


def count_tables(text: str) -> int:
    """Count markdown tables in text."""
    # Simple heuristic: count lines that look like table separators
    separator_pattern = re.compile(r"^\s*[-:|]+\s*\|\s*[-:|]+\s*$")
    separators = sum(1 for line in text.split("\n") if separator_pattern.match(line))

    # Each table needs at least one separator, so count separators as table indicators
    return separators


def table_structure_score(reference: str, candidate: str) -> float:
    """Compare table presence between reference and candidate."""
    ref_tables = count_tables(reference)
    cand_tables = count_tables(candidate)

    if ref_tables == 0 and cand_tables == 0:
        return 1.0
    if ref_tables == 0 or cand_tables == 0:
        return 0.0

    return min(ref_tables / cand_tables, cand_tables / ref_tables)


def count_code_blocks(text: str) -> int:
    """Count fenced code blocks in markdown text."""
    # Count opening fence markers
    return len(re.findall(r"^```", text, re.MULTILINE))


def code_block_score(reference: str, candidate: str) -> float:
    """Compare code block presence between reference and candidate."""
    ref_blocks = count_code_blocks(reference)
    cand_blocks = count_code_blocks(candidate)

    if ref_blocks == 0 and cand_blocks == 0:
        return 1.0
    if ref_blocks == 0 or cand_blocks == 0:
        return 0.0

    return min(ref_blocks / cand_blocks, cand_blocks / ref_blocks)


def count_paragraphs(text: str) -> int:
    """Count paragraphs in markdown text, excluding headings and code blocks.

    Code blocks may be fully contained in one block (no blank line between
    the fences) or span multiple blocks. We track the open/closed state by
    counting fence markers rather than toggling once per block, so a
    self-contained ``` … ``` does not leave the state stuck "inside code".
    """
    blocks = [b.strip() for b in text.split("\n\n") if b.strip()]
    paragraphs = 0
    in_code = False

    for block in blocks:
        fence_count = block.count("```")
        if fence_count:
            # Odd → this block flips the in/out state; even → self-contained.
            if fence_count % 2 == 1:
                in_code = not in_code
            continue
        if in_code:
            continue
        if block.startswith("#"):
            continue
        paragraphs += 1

    return paragraphs


def paragraph_structure_score(reference: str, candidate: str) -> float:
    """Compare paragraph count between reference and candidate."""
    ref_para = count_paragraphs(reference)
    cand_para = count_paragraphs(candidate)

    if ref_para == 0 and cand_para == 0:
        return 1.0
    if ref_para == 0:
        return 0.0

    # Allow some tolerance - within 20% is considered good
    ratio = cand_para / ref_para
    if 0.8 <= ratio <= 1.2:
        return 1.0
    elif ratio < 0.8:
        return ratio / 0.8
    else:
        return 1.0 / (ratio / 1.2)


def calculate_word_overlap(reference: str, candidate: str) -> float:
    """Calculate word-level overlap (Jaccard similarity)."""
    ref_words = set(reference.lower().split())
    cand_words = set(candidate.lower().split())

    if not ref_words and not cand_words:
        return 1.0
    if not ref_words or not cand_words:
        return 0.0

    intersection = ref_words & cand_words
    union = ref_words | cand_words

    return len(intersection) / len(union) if union else 0.0


def evaluate_conversion(
    reference: str,
    candidate: str,
    page_number: int,
    strategy: str,
    model: str,
    prompt_variant: str,
    timing_ms: float,
    token_usage: Optional[int] = None,
    error: Optional[str] = None,
) -> EvaluationResult:
    """
    Evaluate a single conversion against a reference.

    Returns an EvaluationResult with all metrics.
    """
    if error:
        return EvaluationResult(
            page_number=page_number,
            strategy=strategy,
            model=model,
            prompt_variant=prompt_variant,
            metrics={
                "text_similarity": 0.0,
                "heading_structure": 0.0,
                "list_structure": 0.0,
                "table_structure": 0.0,
                "code_block_score": 0.0,
                "paragraph_structure": 0.0,
                "word_overlap": 0.0,
            },
            timing_ms=timing_ms,
            token_usage=token_usage,
            error=error,
        )

    metrics = {
        "text_similarity": text_similarity(reference, candidate),
        "heading_structure": heading_structure_score(reference, candidate),
        "list_structure": list_structure_score(reference, candidate),
        "table_structure": table_structure_score(reference, candidate),
        "code_block_score": code_block_score(reference, candidate),
        "paragraph_structure": paragraph_structure_score(reference, candidate),
        "word_overlap": calculate_word_overlap(reference, candidate),
    }

    return EvaluationResult(
        page_number=page_number,
        strategy=strategy,
        model=model,
        prompt_variant=prompt_variant,
        metrics=metrics,
        timing_ms=timing_ms,
        token_usage=token_usage,
    )


def aggregate_results(results: list[EvaluationResult]) -> dict:
    """
    Aggregate multiple evaluation results into summary statistics.

    Returns a dict with:
    - overall_scores: average score per metric across all results
    - by_strategy: scores grouped by strategy
    - by_model: scores grouped by model
    - by_page: scores grouped by page number
    """
    if not results:
        return {"error": "No results to aggregate"}

    # Filter out errors
    valid_results = [r for r in results if not r.error]

    if not valid_results:
        return {"error": "All results had errors"}

    metric_names = list(valid_results[0].metrics.keys())

    # Overall averages
    overall_scores = {}
    for metric in metric_names:
        values = [r.metrics[metric] for r in valid_results]
        overall_scores[metric] = sum(values) / len(values)

    # By strategy
    strategies = set(r.strategy for r in valid_results)
    by_strategy = {}
    for strategy in strategies:
        strat_results = [r for r in valid_results if r.strategy == strategy]
        by_strategy[strategy] = {
            "count": len(strat_results),
            "avg_timing_ms": sum(r.timing_ms for r in strat_results) / len(strat_results),
            "metrics": {
                metric: sum(r.metrics[metric] for r in strat_results) / len(strat_results)
                for metric in metric_names
            }
        }

    # By model
    models = set(r.model for r in valid_results)
    by_model = {}
    for model in models:
        model_results = [r for r in valid_results if r.model == model]
        by_model[model] = {
            "count": len(model_results),
            "avg_timing_ms": sum(r.timing_ms for r in model_results) / len(model_results),
            "metrics": {
                metric: sum(r.metrics[metric] for r in model_results) / len(model_results)
                for metric in metric_names
            }
        }

    # By page
    pages = set(r.page_number for r in valid_results)
    by_page = {}
    for page in sorted(pages):
        page_results = [r for r in valid_results if r.page_number == page]
        by_page[page] = {
            "count": len(page_results),
            "metrics": {
                metric: sum(r.metrics[metric] for r in page_results) / len(page_results)
                for metric in metric_names
            }
        }

    return {
        "total_pages": len(valid_results),
        "error_count": len(results) - len(valid_results),
        "overall_scores": overall_scores,
        "by_strategy": by_strategy,
        "by_model": by_model,
        "by_page": by_page,
    }
