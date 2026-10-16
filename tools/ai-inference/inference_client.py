"""inference_client.py — one tiny client for every OpenAI-compatible endpoint.

Works against llama-server (tools/inference/kaggle-llm-server.sh), Ollama (:11434),
vLLM, SGLang, or any OpenAI-compatible server. stdlib only (urllib) — no pip installs.

    from inference_client import chat
    print(chat("Write a haiku about GPUs"))

Env:
    INFERENCE_URL   base URL, default http://localhost:8080
    INFERENCE_MODEL model name, default t4-llm
"""

import json
import os
import urllib.request
import urllib.error

BASE_URL = os.environ.get("INFERENCE_URL", "http://localhost:8080").rstrip("/")
MODEL = os.environ.get("INFERENCE_MODEL", "t4-llm")
_TIMEOUT = float(os.environ.get("INFERENCE_TIMEOUT", "120"))


def _post(path, payload):
    req = urllib.request.Request(
        BASE_URL + path,
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=_TIMEOUT) as r:
            return json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"inference server {e.code}: {e.read().decode()[:500]}") from e


def chat(prompt, system=None, model=None, max_tokens=512, temperature=0.7, **kw):
    """Single chat completion. Returns the assistant's text."""
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})
    data = _post(
        "/v1/chat/completions",
        {
            "model": model or MODEL,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
            **kw,
        },
    )
    return data["choices"][0]["message"]["content"]


def health():
    """True if the server answers /health or /v1/models."""
    for path in ("/health", "/v1/models"):
        try:
            with urllib.request.urlopen(BASE_URL + path, timeout=5) as r:
                if r.status == 200:
                    return True
        except Exception:
            continue
    return False


if __name__ == "__main__":
    import sys

    prompt = " ".join(sys.argv[1:]) or "Say: inference pipeline online."
    print("server up:", health())
    print(chat(prompt, max_tokens=64))
