#!/usr/bin/env python3
"""No fake data policy gate: runtime patterns only, ignores comments/docstrings."""
from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import List, Sequence

REPO_ROOT = Path(__file__).resolve().parents[2]
WEB_API_ROOT = REPO_ROOT / "apps" / "web" / "app" / "api"

REQUIRED_CORE_FILES: Sequence[Path] = (
    Path("apps/web/app/api/_lib/upstream.ts"),
)

ROUTE_GLOB_TS = "**/route.ts"

PYTHON_API_ROOTS = [
    "ocean-core/curiosity_algebra",
    "services",
    "apps/api/routes",
    "app/routes",
]

ROUTE_GLOB_PY = "**/*.py"


class Violation:
    def __init__(self, file: Path, rule: str, details: str, snippet: str) -> None:
        self.file = file
        self.rule = rule
        self.details = details
        self.snippet = snippet


def _strip_comments_docstrings(text: str) -> str:
    """Remove comments and docstrings."""
    text = re.sub(r'"""[\s\S]*?"""|\'\'\'[\s\S]*?\'\'\'', '', text)
    text = re.sub(r'#.*$', '', text, flags=re.MULTILINE)
    text = re.sub(r'//.*$', '', text, flags=re.MULTILINE)
    text = re.sub(r'/\*[\s\S]*?\*/', '', text)
    return text


def _scan_regex_lines(
    file_path: Path,
    text: str,
    pattern: re.Pattern[str],
    rule: str,
    details: str,
    ignore_comments: bool = False,
) -> List[Violation]:
    """Scan for pattern violations."""
    hits: List[Violation] = []

    if ignore_comments:
        text = _strip_comments_docstrings(text)

    for line_no, line in enumerate(text.splitlines(), start=1):
        stripped = line.strip()
        if any(stripped.startswith(m) for m in ("#", "//", "*", "/*", "-")):
            continue
        if "replace_me" in line or "placeholder" in line:
            continue
        if pattern.search(line):
            hits.append(
                Violation(
                    file=file_path,
                    rule=rule,
                    details=f"{details} (line {line_no})",
                    snippet=line.strip(),
                )
            )
    return hits


def _scan_fake_success_blocks(file_path: Path, text: str) -> List[Violation]:
    """Detect catch blocks returning fake success (JS/TS)."""
    violations: List[Violation] = []
    pattern_catch = re.compile(r"catch\s*\([^)]*\)\s*\{(?P<body>[\s\S]{0,1200}?)\}", re.MULTILINE)
    pattern_success = re.compile(
        r'status\s*:\s*["\']ok["\']|healthy\s*:\s*true|statusCode\s*:\s*200',
        re.IGNORECASE,
    )

    for match in pattern_catch.finditer(text):
        body = match.group("body")
        if pattern_success.search(body):
            line_no = text[: match.start()].count("\n") + 1
            violations.append(
                Violation(
                    file=file_path,
                    rule="errors-must-be-real",
                    details=f"catch block returns fake success (line {line_no})",
                    snippet=body[:60].replace("\n", " "),
                )
            )
    return violations


def _scan_python_fake_success(file_path: Path, text: str) -> List[Violation]:
    """Detect except blocks returning fake success (Python)."""
    violations: List[Violation] = []
    pattern_except = re.compile(r"except\s*[\s\S]{0,500}?(?=\n(?:except|finally|else|def|class|\Z))", re.MULTILINE)
    pattern_success = re.compile(
        r'status\s*=\s*["\']ok["\']|healthy\s*=\s*True|status_code\s*=\s*200',
        re.IGNORECASE,
    )

    for match in pattern_except.finditer(text):
        body = match.group(0)
        if pattern_success.search(body):
            line_no = text[: match.start()].count("\n") + 1
            violations.append(
                Violation(
                    file=file_path,
                    rule="errors-must-be-real",
                    details=f"except block returns fake success (line {line_no})",
                    snippet=body[:60].replace("\n", " "),
                )
            )
    return violations


def _scan_null_silent_returns(file_path: Path, text: str) -> List[Violation]:
    """Detect silent null/None returns inside catch/except error blocks."""
    violations: List[Violation] = []

    # JS/TS: catch(...) { ... return null; ... }
    if file_path.suffix in (".ts", ".tsx", ".js"):
        pattern_catch = re.compile(
            r"catch\s*\([^)]*\)\s*\{(?P<body>[\s\S]{0,1200}?)\}",
            re.MULTILINE,
        )
        null_return = re.compile(r"\breturn\s+null\s*;", re.IGNORECASE)
        for match in pattern_catch.finditer(text):
            body = match.group("body")
            m = null_return.search(body)
            if m:
                line_no = text[: match.start()].count("\n") + 1
                violations.append(
                    Violation(
                        file=file_path,
                        rule="no-null-silent-return",
                        details=f"catch block silently returns null instead of throwing/responding with error status (line {line_no})",
                        snippet=body[max(0, m.start() - 20): m.end() + 20].replace("\n", " ").strip(),
                    )
                )

    # Python: except ... : ... return None
    if file_path.suffix == ".py":
        pattern_except = re.compile(
            r"except[\s\S]{0,500}?(?=\n(?:except|finally|else|def|class|\Z))",
            re.MULTILINE,
        )
        none_return = re.compile(r"\breturn\s+None\b")
        for match in pattern_except.finditer(text):
            body = match.group(0)
            m = none_return.search(body)
            if m:
                line_no = text[: match.start()].count("\n") + 1
                violations.append(
                    Violation(
                        file=file_path,
                        rule="no-null-silent-return",
                        details=f"except block silently returns None instead of raising/returning proper error response (line {line_no})",
                        snippet=body[max(0, m.start() - 20): m.end() + 20].replace("\n", " ").strip(),
                    )
                )

    return violations


def _scan_health_check_realism(file_path: Path, text: str) -> List[Violation]:
    violations: List[Violation] = []
    if "/health" not in text and "health" not in file_path.name.lower():
        return violations

    returns_healthy_literal = re.search(
        r"status\s*:\s*['\"]healthy['\"]|healthy\s*:\s*true",
        text,
        re.IGNORECASE,
    )
    dependency_signal = re.search(
        r"redis|postgres|database|db\.|db_|model|upstream|fetch\(|ping\(|connect\(",
        text,
        re.IGNORECASE,
    )

    if returns_healthy_literal and not dependency_signal:
        violations.append(
            Violation(
                file=file_path,
                rule="health-checks-must-test-dependencies",
                details="health response appears static with no dependency probe",
                snippet=returns_healthy_literal.group(0),
            )
        )

    return violations


def _discover_target_files(repo_root: Path) -> List[Path]:
    discovered: List[Path] = []

    # TypeScript/Next.js routes
    if WEB_API_ROOT.exists():
        for item in WEB_API_ROOT.glob(ROUTE_GLOB_TS):
            if item.is_file():
                discovered.append(item.relative_to(repo_root))

    # Python/FastAPI routes
    for py_root in PYTHON_API_ROOTS:
        py_root_path = repo_root / py_root
        if py_root_path.exists():
            for item in py_root_path.glob(ROUTE_GLOB_PY):
                if item.is_file() and (
                    item.name == "api.py"
                    or item.name.endswith("_routes.py")
                    or item.name.endswith("_api.py")
                    or "route" in item.name.lower()
                ):
                    discovered.append(item.relative_to(repo_root))

    # Add required core files
    for required in REQUIRED_CORE_FILES:
        if required not in discovered:
            discovered.append(required)

    return sorted(set(discovered))


def validate(repo_root: Path) -> List[Violation]:
    violations: List[Violation] = []

    forbidden_runtime_patterns = [
        (re.compile(r"\b(fake|mock|placeholder|dummy)[_-]?[A-Za-z0-9_]*\b", re.IGNORECASE), "no-fake-data", "forbidden fake/mock placeholder token"),
        (re.compile(r"build_fast_first_token_fallback|STREAM_FALLBACK_ENABLED", re.IGNORECASE), "no-fake-data", "forbidden fallback-token helper"),
        (
            re.compile(
                r"Analyzing your request|Po e analizoj(?:\s+(?:pyetjen|kerkesen|k\u00ebrkes\u00ebn))?",
                re.IGNORECASE,
            ),
            "no-fake-data",
            "forbidden synthetic first-token text",
        ),
        (re.compile(r"demo-user|anonymous-user", re.IGNORECASE), "no-fake-data", "forbidden demo identity fallback"),
    ]

    hardcoded_secret_patterns = [
        re.compile(r"(api[_-]?key|secret|token|password)\s*[:=]\s*['\"][^'\"]{8,}['\"]", re.IGNORECASE),
        re.compile(r"Bearer\s+[A-Za-z0-9_\-\.]{16,}", re.IGNORECASE),
        re.compile(r"sk-[A-Za-z0-9]{16,}", re.IGNORECASE),
    ]

    target_files = _discover_target_files(repo_root)
    if not target_files:
        violations.append(
            Violation(
                file=Path("apps/web/app/api"),
                rule="target-files-present",
                details="no API route targets discovered",
                snippet="",
            )
        )
        return violations

    for rel_path in target_files:
        file_path = repo_root / rel_path
        if not file_path.exists():
            violations.append(
                Violation(
                    file=rel_path,
                    rule="critical-file-present",
                    details="missing critical runtime file",
                    snippet="",
                )
            )
            continue

        text = file_path.read_text(encoding="utf-8")

        for pattern, rule, details in forbidden_runtime_patterns:
            violations.extend(
                _scan_regex_lines(
                    rel_path,
                    text,
                    pattern,
                    rule,
                    details,
                    ignore_comments=True,
                )
            )

        # Detect fake success based on file type
        if rel_path.suffix == ".ts" or rel_path.suffix == ".tsx":
            violations.extend(_scan_fake_success_blocks(rel_path, text))
        elif rel_path.suffix == ".py":
            violations.extend(_scan_python_fake_success(rel_path, text))

        violations.extend(_scan_null_silent_returns(rel_path, text))
        violations.extend(_scan_health_check_realism(rel_path, text))

        for pattern in hardcoded_secret_patterns:
            violations.extend(
                _scan_regex_lines(
                    rel_path,
                    text,
                    pattern,
                    "no-hardcoded-secrets",
                    "potential hardcoded credential",
                )
            )

    return violations


def main() -> int:
    violations = validate(REPO_ROOT)
    if not violations:
        print("[NO-FAKE-DATA-GATE] PASS")
        return 0

    print("[NO-FAKE-DATA-GATE] FAIL")
    for item in violations:
        print(f"- {item.rule}: {item.file} -> {item.details}")
        if item.snippet:
            print(f"  snippet: {item.snippet}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
