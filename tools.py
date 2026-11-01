from datetime import datetime
from pathlib import Path
import ast
import operator

# Restrict calculations to approved arithmetic operations.
OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
}


def calculate(expression: str):
    """Evaluate a restricted arithmetic expression."""
    expression = (
    expression
    .replace("×", "*")
    .replace("÷", "/")
    .replace("−", "-")
    .replace("–", "-")
    .replace("^", "**")
)

    def evaluate(node):
        if isinstance(node, ast.Constant) and type(node.value) in (int, float):
            return node.value

        if isinstance(node, ast.UnaryOp) and type(node.op) in OPERATORS:
            return OPERATORS[type(node.op)](evaluate(node.operand))

        if isinstance(node, ast.BinOp) and type(node.op) in OPERATORS:
            left = evaluate(node.left)
            right = evaluate(node.right)

            if isinstance(node.op, ast.Pow) and abs(right) > 10:
                raise ValueError("Exponent magnitude cannot exceed 10.")

            if abs(left) > 1e12 or abs(right) > 1e12:
                raise ValueError("Input values are too large.")

            result = OPERATORS[type(node.op)](left, right)

            if isinstance(result, (int, float)) and abs(result) > 1e12:
                raise ValueError("Result is too large.")

            return result

        raise ValueError("Unsupported expression.")

    try:
        tree = ast.parse(expression, mode="eval")
        result = evaluate(tree.body)

        if isinstance(result, float) and not __import__("math").isfinite(result):
            raise ValueError("Result must be finite.")

        return {"success": True, "result": result}

    except (ValueError, TypeError, ZeroDivisionError, SyntaxError, OverflowError) as error:
        return {"success": False, "error": str(error)}


def get_current_time():
    """Return the current local system time."""
    return {
        "success": True,
        "time": datetime.now().astimezone().isoformat()
    }


def save_report(content: str, filename: str = "report.txt"):
    """Save a text report inside data/reports."""

    reports_dir = Path(__file__).resolve().parent / "data" / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)

    # Prevent path traversal and restrict filenames.
    if Path(filename).name != filename or filename in ("", ".", ".."):
        return {"success": False, "error": "Invalid filename."}

    if not filename.endswith(".txt"):
        return {"success": False, "error": "Only .txt reports are allowed."}

    report_path = reports_dir / filename

    try:
        report_path.write_text(content, encoding="utf-8")
        return {
            "success": True,
            "message": "Report saved successfully.",
            "path": str(report_path)
        }
    except OSError as error:
        return {"success": False, "error": str(error)}
