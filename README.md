# Local & Cloud GitHub Repository Code Explainer (RepoLens AI)

A student-friendly GenAI project that accepts a public GitHub repository URL, clones the repository, extracts relevant source-code files, and generates a simple-language explanation using an AI-powered Qwen model.

## Architecture

```
GitHub Repository
  → Repository Processing (GitPython + Code Processor)
  → Qwen AI Model (Ollama locally / Hugging Face Serverless on Cloud)
  → Streamlit Frontend
  → Structured Beginner-Friendly Explanation
```

## Technology Stack

- **Frontend:** Streamlit
- **Backend/Processing:** Python, GitPython, FastAPI, Pydantic
- **AI Models:**
  - **Local:** Ollama + Qwen 2.5 (`qwen2.5:0.5b` or `qwen2.5:3b`)
  - **Cloud:** Hugging Face Serverless Inference API (`Qwen/Qwen2.5-Coder-32B-Instruct`)

---

## 1. Local Run (Ollama)

### Prerequisites

1. Python 3.10+
2. Git
3. Ollama (download from [ollama.com](https://ollama.com))

Install dependencies:
```bash
pip install -r requirements.txt
```

Download and run the local Qwen model:
```bash
ollama run qwen2.5:0.5b
```

### Launch the App

```bash
streamlit run frontend/app.py
```

The app will automatically detect your local Ollama instance and use it for inference.

---

## 2. Cloud Deployment (Streamlit Cloud)

When deployed to Streamlit Community Cloud:

1. The app connects to the **Hugging Face Serverless Inference API** running Qwen 2.5 on cloud GPUs (lightweight and fast, with zero heavy local CPU model loading).
2. Configure your free Hugging Face User Access Token:
   - In Streamlit Cloud: Go to **App Settings** → **Secrets** and add:
     ```toml
     HF_TOKEN = "hf_your_token_here"
     ```
   - Or enter it directly in the app's sidebar under **Cloud AI Settings**.
   - Create a free token at [huggingface.co/settings/tokens](https://huggingface.co/settings/tokens).

---

## Example Repositories to Test

Use public repository URLs such as:
- `https://github.com/psf/requests`
- `https://github.com/pallets/click`

The application will:
1. Validate the GitHub URL.
2. Clone the repository into a temporary workspace.
3. Find relevant source-code files and filter out noise (tests, lock files, virtual environments).
4. Extract a bounded amount of source code.
5. Send the code to Qwen AI.
6. Display a clean, structured explanation and file map.
