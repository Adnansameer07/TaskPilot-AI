
from agent import run_agent


def test_calculator():
    result = run_agent("Calculate 125 multiplied by 48.")

    assert result is not None
    assert "6000" in str(result["answer"])
    assert any(
        item.get("tool") == "calculator"
        for item in result["trace"]
    )


def test_current_time():
    result = run_agent("What is the current local date and time?")

    assert result is not None
    assert any(
        item.get("tool") == "current_time"
        for item in result["trace"]
    )


def test_report_writer():
    result = run_agent(
        "Create a report named pytest_test_report.txt summarizing TaskPilot-AI."
    )

    assert result is not None
    assert any(
        item.get("tool") == "report_writer"
        for item in result["trace"]
    )


def test_document_search():
    result = run_agent(
        "Search my indexed documents and explain the main purpose of SemCache."
    )

    assert result is not None
    assert any(
        item.get("tool") == "document_search"
        for item in result["trace"]
    )
