"""Evaluation module for PDF-to-Markdown conversion experiments."""

from evaluation.metrics import (
    evaluate_conversion,
    aggregate_results,
    text_similarity,
    heading_structure_score,
    list_structure_score,
    table_structure_score,
    code_block_score,
    paragraph_structure_score,
    calculate_word_overlap,
    EvaluationResult,
    MetricResult,
)
from evaluation.compare import (
    run_experiment,
    run_experiment_from_config,
    save_results,
    ExperimentConfig,
    load_experiment_config,
)
from evaluation.report import (
    generate_full_report,
    generate_summary_table,
    generate_model_comparison,
    generate_strategy_model_matrix,
    generate_per_page_breakdown,
    load_results,
)

__all__ = [
    # Metrics
    "evaluate_conversion",
    "aggregate_results",
    "text_similarity",
    "heading_structure_score",
    "list_structure_score",
    "table_structure_score",
    "code_block_score",
    "paragraph_structure_score",
    "calculate_word_overlap",
    "EvaluationResult",
    "MetricResult",
    # Compare
    "run_experiment",
    "run_experiment_from_config",
    "save_results",
    "ExperimentConfig",
    "load_experiment_config",
    # Report
    "generate_full_report",
    "generate_summary_table",
    "generate_model_comparison",
    "generate_strategy_model_matrix",
    "generate_per_page_breakdown",
    "load_results",
]
