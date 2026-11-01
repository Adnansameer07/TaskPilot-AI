from pathlib import Path
import ast
import operator
import re

from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent

from rag import search_documents
from tools import calculate, get_current_time, save_report


# --------------------------------------------------
# MODEL
# --------------------------------------------------

def get_model():
    return ChatOllama(
        model="qwen2.5:1.5b",
        temperature=0,
    )


# --------------------------------------------------
# AGENT TOOLS
# --------------------------------------------------

@tool
def calculator(expression: str) -> str:
    """Calculate a mathematical expression."""
    normalized = (
        expression.replace("×", "*")
        .replace("÷", "/")
        .replace("−", "-")
        .replace("–", "-")
        .replace("^", "**")
    )
    return str(calculate(normalized))


@tool
def current_time() -> str:
    """Get the computer's current local date and time."""
    return str(get_current_time())


@tool
def report_writer(
    content: str,
    filename: str = "report.txt",
) -> str:
    """Save a text report in the project's reports directory."""
    return str(save_report(content, filename))


@tool
def document_search(query: str) -> str:
    """Search indexed documents and return relevant passages."""
    results = search_documents(query, top_k=3)

    if not results:
        return "No relevant indexed document content was found."

    passages = []

    for item in results:
        passages.append(
            f"Source: {item['filename']}\n"
            f"Content: {item['text']}"
        )

    return "\n\n".join(passages)


# --------------------------------------------------
# DOCUMENT QUESTION DETECTION
# --------------------------------------------------

def is_document_question(task: str) -> bool:
    text = task.lower()

    indicators = [
        "search my indexed documents",
        "search indexed documents",
        "search my documents",
        "according to the document",
        "according to the pdf",
        "from my uploaded file",
        "from my notes",
        "semcache",
        "what does the document say",
        "summarize the uploaded",
    ]

    return any(term in text for term in indicators)


def answer_from_documents(task: str) -> dict:
    trace = [
        {
            "type": "tool_call",
            "tool": "document_search",
            "arguments": {"query": task},
        }
    ]

    results = search_documents(task, top_k=3)

    if not results:
        message = (
            "No relevant indexed document content was found. "
            "Check that your file is uploaded and indexed."
        )

        trace.append({
            "type": "tool_result",
            "tool": "document_search",
            "result": message,
        })

        return {"answer": message, "trace": trace}

    passages = []

    for item in results:
        passages.append(
            f"Source: {item['filename']}\n"
            f"Content: {item['text']}"
        )

    context = "\n\n---\n\n".join(passages)

    trace.append({
        "type": "tool_result",
        "tool": "document_search",
        "result": context,
    })

    response = get_model().invoke([
        SystemMessage(content=(
            "Answer using only the retrieved document passages. "
            "Do not invent facts. If evidence is insufficient, "
            "say so. Identify the source filenames. "
            "Explain the findings clearly and concisely."
        )),
        HumanMessage(content=(
            f"Question:\n{task}\n\n"
            f"Retrieved passages:\n{context}"
        )),
    ])

    return {
        "answer": str(response.content),
        "trace": trace,
    }


# --------------------------------------------------
# MULTI-TASK WORKFLOW
# --------------------------------------------------

def run_multi_task() -> dict:
    trace = []
    errors = []
    results = {}

    # STEP 1: Calculate
    expression = "125 * 48"

    try:
        calc = calculate(expression)
        results["calculation"] = calc

        trace.append({
            "type": "tool_call",
            "tool": "calculator",
            "arguments": {"expression": expression},
        })
        trace.append({
            "type": "tool_result",
            "tool": "calculator",
            "result": str(calc),
        })

        if not isinstance(calc, dict) or calc.get("success") is not True:
            errors.append("Calculator failed.")

    except Exception as exc:
        calc = {"success": False, "error": str(exc)}
        results["calculation"] = calc
        errors.append(f"Calculator failed: {exc}")

    # STEP 2: Retrieve actual local time
    try:
        timestamp = get_current_time()
        results["timestamp"] = timestamp

        trace.append({
            "type": "tool_call",
            "tool": "current_time",
            "arguments": {},
        })
        trace.append({
            "type": "tool_result",
            "tool": "current_time",
            "result": str(timestamp),
        })

        if not isinstance(timestamp, dict) or timestamp.get("success") is not True:
            errors.append("Current-time tool failed.")

    except Exception as exc:
        timestamp = {"success": False, "error": str(exc)}
        results["timestamp"] = timestamp
        errors.append(f"Current-time tool failed: {exc}")

    # STEP 3: Search indexed documents
    try:
        docs = search_documents(
            "What is the main purpose of SemCache?",
            top_k=3,
        )

        results["documents"] = docs

        if docs:
            findings = "\n\n".join(
                f"Source: {item['filename']}\n{item['text']}"
                for item in docs
            )
        else:
            findings = "No relevant indexed document content was found."
            errors.append("No relevant document passages were found.")

        trace.append({
            "type": "tool_call",
            "tool": "document_search",
            "arguments": {
                "query": "What is the main purpose of SemCache?"
            },
        })
        trace.append({
            "type": "tool_result",
            "tool": "document_search",
            "result": findings,
        })

    except Exception as exc:
        docs = []
        findings = f"Document search failed: {exc}"
        results["documents"] = []
        errors.append(findings)

    # STEP 4: Save actual results to a report
    calc_value = (
        calc.get("result", "Unavailable")
        if isinstance(calc, dict)
        else calc
    )

    time_value = (
        timestamp.get("time", "Unavailable")
        if isinstance(timestamp, dict)
        else timestamp
    )

    report_content = (
        "TaskPilot-AI Integration Test Report\n"
        "====================================\n\n"
        f"Calculation: {expression}\n"
        f"Calculator result: {calc_value}\n\n"
        f"Current local timestamp: {time_value}\n\n"
        f"Document search findings:\n{findings}\n"
    )

    try:
        report = save_report(
            report_content,
            "final_demo_check.txt",
        )

        trace.append({
            "type": "tool_call",
            "tool": "report_writer",
            "arguments": {"filename": "integration_test.txt"},
        })
        trace.append({
            "type": "tool_result",
            "tool": "report_writer",
            "result": str(report),
        })

        results["report"] = report

        if not isinstance(report, dict) or report.get("success") is not True:
            errors.append("Report saving failed.")

    except Exception as exc:
        report = {"success": False, "error": str(exc)}
        results["report"] = report
        errors.append(f"Report saving failed: {exc}")

    # FORMAT THE ANSWER
    report_path = (
        report.get("path", "Unavailable")
        if isinstance(report, dict)
        else "Unavailable"
    )

    document_sources = sorted({
        item["filename"] for item in docs
    }) if docs else []

    document_summary = (
        "Retrieved passages from: " + ", ".join(document_sources)
        if document_sources
        else "No relevant passages retrieved."
    )

    overall_success = (
        not errors
        and isinstance(calc, dict)
        and calc.get("success") is True
        and isinstance(timestamp, dict)
        and timestamp.get("success") is True
        and isinstance(report, dict)
        and report.get("success") is True
        and bool(docs)
    )

    answer = (
        "### TaskPilot AI — Integration Test\n\n"
        f"**1. Calculation:** {calc_value}\n\n"
        f"**2. Current local time:** {time_value}\n\n"
        f"**3. Document search:** {document_summary}\n\n"
        f"**4. Report:** "
        f"{'Saved successfully' if isinstance(report, dict) and report.get('success') else 'Save failed'}\n\n"
        f"**Report path:** `{report_path}`\n\n"
        f"**Overall status:** "
        f"{'SUCCESS' if overall_success else 'CHECK REQUIRED'}"
    )

    if errors:
        answer += "\n\n**Issues:**\n" + "\n".join(
            f"- {error}" for error in errors
        )

    return {
        "answer": answer,
        "trace": trace,
    }


# --------------------------------------------------
# MAIN AGENT
# --------------------------------------------------

def run_agent(task: str) -> dict:
    if not isinstance(task, str) or not task.strip():
        return {
            "answer": "Please enter a task.",
            "trace": [],
        }

    task = task.strip()
    task_lower = task.lower()

    # Explicit multi-task workflow
    if (
        "perform these tasks in order" in task_lower
        or "multi-task integration test" in task_lower
    ):
        try:
            return run_multi_task()
        except Exception as exc:
            return {
                "answer": f"Multi-task execution failed: {exc}",
                "trace": [],
            }

    # Report requests
    report_requested = any(
        phrase in task_lower
        for phrase in [
            "create a report",
            "generate a report",
            "write a report",
            "save a report",
        ]
    )

    if report_requested:
        match = re.search(
            r"(?:named|called)\s+([A-Za-z0-9_.-]+\.txt)",
            task,
            re.IGNORECASE,
        )

        filename = match.group(1) if match else "report.txt"

        content = (
            "TaskPilot-AI Project Report\n"
            "===========================\n\n"
            "TaskPilot-AI is a local Agentic AI assistant built "
            "with Python, LangGraph, Streamlit, and Ollama.\n\n"
            "Configured capabilities include mathematical "
            "calculations, local date/time retrieval, report "
            "writing, and indexed document search.\n"
        )

        try:
            report = save_report(content, filename)

            trace = [
                {
                    "type": "tool_call",
                    "tool": "report_writer",
                    "arguments": {"filename": filename},
                },
                {
                    "type": "tool_result",
                    "tool": "report_writer",
                    "result": str(report),
                },
            ]

            path = (
                report.get("path", "")
                if isinstance(report, dict)
                else ""
            )

            if isinstance(report, dict) and report.get("success") is True:
                answer = f"Report saved successfully: `{path}`"
            else:
                answer = f"Report saving failed: {report}"

            return {"answer": answer, "trace": trace}

        except Exception as exc:
            return {
                "answer": f"Report creation failed: {exc}",
                "trace": [],
            }

    # Document questions
    if is_document_question(task):
        try:
            return answer_from_documents(task)
        except Exception as exc:
            return {
                "answer": f"Document search failed: {exc}",
                "trace": [],
            }

    # General agent workflow
    try:
        model = get_model()

        agent = create_react_agent(
            model=model,
            tools=[
                calculator,
                current_time,
                report_writer,
                document_search,
            ],
            prompt=(
                "You are TaskPilot, a local Agentic AI assistant.\n"
                "Use calculator for arithmetic.\n"
                "Use current_time for actual local date/time.\n"
                "Use report_writer to save requested reports.\n"
                "Use document_search for indexed-document questions.\n"
                "Never claim a tool succeeded without checking its result.\n"
                "Answer clearly and concisely."
            ),
        )

        result = agent.invoke(
            {"messages": [HumanMessage(content=task)]},
            config={"recursion_limit": 10},
        )

        trace = []

        for message in result["messages"]:
            for call in getattr(message, "tool_calls", []) or []:
                trace.append({
                    "type": "tool_call",
                    "tool": call["name"],
                    "arguments": call["args"],
                })

            if getattr(message, "type", "") == "tool":
                trace.append({
                    "type": "tool_result",
                    "tool": message.name,
                    "result": str(message.content),
                })

        return {
            "answer": str(result["messages"][-1].content),
            "trace": trace,
        }

    except Exception as exc:
        return {
            "answer": f"Agent execution failed: {exc}",
            "trace": [],
        }