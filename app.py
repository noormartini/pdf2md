import os
import fitz

from config import Config

from extraction.text import extract_pages_from_pdf
from extraction.image import extract_page_figures
from postprocess import postprocess_markdown
from strategies.text_only import text_strategy
from strategies.image_only import image_strategy
from strategies.hybrid import hybrid_strategy
from strategies.adaptive import analyze_page, adaptive_strategy, render_page_as_base64, PageType


def run(config: Config):
    figures_dir = os.path.join(os.path.dirname(os.path.abspath(config.output)), "figures")
    cleaned_pages: list[str] = []

    match (config.strategy):
        case "text":
            doc = fitz.open(config.input)
            num_pages = min(len(doc), config.max_pages)
            doc.close()
            if num_pages == 0:
                raise ValueError("No pages could be read from the PDF.")
            for i in range(num_pages):
                print(f"Converting page {i+1}/{num_pages} to Markdown...")
                result = text_strategy(
                    base_url=config.base_url,
                    model_name=config.model,
                    pdf_path=config.input,
                    page_num=i,
                    temperature=config.temperature,
                    max_tokens=config.max_tokens,
                    figures_dir=figures_dir,
                )
                cleaned_pages.append(result.markdown)

        case "image":
            doc = fitz.open(config.input)
            num_pages = min(len(doc), config.max_pages)
            if num_pages == 0:
                doc.close()
                raise ValueError("No pages could be read from the PDF.")
            for i in range(num_pages):
                page = doc[i]
                page_image = render_page_as_base64(page)
                figure_refs = extract_page_figures(page, doc, i, figures_dir)
                print(f"Sending page {i+1}/{num_pages} to LM Studio...")
                result = image_strategy(
                    base_url=config.base_url,
                    model_name=config.model,
                    images=[page_image],
                    temperature=config.temperature,
                    max_tokens=config.max_tokens,
                    prompt_variant="default",
                    figure_refs=figure_refs or None,
                )
                cleaned_pages.append(result.markdown)
            doc.close()

        case "hybrid":
            pages = extract_pages_from_pdf(config.input, max_pages=config.max_pages)
            if not pages:
                raise ValueError("No text could be extracted from the PDF.")
            doc = fitz.open(config.input)
            num_pages = min(len(doc), config.max_pages)
            for i in range(num_pages):
                page = doc[i]
                page_image = render_page_as_base64(page)
                figure_refs = extract_page_figures(page, doc, i, figures_dir)
                page_text = pages[i] if i < len(pages) else ""
                print(f"Sending page {i+1}/{num_pages} to LM Studio...")
                result = hybrid_strategy(
                    base_url=config.base_url,
                    model_name=config.model,
                    text=page_text,
                    images=[page_image],
                    temperature=config.temperature,
                    max_tokens=config.max_tokens,
                    prompt_variant="default",
                    figure_refs=figure_refs or None,
                )
                cleaned_pages.append(result.markdown)
            doc.close()

        case "adaptive":
            doc = fitz.open(config.input)
            num_pages = min(len(doc), config.max_pages)
            for i in range(num_pages):
                page = doc[i]
                analysis = analyze_page(page)
                print(
                    f"Page {i+1}/{num_pages} → "
                    f"{analysis.page_type.value} "
                    f"(conf={analysis.confidence:.2f})..."
                )
                page_image = render_page_as_base64(page)
                # Extract embedded figures for vision-processed pages so the
                # LLM can reference them as individual Markdown image links.
                figure_refs = (
                    extract_page_figures(page, doc, i, figures_dir)
                    if analysis.page_type != PageType.TEXT
                    else None
                )
                result = adaptive_strategy(
                    base_url=config.base_url,
                    model_name=config.model,
                    pdf_path=config.input,
                    page_num=i,
                    page_image=page_image,
                    page_type=analysis.page_type,
                    temperature=config.temperature,
                    max_tokens=config.max_tokens,
                    figures_dir=figures_dir,
                    figure_refs=figure_refs,
                )
                cleaned_pages.append(result.markdown)
            doc.close()

        case _:
            raise ValueError(f"Unknown strategy: {config.strategy}")

    markdown = "\n\n".join(cleaned_pages)
    markdown = postprocess_markdown(markdown)

    print("Saving Markdown output...")
    with open(config.output, "w", encoding="utf-8") as f:
        f.write(markdown)

    print(f"Done! Output saved as '{config.output}'.")
