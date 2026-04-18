"""Evaluation module for PDF-to-Markdown conversion experiments.

Submodules are imported directly (e.g. `from evaluation.metrics import ...`)
rather than re-exported here, so that lightweight modules like `metrics`
do not transitively pull in `fitz`, `requests`, and the strategies layer.
"""
