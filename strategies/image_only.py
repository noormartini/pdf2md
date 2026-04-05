from llm.prompts import PROMPTS
from llm.client import call_llm


def image_strategy(
    base_url: str,
    model_name: str,
    images: list[str],
    temperature: float,
    max_tokens: int,
    prompt_variant: str = "default",
) -> str:
    """
    Strategy for converting images to markdown using an LLM.
    
    Args:
        base_url: Base URL for the LLM API
        model_name: The name of the LLM model to use
        images: List of base64-encoded image strings
        temperature: Temperature parameter for the LLM
        max_tokens: Maximum tokens for the LLM response
        prompt_variant: The prompt variant to use from PROMPTS
    """
    # Build content with images
    content: list[dict[str, object]] = []
    
    for img_base64 in images:
        content.append({
            "type": "image_url",
            "image_url": {
                "url": f"data:image/png;base64,{img_base64}",
            },
        })
    
    messages = [
        {"role": "system", "content": PROMPTS[prompt_variant]["system"]},
        {"role": "user", "content": content},
    ]

    return call_llm(base_url, model_name, messages, temperature, max_tokens)