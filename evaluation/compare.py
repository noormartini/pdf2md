"""Experiment runner for PDF-to-Markdown conversion comparisons."""

import json
import time
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Optional

import fitz

from config import Config
from strategies.text_only import text_strategy
from strategies.image_only import image_strategy
from strategies.hybrid import hybrid_strategy
from strategies.adaptive import analyze_page, adaptive_strategy, render_page_as_base64, PageType
from extraction.text import extract_pages_from_pdf
from extraction.image import extract_pages_from_pdf as extract_images_from_pdf
from evaluation.metrics import evaluate_conversion, EvaluationResult, aggregate_results


@dataclass
class ExperimentConfig:
    """Configuration for a single experiment run."""
    name: str
    input_pdf: str
    reference_dir: str
    strategies: list[str]
    models: list[str]
    prompt_variants: list[str]
    temperatures: list[float]
    max_pages: Optional[int] = None
    base_url: str = "http://localhost:1234/v1"


def load_experiment_config(config_path: str) -> ExperimentConfig:
    """Load experiment configuration from JSON file."""
    with open(config_path, "r") as f:
        data = json.load(f)

    return ExperimentConfig(
        name=data.get("name", "experiment"),
        input_pdf=data["input_pdf"],
        reference_dir=data["reference_dir"],
        strategies=data.get("strategies", ["text"]),
        models=data.get("models", ["default"]),
        prompt_variants=data.get("prompt_variants", ["default"]),
        temperatures=data.get("temperatures", [0.0]),
        max_pages=data.get("max_pages"),
        base_url=data.get("base_url", "http://localhost:1234/v1"),
    )


def load_reference(reference_dir: str, page_number: int) -> Optional[str]:
    """Load reference markdown for a specific page."""
    ref_path = Path(reference_dir) / f"page_{page_number:03d}.md"

    if ref_path.exists():
        return ref_path.read_text(encoding="utf-8")

    # Also try without zero-padding
    ref_path = Path(reference_dir) / f"page_{page_number}.md"
    if ref_path.exists():
        return ref_path.read_text(encoding="utf-8")

    return None


def run_strategy(
    strategy: str,
    base_url: str,
    model: str,
    page_text: str,
    page_image: Optional[str],
    temperature: float,
    max_tokens: int,
    prompt_variant: str,
    page_type: Optional[PageType] = None,
) -> tuple[Optional[str], float, Optional[str]]:
    """
    Run a conversion strategy and return (result, timing_ms, error).

    Args:
        strategy:     One of "text", "image", "hybrid", "adaptive".
        page_type:    Pre-computed PageType for "adaptive" strategy (required when
                      strategy=="adaptive").
    """
    start_time = time.perf_counter()

    try:
        match strategy:
            case "text":
                result = text_strategy(
                    base_url=base_url,
                    model_name=model,
                    text=page_text,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    prompt_variant=prompt_variant,
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
                    text=page_text,
                    page_image=page_image,
                    page_type=page_type,
                    temperature=temperature,
                    max_tokens=max_tokens,
                )
            case _:
                raise ValueError(f"Unknown strategy: {strategy}")

        elapsed_ms = (time.perf_counter() - start_time) * 1000
        return result, elapsed_ms, None

    except Exception as e:
        elapsed_ms = (time.perf_counter() - start_time) * 1000
        return None, elapsed_ms, str(e)


def run_experiment(config: ExperimentConfig, max_tokens: int = 4096) -> list[EvaluationResult]:
    """
    Run a full experiment across all strategy/model/prompt/temperature combinations.

    Returns a list of EvaluationResult objects.
    """
    results = []

    print(f"\n{'='*60}")
    print(f"Experiment: {config.name}")
    print(f"{'='*60}")
    print(f"Input PDF: {config.input_pdf}")
    print(f"Reference dir: {config.reference_dir}")
    print(f"Strategies: {config.strategies}")
    print(f"Models: {config.models}")
    print(f"Prompt variants: {config.prompt_variants}")
    print(f"Temperatures: {config.temperatures}")
    print(f"{'='*60}\n")

    # Extract text and images once
    print("Extracting text from PDF...")
    pages = extract_pages_from_pdf(config.input_pdf, max_pages=config.max_pages)

    print("Extracting images from PDF...")
    images = extract_images_from_pdf(config.input_pdf, max_pages=config.max_pages)

    num_pages = len(pages)
    print(f"Processing {num_pages} pages\n")

    # Pre-analyse pages for the adaptive strategy (needs fitz.Page objects)
    page_analyses = None
    if "adaptive" in config.strategies:
        print("Pre-analysing pages for adaptive strategy...")
        doc = fitz.open(config.input_pdf)
        limit = config.max_pages if config.max_pages else len(doc)
        page_analyses = [analyze_page(doc[i]) for i in range(min(limit, len(doc)))]
        # Also build aligned image list for adaptive (render_page_as_base64 per page)
        adaptive_images = [render_page_as_base64(doc[i]) for i in range(min(limit, len(doc)))]
        doc.close()
        print(f"  Page types: {[a.page_type.value for a in page_analyses]}\n")

    total_combinations = (
        len(config.strategies)
        * len(config.models)
        * len(config.prompt_variants)
        * len(config.temperatures)
        * num_pages
    )
    current = 0

    for strategy in config.strategies:
        for model in config.models:
            for prompt_variant in config.prompt_variants:
                for temperature in config.temperatures:
                    for page_idx in range(num_pages):
                        current += 1
                        page_num = page_idx + 1

                        print(f"[{current}/{total_combinations}] "
                              f"Page {page_num} | {strategy} | {model} | "
                              f"prompt={prompt_variant} | temp={temperature}")

                        # Load reference
                        reference = load_reference(config.reference_dir, page_num)
                        if reference is None:
                            print(f"  ⚠ No reference found for page {page_num}, skipping")
                            continue

                        # Get page content
                        page_text = pages[page_idx]

                        # Adaptive uses its own aligned image list; others use standard extraction
                        if strategy == "adaptive" and page_analyses is not None:
                            page_image = adaptive_images[page_idx] if page_idx < len(adaptive_images) else None
                            page_type = page_analyses[page_idx].page_type if page_idx < len(page_analyses) else None
                        else:
                            page_image = images[page_idx] if images else None
                            page_type = None

                        # Run conversion
                        result, timing_ms, error = run_strategy(
                            strategy=strategy,
                            base_url=config.base_url,
                            model=model,
                            page_text=page_text,
                            page_image=page_image,
                            temperature=temperature,
                            max_tokens=max_tokens,
                            prompt_variant=prompt_variant,
                            page_type=page_type,
                        )

                        if error:
                            print(f"  ✗ Error: {error}")
                        else:
                            print(f"  ✓ Completed in {timing_ms:.0f}ms")

                        # Evaluate
                        eval_result = evaluate_conversion(
                            reference=reference,
                            candidate=result or "",
                            page_number=page_num,
                            strategy=strategy,
                            model=model,
                            prompt_variant=prompt_variant,
                            timing_ms=timing_ms,
                            error=error,
                        )
                        results.append(eval_result)

    return results


def save_results(results: list[EvaluationResult], output_path: str) -> None:
    """Save evaluation results to JSON file."""
    # Convert dataclasses to dicts for JSON serialization
    serializable = []
    for r in results:
        d = asdict(r)
        serializable.append(d)

    with open(output_path, "w") as f:
        json.dump(serializable, f, indent=2)

    print(f"\nResults saved to {output_path}")


def run_experiment_from_config(
    config_path: str,
    output_path: str,
    max_tokens: int = 4096,
) -> list[EvaluationResult]:
    """
    Load experiment config from JSON, run experiment, and save results.
    """
    config = load_experiment_config(config_path)
    results = run_experiment(config, max_tokens=max_tokens)
    save_results(results, output_path)

    # Print summary
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
    parser.add_argument("-o", "--output", required=True, help="Path to save results JSON")
    parser.add_argument("--max-tokens", type=int, default=4096, help="Max tokens for LLM")

    args = parser.parse_args()

    run_experiment_from_config(args.config, args.output, args.max_tokens)


if __name__ == "__main__":
    main()
