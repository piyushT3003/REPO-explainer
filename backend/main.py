from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from backend.repository import clone_repository
from backend.code_processor import build_repository_context
from backend.llm import explain_repository


app = FastAPI(
    title="Local GitHub Repository Code Explainer",
    description="Explains public GitHub repositories using a locally running LLM.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ExplainRequest(BaseModel):
    github_url: str = Field(..., min_length=10)


@app.get("/")
def home():
    return {
        "message": "GitHub Code Explainer API is running",
        "docs": "/docs",
    }


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/explain")
def explain(request: ExplainRequest):
    repo_path = None
    try:
        repo_path = clone_repository(request.github_url)
        context, files = build_repository_context(repo_path)

        if not context.strip():
            raise HTTPException(
                status_code=400,
                detail="No supported source-code files were found in the repository.",
            )

        explanation = explain_repository(context)

        return {
            "github_url": request.github_url,
            "files_analyzed": files,
            "explanation": explanation,
        }

    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
    finally:
        if repo_path:
            from backend.repository import cleanup_repository
            cleanup_repository(repo_path)
