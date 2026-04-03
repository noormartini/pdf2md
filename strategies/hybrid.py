from llm.prompts import PROMPTS
from llm.client import call_llm


def hybrid_strategy(
    base_url: str,
    model_name: str,
    text: str,
    images: list[str],
    temperature: float,
    max_tokens: int,
    prompt_variant: str = "default",
) -> str:
    """Converts PDF pages using both text and images into markdown using an LLM.
    
    Args:
        base_url: The base URL of the LLM server
        model_name: The name of the LLM model to use
        text: The extracted text from the PDF page
        images: List of base64-encoded image strings
        temperature: Temperature parameter for the LLM
        max_tokens: Maximum tokens for the LLM response
        prompt_variant: The prompt variant to use from PROMPTS
    """
    # Build content with both text and images
    content: list[dict[str, object]] = [
        {"type": "text", "text": PROMPTS[prompt_variant]["user"].format(text=text)}
    ]
    
    for img_base64 in images:
        content.append({
            "type": "image",
            "source": {
                "type": "base64",
                "media_type": "image/png",
                "data": img_base64,
            },
        })
    
    messages = [
        {"role": "system", "content": PROMPTS[prompt_variant]["system"]},
        {"role": "user", "content": content},
    ]

    return call_llm(base_url, model_name, messages, temperature, max_tokens)
