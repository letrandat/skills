#!/usr/bin/env python3
"""Dependency-free structural validator for an OKF Knowledge Bundle."""

from __future__ import annotations

import json
import os
import re
import sys
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Iterable, List, Optional, Sequence, TextIO, Tuple
from urllib.parse import unquote


ERROR = "error"
WARNING = "warning"
IGNORED_DIRECTORIES = frozenset({".git", ".obsidian"})
URI_SCHEME = re.compile(r"^[A-Za-z][A-Za-z0-9+.-]*:")
DATE_HEADING = re.compile(r"^##[ \t]+(\d{4}-\d{2}-\d{2})[ \t]*$", re.MULTILINE)
NON_STRING_PLAIN_TYPE = re.compile(
    r"^(?:true|false|yes|no|on|off|null|~|[-+]?(?:\d[\d_]*)(?:\.\d[\d_]*)?"
    r"(?:e[-+]?\d+)?|[-+]?\.(?:inf|nan)|\d{4}-\d{2}-\d{2})$",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class Diagnostic:
    severity: str
    code: str
    path: str
    message: str


@dataclass
class ValidationReport:
    root: Path
    concept_count: int = 0
    diagnostics: List[Diagnostic] = field(default_factory=list)

    @property
    def errors(self) -> List[Diagnostic]:
        return [item for item in self.diagnostics if item.severity == ERROR]

    @property
    def warnings(self) -> List[Diagnostic]:
        return [item for item in self.diagnostics if item.severity == WARNING]

    @property
    def exit_status(self) -> int:
        return 1 if self.errors else 0

    def add(self, severity: str, code: str, path: str, message: str) -> None:
        self.diagnostics.append(Diagnostic(severity, code, path, message))


def _strip_yaml_comment(value: str) -> str:
    single_quoted = False
    double_quoted = False
    escaped = False
    for index, character in enumerate(value):
        if escaped:
            escaped = False
            continue
        if character == "\\" and double_quoted:
            escaped = True
            continue
        if character == "'" and not double_quoted:
            single_quoted = not single_quoted
            continue
        if character == '"' and not single_quoted:
            double_quoted = not double_quoted
            continue
        if (
            character == "#"
            and not single_quoted
            and not double_quoted
            and (index == 0 or value[index - 1].isspace())
        ):
            return value[:index].rstrip()
    return value.strip()


def _parse_type(value: str) -> Tuple[Optional[str], Optional[str]]:
    value = _strip_yaml_comment(value).strip()
    if not value or value in {"~", "null", "Null", "NULL", "''", '\"\"'}:
        return None, "Missing required non-empty 'type' value"

    if value.startswith('"'):
        try:
            parsed = json.loads(value)
        except (json.JSONDecodeError, TypeError):
            return None, "Malformed quoted 'type' value"
        if not isinstance(parsed, str) or not parsed.strip():
            return None, "Required 'type' value must be a non-empty string"
        return parsed, None

    if value.startswith("'"):
        if len(value) < 2 or not value.endswith("'"):
            return None, "Malformed quoted 'type' value"
        parsed = value[1:-1].replace("''", "'")
        if not parsed.strip():
            return None, "Required 'type' value must be a non-empty string"
        return parsed, None

    if (
        value[0] in "[{|>!"
        or value.startswith(("&", "*"))
        or NON_STRING_PLAIN_TYPE.match(value)
        or re.search(r":[ \t]", value)
    ):
        return None, "Required 'type' value must be a scalar string"
    return value, None


def parse_concept(
    content: str,
) -> Tuple[Optional[str], Optional[Tuple[str, str]]]:
    """Read the OKF-required frontmatter boundary and top-level type field.

    Producer-defined fields are deliberately left uninterpreted. The small parser
    accepts nested or list continuations while enforcing a top-level YAML mapping.
    """

    lines = content.splitlines()
    if not lines or lines[0] != "---":
        return None, (
            "FRONTMATTER_MISSING",
            "Missing YAML frontmatter block starting with '---'",
        )

    closing_index = next(
        (index for index, line in enumerate(lines[1:], start=1) if line == "---"),
        None,
    )
    if closing_index is None:
        return None, (
            "FRONTMATTER_UNCLOSED",
            "YAML frontmatter has no closing '---' delimiter",
        )

    current_key: Optional[str] = None
    concept_type: Optional[str] = None
    for line_number, line in enumerate(lines[1:closing_index], start=2):
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if line[0].isspace():
            if current_key is None:
                return None, (
                    "FRONTMATTER_MALFORMED",
                    f"Unexpected indented content on frontmatter line {line_number}",
                )
            continue

        if line.startswith("-") or ":" not in line:
            return None, (
                "FRONTMATTER_MALFORMED",
                f"Expected a top-level YAML key on frontmatter line {line_number}",
            )
        current_key, value = (part.strip() for part in line.split(":", 1))
        if not current_key:
            return None, (
                "FRONTMATTER_MALFORMED",
                f"Expected a top-level YAML key on frontmatter line {line_number}",
            )
        if current_key in {'"type"', "'type'"}:
            current_key = "type"
        if current_key != "type":
            continue
        if concept_type is not None:
            return None, (
                "TYPE_DUPLICATE",
                "Frontmatter defines 'type' more than once",
            )
        concept_type, error = _parse_type(value)
        if error:
            return None, ("TYPE_INVALID", error)

    if concept_type is None:
        return None, ("TYPE_MISSING", "Missing required non-empty 'type' field")

    return "\n".join(lines[closing_index + 1 :]), None


def extract_links(markdown: str) -> List[str]:
    """Extract inline Markdown links, including targets with balanced parentheses."""

    links = []
    cursor = 0
    while cursor < len(markdown):
        label_start = markdown.find("[", cursor)
        if label_start < 0:
            break
        if label_start > 0 and markdown[label_start - 1] == "!":
            cursor = label_start + 1
            continue
        label_end = markdown.find("]", label_start + 1)
        if label_end < 0:
            break
        if label_end + 1 >= len(markdown) or markdown[label_end + 1] != "(":
            cursor = label_end + 1
            continue

        target_start = label_end + 2
        depth = 1
        index = target_start
        escaped = False
        while index < len(markdown) and depth:
            character = markdown[index]
            if escaped:
                escaped = False
            elif character == "\\":
                escaped = True
            elif character == "(":
                depth += 1
            elif character == ")":
                depth -= 1
            index += 1
        if depth:
            break

        payload = markdown[target_start : index - 1].strip()
        if payload.startswith("<") and ">" in payload:
            target = payload[1 : payload.find(">")]
        else:
            target = payload.split(maxsplit=1)[0] if payload else ""
        if target:
            links.append(target.replace("\\(", "(").replace("\\)", ")"))
        cursor = index
    return links


def _is_within(path: Path, root: Path) -> bool:
    try:
        return os.path.commonpath((str(path), str(root))) == str(root)
    except ValueError:
        return False


def resolve_internal_target(target: str, current_dir: Path, root: Path) -> Optional[Path]:
    target = target.strip()
    if (
        not target
        or target.startswith(("#", "/", "//"))
        or URI_SCHEME.match(target)
    ):
        return None

    target = target.split("#", 1)[0].split("?", 1)[0]
    if not target:
        return None
    candidate = (current_dir / unquote(target)).resolve(strict=False)
    if not _is_within(candidate, root):
        return None
    if candidate.is_dir():
        index_path = candidate / "index.md"
        if index_path.is_file():
            candidate = index_path
    return candidate


def walk_markdown_files(report: ValidationReport) -> Iterable[Path]:
    root = report.root

    def on_error(error: OSError) -> None:
        filename = Path(error.filename) if error.filename else root
        try:
            relative = filename.relative_to(root).as_posix()
        except ValueError:
            relative = "."
        report.add(ERROR, "TRAVERSAL_FAILED", relative, str(error))

    for dirpath, dirnames, filenames in os.walk(
        str(root), topdown=True, onerror=on_error, followlinks=False
    ):
        directory = Path(dirpath)
        dirnames[:] = sorted(
            name
            for name in dirnames
            if name not in IGNORED_DIRECTORIES and not (directory / name).is_symlink()
        )
        for filename in sorted(filenames):
            path = directory / filename
            if path.suffix == ".md" and not path.is_symlink():
                yield path


def _read_text(path: Path, report: ValidationReport) -> Optional[str]:
    relative = path.relative_to(report.root).as_posix()
    try:
        return path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as error:
        report.add(ERROR, "READ_FAILED", relative, str(error))
        return None


def _check_links(
    source: Path,
    markdown: str,
    report: ValidationReport,
) -> set:
    targets = set()
    source_relative = source.relative_to(report.root).as_posix()
    for raw_target in extract_links(markdown):
        target = resolve_internal_target(raw_target, source.parent, report.root)
        if target is None:
            continue
        targets.add(target)
        if not target.exists():
            report.add(
                WARNING,
                "LINK_BROKEN",
                source_relative,
                f"Broken internal link '{raw_target}'",
            )
    return targets


def _check_log(
    path: Path,
    content: str,
    report: ValidationReport,
) -> None:
    relative = path.relative_to(report.root).as_posix()
    first_line = next((line.strip() for line in content.splitlines() if line.strip()), "")
    if first_line != "# Change Log":
        report.add(
            WARNING,
            "LOG_HEADING",
            relative,
            "Change log should start with '# Change Log'",
        )

    raw_dates = DATE_HEADING.findall(content)
    if not raw_dates:
        report.add(
            WARNING,
            "LOG_DATES_MISSING",
            relative,
            "Change log has no '## YYYY-MM-DD' entries",
        )
        return

    parsed_dates = []
    for raw_date in raw_dates:
        try:
            parsed_dates.append(date.fromisoformat(raw_date))
        except ValueError:
            report.add(
                WARNING,
                "LOG_DATE_INVALID",
                relative,
                f"Invalid change-log date '{raw_date}'",
            )
    if parsed_dates and parsed_dates != sorted(parsed_dates, reverse=True):
        report.add(
            WARNING,
            "LOG_ORDER",
            relative,
            "Change-log dates should be newest first",
        )


def validate(root_dir: Path) -> ValidationReport:
    root = root_dir.expanduser().resolve(strict=False)
    report = ValidationReport(root=root)
    if not root.is_dir():
        report.add(ERROR, "ROOT_INVALID", ".", "Brain Root is not a directory")
        return report

    concepts = []
    index_targets = {}
    index_paths = []

    for path in walk_markdown_files(report):
        content = _read_text(path, report)
        if content is None:
            continue
        relative = path.relative_to(root).as_posix()

        if path.name == "index.md":
            index_paths.append(path)
            index_targets[path] = _check_links(path, content, report)
            continue
        if path.name == "log.md":
            _check_log(path, content, report)
            continue

        report.concept_count += 1
        parsed, parse_error = parse_concept(content)
        if parse_error:
            code, message = parse_error
            report.add(ERROR, code, relative, message)
            continue
        assert parsed is not None
        concepts.append(path)
        _check_links(path, parsed, report)

    for concept in concepts:
        relative = concept.relative_to(root).as_posix()
        parent_index = concept.parent / "index.md"
        parent_relative = parent_index.relative_to(root).as_posix()
        if not parent_index.is_file():
            report.add(
                WARNING,
                "INDEX_MISSING",
                relative,
                f"Parent index is missing at '{parent_relative}'",
            )
        elif concept not in index_targets.get(parent_index, set()):
            report.add(
                WARNING,
                "INDEX_ENTRY_MISSING",
                relative,
                f"Concept is not linked from '{parent_relative}'",
            )

    root_index = root / "index.md"
    for index_path in index_paths:
        if index_path == root_index:
            continue
        parent_index = index_path.parent.parent / "index.md"
        relative = index_path.relative_to(root).as_posix()
        parent_relative = parent_index.relative_to(root).as_posix()
        if not parent_index.is_file():
            report.add(
                WARNING,
                "INDEX_PARENT_MISSING",
                relative,
                f"Parent index is missing at '{parent_relative}'",
            )
        elif index_path not in index_targets.get(parent_index, set()):
            report.add(
                WARNING,
                "INDEX_ENTRY_MISSING",
                relative,
                f"Subdirectory index is not linked from '{parent_relative}'",
            )

    return report


def render_report(report: ValidationReport) -> str:
    lines = [
        f"Scanning Knowledge Bundle at: {report.root}",
        "",
        "--- Validation Results ---",
        f"Scanned {report.concept_count} concepts.",
    ]
    warnings = sorted(report.warnings, key=lambda item: (item.path, item.code, item.message))
    errors = sorted(report.errors, key=lambda item: (item.path, item.code, item.message))

    if warnings:
        lines.extend(["", f"Warnings ({len(warnings)}):"])
        lines.extend(
            f"  [WARN] {item.path}: {item.message} ({item.code})" for item in warnings
        )
    if errors:
        lines.extend(["", f"Errors ({len(errors)}):"])
        lines.extend(
            f"  [FAIL] {item.path}: {item.message} ({item.code})" for item in errors
        )
        lines.extend(["", "Validation FAILED."])
    else:
        lines.extend(["", "Validation PASSED."])
    return "\n".join(lines) + "\n"


def main(argv: Optional[Sequence[str]] = None, output: Optional[TextIO] = None) -> int:
    arguments = list(sys.argv[1:] if argv is None else argv)
    stream = sys.stdout if output is None else output
    if len(arguments) != 1:
        stream.write("Usage: python3 validate.py <path_to_brain_root>\n")
        return 1

    report = validate(Path(arguments[0]))
    stream.write(render_report(report))
    return report.exit_status


if __name__ == "__main__":
    sys.exit(main())
