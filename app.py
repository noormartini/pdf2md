import os

import fitz

from config import Config

from extraction.text import extract_pages_from_pdf
from extraction.image import extract_pages_from_pdf as extract_images_from_pdf, extract_embedded_images
from postprocess import postprocess_markdown
from strategies.text_only import text_strategy
from strategies.image_only import image_strategy
from strategies.hybrid import hybrid_strategy
from strategies.adaptive import analyze_page, adaptive_strategy, render_page_as_base64


def _images_dir(output_path: str) -> str:
    """Return the images/ directory next to the output Markdown file."""
    return os.path.join(os.path.dirname(os.path.abspath(output_path)), "images")


def run(config: Config):
    match (config.strategy):
        case "text":
            pages = extract_pages_from_pdf(config.input, max_pages=config.max_pages)
            if not pages:
                raise ValueError("No text could be extracted from the PDF.")
            cleaned_pages = []
            for i, page_text in enumerate(pages):
                print(f"Sending page {i+1} to LM Studio...")
                cleaned = text_strategy(
                    base_url=config.base_url,
                    model_name=config.model,
                    text=page_text,
                    temperature=config.temperature,
                    max_tokens=config.max_tokens,
                    prompt_variant="default",
                )
                img_refs = extract_embedded_images(config.input, i, _images_dir(config.output))
                if img_refs:
                    cleaned += "\n\n" + "\n\n".join(img_refs)
                cleaned_pages.append(cleaned)

        case "image":
            images = extract_images_from_pdf(config.input, max_pages=config.max_pages)
            if not images:
                raise ValueError("No images could be extracted from the PDF.")
            cleaned_pages = []
            for i, page_image in enumerate(images):
                print(f"Sending page {i+1} to LM Studio...")
                cleaned = image_strategy(
                    base_url=config.base_url,
                    model_name=config.model,
                    images=[page_image],
                    temperature=config.temperature,
                    max_tokens=config.max_tokens,
                    prompt_variant="default",
                )
                img_refs = extract_embedded_images(config.input, i, _images_dir(config.output))
                if img_refs:
                    cleaned += "\n\n" + "\n\n".join(img_refs)
                cleaned_pages.append(cleaned)

        case "hybrid":
            pages = extract_pages_from_pdf(config.input, max_pages=config.max_pages)
            images = extract_images_from_pdf(config.input, max_pages=config.max_pages)
            if not pages:
                raise ValueError("No text could be extracted from the PDF.")
            if not images:
                raise ValueError("No images could be extracted from the PDF.")
            cleaned_pages = []
            for i, (page_text, page_image) in enumerate(zip(pages, images)):
                print(f"Sending page {i+1} to LM Studio...")
                cleaned = hybrid_strategy(
                    base_url=config.base_url,
                    model_name=config.model,
                    text=page_text,
                    images=[page_image],
                    temperature=config.temperature,
                    max_tokens=config.max_tokens,
                    prompt_variant="default",
                )
                img_refs = extract_embedded_images(config.input, i, _images_dir(config.output))
                if img_refs:
                    cleaned += "\n\n" + "\n\n".join(img_refs)
                cleaned_pages.append(cleaned)

        case "adaptive":
            doc = fitz.open(config.input)
            num_pages = min(len(doc), config.max_pages)
            cleaned_pages = []
            for i in range(num_pages):
                page = doc[i]
                analysis = analyze_page(page)
                print(
                    f"Page {i+1}/{num_pages} → "
                    f"{analysis.page_type.value} "
                    f"(conf={analysis.confidence:.2f}) — sending to LM Studio..."
                )
                page_text = page.get_text("text").strip()
                page_image = render_page_as_base64(page)
                cleaned = adaptive_strategy(
                    base_url=config.base_url,
                    model_name=config.model,
                    text=page_text,
                    page_image=page_image,
                    page_type=analysis.page_type,
                    temperature=config.temperature,
                    max_tokens=config.max_tokens,
                )
                img_refs = extract_embedded_images(config.input, i, _images_dir(config.output))
                if img_refs:
                    cleaned += "\n\n" + "\n\n".join(img_refs)
                cleaned_pages.append(cleaned)
            doc.close()

        case _:
            raise ValueError(f"Unknown strategy: {config.strategy}")

    markdown = "\n\n".join(cleaned_pages)
    markdown = postprocess_markdown(markdown)

    print("Saving Markdown output...")
    with open(config.output, "w", encoding="utf-8") as f:
        f.write(markdown)

    print(f"Done! Output saved as '{config.output}'.")
