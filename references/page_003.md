## Data and Tables

This page demonstrates table handling in PDF-to-Markdown conversion.

### Sample Data

| Model | Parameters | Accuracy | Speed |
|-------|------------|----------|-------|
| Gemma 3 | 4B | 85.2% | 120 ms |
| Qwen 2.5 | 7B | 87.4% | 95 ms |
| LLaMA 3 | 8B | 89.1% | 88 ms |

### Comparison Results

| Strategy | Text Similarity | Structure Score | Time (ms) |
|----------|-----------------|-----------------|-----------|
| Text-only | 0.82 | 0.75 | 450 |
| Image-only | 0.88 | 0.91 | 1200 |
| Hybrid | 0.91 | 0.94 | 1450 |

### Key Findings

The hybrid approach consistently outperforms single-modality strategies on structured content.
