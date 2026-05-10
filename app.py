import os
import fitz

from config import Config

from extraction.text import extract_pages_from_pdf
from extraction.image import extract_page_figures
from extraction.language import detect_language, language_name
from postprocess import postprocess_markdown
from strategies.text_only import text_strategy
from strategies.image_only import image_strategy
from strategies.hybrid import hybrid_strategy
from strategies.adaptive import analyze_page, adaptive_strategy, render_page_as_base64, PageType


def _page_label(doc: fitz.Document, index: int) -> str:
    """Return the printed page label (e.g. 'v', '3') for a 0-based page index."""
    label = doc[index].get_label()
    return label if label else str(index + 1)


def run(config: Config):
    figures_dir = os.path.join(os.path.dirname(os.path.abspath(config.output)), "figures")
    cleaned_pages: list[str] = []

    # Detect document language from the first page's text
    with fitz.open(config.input) as _doc:
        sample_text = _doc[0].get_text("text") if len(_doc) > 0 else ""
    language = detect_language(sample_text)
    print(f"Detected language: {language_name(language)} ({language})")

    match (config.strategy):
        case "text":
            doc = fitz.open(config.input)
            num_pages = min(len(doc), config.max_pages)
            if num_pages == 0:
                doc.close()
                raise ValueError("No pages could be read from the PDF.")
            for i in range(num_pages):
                label = _page_label(doc, i)
                print(f"Converting page {i+1}/{num_pages} (page {label}) to Markdown...")
                result = text_strategy(
                    base_url=config.base_url,
                    model_name=config.model,
                    pdf_path=config.input,
                    page_num=i,
                    temperature=config.temperature,
                    max_tokens=config.max_tokens,
                    figures_dir=figures_dir,
                )
                cleaned_pages.append(f"<!-- Page {label} -->\n\n{result.markdown}")
            doc.close()

        case "image":
            doc = fitz.open(config.input)
            num_pages = min(len(doc), config.max_pages)
            if num_pages == 0:
                doc.close()
                raise ValueError("No pages could be read from the PDF.")
            for i in range(num_pages):
                page = doc[i]
                label = _page_label(doc, i)
                page_image = render_page_as_base64(page)
                figure_refs = extract_page_figures(page, doc, i, figures_dir)
                print(f"Sending page {i+1}/{num_pages} (page {label}) to LM Studio...")
                result = image_strategy(
                    base_url=config.base_url,
                    model_name=config.model,
                    images=[page_image],
                    temperature=config.temperature,
                    max_tokens=config.max_tokens,
                    prompt_variant="default",
                    figure_refs=figure_refs or None,
                    language=language,
                )
                cleaned_pages.append(f"<!-- Page {label} -->\n\n{result.markdown}")
            doc.close()

        case "hybrid":
            pages = extract_pages_from_pdf(config.input, max_pages=config.max_pages)
            if not pages:
                raise ValueError("No text could be extracted from the PDF.")
            doc = fitz.open(config.input)
            num_pages = min(len(doc), config.max_pages)
            for i in range(num_pages):
                page = doc[i]
                label = _page_label(doc, i)
                page_image = render_page_as_base64(page)
                figure_refs = extract_page_figures(page, doc, i, figures_dir)
                page_text = pages[i] if i < len(pages) else ""
                print(f"Sending page {i+1}/{num_pages} (page {label}) to LM Studio...")
                result = hybrid_strategy(
                    base_url=config.base_url,
                    model_name=config.model,
                    text=page_text,
                    images=[page_image],
                    temperature=config.temperature,
                    max_tokens=config.max_tokens,
                    prompt_variant="default",
                    figure_refs=figure_refs or None,
                    language=language,
                )
                cleaned_pages.append(f"<!-- Page {label} -->\n\n{result.markdown}")
            doc.close()

        case "adaptive":
            doc = fitz.open(config.input)
            num_pages = min(len(doc), config.max_pages)
            for i in range(num_pages):
                page = doc[i]
                label = _page_label(doc, i)
                analysis = analyze_page(page)
                print(
                    f"Page {i+1}/{num_pages} (page {label}) → "
                    f"{analysis.page_type.value} "
                    f"(conf={analysis.confidence:.2f})..."
                )
                page_image = render_page_as_base64(page)
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
                    language=language,
                )
                cleaned_pages.append(f"<!-- Page {label} -->\n\n{result.markdown}")
            doc.close()

        case _:
            raise ValueError(f"Unknown strategy: {config.strategy}")

    markdown = "\n\n---\n\n".join(cleaned_pages)
    markdown = postprocess_markdown(markdown)

    print("Saving Markdown output...")
    os.makedirs(os.path.dirname(os.path.abspath(config.output)), exist_ok=True)
    with open(config.output, "w", encoding="utf-8") as f:
        f.write(markdown)

    print(f"Done! Output saved as '{config.output}'.")
