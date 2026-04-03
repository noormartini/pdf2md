from app import extract_pages_from_pdf, clean_text_with_llm, postprocess_markdown
import argparse                                                                                                                                


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input",  default="test_pdf_source.pdf", help="Input PDF file",)
    parser.add_argument("-o", "--output", default="output/test_pdf_output.md", help="Output Markdown file")     
    parser.add_argument("-b", "--base-url", default="http://127.0.0.1:1234/v1", help="LM Studio base url",) 
    parser.add_argument("-m", "--model", default="google/gemma-3-4b", help="Model name")
    parser.add_argument("-n", "--max-pages", type=int, default=3, help="Max pages to convert to markdown")                                                           
    args = parser.parse_args()

    pages = extract_pages_from_pdf(args.input, max_pages=args.max_pages)

    if not pages:
        raise ValueError("No text could be extracted from the PDF.")

    cleaned_pages = []

    for i, page_text in enumerate(pages, start=1):
        print(f"Sending page {i} to LM Studio...")
        cleaned = clean_text_with_llm(args.base_url, args.model, page_text)
        cleaned_pages.append(cleaned)

    markdown = "\n\n".join(cleaned_pages)
    markdown = postprocess_markdown(markdown)

    print("Saving Markdown output...")
    with open(args.output, "w", encoding="utf-8") as f:
        f.write(markdown)

    print(f"Done! Output saved as '{args.output}'.")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Error: {e}")