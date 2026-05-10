import re


def postprocess_markdown(md: str) -> str:
    """Clean up line endings, excessive blank lines, and LLM code-fence wrappers."""
    md = md.replace("\r\n", "\n").replace("\r", "\n")

    # LLMs sometimes wrap their entire response in ```markdown ... ```.
    # Strip those wrappers while leaving legitimate code blocks (```python etc.) intact.
    md = re.sub(r"```markdown\n(.*?)```", lambda m: m.group(1), md, flags=re.DOTALL)

    while "\n\n\n" in md:
        md = md.replace("\n\n\n", "\n\n")

    return md.strip() + "\n"
