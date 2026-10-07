import os
import requests
import streamlit as st

OLLAMA_URL = os.getenv(
    "OLLAMA_URL",
    "http://localhost:11434"
)

OLLAMA_MODEL = os.getenv(
    "OLLAMA_MODEL",
    "qwen2.5:0.5b"
)

HF_MODELS = [
    "Qwen/Qwen2.5-Coder-32B-Instruct",
    "Qwen/Qwen2.5-7B-Instruct",
    "Qwen/Qwen2.5-0.5B-Instruct",
]


def build_prompt(repository_context: str) -> str:
    return f"""
You are an expert software engineering teacher.

Your job is to understand an ENTIRE GitHub repository
and explain the project to a college student.

IMPORTANT:

- Analyze the repository as a complete project.
- Do NOT rewrite the code.
- Do NOT clean the code.
- Do NOT generate replacement code.
- Do NOT focus on one individual file.
- Do NOT reproduce large amounts of source code.
- Do NOT invent features.
- Only describe functionality that can be reasonably
  understood from the provided repository.
- Test files should NOT be treated as the main application.
- Explain everything in simple beginner-friendly language.

The repository may contain multiple programming languages,
frameworks and files.

Use the following EXACT structure.

# Project Overview

Explain:

1. What the project is.
2. What problem it solves.
3. What the application is used for.

Write approximately 3-5 sentences.

# Main Features

List the major features as bullet points.

# Project Structure

Explain the important folders and files.

Use this format:

- `filename` — explanation
- `folder/` — explanation

Focus on application files rather than tests.

# How the Application Works

Explain the complete flow of the application.

For example:

User
↓
Frontend
↓
Backend
↓
Processing
↓
Database/API
↓
Output

Use the actual architecture found in the repository.

# Technologies Used

Identify:

- Programming languages
- Frameworks
- Libraries
- Databases
- APIs
- Development tools

# Important Code Components

Explain important:

- functions
- classes
- modules
- components

Do NOT reproduce their source code.

Only explain their purpose.

# Simple Summary

Give a short explanation of the complete project
in 5-8 sentences that a beginner can understand.

Remember:

You are explaining the PROJECT.

You are NOT editing or cleaning the code.

Here is the repository:

{repository_context}
"""


def check_ollama_status() -> bool:
    """Check if local Ollama server is running and reachable."""
    try:
        res = requests.get(f"{OLLAMA_URL.rstrip('/')}/api/tags", timeout=1.5)
        return res.status_code == 200
    except Exception:
        return False


def _explain_with_ollama(repository_context: str) -> str:
    prompt = build_prompt(repository_context)

    response = requests.post(
        f"{OLLAMA_URL.rstrip('/')}/api/generate",
        json={
            "model": OLLAMA_MODEL,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.1,
                "num_ctx": 4096,
                "num_predict": 900
            }
        },
        timeout=600
    )

    response.raise_for_status()
    data = response.json()
    explanation = data.get("response", "").strip()

    if not explanation:
        raise RuntimeError("Ollama returned an empty response.")

    return explanation


def get_hf_token(explicit_token: str = None) -> str:
    """Retrieve Hugging Face token from explicit arg, session state, secrets, or env."""
    if explicit_token and explicit_token.strip():
        return explicit_token.strip()

    try:
        if "hf_token" in st.session_state and st.session_state["hf_token"]:
            return str(st.session_state["hf_token"]).strip()
    except Exception:
        pass

    try:
        if hasattr(st, "secrets"):
            for key in ["HF_TOKEN", "HUGGINGFACEHUB_API_TOKEN", "HUGGING_FACE_HUB_TOKEN"]:
                if key in st.secrets and st.secrets[key]:
                    return str(st.secrets[key]).strip()
    except Exception:
        pass

    for key in ["HF_TOKEN", "HUGGINGFACEHUB_API_TOKEN", "HUGGING_FACE_HUB_TOKEN"]:
        val = os.getenv(key)
        if val and val.strip():
            return val.strip()

    return ""


def _explain_with_huggingface(repository_context: str, token: str = None) -> str:
    """Run Qwen inference via Hugging Face Serverless Inference API."""
    token = get_hf_token(token)

    if not token:
        raise RuntimeError(
            "Hugging Face API token is required for cloud AI inference.\n\n"
            "How to fix:\n"
            "1. Enter your free token in the sidebar under 'Cloud AI Settings', OR\n"
            "2. Add HF_TOKEN to your Streamlit Cloud App Secrets.\n\n"
            "👉 Get a free token in seconds at: https://huggingface.co/settings/tokens"
        )

    prompt = build_prompt(repository_context)
    messages = [
        {
            "role": "system",
            "content": (
                "You are an expert software engineering teacher "
                "who explains GitHub repositories to college students."
            )
        },
        {
            "role": "user",
            "content": prompt
        }
    ]

    try:
        from huggingface_hub import InferenceClient
        for model_id in HF_MODELS:
            try:
                client = InferenceClient(model=model_id, token=token, timeout=120)
                completion = client.chat.completions.create(
                    messages=messages,
                    max_tokens=1500,
                    temperature=0.2
                )
                if completion.choices and completion.choices[0].message.content:
                    return completion.choices[0].message.content.strip()
            except Exception:
                continue
    except ImportError:
        pass

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    payload = {
        "messages": messages,
        "max_tokens": 1500,
        "temperature": 0.2
    }

    last_error = None
    for model_id in HF_MODELS:
        endpoints = [
            f"https://router.huggingface.co/hf-inference/models/{model_id}/v1/chat/completions",
            f"https://api-inference.huggingface.co/models/{model_id}/v1/chat/completions"
        ]
        for url in endpoints:
            try:
                resp = requests.post(url, headers=headers, json={"model": model_id, **payload}, timeout=90)
                if resp.status_code == 200:
                    data = resp.json()
                    choices = data.get("choices", [])
                    if choices and "message" in choices[0]:
                        content = choices[0]["message"].get("content", "").strip()
                        if content:
                            return content
                elif resp.status_code == 401:
                    raise RuntimeError(
                        "Invalid Hugging Face API token. Please verify your token at https://huggingface.co/settings/tokens"
                    )
                else:
                    last_error = f"Status {resp.status_code}: {resp.text[:200]}"
            except requests.RequestException as exc:
                last_error = str(exc)
                continue

    raise RuntimeError(
        f"Could not generate explanation using Hugging Face Qwen models. Last error: {last_error}"
    )


def explain_repository(repository_context: str, hf_token: str = None) -> str:
    """
    Unified LLM pipeline:
    1. Uses local Ollama if reachable (default for local runs).
    2. Falls back to Hugging Face Serverless Inference API (Qwen 2.5 Coder) for cloud deployment.
    """
    if check_ollama_status():
        try:
            return _explain_with_ollama(repository_context)
        except Exception:
            pass

    return _explain_with_huggingface(repository_context, token=hf_token)