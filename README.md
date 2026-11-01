# TaskPilot AI

TaskPilot AI is a local AI assistant built with Streamlit, LangGraph, and Ollama. It combines a chat interface with utility tools and retrieval-augmented search over documents you upload.

## Features

- Chat with a local Qwen 2.5 1.5B model through Ollama.
- Calculate arithmetic expressions and retrieve the computer's local date and time.
- Create and browse text reports saved in the project.
- Upload PDF and TXT documents, index their contents locally, and search for relevant passages.
- Inspect tool calls and results in the interface.

## Requirements

- Python 3.11
- [Ollama](https://ollama.com/) installed and running
- The Ollama models used by this project:

  ```powershell
  ollama pull qwen2.5:1.5b
  ollama pull nomic-embed-text
  ```

## Setup

In PowerShell, from the project directory:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

If PowerShell prevents environment activation, run the commands using `.venv\Scripts\python.exe` instead of activating the environment.

Start the app:

```powershell
streamlit run app.py
```

Streamlit prints a local URL (usually `http://localhost:8501`) to open in your browser. Ollama must be running locally and the model names above must be available before using chat or document search.

## Using the app

Use the sidebar to move between **AI Assistant**, **Document Library**, **Saved Reports**, and **About**.

1. In **Document Library**, upload PDF or TXT files and index them.
2. Ask questions about indexed files in **AI Assistant** or use document search in the library.
3. Ask the assistant to calculate, report the local time, or save a report.
4. Review saved text reports in **Saved Reports**.

Uploaded documents, generated reports, and the ChromaDB index are stored under `data/` and are excluded from Git. They are local to this checkout and can be recreated by uploading documents again.

## Tests

The agent tests call the local Ollama model. Start Ollama and make sure `qwen2.5:1.5b` and `nomic-embed-text` are available, then run:

```powershell
python -m pytest -q
```

## Project layout

```text
app.py          Streamlit user interface
agent.py        LangGraph assistant and tool routing
rag.py          PDF/TXT extraction, embeddings, and ChromaDB search
tools.py        Calculator, local time, and report-writing tools
test_agent.py   Agent tests
data/           Local uploads, reports, and vector database (ignored)
streamlit/      Streamlit theme configuration
```

## Privacy

This project uses Ollama for local model inference and embeddings. Uploaded documents and generated reports are kept in the local `data/` directory. Do not commit credentials, private documents, generated reports, or local database files.
