from config import Config

from extraction.text import extract_pages_from_pdf
from extraction.image import extract_pages_from_pdf as extract_images_from_pdf
from postprocess import postprocess_markdown
from strategies.text_only import text_strategy
from strategies.image_only import image_strategy
from strategies.hybrid import hybrid_strategy

def run(config: Config):
    match (config.strategy):
        case "text":
            pages = extract_pages_from_pdf(config.input, max_pages=config.max_pages)
            if not pages:
                raise ValueError("No text could be extracted from the PDF.")
            cleaned_pages = []
            for i, page_text in enumerate(pages):
                print(f"Sending page {i+1} to LM Studio...")
                result = text_strategy(
                    base_url=config.base_url,
                    model_name=config.model,
                    text=page_text,
                    temperature=config.temperature,
                    max_tokens=config.max_tokens,
                    prompt_variant="default"
                )
                cleaned_pages.append(result.markdown)
        case "image":
            images = extract_images_from_pdf(config.input, max_pages=config.max_pages)
            if not images:
                raise ValueError("No images could be extracted from the PDF.")
            cleaned_pages = []
            for i, page_images in enumerate(images):
                print(f"Sending page {i+1} to LM Studio...")
                result = image_strategy(
                    base_url=config.base_url,
                    model_name=config.model,
                    images=[page_images],
                    temperature=config.temperature,
                    max_tokens=config.max_tokens,
                    prompt_variant="default"
                )
                cleaned_pages.append(result.markdown)
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
                result = hybrid_strategy(
                    base_url=config.base_url,
                    model_name=config.model,
                    text=page_text,
                    images=[page_image],
                    temperature=config.temperature,
                    max_tokens=config.max_tokens,
                    prompt_variant="default"
                )
                cleaned_pages.append(result.markdown)
        case _:
            raise ValueError(f"Unknown strategy: {config.strategy}") 

    markdown = "\n\n".join(cleaned_pages)
    markdown = postprocess_markdown(markdown)

    print("Saving Markdown output...")
    with open(config.output, "w", encoding="utf-8") as f:
        f.write(markdown)

    print(f"Done! Output saved as '{config.output}'.")
