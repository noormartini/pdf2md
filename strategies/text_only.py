from llm.prompts import PROMPTS
from llm.client import call_llm


def text_strategy(
    base_url: str,
    model_name: str,
    text: str,
    temperature: float,
    max_tokens: int,
    prompt_variant: str = "default",
):
    """Converts a pdf in text form into a markdown using an LLM. It uses text only, no image input to the LLM."""
    messages = [
        {"role": "system", "content": PROMPTS[prompt_variant]["system"]},
        {"role": "user", "content": PROMPTS[prompt_variant]["user"].format(text=text)},
    ]

    return call_llm(base_url, model_name, messages, temperature, max_tokens)
