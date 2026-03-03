# ai/validators/java_scanner.py
from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional
import re
import fnmatch


@dataclass(frozen=True)
class JavaIssue:
    code: str
    message: str
    line: Optional[int] = None


def _line_of(java_source: str, idx: int) -> int:
    # 1-based line number
    return java_source.count("\n", 0, idx) + 1


def validate_java_source(
    java_source: str,
    *,
    forbidden_import_patterns: Optional[List[str]] = None,
    forbidden_annotation_tokens: Optional[List[str]] = None,
) -> List[JavaIssue]:
    """
    Lightweight Java source scanner (regex-based) to keep dependencies minimal.
    Intended for fast "contract checks" and hygiene checks.

    Returns a list of JavaIssue.
    """

    issues: List[JavaIssue] = []
    forbidden_import_patterns = forbidden_import_patterns or []
    forbidden_annotation_tokens = forbidden_annotation_tokens or []

    # Imports
    for m in re.finditer(r"^\s*import\s+([^;]+);", java_source, flags=re.MULTILINE):
        imp = m.group(1).strip()
        for pat in forbidden_import_patterns:
            if fnmatch.fnmatch(imp, pat):
                issues.append(
                    JavaIssue(
                        code="FORBIDDEN_IMPORT",
                        message=f"Forbidden import '{imp}' matches pattern '{pat}'",
                        line=_line_of(java_source, m.start()),
                    )
                )

    # Annotations (first token)
    for m in re.finditer(r"^\s*(@\w+)", java_source, flags=re.MULTILINE):
        ann = m.group(1)
        if ann in forbidden_annotation_tokens:
            issues.append(
                JavaIssue(
                    code="FORBIDDEN_ANNOTATION",
                    message=f"Forbidden annotation '{ann}'",
                    line=_line_of(java_source, m.start()),
                )
            )

    # Basic hygiene checks (optional but useful)
    if "\t" in java_source:
        issues.append(JavaIssue(code="TAB_CHARACTER", message="Tab character found; prefer spaces."))

    # Detect duplicate package declaration
    pkg = re.findall(r"^\s*package\s+[^;]+;", java_source, flags=re.MULTILINE)
    if len(pkg) > 1:
        issues.append(JavaIssue(code="MULTIPLE_PACKAGES", message="Multiple package declarations found."))

    return issues