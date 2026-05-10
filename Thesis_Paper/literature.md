# Literature Suggestions

Sources marked **[IN BIB]** are already in your bibliography. All others need to be added.

---

## Chapter 2 — Background and Fundamentals

### Section 2.3 — Large Language Models

| Paper | Authors | Year | Link | Why |
|---|---|---|---|---|
| Attention is All You Need | Vaswani et al. | 2017 | https://arxiv.org/abs/1706.03762 | Foundational transformer architecture — cite when introducing LLMs |
| LLaVA: Visual Instruction Tuning | Liu et al. | 2023 | https://arxiv.org/abs/2304.08485 | Explains how LLMs gain vision capabilities — supports the image-based strategy |
| Qwen-VL | Bai et al. | 2023 | https://arxiv.org/abs/2308.12966 | Your system uses Qwen models — cite the model's own paper |
| Natural Language Processing with Transformers *(book)* | Tunstall, von Werra & Wolf | 2022 | O'Reilly | Covers LLMs, prompt engineering, and vision-language models — useful for prompt design section |
| Deep Learning *(book)* | Goodfellow, Bengio & Courville | 2016 | MIT Press | Foundational neural network theory — for LLM architecture background |
| Speech and Language Processing *(book)* | Jurafsky & Martin | 2023 (3rd ed.) | https://web.stanford.edu/~jurafsky/slp3/ | NLP fundamentals, evaluation metrics, text processing |

### Section 2.4 — Multimodal Processing Strategies

| Paper | Authors | Year | Link | Why |
|---|---|---|---|---|
| Donut: Document Understanding Transformer | Kim et al. | 2022 | https://arxiv.org/abs/2111.15664 | OCR-free vision-only document understanding — motivates image-based strategy |
| Document Intelligence in the Era of LLMs | — | 2024 | https://arxiv.org/abs/2510.13366 | Survey covering text-only, image-based, and hybrid strategies — maps directly onto your three strategies |
| Computer Vision: Algorithms and Applications *(book)* | Szeliski | 2022 | Springer | Image processing and document layout analysis — supports image extraction module |

---

## Chapter 3 — Related Work

### Section 3.2 — Modern Document Conversion Tools

| Paper | Authors | Year | Link | Why |
|---|---|---|---|---|
| Nougat | Blecher et al. | 2023 | https://arxiv.org/abs/2308.13418 | **[IN BIB]** Neural OCR for academic PDFs |
| MinerU | Wang et al. | 2024 | https://arxiv.org/abs/2409.18839 | **[IN BIB]** Open-source dual-engine PDF-to-Markdown system |
| Accelerating PDF to Markdown (Cassel) | Cassel et al. | 2025 | https://arxiv.org/abs/2512.18122 | **[IN BIB]** End-to-end decoder transformer approach |
| PDF-WuKong | — | 2024 | https://arxiv.org/abs/2410.05970 | State-of-the-art multimodal model for long PDFs — useful for efficiency trade-off discussion |
| ParseBench | Zhang et al. | 2026 | https://arxiv.org/abs/2604.08538 | **[IN BIB]** Benchmark comparing LlamaParse, Mistral OCR and others |

### Section 3.3 — LLM-based Document Understanding

| Paper | Authors | Year | Link | Why |
|---|---|---|---|---|
| LayoutLM | Xu et al. | 2020 | https://arxiv.org/abs/1912.13318 | Seminal paper on combining text + layout for document understanding |
| LayoutLMv3 | Huang et al. | 2022 | https://arxiv.org/abs/2204.08387 | Extends LayoutLM with unified text and image masking — essential for hybrid strategy background |
| Deep Learning for Visually Rich Documents (survey) | Ding et al. | 2024 | https://arxiv.org/abs/2408.01287 | **[IN BIB]** Frames the comparison of text-only, image-only, and hybrid approaches |
| Document Parsing Unveiled | Zhang et al. | 2024 | https://arxiv.org/abs/2410.21169 | **[IN BIB]** Techniques and challenges for structured information extraction |

---

## Chapter 4 — Methodology

### Section 4.3 — Evaluation Metrics

| Paper | Authors | Year | Link | Why |
|---|---|---|---|---|
| BLEU | Papineni et al. | 2002 | https://aclanthology.org/P02-1040 | Original BLEU paper — must cite when using or critiquing BLEU |
| ROUGE | Lin | 2004 | https://aclanthology.org/W04-1013 | Original ROUGE paper — must cite when using or critiquing ROUGE |
| A Survey of OCR Evaluation Methods and Metrics | — | 2025 | https://arxiv.org/abs/2603.25761 | Covers OCR evaluation including limitations of token-level metrics — justifies your extended evaluation methodology |
| Benchmarking Document Parsers on Math Formula Extraction | — | 2024 | https://arxiv.org/abs/2512.09874 | Supports argument that n-gram metrics fall short for structured/formula-heavy content |
