import sys
from pathlib import Path
from urllib.parse import urlparse

# ============================================================
# PROJECT ROOT
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


import streamlit as st

from backend.repository import (
    clone_repository,
    cleanup_repository
)

from backend.code_processor import (
    build_repository_context
)

from backend.llm import (
    explain_repository,
    check_ollama_status,
    get_hf_token
)

# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="RepoLens AI",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown(
    """<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Space+Grotesk:wght@500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: Inter, sans-serif;
}

.stApp {
    background:
        radial-gradient(circle at 8% 8%, rgba(139,92,246,.16), transparent 27%),
        radial-gradient(circle at 92% 12%, rgba(6,182,212,.13), transparent 24%),
        radial-gradient(circle at 50% 100%, rgba(99,102,241,.09), transparent 32%),
        #070a12;
}

[data-testid="stHeader"] {
    background: transparent;
}

[data-testid="stSidebar"] {
    background: rgba(7,10,18,.94);
    border-right: 1px solid rgba(148,163,184,.14);
}

.block-container {
    max-width: 1280px;
    padding-top: 2.2rem;
    padding-bottom: 4rem;
}

#MainMenu, footer {
    visibility: hidden;
}

/* Hero */
.hero {
    padding: 30px 0 16px;
}

.eyebrow {
    display: inline-flex;
    padding: 7px 14px;
    border-radius: 999px;
    color: #c4b5fd;
    background: rgba(139,92,246,.12);
    border: 1px solid rgba(139,92,246,.28);
    font-size: 12px;
    font-weight: 800;
    letter-spacing: .5px;
    margin-bottom: 12px;
}

.hero h1 {
    font-family: "Space Grotesk", sans-serif;
    font-size: clamp(40px, 5.5vw, 70px);
    line-height: 1.05;
    letter-spacing: -2px;
    margin: 12px 0 16px;
    background: linear-gradient(90deg, #fff 5%, #ddd6fe 45%, #67e8f9 90%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.hero p {
    max-width: 800px;
    color: #a8b3c7;
    font-size: 16px;
    line-height: 1.7;
    margin-bottom: 24px;
}

.glow-line {
    height: 1px;
    margin: 24px 0 32px;
    background: linear-gradient(90deg, transparent, #8b5cf6, #06b6d4, transparent);
}

/* Input fields */
div[data-testid="stTextInput"] input {
    background: rgba(8,12,22,.88) !important;
    border: 1px solid rgba(148,163,184,.20) !important;
    border-radius: 13px !important;
    color: #f8fafc !important;
    height: 52px !important;
    font-size: 15px !important;
}

div[data-testid="stTextInput"] input:focus {
    border-color: rgba(139,92,246,.8) !important;
    box-shadow: 0 0 0 2px rgba(139,92,246,.15) !important;
}

/* Primary Button */
.stButton > button {
    width: 100%;
    height: 52px;
    border: 0 !important;
    border-radius: 13px !important;
    background: linear-gradient(100deg, #7c3aed, #8b5cf6 48%, #06b6d4) !important;
    color: white !important;
    font-weight: 800 !important;
    box-shadow: 0 12px 30px rgba(124,58,237,.23);
    transition: all 0.2s ease;
}

.stButton > button:hover {
    transform: translateY(-2px);
    box-shadow: 0 16px 36px rgba(124,58,237,.35);
}

/* Metrics */
.metric-card {
    background: linear-gradient(145deg, rgba(18,25,42,.82), rgba(12,17,30,.72));
    border: 1px solid rgba(148,163,184,.16);
    border-radius: 18px;
    padding: 18px 20px;
    min-height: 110px;
}

.metric-icon {
    font-size: 18px;
    margin-bottom: 8px;
    color: #a78bfa;
}

.metric-label {
    color: #8fa0b8;
    font-size: 12px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: .8px;
}

.metric-value {
    margin-top: 4px;
    font-family: "Space Grotesk", sans-serif;
    font-size: 24px;
    font-weight: 700;
    color: #fff;
}

/* Section titles */
.section-title {
    font-family: "Space Grotesk", sans-serif;
    font-size: 24px;
    font-weight: 700;
    color: #f1f5f9;
    margin: 28px 0 8px;
}

.section-subtitle {
    color: #8290a7;
    font-size: 13px;
    margin-bottom: 18px;
}

/* Info Cards */
.info-card {
    border: 1px solid rgba(148,163,184,.14);
    background: rgba(15,23,42,.52);
    border-radius: 18px;
    padding: 22px;
    height: 100%;
}

.info-card h4 {
    margin: 0 0 10px;
    color: #f8fafc;
    font-family: "Space Grotesk", sans-serif;
    font-size: 16px;
}

.info-card p {
    margin: 0;
    color: #8fa0b8;
    line-height: 1.65;
    font-size: 13px;
}

/* Repository pill */
.repo-pill {
    display: inline-flex;
    padding: 6px 12px;
    border-radius: 999px;
    color: #c4b5fd;
    background: rgba(139,92,246,.12);
    border: 1px solid rgba(139,92,246,.25);
    font-size: 12px;
    font-weight: 700;
}

/* Architecture */
.arch {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 12px;
    flex-wrap: wrap;
    padding: 20px 10px;
}

.arch-node {
    padding: 12px 18px;
    border-radius: 14px;
    background: linear-gradient(145deg, rgba(30,41,59,.82), rgba(15,23,42,.72));
    border: 1px solid rgba(148,163,184,.16);
    text-align: center;
    min-width: 120px;
}

.arch-node strong {
    display: block;
    font-size: 13px;
    color: #f8fafc;
}

.arch-node span {
    display: block;
    font-size: 11px;
    color: #7f8da5;
    margin-top: 3px;
}

.arch-arrow {
    color: #8b5cf6;
    font-size: 20px;
    font-weight: 800;
}

/* File list */
.file-item {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 12px 16px;
    margin-bottom: 8px;
    border-radius: 12px;
    background: rgba(15,23,42,.60);
    border: 1px solid rgba(148,163,184,.10);
}

.file-name {
    color: #dbeafe;
    font-family: ui-monospace, monospace;
    font-size: 13px;
}

.file-ext {
    color: #7dd3fc;
    font-size: 11px;
    font-weight: 700;
    text-transform: uppercase;
}

/* Sidebar */
.sidebar-logo {
    font-family: "Space Grotesk", sans-serif;
    font-size: 20px;
    font-weight: 800;
    color: #f8fafc;
}

.sidebar-caption {
    color: #77869e;
    font-size: 12px;
    line-height: 1.5;
    margin-bottom: 18px;
}

/* Footer */
.footer {
    text-align: center;
    color: #56647a;
    font-size: 12px;
    padding-top: 36px;
    padding-bottom: 20px;
}
</style>""",
    unsafe_allow_html=True
)


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def repo_name(url: str) -> str:
    parts = [
        p
        for p in urlparse(url.strip()).path.strip("/").split("/")
        if p
    ]
    if len(parts) >= 2:
        return parts[1].replace(".git", "")
    return "Repository"


def file_ext(name: str) -> str:
    suffix = Path(name).suffix.lower()
    return suffix[1:] if suffix else "file"


def valid_repo_url(url: str) -> bool:
    parsed = urlparse(url.strip())
    parts = [p for p in parsed.path.strip("/").split("/") if p]
    return (
        parsed.netloc.lower() in {"github.com", "www.github.com"}
        and len(parts) >= 2
    )


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:
    st.markdown(
        '<div class="sidebar-logo">◈ RepoLens AI</div>',
        unsafe_allow_html=True
    )
    st.markdown(
        '<div class="sidebar-caption">Understand unfamiliar GitHub repositories with an AI-powered Qwen language model.</div>',
        unsafe_allow_html=True
    )

    ollama_ready = check_ollama_status()
    current_token = get_hf_token()

    if ollama_ready:
        st.success("● Ollama Active (Local Qwen)")
    elif current_token:
        st.success("● Hugging Face Active (Cloud Qwen)")
    else:
        st.warning("○ Cloud Mode (Token Needed)")

    # Cloud AI Settings
    with st.expander("⚙️ Cloud AI Settings", expanded=(not ollama_ready and not current_token)):
        st.caption("On Streamlit Cloud, inference runs via Hugging Face Serverless API (Qwen 2.5 Coder).")
        entered_token = st.text_input(
            "Hugging Face Token",
            type="password",
            value=st.session_state.get("hf_token", ""),
            placeholder="hf_...",
            help="Free token at https://huggingface.co/settings/tokens"
        )
        if entered_token:
            st.session_state["hf_token"] = entered_token.strip()
            st.rerun()

    st.markdown("---")

    st.markdown("### Workflow")
    workflow_items = [
        "01  Paste URL",
        "02  Clone repository",
        "03  Extract code",
        "04  Ask Qwen",
        "05  Explain"
    ]
    for item in workflow_items:
        st.caption(item)

    st.markdown("---")

    st.markdown("### Stack")
    st.caption("Python • Streamlit • GitPython")
    st.caption("Qwen 2.5 • Ollama • Hugging Face")

    st.markdown("---")
    st.caption("Ollama runs locally; Hugging Face serverless powers cloud deployments.")


# ============================================================
# HERO SECTION
# ============================================================

st.markdown(
    """<div class="hero">
<div class="eyebrow">✦ GenAI • Developer Tool</div>
<h1>Understand any<br>repository faster.</h1>
<p>RepoLens AI reads a public GitHub repository, identifies important source files, and uses Qwen to turn unfamiliar code into a clear, beginner-friendly explanation.</p>
</div>""",
    unsafe_allow_html=True
)

st.markdown('<div class="glow-line"></div>', unsafe_allow_html=True)


# ============================================================
# SEARCH & INPUT AREA
# ============================================================

github_url = st.text_input(
    "GitHub Repository URL",
    placeholder="https://github.com/username/repository"
)

st.caption("Tip: use the repository URL, not a /blob/main/file.py URL.")

if st.button("✦  Analyze Repository", type="primary"):
    if not github_url.strip():
        st.error("Please enter a GitHub repository URL.")
    elif not valid_repo_url(github_url):
        st.error("Please enter a valid public GitHub repository URL.")
    else:
        repo_path = None
        try:
            with st.status("Analyzing repository...", expanded=True) as status:
                st.write("🔗 Validating GitHub repository...")

                st.write("📥 Cloning repository...")
                repo_path = clone_repository(github_url.strip())

                st.write("🔎 Finding relevant source files...")
                context, files = build_repository_context(repo_path)

                if not context.strip():
                    raise RuntimeError(
                        "No supported source-code files were found in the repository."
                    )

                st.write(f"📄 Selected {len(files)} relevant files.")

                st.write("🤖 Generating explanation with Qwen AI...")
                explanation = explain_repository(
                    context,
                    hf_token=st.session_state.get("hf_token")
                )

                st.session_state["analysis"] = {
                    "github_url": github_url.strip(),
                    "files_analyzed": files,
                    "explanation": explanation
                }
                st.session_state["analyzed_url"] = github_url.strip()

                status.update(
                    label="Analysis completed successfully!",
                    state="complete",
                    expanded=False
                )

            st.rerun()

        except Exception as exc:
            st.error(f"Analysis failed: {exc}")

        finally:
            if repo_path:
                cleanup_repository(repo_path)


# ============================================================
# RESULTS SECTION
# ============================================================

result = st.session_state.get("analysis")

if result:
    analyzed_url = st.session_state.get("analyzed_url", result.get("github_url", ""))
    files = result.get("files_analyzed", [])
    explanation = result.get("explanation", "")

    languages = sorted(
        {file_ext(f) for f in files if file_ext(f) not in {"file", "md", "txt"}}
    )

    st.markdown('<div class="section-title">Repository Intelligence</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-subtitle">Qwen AI analysis completed successfully.</div>', unsafe_allow_html=True)

    metric_cols = st.columns(4)
    metrics = [
        ("◉", "Repository", repo_name(analyzed_url)),
        ("⌘", "Files analyzed", str(len(files))),
        ("◇", "File types", str(len(languages))),
        ("✦", "AI engine", "Qwen 2.5")
    ]

    for col, (icon, label, value) in zip(metric_cols, metrics):
        with col:
            st.markdown(
                f"""<div class="metric-card">
<div class="metric-icon">{icon}</div>
<div class="metric-label">{label}</div>
<div class="metric-value">{value}</div>
</div>""",
                unsafe_allow_html=True
            )

    st.markdown(
        f"""<div style="margin-top:18px;">
<span class="repo-pill">● Analysis completed</span>
<span style="color:#64748b;font-size:12px;margin-left:8px;">{analyzed_url}</span>
</div>""",
        unsafe_allow_html=True
    )

    st.markdown('<div class="section-title">Analysis Pipeline</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-subtitle">How your repository moves through the GenAI system.</div>', unsafe_allow_html=True)

    st.markdown(
        """<div class="info-card">
<div class="arch">
<div class="arch-node"><strong>GitHub</strong><span>Repository</span></div>
<div class="arch-arrow">→</div>
<div class="arch-node"><strong>GitPython</strong><span>Clone & scan</span></div>
<div class="arch-arrow">→</div>
<div class="arch-node"><strong>Code Processor</strong><span>Relevant files</span></div>
<div class="arch-arrow">→</div>
<div class="arch-node"><strong>Qwen AI</strong><span>Language Model</span></div>
<div class="arch-arrow">→</div>
<div class="arch-node"><strong>Explanation</strong><span>Streamlit UI</span></div>
</div>
</div>""",
        unsafe_allow_html=True
    )

    # TABS
    tab_ai, tab_files, tab_system = st.tabs([
        "✦ AI Explanation",
        "⌘ Files Analyzed",
        "◎ System"
    ])

    with tab_ai:
        st.markdown('<div class="section-title">AI-Generated Explanation</div>', unsafe_allow_html=True)
        st.markdown(explanation)

    with tab_files:
        st.markdown('<div class="section-title">Repository File Map</div>', unsafe_allow_html=True)
        st.caption("Files selected by the repository processor and provided to Qwen.")

        if files:
            left, right = st.columns(2)
            for index, name in enumerate(files):
                target = left if index % 2 == 0 else right
                with target:
                    st.markdown(
                        f"""<div class="file-item">
<span class="file-name">⌁ {name}</span>
<span class="file-ext">{file_ext(name)}</span>
</div>""",
                        unsafe_allow_html=True
                    )
        else:
            st.info("No file list was returned.")

    with tab_system:
        a, b, c = st.columns(3)
        cards = [
            ("Qwen 2.5", "High-performance coding model delivering clear explanations for beginners."),
            ("Repository Processing", "GitPython clones the repository and extracts key architecture files."),
            ("Dual Deployment", "Ollama provides private local inference; Hugging Face serverless powers cloud runs.")
        ]
        for col, (title, body) in zip((a, b, c), cards):
            with col:
                st.markdown(
                    f"""<div class="info-card">
<h4>{title}</h4>
<p>{body}</p>
</div>""",
                    unsafe_allow_html=True
                )

else:
    # EMPTY STATE
    st.markdown('<div class="section-title">Built for understanding code</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-subtitle">From a GitHub URL to a simple explanation in one workflow.</div>', unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    cards = [
        ("⌘ Repository Intelligence", "Clone a public repository and identify useful source files automatically."),
        ("✦ Qwen AI Analysis", "Use Qwen 2.5 to turn complex codebases into beginner-friendly explanations."),
        ("↗ Dual Deployment", "Run locally with Ollama or deploy anywhere in seconds via Streamlit Cloud.")
    ]
    for col, (title, body) in zip((c1, c2, c3), cards):
        with col:
            st.markdown(
                f"""<div class="info-card">
<h4>{title}</h4>
<p>{body}</p>
</div>""",
                unsafe_allow_html=True
            )


# ============================================================
# FOOTER
# ============================================================

st.markdown(
    '<div class="footer">RepoLens AI · Qwen 2.5 · Streamlit · GitPython · Ollama · Hugging Face</div>',
    unsafe_allow_html=True
)