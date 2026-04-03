from app import extract_pages_from_pdf, clean_text_with_llm, postprocess_markdown
from config import Config
import argparse


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-i",
        "--input",
        default="test_pdf_source.pdf",
        help="Input PDF file",
    )
    parser.add_argument(
        "-o",
        "--output",
        default="output/test_pdf_output.md",
        help="Output Markdown file",
    )
    parser.add_argument(
        "-b",
        "--base-url",
        default="http://127.0.0.1:1234/v1",
        help="LM Studio base url",
    )
    parser.add_argument("-m", "--model", default="google/gemma-3-4b", help="Model name")
    parser.add_argument(
        "-n",
        "--max-pages",
        type=int,
        default=3,
        help="Max pages to convert to markdown",
    )
    parser.add_argument(
        "-s",
        "--strategy",
        default="text",
        choices=["text", "image", "hybrid"],
        help="Conversion strategy",
    )
    parser.add_argument(
        "-t",
        "--temperature",
        type=float,
        default=0.2,
        help="LLM creativity (0.0 = deterministic, 1.0 = creative)",
    )
    parser.add_argument(
        "-T",
        "--max-tokens",
        type=int,
        default=4096,
        help="Max response length from LLM"
    )
    args = parser.parse_args()

    config = Config(
        input=args.input,
        output=args.output,
        base_url=args.base_url,
        model=args.model,
        max_pages=args.max_pages,
        strategy=args.strategy,
        temperature=args.temperature,
        max_tokens=args.max_tokens
    )

    pages = extract_pages_from_pdf(config.input, max_pages=config.max_pages)

    if not pages:
        raise ValueError("No text could be extracted from the PDF.")

    cleaned_pages = []

    for i, page_text in enumerate(pages, start=1):
        print(f"Sending page {i} to LM Studio...")
        cleaned = clean_text_with_llm(config.base_url, config.model, page_text)
        cleaned_pages.append(cleaned)

    markdown = "\n\n".join(cleaned_pages)
    markdown = postprocess_markdown(markdown)

    print("Saving Markdown output...")
    with open(config.output, "w", encoding="utf-8") as f:
        f.write(markdown)

    print(f"Done! Output saved as '{config.output}'.")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Error: {e}")
