"""Experiment runner for PDF-to-Markdown conversion comparisons."""

import json
import os
import re
import time
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Callable, Optional

import fitz

from strategies.text_only import text_strategy
from strategies.image_only import image_strategy
from strategies.hybrid import hybrid_strategy
from strategies.adaptive import analyze_page, adaptive_strategy, render_page_as_base64, PageType
from strategies.result import ConversionResult
from extraction.text import extract_pages_from_pdf, extract_monospace_lines
from extraction.image import extract_pages_from_pdf as extract_images_from_pdf
from evaluation.metrics import evaluate_conversion, EvaluationResult, aggregate_results
from postprocess import clean_page, postprocess_markdown


_PAGE_MARKER_RE = re.compile(r"<!--\s*Page\s+(.+?)\s*-->")


def _page_label(doc: fitz.Document, index: int) -> str:
    """Return the printed page label (e.g. 'v', '3') for a 0-based page index.

    Mirrors app.py's `_page_label` exactly so postprocess_markdown sees the
    same page-comment format the real pipeline produces.
    """
    label = doc[index].get_label()
    return label if label else str(index + 1)


def _split_postprocessed_pages(joined: str, expected_count: int) -> list[str]:
    """Split a postprocess_markdown'd document back into per-page bodies.

    Splits on the `<!-- Page X -->` markers `clean_page` output was joined
    with, discarding the marker itself so the returned strings are directly
    comparable to what the old (pre-fix) evaluation scored.
    """
    parts = _PAGE_MARKER_RE.split(joined)
    # re.split with a capturing group yields [pre, label1, body1, label2, body2, ...]
    bodies = [parts[i] for i in range(2, len(parts), 2)]
    if len(bodies) != expected_count:
        print(f"  ⚠ Page split mismatch: expected {expected_count}, got {len(bodies)}")
    return bodies


@dataclass
class ExperimentConfig:
    """Configuration for a single experiment run."""
    name: str
    input_pdfs: list[str]
    reference_dir: str
    strategies: list[str]
    models: list[str]
    prompt_variants: list[str]
    temperatures: list[float]
    max_pages: Optional[int] = None
    base_url: str = "http://localhost:1234/v1"
    pdf_categories: dict[str, str] = None

    def __post_init__(self):
        if self.pdf_categories is None:
            self.pdf_categories = {}


def load_experiment_config(config_path: str) -> ExperimentConfig:
    """Load experiment configuration from JSON file."""
    with open(config_path, "r") as f:
        data = json.load(f)

    raw = data.get("input_pdfs") or [data["input_pdf"]]
    input_pdfs: list[str] = []
    pdf_categories: dict[str, str] = {}
    for entry in raw:
        if isinstance(entry, str):
            input_pdfs.append(entry)
        else:
            path = entry["path"]
            input_pdfs.append(path)
            if "category" in entry:
                pdf_categories[path] = entry["category"]

    return ExperimentConfig(
        name=data.get("name", "experiment"),
        input_pdfs=input_pdfs,
        pdf_categories=pdf_categories,
        reference_dir=data["reference_dir"],
        strategies=data.get("strategies", ["text"]),
        models=data.get("models", ["default"]),
        prompt_variants=data.get("prompt_variants", ["default"]),
        temperatures=data.get("temperatures", [0.0]),
        max_pages=data.get("max_pages"),
        base_url=data.get("base_url", "http://localhost:1234/v1"),
    )


def load_reference(reference_dir: str, page_number: int, pdf_path: str = "") -> Optional[str]:
    """Load reference markdown for a specific page of a specific PDF."""
    candidates: list[Path] = []

    if pdf_path:
        pdf_stem = Path(pdf_path).stem
        candidates += [
            Path(reference_dir) / pdf_stem / f"page_{page_number:03d}.md",
            Path(reference_dir) / pdf_stem / f"page_{page_number}.md",
        ]

    candidates += [
        Path(reference_dir) / f"page_{page_number:03d}.md",
        Path(reference_dir) / f"page_{page_number}.md",
    ]

    for path in candidates:
        if path.exists():
            return path.read_text(encoding="utf-8")

    return None


def run_strategy(
    strategy: str,
    base_url: str,
    model: str,
    pdf_path: str,
    page_num: int,
    page_text: str,
    page_image: Optional[str],
    temperature: float,
    max_tokens: int,
    prompt_variant: str,
    page_type: Optional[PageType] = None,
    figures_dir: str = "output/figures",
) -> tuple[Optional[ConversionResult], Optional[str]]:
    """Run a conversion strategy and return (result, error)."""
    try:
        match strategy:
            case "text":
                result = text_strategy(
                    base_url=base_url,
                    model_name=model,
                    pdf_path=pdf_path,
                    page_num=page_num,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    prompt_variant=prompt_variant,
                    figures_dir=figures_dir,
                )
            case "image":
                if page_image is None:
                    raise ValueError("Image strategy requires page image")
                result = image_strategy(
                    base_url=base_url,
                    model_name=model,
                    images=[page_image],
                    temperature=temperature,
                    max_tokens=max_tokens,
                    prompt_variant=prompt_variant,
                )
            case "hybrid":
                if page_image is None:
                    raise ValueError("Hybrid strategy requires page image")
                result = hybrid_strategy(
                    base_url=base_url,
                    model_name=model,
                    text=page_text,
                    images=[page_image],
                    temperature=temperature,
                    max_tokens=max_tokens,
                    prompt_variant=prompt_variant,
                )
            case "adaptive":
                if page_type is None:
                    raise ValueError("Adaptive strategy requires a pre-computed page_type")
                if page_image is None:
                    raise ValueError("Adaptive strategy requires page image")
                result = adaptive_strategy(
                    base_url=base_url,
                    model_name=model,
                    pdf_path=pdf_path,
                    page_num=page_num,
                    page_image=page_image,
                    page_type=page_type,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    figures_dir=figures_dir,
                )
            case _:
                raise ValueError(f"Unknown strategy: {strategy}")

        return result, None

    except Exception as e:
        return None, str(e)


def run_strategy_with_retry(
    *args,
    max_retries: int = 3,
    retry_delay: float = 5.0,
    **kwargs,
) -> tuple[ConversionResult | None, str | None]:
    """Call run_strategy with automatic retry on transient errors (e.g. timeouts)."""
    last_error: str | None = None
    for attempt in range(1, max_retries + 1):
        result, error = run_strategy(*args, **kwargs)
        if error is None:
            return result, None
        last_error = error
        if attempt < max_retries:
            print(f"  ↻ Retry {attempt}/{max_retries - 1} after error: {error[:80]}")
            time.sleep(retry_delay)
    return None, last_error


def _done_key(pdf_path: str, page_number: int, strategy: str, model: str,
               prompt_variant: str, temperature: float) -> tuple:
    return (pdf_path, page_number, strategy, model, prompt_variant, temperature)


def load_existing_results(output_path: str) -> tuple[list[EvaluationResult], set[tuple]]:
    """Load previously saved results and build a completed-key set for resume.

    Only successful results (no error) count as done — failed pages are retried.
    """
    if not os.path.exists(output_path):
        return [], set()
    try:
        with open(output_path) as f:
            data = json.load(f)
        results = [EvaluationResult(**r) for r in data]
        # Keep all results in memory but only mark error-free ones as done
        done = {
            _done_key(r.pdf_path, r.page_number, r.strategy, r.model,
                      r.prompt_variant, r.temperature)
            for r in results
            if not r.error
        }
        errors = sum(1 for r in results if r.error)
        print(f"Resuming: {len(results)} results loaded, {len(done)} successful, {errors} will be retried.")
        # Remove error results so they get re-run and replaced
        results = [r for r in results if not r.error]
        return results, done
    except Exception:
        return [], set()


def prepare_pages(config: ExperimentConfig, pdf_path: str) -> tuple[list[str], list[str]]:
    """Extract text and rendered page images for a single PDF."""
    if config.max_pages is None:
        with fitz.open(pdf_path) as doc:
            max_pages = len(doc)
    else:
        max_pages = config.max_pages

    print("Extracting text from PDF...")
    pages = extract_pages_from_pdf(pdf_path, max_pages=max_pages)

    print("Extracting images from PDF...")
    images = extract_images_from_pdf(pdf_path, max_pages=max_pages)

    return pages, images


def run_combinations(
    pages: list[str],
    images: list[str],
    config: ExperimentConfig,
    pdf_path: str,
    max_tokens: int = 4096,
    runner: Callable = run_strategy_with_retry,
    category: Optional[str] = None,
    all_results: list[EvaluationResult] = None,
    done_keys: set[tuple] = None,
    output_path: str = "",
) -> list[EvaluationResult]:
    """Loop over every (strategy, model, prompt, temperature) combination.

    For each combination, every page is converted first, then run through
    the same two-stage postprocessing the real pipeline (app.py) applies —
    `clean_page()` per page, then `postprocess_markdown()` once on the whole
    joined document — before being split back apart and scored. This mirrors
    what a real user of the tool actually receives, rather than scoring the
    raw pre-postprocessing strategy output.

    Skips a combination entirely if all of its pages are already present in
    `done_keys`; otherwise the whole combination is redone (postprocessing
    needs every page together, so partial per-page resume isn't possible
    within a combination). Saves incrementally to `output_path` after each
    completed combination.
    """
    if all_results is None:
        all_results = []
    if done_keys is None:
        done_keys = set()

    new_results: list[EvaluationResult] = []
    num_pages = len(pages)

    doc = fitz.open(pdf_path)
    limit = config.max_pages if config.max_pages else len(doc)
    limit = min(limit, len(doc), num_pages)
    page_labels = [_page_label(doc, i) for i in range(limit)]
    raw_page_texts = [doc[i].get_text("text") for i in range(limit)]
    code_lines_all = [extract_monospace_lines(doc[i]) for i in range(limit)]

    page_analyses = None
    adaptive_images = None
    if "adaptive" in config.strategies:
        print("Pre-analysing pages for adaptive strategy...")
        page_analyses = [analyze_page(doc[i]) for i in range(limit)]
        adaptive_images = [render_page_as_base64(doc[i]) for i in range(limit)]
        print(f"  Page types: {[a.page_type.value for a in page_analyses]}\n")
    doc.close()

    total_combinations = (
        len(config.strategies)
        * len(config.models)
        * len(config.prompt_variants)
        * len(config.temperatures)
    )
    current = 0

    for strategy in config.strategies:
        for model in config.models:
            for prompt_variant in config.prompt_variants:
                for temperature in config.temperatures:
                    current += 1
                    combo_keys = [
                        _done_key(pdf_path, i + 1, strategy, model, prompt_variant, temperature)
                        for i in range(num_pages)
                    ]
                    if all(k in done_keys for k in combo_keys):
                        print(f"[{current}/{total_combinations}] "
                              f"{strategy} | {model} | skipped (already done)")
                        continue

                    print(f"[{current}/{total_combinations}] "
                          f"{strategy} | {model} | prompt={prompt_variant} | temp={temperature}")

                    # Stage 0: convert every page, raw (matches the old per-page loop).
                    raw_results: list[tuple] = []  # (markdown, timing_ms, token_usage, llm_calls, error)
                    for page_idx in range(num_pages):
                        page_text = pages[page_idx]

                        if strategy == "adaptive" and page_analyses is not None:
                            page_image = adaptive_images[page_idx] if page_idx < len(adaptive_images) else None
                            page_type = page_analyses[page_idx].page_type if page_idx < len(page_analyses) else None
                        else:
                            page_image = images[page_idx] if images else None
                            page_type = None

                        result, error = runner(
                            strategy=strategy,
                            base_url=config.base_url,
                            model=model,
                            pdf_path=pdf_path,
                            page_num=page_idx,
                            page_text=page_text,
                            page_image=page_image,
                            temperature=temperature,
                            max_tokens=max_tokens,
                            prompt_variant=prompt_variant,
                            page_type=page_type,
                        )
                        markdown = result.markdown if result else ""
                        timing_ms = result.timing_ms if result else 0.0
                        token_usage = result.token_usage if result else None
                        llm_calls = result.llm_calls if result else 0
                        if error:
                            print(f"  ✗ Page {page_idx + 1}: {error}")
                        raw_results.append((markdown, timing_ms, token_usage, llm_calls, error))

                    # Stage 1: clean_page() per page — same args app.py passes per strategy.
                    cleaned_pages: list[str] = []
                    for page_idx, (markdown, *_rest) in enumerate(raw_results):
                        label = page_labels[page_idx] if page_idx < len(page_labels) else str(page_idx + 1)
                        if strategy == "text":
                            raw_text = raw_page_texts[page_idx] if page_idx < len(raw_page_texts) else ""
                            code_lines = code_lines_all[page_idx] if page_idx < len(code_lines_all) else None
                            cleaned = clean_page(markdown, raw_page_text=raw_text, code_lines=code_lines)
                        elif strategy == "adaptive":
                            raw_text = raw_page_texts[page_idx] if page_idx < len(raw_page_texts) else ""
                            is_text_page = (
                                page_analyses is not None
                                and page_idx < len(page_analyses)
                                and page_analyses[page_idx].page_type == PageType.TEXT
                            )
                            code_lines = code_lines_all[page_idx] if is_text_page and page_idx < len(code_lines_all) else None
                            cleaned = clean_page(markdown, raw_page_text=raw_text, code_lines=code_lines)
                        else:  # image, hybrid
                            cleaned = clean_page(markdown)
                        cleaned_pages.append(f"<!-- Page {label} -->\n\n{cleaned}")

                    # Stage 2: join + postprocess_markdown() once, then split back apart.
                    joined = "\n\n---\n\n".join(cleaned_pages)
                    joined = postprocess_markdown(joined)
                    final_pages = _split_postprocessed_pages(joined, num_pages)

                    # Score each page against its reference using the final, postprocessed text.
                    for page_idx in range(num_pages):
                        page_num = page_idx + 1
                        key = combo_keys[page_idx]
                        if key in done_keys:
                            continue

                        reference = load_reference(config.reference_dir, page_num, pdf_path)
                        if reference is None:
                            print(f"  ⚠ No reference found for page {page_num}, skipping")
                            continue

                        _, timing_ms, token_usage, llm_calls, error = raw_results[page_idx]
                        final_markdown = final_pages[page_idx] if page_idx < len(final_pages) else ""

                        eval_result = evaluate_conversion(
                            reference=reference,
                            candidate=final_markdown,
                            page_number=page_num,
                            strategy=strategy,
                            model=model,
                            prompt_variant=prompt_variant,
                            temperature=temperature,
                            timing_ms=timing_ms,
                            token_usage=token_usage,
                            error=error,
                            category=category,
                            llm_calls=llm_calls,
                            pdf_path=pdf_path,
                        )
                        new_results.append(eval_result)
                        all_results.append(eval_result)
                        done_keys.add(key)

                    print(f"  ✓ Combination done ({num_pages} pages)")
                    if output_path:
                        save_results(all_results, output_path)

    return new_results


def run_experiment(
    config: ExperimentConfig,
    max_tokens: int = 4096,
    output_path: str = "",
) -> list[EvaluationResult]:
    """Run a full experiment across all combinations defined in the config."""
    print(f"\n{'='*60}")
    print(f"Experiment: {config.name}")
    print(f"{'='*60}")
    print(f"Input PDFs: {config.input_pdfs}")
    print(f"Reference dir: {config.reference_dir}")
    print(f"Strategies: {config.strategies}")
    print(f"Models: {config.models}")
    print(f"Prompt variants: {config.prompt_variants}")
    print(f"Temperatures: {config.temperatures}")
    print(f"{'='*60}\n")

    all_results, done_keys = load_existing_results(output_path)

    for pdf_path in config.input_pdfs:
        category = config.pdf_categories.get(pdf_path)
        print(f"--- PDF: {pdf_path} (category: {category or 'unset'}) ---")
        pages, images = prepare_pages(config, pdf_path)
        print(f"Processing {len(pages)} pages\n")
        run_combinations(
            pages, images, config, pdf_path,
            max_tokens=max_tokens,
            category=category,
            all_results=all_results,
            done_keys=done_keys,
            output_path=output_path,
        )
    return all_results


def save_results(results: list[EvaluationResult], output_path: str) -> None:
    """Save evaluation results to JSON file. Creates the parent dir if needed."""
    serializable = [asdict(r) for r in results]

    parent = os.path.dirname(output_path)
    if parent:
        os.makedirs(parent, exist_ok=True)

    with open(output_path, "w") as f:
        json.dump(serializable, f, indent=2)


def run_experiment_from_config(
    config_path: str,
    output_path: str,
    max_tokens: int = 4096,
) -> list[EvaluationResult]:
    """Load experiment config from JSON, run experiment, and save results."""
    config = load_experiment_config(config_path)
    results = run_experiment(config, max_tokens=max_tokens, output_path=output_path)
    save_results(results, output_path)
    print(f"\nResults saved to {output_path}")

    summary = aggregate_results(results)
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)

    if "error" in summary:
        print(f"Error: {summary['error']}")
    else:
        print(f"Total pages evaluated: {summary['total_pages']}")
        print(f"Errors: {summary['error_count']}")
        print("\nOverall scores:")
        for metric, score in summary["overall_scores"].items():
            print(f"  {metric}: {score:.3f}")

    return results


def main():
    """CLI entry point for running experiments."""
    import argparse

    parser = argparse.ArgumentParser(description="Run PDF-to-Markdown conversion experiments")
    parser.add_argument("-c", "--config", required=True, help="Path to experiment config JSON")
    parser.add_argument(
        "-o", "--output",
        default="output/results.json",
        help="Path to save results JSON (default: output/results.json)",
    )
    parser.add_argument("--max-tokens", type=int, default=4096, help="Max tokens for LLM")

    args = parser.parse_args()

    run_experiment_from_config(args.config, args.output, args.max_tokens)


if __name__ == "__main__":
    main()
