from pathlib import Path

import streamlit as st

from agent import run_agent
from rag import index_document, search_documents


# =========================================================
# CONFIGURATION
# =========================================================

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
UPLOAD_DIR = DATA_DIR / "uploads"
REPORT_DIR = DATA_DIR / "reports"

UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
REPORT_DIR.mkdir(parents=True, exist_ok=True)

st.set_page_config(
    page_title="TaskPilot AI",
    page_icon="✦",
    layout="wide",
    initial_sidebar_state="expanded",
)


# =========================================================
# DESIGN SYSTEM
# =========================================================

st.markdown(
    """
    <style>
    /* ---------- GLOBAL ---------- */

    :root {
        color-scheme: light;
        --primary: #635BFF;
        --primary-dark: #5046E5;
        --ink: #172033;
        --muted: #667085;
        --border: #E7EAF2;
        --surface: #FFFFFF;
        --background: #F7F8FC;
        --success: #138A63;
    }

    html, body, [data-testid="stAppViewContainer"] {
        background: var(--background) !important;
        color: var(--ink) !important;
    }

    [data-testid="stAppViewContainer"] * {
        box-sizing: border-box;
    }

    [data-testid="stHeader"] {
        background: rgba(247, 248, 252, 0.96) !important;
    }

    [data-testid="stMain"] {
        background: var(--background) !important;
    }

    .block-container {
        max-width: 1450px;
        padding-top: 2.1rem;
        padding-bottom: 3rem;
    }

    h1, h2, h3, h4, p, label {
        color: var(--ink);
    }

    h1 {
        letter-spacing: -1.1px;
        font-weight: 750 !important;
    }

    h2, h3 {
        letter-spacing: -0.4px;
    }

    /* ---------- SIDEBAR ---------- */

    [data-testid="stSidebar"] {
        background: #FFFFFF !important;
        border-right: 1px solid var(--border);
    }

    [data-testid="stSidebar"] > div:first-child {
        background: #FFFFFF !important;
    }

    [data-testid="stSidebar"] * {
        color: var(--ink);
    }

    [data-testid="stSidebar"] .block-container {
        padding-top: 1.4rem;
    }

    .brand {
        display: flex;
        align-items: center;
        gap: 11px;
        margin: 0 0 6px 0;
    }

    .brand-icon {
        display: flex;
        justify-content: center;
        align-items: center;
        width: 42px;
        height: 42px;
        border-radius: 13px;
        color: #FFFFFF !important;
        background: linear-gradient(135deg, #635BFF, #8B5CF6);
        font-size: 23px;
        font-weight: 800;
        box-shadow: 0 5px 14px rgba(99, 91, 255, 0.22);
    }

    .brand-name {
        font-size: 20px;
        font-weight: 800;
        letter-spacing: -0.6px;
        color: var(--ink) !important;
    }

    .brand-subtitle {
        color: var(--muted) !important;
        font-size: 12px;
        margin-bottom: 25px;
    }

    .side-label {
        text-transform: uppercase;
        letter-spacing: 1.1px;
        font-size: 10px;
        font-weight: 800;
        color: #98A2B3 !important;
        margin: 22px 0 9px;
    }

    .model-card {
        padding: 15px;
        background: #F7F7FF;
        border: 1px solid #E7E5FF;
        border-radius: 14px;
        margin-top: 10px;
    }

    .model-name {
        font-weight: 750;
        font-size: 14px;
        margin-bottom: 6px;
        color: #292554 !important;
    }

    .model-description {
        color: #77749B !important;
        font-size: 12px;
        line-height: 1.6;
    }

    .status-dot {
        display: inline-block;
        width: 8px;
        height: 8px;
        background: #18A875;
        border-radius: 50%;
        margin-right: 7px;
    }

    /* ---------- HERO ---------- */

    .hero {
        position: relative;
        overflow: hidden;
        padding: 32px 34px;
        border-radius: 22px;
        color: white !important;
        background: linear-gradient(120deg, #27235F 0%, #5146D8 58%, #8276FF 100%);
        box-shadow: 0 12px 35px rgba(66, 56, 180, 0.13);
        margin-bottom: 26px;
    }

    .hero:after {
        content: "";
        position: absolute;
        width: 240px;
        height: 240px;
        right: -70px;
        top: -110px;
        border-radius: 50%;
        border: 35px solid rgba(255, 255, 255, 0.08);
    }

    .hero-eyebrow {
        color: #DDD9FF !important;
        text-transform: uppercase;
        font-size: 11px;
        font-weight: 800;
        letter-spacing: 1.8px;
        margin-bottom: 12px;
    }

    .hero h1 {
        color: #FFFFFF !important;
        font-size: clamp(28px, 3vw, 40px);
        line-height: 1.2;
        margin: 0 0 12px 0;
    }

    .hero p {
        color: #E6E4FF !important;
        font-size: 15px;
        line-height: 1.8;
        max-width: 700px;
        margin: 0;
    }

    /* ---------- CARDS ---------- */

    .metric-card, .feature-card, .content-card {
        background: var(--surface);
        border: 1px solid var(--border);
        border-radius: 17px;
        padding: 21px;
        height: 100%;
        box-shadow: 0 2px 5px rgba(16, 24, 40, 0.02);
    }

    .metric-label {
        color: var(--muted) !important;
        font-size: 13px;
        margin-bottom: 11px;
    }

    .metric-value {
        font-size: 25px;
        font-weight: 800;
        letter-spacing: -0.7px;
        color: var(--ink) !important;
    }

    .metric-note {
        color: var(--muted) !important;
        font-size: 12px;
        margin-top: 8px;
    }

    .feature-icon {
        display: inline-flex;
        justify-content: center;
        align-items: center;
        width: 43px;
        height: 43px;
        background: #F0EFFF;
        border-radius: 12px;
        font-size: 21px;
        margin-bottom: 15px;
    }

    .feature-title {
        color: var(--ink) !important;
        font-size: 15px;
        font-weight: 750;
        margin-bottom: 7px;
    }

    .feature-description {
        color: var(--muted) !important;
        font-size: 13px;
        line-height: 1.75;
    }

    .section-heading {
        font-size: 21px;
        font-weight: 800;
        color: var(--ink) !important;
        margin: 28px 0 5px;
    }

    .section-description {
        color: var(--muted) !important;
        font-size: 13px;
        margin-bottom: 18px;
    }

    /* ---------- INPUTS ---------- */

    input, textarea,
    [data-baseweb="input"] input,
    [data-baseweb="textarea"] textarea {
        color: #172033 !important;
        background: #FFFFFF !important;
        -webkit-text-fill-color: #172033 !important;
        caret-color: #635BFF !important;
    }

    input::placeholder, textarea::placeholder {
        color: #98A2B3 !important;
        -webkit-text-fill-color: #98A2B3 !important;
    }

    [data-baseweb="input"],
    [data-baseweb="textarea"],
    [data-testid="stFileUploaderDropzone"] {
        background: #FFFFFF !important;
        border-color: #DDE2EC !important;
        border-radius: 12px !important;
    }

    [data-testid="stChatInput"] {
        background: #FFFFFF !important;
        border: 1px solid #DDE2EC !important;
        border-radius: 16px !important;
        box-shadow: 0 5px 20px rgba(16, 24, 40, 0.05);
    }
    [data-testid="stBottom"] {
    background: #F7F8FC !important;
    background-color: #F7F8FC !important;
}

[data-testid="stBottom"] > div {
    background: #F7F8FC !important;
}

[data-testid="stBottom"]::before {
    background: #F7F8FC !important;
}

[data-testid="stChatInput"] {
    background: #FFFFFF !important;
    border: 1px solid #DDE2EC !important;
}

[data-testid="stChatInput"] textarea {
    background: #FFFFFF !important;
    color: #172033 !important;
    -webkit-text-fill-color: #172033 !important;
}

    [data-testid="stChatInput"] textarea {
        background: #FFFFFF !important;
        color: #172033 !important;
        -webkit-text-fill-color: #172033 !important;
    }

    /* ---------- BUTTONS ---------- */

    .stButton > button,
    .stDownloadButton > button {
        border-radius: 10px !important;
        min-height: 42px;
        font-weight: 650 !important;
        transition: all 0.15s ease;
    }

    .stButton > button[kind="primary"],
    .stDownloadButton > button {
        background: var(--primary) !important;
        color: #FFFFFF !important;
        border: 1px solid var(--primary) !important;
    }

    .stButton > button[kind="primary"]:hover,
    .stDownloadButton > button:hover {
        background: var(--primary-dark) !important;
        border-color: var(--primary-dark) !important;
    }

    .stButton > button[kind="secondary"] {
        background: #FFFFFF !important;
        color: var(--ink) !important;
        border: 1px solid var(--border) !important;
    }

    /* ---------- CHAT ---------- */

    [data-testid="stChatMessage"] {
        background: #FFFFFF !important;
        border: 1px solid var(--border);
        border-radius: 15px;
        padding: 15px;
        margin-bottom: 13px;
    }

    [data-testid="stChatMessage"] p,
    [data-testid="stChatMessage"] li {
        color: #172033 !important;
        line-height: 1.75;
    }

    /* ---------- EXPANDERS / ALERTS ---------- */

    [data-testid="stExpander"] {
        background: #FFFFFF !important;
        border: 1px solid var(--border) !important;
        border-radius: 13px !important;
        overflow: hidden;
    }

    [data-testid="stExpander"] summary,
    [data-testid="stExpander"] summary span {
        color: #172033 !important;
    }

    [data-testid="stAlert"] {
        border-radius: 12px;
    }

    [data-testid="stCode"],
    [data-testid="stCode"] pre,
    [data-testid="stCode"] code {
        background: #F1F3F9 !important;
        color: #25314B !important;
    }

    [data-testid="stFileUploaderDropzone"] * {
        color: #344054 !important;
    }

    hr {
        border-color: var(--border) !important;
    }

    /* ---------- FOOTER ---------- */

    .footer {
        margin-top: 35px;
        padding-top: 18px;
        border-top: 1px solid var(--border);
        color: #98A2B3 !important;
        font-size: 12px;
        text-align: center;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# SESSION STATE
# =========================================================

if "messages" not in st.session_state:
    st.session_state.messages = []

if "traces" not in st.session_state:
    st.session_state.traces = []

if "indexed_files" not in st.session_state:
    st.session_state.indexed_files = {}


# =========================================================
# HELPERS
# =========================================================

def render_hero(eyebrow, title, description):
    st.markdown(
        f"""
        <div class="hero">
            <div class="hero-eyebrow">{eyebrow}</div>
            <h1>{title}</h1>
            <p>{description}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_trace(trace):
    if not trace:
        st.caption("No tool execution details were returned.")
        return

    for index, event in enumerate(trace, start=1):
        if event.get("type") == "tool_call":
            with st.expander(
                f"⚙️ Step {index} · {event.get('tool', 'Tool')}"
            ):
                st.markdown("**Arguments supplied to the tool**")
                st.json(event.get("arguments", {}))

        elif event.get("type") == "tool_result":
            with st.expander(
                f"✓ Result · {event.get('tool', 'Tool')}"
            ):
                st.code(str(event.get("result", "")))


def get_local_documents():
    return sorted(
        path
        for path in UPLOAD_DIR.iterdir()
        if path.is_file() and path.suffix.lower() in {".txt", ".pdf"}
    )


def get_reports():
    return sorted(
        REPORT_DIR.glob("*.txt"),
        key=lambda path: path.stat().st_mtime,
        reverse=True,
    )


def process_uploaded_file(uploaded):
    """
    Save and index an uploaded file.

    Uses a temporary file and replaces the destination only after the
    upload has been fully written.
    """
    safe_name = Path(uploaded.name).name
    destination = UPLOAD_DIR / safe_name
    temporary = UPLOAD_DIR / f".uploading_{safe_name}"

    try:
        temporary.write_bytes(uploaded.getvalue())
        temporary.replace(destination)

        result = index_document(str(destination))
        return result

    finally:
        if temporary.exists():
            temporary.unlink()


# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:
    st.markdown(
        """
        <div class="brand">
            <div class="brand-icon">✦</div>
            <div class="brand-name">TaskPilot AI</div>
        </div>
        <div class="brand-subtitle">
            Your intelligent workspace
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<div class="side-label">WORKSPACE</div>', unsafe_allow_html=True)

    page = st.radio(
        "Navigate",
        [
            "AI Assistant",
            "Document Library",
            "Saved Reports",
            "About",
        ],
        label_visibility="collapsed",
        format_func=lambda item: {
            "AI Assistant": "💬  AI Assistant",
            "Document Library": "📚  Document Library",
            "Saved Reports": "📝  Saved Reports",
            "About": "ℹ️  About TaskPilot",
        }[item],
    )

    st.markdown("---")

    st.markdown('<div class="side-label">LOCAL AI MODEL</div>', unsafe_allow_html=True)

    st.markdown(
        """
        <div class="model-card">
            <div class="model-name">Qwen 2.5 · 1.5B</div>
            <div class="model-description">
                <span class="status-dot"></span>
                Configured for local inference<br><br>
                Language model: Ollama<br>
                Embeddings: nomic-embed-text
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<div class="side-label">AGENT CAPABILITIES</div>', unsafe_allow_html=True)

    st.markdown(
        """
        <div style="font-size:13px; line-height:2.3">
        🧮 &nbsp; Calculator<br>
        🕒 &nbsp; Current time<br>
        📝 &nbsp; Report writer<br>
        🔎 &nbsp; Document search
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("---")

    if st.button("＋  New conversation", use_container_width=True):
        st.session_state.messages = []
        st.session_state.traces = []
        st.rerun()

    st.markdown(
        """
        <div style="color:#98A2B3;font-size:11px;margin-top:18px">
            TASKPILOT AI · LOCAL WORKSPACE
        </div>
        """,
        unsafe_allow_html=True,
    )


# =========================================================
# AI ASSISTANT
# =========================================================

if page == "AI Assistant":

    render_hero(
        "YOUR PERSONAL AI WORKSPACE",
        "Turn instructions into action.",
        "Ask questions, retrieve information from your documents, "
        "perform calculations, and generate reports with an AI agent.",
    )

    doc_count = len(get_local_documents())
    report_count = len(get_reports())

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-label">AI MODEL</div>
                <div class="metric-value" style="font-size:21px">
                    Qwen 2.5 1.5B
                </div>
                <div class="metric-note">Local language model</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col2:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-label">DOCUMENTS</div>
                <div class="metric-value">{doc_count}</div>
                <div class="metric-note">Files in the upload folder</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col3:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-label">SAVED REPORTS</div>
                <div class="metric-value">{report_count}</div>
                <div class="metric-note">Text reports available</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown(
        '<div class="section-heading">What can I help you with?</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="section-description">'
        'Choose a starting point or enter your own task below.'
        '</div>',
        unsafe_allow_html=True,
    )

    example_columns = st.columns(3)

    examples = [
        ("🧮", "Calculate", "Calculate 125 multiplied by 48."),
        ("🔎", "Search documents", "Search my indexed documents and summarize the project."),
        ("📝", "Create a report", "Create a report named overview.txt about TaskPilot-AI."),
    ]

    for col, (icon, title, example) in zip(example_columns, examples):
        with col:
            st.markdown(
                f"""
                <div class="feature-card">
                    <div class="feature-icon">{icon}</div>
                    <div class="feature-title">{title}</div>
                    <div class="feature-description">
                        {example}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.markdown(
        '<div class="section-heading">Conversation</div>',
        unsafe_allow_html=True,
    )

    if not st.session_state.messages:
        st.info(
            "Start with a task below. For document questions, "
            "upload and index your files in Document Library first."
        )

    for index, message in enumerate(st.session_state.messages):
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

            if message["role"] == "assistant":
                trace = (
                    st.session_state.traces[index]
                    if index < len(st.session_state.traces)
                    else []
                )

                if trace:
                    with st.expander("⚙️ View execution trace", expanded=False):
                        render_trace(trace)

    prompt = st.chat_input(
        "Tell TaskPilot what you want to accomplish..."
    )

    if prompt:
        st.session_state.messages.append(
            {"role": "user", "content": prompt}
        )
        st.session_state.traces.append([])

        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            try:
                with st.spinner("TaskPilot is working on your request..."):
                    result = run_agent(prompt)

                answer = str(result["answer"])
                trace = result.get("trace", [])

                st.markdown(answer)

                if trace:
                    with st.expander("⚙️ View execution trace", expanded=True):
                        render_trace(trace)

            except Exception as exc:
                answer = (
                    "I couldn't complete this task. "
                    "Please check the terminal for the error details."
                )
                trace = []

                st.error(answer)
                st.exception(exc)

        st.session_state.messages.append(
            {"role": "assistant", "content": answer}
        )
        st.session_state.traces.append(trace)
        st.rerun()


# =========================================================
# DOCUMENT LIBRARY
# =========================================================

elif page == "Document Library":

    render_hero(
        "KNOWLEDGE BASE",
        "Your documents. Searchable.",
        "Upload text-based PDFs or TXT files, index their content, "
        "and retrieve relevant passages using semantic search.",
    )

    st.markdown(
        '<div class="section-heading">Upload documents</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="section-description">'
        'Supported formats: PDF and TXT. Files are stored locally.'
        '</div>',
        unsafe_allow_html=True,
    )

    with st.container(border=True):
        uploaded_files = st.file_uploader(
            "Drop files here or browse your computer",
            type=["pdf", "txt"],
            accept_multiple_files=True,
            help="Text-based PDF and TXT files are supported.",
        )

        if uploaded_files:
            st.write(f"**{len(uploaded_files)} file(s) selected**")

            for uploaded in uploaded_files:
                st.caption(
                    f"📄 {uploaded.name} · {uploaded.size:,} bytes"
                )

        if st.button(
            "Upload and index documents",
            type="primary",
            use_container_width=True,
        ):
            if not uploaded_files:
                st.warning("Choose at least one document first.")
            else:
                succeeded = 0

                for uploaded in uploaded_files:
                    try:
                        with st.spinner(f"Indexing {uploaded.name}..."):
                            result = process_uploaded_file(uploaded)

                        st.session_state.indexed_files[uploaded.name] = result

                        st.success(
                            f"{uploaded.name}: "
                            f"{result['chunks_indexed']} chunk(s) indexed."
                        )
                        succeeded += 1

                    except Exception as exc:
                        st.error(f"{uploaded.name} failed: {exc}")

                if succeeded:
                    st.toast(f"Successfully indexed {succeeded} document(s).")

    st.markdown(
        '<div class="section-heading">Stored documents</div>',
        unsafe_allow_html=True,
    )

    files = get_local_documents()

    if not files:
        st.info("Your document library is empty. Upload a file above.")
    else:
        for path in files:
            with st.container(border=True):
                file_col, size_col = st.columns([4, 1])

                with file_col:
                    st.markdown(f"**📄 {path.name}**")
                    st.caption("Stored in your local project")

                with size_col:
                    st.metric("Size", f"{path.stat().st_size / 1024:.1f} KB")

    st.markdown(
        '<div class="section-heading">Search your knowledge base</div>',
        unsafe_allow_html=True,
    )

    with st.form("document_search_form"):
        query = st.text_input(
            "What would you like to know?",
            placeholder="e.g. What are the main objectives in my document?",
        )

        submitted = st.form_submit_button(
            "Search indexed documents",
            type="primary",
            use_container_width=True,
        )

    if submitted:
        if not query.strip():
            st.warning("Enter a question to search.")
        else:
            try:
                with st.spinner("Searching indexed content..."):
                    results = search_documents(query, top_k=3)

                if not results:
                    st.warning(
                        "No indexed content was found. Upload and index "
                        "the document before searching."
                    )
                else:
                    st.success(f"Found {len(results)} relevant passage(s).")

                    for result in results:
                        with st.container(border=True):
                            st.markdown(
                                f"**📄 Source: {result['filename']}**"
                            )
                            st.write(result["text"])
                            st.caption(
                                f"Chunk {result['chunk_index']} · "
                                f"Distance: {result['distance']:.4f}"
                            )

            except Exception as exc:
                st.error(f"Document search failed: {exc}")


# =========================================================
# SAVED REPORTS
# =========================================================

elif page == "Saved Reports":

    render_hero(
        "YOUR OUTPUTS",
        "Reports, ready when you are.",
        "Review and download text reports generated by your AI agent.",
    )

    reports = get_reports()

    st.markdown(
        '<div class="section-heading">Report library</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        f'<div class="section-description">'
        f'{len(reports)} saved report(s)'
        f'</div>',
        unsafe_allow_html=True,
    )

    if not reports:
        st.info(
            "No reports yet. Ask TaskPilot to create a report "
            "using the report writer tool."
        )
    else:
        for report in reports:
            try:
                content = report.read_text(
                    encoding="utf-8",
                    errors="replace",
                )

                with st.container(border=True):
                    report_col, button_col = st.columns([4, 1])

                    with report_col:
                        st.markdown(f"**📝 {report.name}**")
                        st.caption(
                            f"Updated {report.stat().st_mtime:.0f}"
                        )

                    with button_col:
                        st.download_button(
                            "Download",
                            data=content,
                            file_name=report.name,
                            mime="text/plain",
                            key=f"download_{report.name}",
                            use_container_width=True,
                        )

                    with st.expander("Preview report"):
                        st.text_area(
                            "Report content",
                            value=content,
                            height=180,
                            key=f"preview_{report.name}",
                        )

            except OSError as exc:
                st.error(f"Could not read {report.name}: {exc}")


# =========================================================
# ABOUT
# =========================================================

elif page == "About":

    render_hero(
        "ABOUT THE PROJECT",
        "Meet TaskPilot AI.",
        "An experimental local Agentic AI workspace combining tool "
        "execution with retrieval-augmented generation.",
    )

    st.markdown(
        '<div class="section-heading">Technology stack</div>',
        unsafe_allow_html=True,
    )

    technologies = [
        (
            "🧠",
            "LangGraph",
            "Orchestrates the agent workflow and tool interactions.",
        ),
        (
            "💬",
            "Ollama + Qwen",
            "Runs the language model locally on your computer.",
        ),
        (
            "🔎",
            "RAG + ChromaDB",
            "Retrieves relevant content from indexed documents.",
        ),
        (
            "🧬",
            "nomic-embed-text",
            "Converts document passages and queries into embeddings.",
        ),
        (
            "⚡",
            "Streamlit",
            "Provides the interactive user interface.",
        ),
        (
            "🐍",
            "Python",
            "Connects tools, retrieval, and application logic.",
        ),
    ]

    cols = st.columns(3)

    for index, (icon, title, description) in enumerate(technologies):
        with cols[index % 3]:
            st.markdown(
                f"""
                <div class="feature-card" style="margin-bottom:15px">
                    <div class="feature-icon">{icon}</div>
                    <div class="feature-title">{title}</div>
                    <div class="feature-description">{description}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.markdown(
        '<div class="section-heading">Agent workflow</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="content-card">
            <div class="feature-title">
                01 · User request
            </div>
            <div class="feature-description">
                A user submits a natural-language task.
            </div>
            <br>
            <div class="feature-title">
                02 · Agent decision
            </div>
            <div class="feature-description">
                The agent determines which available tool is appropriate.
            </div>
            <br>
            <div class="feature-title">
                03 · Tool execution
            </div>
            <div class="feature-description">
                The selected tool performs the operation and returns a result.
            </div>
            <br>
            <div class="feature-title">
                04 · Observation and response
            </div>
            <div class="feature-description">
                The agent uses the returned result to formulate its answer.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.caption(
        "Project capabilities should be described according to "
        "what has actually been implemented and tested."
    )


# =========================================================
# FOOTER
# =========================================================

st.markdown(
    """
    <div class="footer">
        TaskPilot AI · Local Agentic AI Workspace · Built with Python
    </div>
    """,
    unsafe_allow_html=True,
)