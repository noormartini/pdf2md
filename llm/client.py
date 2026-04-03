import requests


def call_llm(
    base_url: str,
    model_name: str,
    messages: list[dict],
    temperature: float,
    max_tokens: int,
) -> str:
    """Send messages to the LLM and return the response."""
    payload = {
        "model": model_name,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
    }

    response = requests.post(f"{base_url}/chat/completions", json=payload, timeout=120)
    response.raise_for_status()
    data = response.json()
    return data["choices"][0]["message"]["content"]
