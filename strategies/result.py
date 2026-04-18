"""Common return type for conversion strategies."""

from dataclasses import dataclass
from typing import Optional


@dataclass
class ConversionResult:
    """Result of converting one PDF page via an LLM strategy.

    The caller already knows which strategy and model it invoked, so those
    are not duplicated here.
    """
    markdown: str
    timing_ms: float
    token_usage: Optional[int]
