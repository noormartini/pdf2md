from typing import Optional

import requests


def call_llm(
    base_url: str,
    model_name: str,
    messages: list[dict],
    temperature: float,
    max_tokens: int,
    timeout: int = 300,
) -> tuple[str, Optional[int]]:
    """Send messages to the LLM and return (content, total_token_usage).

    `total_token_usage` is `usage.total_tokens` from the response if the
    server returns it (LM Studio / OpenAI-compatible APIs do), else None.
    """
    payload = {
        "model": model_name,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
    }

    response = requests.post(f"{base_url}/chat/completions", json=payload, timeout=timeout)
    response.raise_for_status()
    data = response.json()
    content = data["choices"][0]["message"]["content"]
    token_usage = data.get("usage", {}).get("total_tokens")
    return content, token_usage
