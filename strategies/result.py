"""Common return type for conversion strategies."""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class ConversionResult:
    """Result of converting one PDF page via a conversion strategy."""
    markdown: str
    timing_ms: float
    token_usage: Optional[int]
    image_refs: list[str] = field(default_factory=list)
