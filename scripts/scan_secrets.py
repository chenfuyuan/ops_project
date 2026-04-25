#!/usr/bin/env python3
from __future__ import annotations

import argparse
import dataclasses
import re
import subprocess
import sys
from collections.abc import Iterable


@dataclasses.dataclass(frozen=True)
class Finding:
    path: str
    line: int | None
    pattern: str
    value: str
    text: str


SECRET_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("private_key_block", re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----")),
    ("aws_access_key", re.compile(r"AKIA[0-9A-Z]{16}")),
    ("github_token", re.compile(r"gh[pousr]_[A-Za-z0-9_]{20,}|github_pat_[A-Za-z0-9_]{20,}")),
    ("anthropic_key", re.compile(r"\bsk-ant-[A-Za-z0-9_-]{20,}\b")),
    ("openai_key", re.compile(r"\bsk-(?!ant-)[A-Za-z0-9_-]{20,}\b")),
    ("slack_token", re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{20,}\b")),
    ("google_api_key", re.compile(r"\bAIza[0-9A-Za-z_-]{20,}\b")),
    ("jwt_like", re.compile(r"\beyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\b")),
    (
        "aws_secret_assignment",
        re.compile(r"(?i)\baws_secret_access_key\b\s*[:=]\s*[\"']?([^\"'\s,}#]+)"),
    ),
    (
        "generic_secret_assignment",
        re.compile(r"(?i)[\"']?\b(api[_-]?key|secret|token|password|passwd|pwd|authorization)\b[\"']?\s*[:=]\s*[\"']?([^\"'\s,}#]+)"),
    ),
)

SAFE_PATH_PATTERN = re.compile(r"(^|/)(tests?|docs?|ai_docs|openspec|\.claude/skills)(/|$)|\.example\.|README\.md$|\.http$")
SAFE_LITERAL_PATTERN = re.compile(
    r"(?i)^(replace|replace-locally-do-not-commit|example|sample|dummy|test|test-token|secret-value|"
    r"secret-api-key|shared-token|plaintext-secret|none|null|true|false|str|api_key)$"
)
SAFE_ENV_REFERENCE_PATTERN = re.compile(r"^\$\{?[A-Z0-9_]+\}?$|^[A-Z0-9_]+$")
REFERENCE_VALUE_PATTERN = re.compile(r"^[A-Za-z_][A-Za-z0-9_\.(){}\[\]]*$")


def scan_diff(diff_text: str) -> list[Finding]:
    findings: list[Finding] = []
    current_file = "<unknown>"
    new_line: int | None = None

    for raw_line in diff_text.splitlines():
        if raw_line.startswith("+++ b/"):
            current_file = raw_line[6:]
            new_line = None
            continue
        if raw_line.startswith("@@"):
            new_line = _parse_hunk_start(raw_line)
            continue
        if not raw_line.startswith("+") or raw_line.startswith("+++"):
            continue

        body = raw_line[1:]
        findings.extend(_scan_added_line(current_file, new_line, body))
        if new_line is not None:
            new_line += 1

    return findings


def _parse_hunk_start(line: str) -> int | None:
    match = re.search(r"\+(\d+)", line)
    if match is None:
        return None
    return int(match.group(1))


def _scan_added_line(path: str, line_number: int | None, line: str) -> list[Finding]:
    findings: list[Finding] = []
    for pattern_name, pattern in SECRET_PATTERNS:
        for match in pattern.finditer(line):
            value = _matched_value(pattern_name, match)
            if _is_safe_match(path, pattern_name, value):
                continue
            findings.append(
                Finding(
                    path=path,
                    line=line_number,
                    pattern=pattern_name,
                    value=_redact(value),
                    text=line[:240],
                )
            )
    return findings


def _matched_value(pattern_name: str, match: re.Match[str]) -> str:
    if pattern_name == "generic_secret_assignment":
        return match.group(2).strip().strip("\"'")
    if pattern_name == "aws_secret_assignment":
        return match.group(1).strip().strip("\"'")
    return match.group(0).strip().strip("\"'")


def _is_safe_match(path: str, pattern_name: str, value: str) -> bool:
    if pattern_name != "generic_secret_assignment":
        return SAFE_LITERAL_PATTERN.fullmatch(value) is not None
    if SAFE_LITERAL_PATTERN.fullmatch(value) or SAFE_ENV_REFERENCE_PATTERN.fullmatch(value):
        return True
    if REFERENCE_VALUE_PATTERN.fullmatch(value):
        return True
    if SAFE_PATH_PATTERN.search(path):
        return True
    return False


def _redact(value: str) -> str:
    if len(value) <= 16:
        return value
    return f"{value[:6]}…{value[-4:]}"


def _git_diff(args: Iterable[str]) -> str:
    result = subprocess.run(
        ["git", "diff", *args],
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip())
    return result.stdout


def _print_findings(findings: list[Finding]) -> None:
    print("Secret scan failed: suspected secrets found in staged changes.", file=sys.stderr)
    for finding in findings:
        location = finding.path
        if finding.line is not None:
            location = f"{location}:{finding.line}"
        print(f"- {location} [{finding.pattern}] {finding.value}", file=sys.stderr)
        print(f"  {finding.text}", file=sys.stderr)


def main() -> int:
    parser = argparse.ArgumentParser(description="Scan git diffs for committed secrets.")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--staged", action="store_true", help="scan staged changes")
    group.add_argument("--range", dest="revision_range", help="scan a git revision range, for example origin/main...HEAD")
    args = parser.parse_args()

    if args.revision_range:
        diff_text = _git_diff(["--unified=0", args.revision_range])
    else:
        diff_args = ["--cached", "--unified=0"] if args.staged else ["--unified=0"]
        diff_text = _git_diff(diff_args)

    findings = scan_diff(diff_text)
    if findings:
        _print_findings(findings)
        return 1

    print("Secret scan passed: no suspected secrets found.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
