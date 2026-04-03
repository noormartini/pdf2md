from dataclasses import dataclass


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
