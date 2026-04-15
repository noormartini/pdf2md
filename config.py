from dataclasses import dataclass

# ---------------------------------------------------------------------------
# Adaptive strategy — page classification thresholds
# ---------------------------------------------------------------------------

# Any embedded image on a page triggers vision mode
ADAPTIVE_IMAGE_THRESHOLD: int = 0

# Number of short vector paths (width/height < 20px) that indicates formulas
ADAPTIVE_VECTOR_PATH_THRESHOLD: int = 30

# Pages with fewer characters than this are not classified as "text-only"
ADAPTIVE_MIN_TEXT_CHARACTERS: int = 50

# DPI used when rendering a page to PNG for vision strategies
ADAPTIVE_RENDER_DPI: int = 150


@dataclass
class Config:
    input: str
    output: str
    base_url: str
    model: str
    max_pages: int
    strategy: str = "text"
    temperature: float = 0.2
    max_tokens: int = 4096
