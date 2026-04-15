import argparse


def parse_args():
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
    return parser.parse_args()
