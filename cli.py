import argparse

from config import DEFAULT_BASE_URL, DEFAULT_CONCURRENCY, DEFAULT_MODEL


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-i",
        "--input",
        default="pdf_source/test_pdf_source.pdf",
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
        default=DEFAULT_BASE_URL,
        help="LM Studio base url",
    )
    parser.add_argument("-m", "--model", default=DEFAULT_MODEL, help="Model name")
    parser.add_argument(
        "-n",
        "--max-pages",
        type=int,
        default=10000,
        help="Max pages to convert (default: entire PDF)",
    )
    parser.add_argument(
        "-s",
        "--strategy",
        default="text",
        choices=["text", "image", "hybrid", "adaptive"],
        help="Conversion strategy: text, image, hybrid, or adaptive (per-page auto-detection)",
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
        help="Max response length from LLM",
    )
    parser.add_argument(
        "-c",
        "--concurrency",
        type=int,
        default=DEFAULT_CONCURRENCY,
        help="Number of pages converted in parallel (LLM calls are run in a thread pool)",
    )
    return parser.parse_args()
