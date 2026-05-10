# Research Notes and Sources for PDF-to-Markdown Conversion Thesis

Based on the thesis structure and code implementation (focusing on PDF-to-Markdown conversion using LLMs with text-only, image-only, and hybrid strategies), here are recommended websites, sources, books, and academic resources. These are prioritized for document AI, multimodal LLMs, OCR/text extraction, evaluation metrics, and existing PDF processing tools.

## Academic Papers & Preprints (arXiv/Google Scholar)
These are foundational for the literature review, especially for the "Related Work" and "Background" sections:

1. **Nougat: Neural Optical Understanding for Academic Documents** (arXiv:2308.13418)  
   - Focuses on converting academic PDFs to structured formats like Markdown using neural methods. Directly relevant to hybrid and image-based strategies, addressing semantic loss in PDFs (e.g., math expressions).  
   - *Relevance:* Provides a baseline for academic document processing and evaluation.

2. **LayoutLMv3: Pre-training for Document AI with Unified Text and Image Masking** (arXiv:2204.08387)  
   - Introduces transformer-based models for multimodal document understanding, combining text and images.  
   - *Relevance:* Essential for hybrid strategy and LLM integration section.

3. **Deep Learning based Visually Rich Document Content Understanding: A Survey** (arXiv:2408.01287)  
   - Comprehensive survey on document analysis, covering text-only, image-only, and hybrid approaches.  
   - *Relevance:* Helps frame the comparison of extraction strategies.

4. **PDF-WuKong: A Large Multimodal Model for Efficient Long PDF Reading** (arXiv:2410.05970)  
   - State-of-the-art multimodal model for long PDF processing.  
   - *Relevance:* Relevant for scaling hybrid approach and discussing efficiency trade-offs.

5. **A Survey of OCR Evaluation Methods and Metrics** (arXiv:2603.25761)  
   - Covers OCR evaluation, including fairness in historical documents.  
   - *Relevance:* Crucial for "Evaluation Metrics" section (BLEU, ROUGE, token-level accuracy).

6. **BLEU: a Method for Automatic Evaluation of Machine Translation** (Papineni et al., ACL 2002) – Available on ACL Anthology.  
   - Original paper on BLEU score.  
   - *Relevance:* Core metric for quantitative evaluation.

7. **ROUGE: A Package for Automatic Evaluation of Summaries** (Lin, ACL 2004) – Available on ACL Anthology.  
   - Original paper on ROUGE metrics.  
   - *Relevance:* For assessing markdown output quality.

## Books
These provide theoretical depth for the "Background and Fundamentals" section:

1. **Natural Language Processing with Transformers** by Lewis Tunstall, Leandro von Werra, and Thomas Wolf (2022)  
   - Covers LLMs, prompt engineering, and multimodal models (e.g., vision-language integration).  
   - *Relevance:* Directly applicable to LLM integration and prompt design.

2. **Deep Learning** by Ian Goodfellow, Yoshua Bengio, and Aaron Courville (2016)  
   - Foundational text on neural networks, including multimodal learning.  
   - *Relevance:* For understanding LLM architectures and vision capabilities.

3. **Computer Vision: Algorithms and Applications** by Richard Szeliski (2022)  
   - Details image processing, OCR, and document layout analysis.  
   - *Relevance:* Supports image extraction module and visual parsing strategies.

4. **Speech and Language Processing** by Daniel Jurafsky and James H. Martin (3rd ed., 2023)  
   - Covers NLP fundamentals, including evaluation metrics and text processing.  
   - *Relevance:* For text extraction, cleaning, and markdown generation.

## Websites & Online Resources
These are practical for implementation, tools, and staying updated:

1. **arXiv.org** (arxiv.org)  
   - Search for "PDF to Markdown", "multimodal document AI", or "LLM document processing". Great for recent preprints on tools like Nougat or Marker.

2. **Hugging Face** (huggingface.co)  
   - Models hub for LLMs (e.g., LayoutLM, vision-language models) and datasets for document AI. Includes tutorials on multimodal fine-tuning.  
   - *Relevance:* For benchmarking strategies against open-source models.

3. **Papers with Code** (paperswithcode.com)  
   - Benchmarks for document understanding tasks (e.g., DocVQA, document layout analysis). Compare evaluation metrics here.

4. **PyMuPDF Documentation** (pymupdf.readthedocs.io)  
   - Official docs for PDF parsing library. Includes examples for text/image extraction.  
   - *Relevance:* Reference for "Text Extraction Module" and "Image Extraction Module".

5. **LM Studio Documentation** (lmstudio.ai)  
   - Guides for running local LLMs (e.g., Qwen, Gemma as mentioned in README).  
   - *Relevance:* For "LLM Integration" section and reproducibility.

6. **Google Scholar** (scholar.google.com)  
   - Search for "PDF parsing LLM" or "multimodal document conversion" to find cited papers and reviews.

7. **ACM Digital Library** (dl.acm.org) or **IEEE Xplore** (ieeexplore.ieee.org)  
   - Access to conference papers on document AI (e.g., ICDAR, CVPR) and multimodal learning.

## Additional Tips
- **For Related Work:** Examine GitHub repos like [Nougat](https://github.com/facebookresearch/nougat), [MinerU](https://github.com/opendatalab/MinerU), and [Marker](https://github.com/adithya-s-k/marker-api) for implementation insights and to compare with hybrid approach.
- **Evaluation Focus:** Use the OCR evaluation survey to justify metrics and discuss limitations (e.g., cultural biases in text extraction).
- **Staying Current:** Follow arXiv's "Computer Vision and Pattern Recognition" section for new multimodal models.
- **Thesis-Specific:** Structure already mentions tools like LLama Parse—cite their docs or papers for comparisons.

-------------------------

  Step 3 — Flesh out Related Work (biggest missing section)                                                                              
  Write out the three subsections that are currently empty bullet outlines:
  - Traditional PDF tools (PyMuPDF, pdfplumber, Tesseract) — what they do and where they fail                                                                    
  - Modern conversion tools (Marker, LlamaParse, Nougat, MinerU) — same                                                                                        
  - Limitations of current solutions — synthesize the common failure pattern (single-strategy, no content-type awareness)
                                                                                                                                                                 
  The story this section should tell: every existing tool applies one strategy to the whole document, which is why mixed-content PDFs break them.                
                                                                                                                                                                 
  Step 4 — Add a closing "gap → your fix" sentence to Related Work                                                                                               
                                                                                                                                                                 
  End the Related Work section with one explicit sentence connecting the surveyed gaps to your adaptive approach. Something like: "None of the surveyed tools    
  select a strategy per page based on detected content type — this gap motivates the system proposed in Chapter 5."                                            
                                                                                                                                                                 
  Step 5 — Write out the Background section                                                                                                                    

  Sections 2.2 (Markdown Format), 2.3 (Large Language Models), and 2.4 (Multimodal Processing Strategies) are still bullet-point outlines. These need full prose.
   Do this after Related Work since Background should feel like it's building toward what Related Work surveys.