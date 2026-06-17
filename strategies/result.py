"""Common return type for conversion strategies."""

from dataclasses import dataclass
from typing import Optional


@dataclass
class ConversionResult:
    """Result of converting one PDF page via a conversion strategy."""
    markdown: str
    timing_ms: float
    token_usage: Optional[int]  # None means LM Studio did not report usage
    llm_calls: int = 0          # 0 when the LLM was skipped entirely
