import re


def verify_java_code(code: str):
    issues = []

    if not code.strip().startswith("package "):
        issues.append("Missing package declaration")

    if "class  " in code:
        issues.append("Double space in class declaration")

    if "import com.example" in code:
        issues.append("Invalid import com.example")

    if "TODO" in code:
        issues.append("TODO left in generated code")

    return {
        "valid": len(issues) == 0,
        "issues": issues
    }