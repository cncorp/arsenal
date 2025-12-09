#!/usr/bin/env python3
"""
Check for LLM-generated anti-patterns.

1. Broad exception catching - catch specific exceptions instead
2. pytest.skip - fix the test instead
3. Late imports - move to top or fix circular dependencies
4. Single-use functions - inline instead of creating one-off functions

Any # noqa must include a comment explaining why it's necessary.
"""

import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Iterable, List, Tuple

# Regex patterns for detection
BROAD_EXCEPT_PATTERNS = [
    (re.compile(r"\bexcept\s*:"), "bare except"),
    (re.compile(r"\bexcept\s+Exception\b"), "except Exception"),
    (re.compile(r"\bexcept\s+BaseException\b"), "except BaseException"),
]

PYTEST_SKIP_PATTERN = re.compile(
    r"pytest\.skip\(|@pytest\.mark\.skip|@pytest\.mark\.skipif"
)
IMPORT_PATTERN = re.compile(r"^\s*(from|import)\s+")

NOQA_PATTERN = re.compile(r"#\s*(?i:noqa):\s*")  # case agnostic
NOQA_BLE001_PATTERN = re.compile(NOQA_PATTERN.pattern + r"BLE001")
NOQA_SKIP001_PATTERN = re.compile(NOQA_PATTERN.pattern + r"SKIP001")
NOQA_E402_PATTERN = re.compile(NOQA_PATTERN.pattern + r"E402")
NOQA_SINGLE_USE_PATTERN = re.compile(NOQA_PATTERN.pattern + r"SINGLE001")

# Pattern to match function definitions in diff output
DIFF_FUNCTION_PATTERN = re.compile(r"^\+\s*def\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\(")

# Threshold for imports after docstring ends (in lines)
# This allows ~50 lines of imports after the docstring ends before flagging
IMPORT_THRESHOLD_AFTER_DOCSTRING = 50


def _find_docstring_end_line(lines: List[str]) -> int:
    """
    Find the line where the module docstring ends.

    Returns the line number (1-indexed) where the docstring ends,
    or 0 if no docstring is found.
    """
    if not lines:
        return 0

    in_docstring = False
    docstring_quote = None

    for line_num, line in enumerate(lines, 1):
        stripped = line.strip()

        if not in_docstring:
            # Look for docstring start (must be at beginning of file, allowing shebang and encoding)
            if stripped.startswith('"""') or stripped.startswith("'''"):
                docstring_quote = stripped[:3]
                # Check if docstring ends on same line (e.g., """Short docstring.""")
                if stripped.count(docstring_quote) >= 2 and len(stripped) > 3:
                    return line_num
                in_docstring = True
            elif stripped and not stripped.startswith("#") and not stripped.startswith("#!/"):
                # Non-empty, non-comment line before docstring means no docstring
                return 0
        else:
            # Look for docstring end
            if docstring_quote in stripped:
                return line_num

    return 0


def check_file(filepath: Path) -> List[Tuple[str, int, str]]:
    """
    Check a single Python file for quality issues.

    Returns list of (issue_type, line_number, message) tuples.
    """
    issues = []

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            lines = f.readlines()
    except (IOError, UnicodeDecodeError):
        return issues

    is_test_file = "/tests/" in str(filepath) or str(filepath).startswith("tests/")

    # Find where the module docstring ends (for late import check)
    docstring_end_line = _find_docstring_end_line(lines)
    # Imports are considered "late" if they're more than IMPORT_THRESHOLD_AFTER_DOCSTRING lines
    # after the docstring ends (or from line 0 if no docstring).
    import_threshold_line = docstring_end_line + IMPORT_THRESHOLD_AFTER_DOCSTRING

    for line_num, line in enumerate(lines, 1):
        # Check 1: Broad exception catching (unless noqa comment present)
        if not NOQA_BLE001_PATTERN.search(line):
            for pattern, desc in BROAD_EXCEPT_PATTERNS:
                if pattern.search(line):
                    issues.append(
                        (
                            "broad-except",
                            line_num,
                            f"Found {desc}. Don't catch exceptions, we want errors. If adding noqa, defend your decision in the code",
                        )
                    )

        # Check 2: pytest.skip usage (in test files, unless noqa comment present)
        if (
            is_test_file
            and PYTEST_SKIP_PATTERN.search(line)
            and not NOQA_SKIP001_PATTERN.search(line)
        ):
            issues.append(
                (
                    "pytest-skip",
                    line_num,
                    "Found pytest.skip. Fix the test instead. If adding noqa, defend your decision in the code",
                )
            )

        # Check 3: Late imports (after import_threshold_line, not in tests)
        # Skip if has noqa: E402 comment (legitimate deferred import)
        if (
            not is_test_file
            and line_num > import_threshold_line
            and IMPORT_PATTERN.match(line)
            and not NOQA_E402_PATTERN.search(line)
        ):
            issues.append(
                (
                    "late-import",
                    line_num,
                    f"Import at line {line_num}. Move to top or refactor circular dependency. If adding noqa, defend your decision in the code",
                )
            )

    return issues


def _is_excluded_path(candidate: Path, excludes: list[Path]) -> bool:
    """Return True when candidate path should be skipped."""
    return any(candidate == subpath or candidate.is_relative_to(subpath) for subpath in excludes)


def find_python_files(
    directory: Path,
    exclude_dirs: Iterable[str] | None = None,
    exclude_subpaths: Iterable[str] | None = None,
) -> List[Path]:
    """Find all Python files in directory, excluding specified directories/subpaths."""
    if exclude_dirs is None:
        exclude_dirs = {".venv", "venv", "__pycache__", ".git", ".uv", "build", "dist"}
    else:
        exclude_dirs = set(exclude_dirs)

    exclude_path_objs = [Path(subpath) for subpath in (exclude_subpaths or [])]

    python_files = []
    base_dir = directory.resolve()

    for root, dirs, files in os.walk(directory):
        root_path = Path(root).resolve()
        rel_root = root_path.relative_to(base_dir)

        if _is_excluded_path(rel_root, exclude_path_objs):
            dirs[:] = []
            continue

        # Remove excluded directories from dirs to prevent walking into them
        dirs[:] = [
            d
            for d in dirs
            if d not in exclude_dirs
            and not _is_excluded_path(rel_root / d, exclude_path_objs)
        ]

        for file in files:
            if file.endswith(".py"):
                python_files.append(Path(root) / file)

    return python_files


def _parse_count_output(stdout: str) -> int:
    """Parse ripgrep/grep count output and sum the counts."""
    total = 0
    for line in stdout.strip().split("\n"):
        if line and ":" in line:
            count = int(line.split(":")[-1])
            total += count
    return total


def check_single_use_functions(check_dirs: List[Path]) -> List[Tuple[str, str, int]]:
    """
    Check for newly added functions that are only used once.

    Returns list of (filepath, function_name, usage_count) for single-use functions.
    """
    # Get git diff for staged and unstaged changes
    staged_diff = subprocess.run(
        ["git", "diff", "--staged"],
        capture_output=True,
        text=True,
        check=True,
    ).stdout

    unstaged_diff = subprocess.run(
        ["git", "diff", "HEAD"],
        capture_output=True,
        text=True,
        check=True,
    ).stdout

    combined_diff = staged_diff + "\n" + unstaged_diff

    # Parse diff to find new function definitions
    new_functions = {}  # {function_name: filepath}
    current_file = None

    for line in combined_diff.split("\n"):
        # Track which file we're in
        if line.startswith("+++"):
            # Extract filename from "+++ b/path/to/file.py"
            match = re.match(r"^\+\+\+ b/(.+\.py)$", line)
            if match:
                current_file = match.group(1)

        # Find new function definitions
        if line.startswith("+") and current_file:
            # Skip if line has noqa comment
            if NOQA_SINGLE_USE_PATTERN.search(line):
                continue

            func_match = DIFF_FUNCTION_PATTERN.match(line)
            if func_match:
                func_name = func_match.group(1)
                # Only check private functions (starting with _)
                # Public functions might be part of an API
                if func_name.startswith("_") and not func_name.startswith("__"):
                    new_functions[func_name] = current_file

    # For each new function, count usages in the codebase
    issues = []
    for func_name, filepath in new_functions.items():
        usage_count = 0

        for check_dir in check_dirs:
            # Search for function calls: func_name( or self.func_name( or obj.func_name(
            search_pattern = rf"\b{func_name}\s*\("

            try:
                # Try ripgrep first (faster, respects .gitignore)
                result = subprocess.run(
                    ["rg", "-c", search_pattern, str(check_dir), "--type", "py"],
                    capture_output=True,
                    text=True,
                )
                # ripgrep returns 0 if matches found, 1 if no matches
                if result.returncode <= 1:
                    usage_count += _parse_count_output(result.stdout)
            except FileNotFoundError:
                # ripgrep not installed, fall back to grep
                grep_pattern = search_pattern.replace(r"\s", "[[:space:]]")
                result = subprocess.run(
                    ["grep", "-r", "-E", "-c", grep_pattern, str(check_dir), "--include=*.py"],
                    capture_output=True,
                    text=True,
                )
                # grep returns 0 if matches found, 1 if no matches
                if result.returncode <= 1:
                    usage_count += _parse_count_output(result.stdout)

        # If function is only used once (just its definition), flag it
        # We expect at least 2: the definition + at least one call
        if usage_count == 1:
            issues.append((filepath, func_name, usage_count))

    return issues


def main():
    """Main entry point for the checker."""
    # Check both api and slack-sidecar directories
    check_dirs = []

    if len(sys.argv) > 1:
        # Use command line argument if provided
        check_dirs = [Path(sys.argv[1])]
    else:
        # Default: check api and slack-sidecar
        for dir_name in ["api", "slack-sidecar"]:
            dir_path = Path(dir_name)
            if dir_path.exists():
                check_dirs.append(dir_path)

    if not check_dirs:
        print("No directories to check")
        return 0

    # Find all Python files in all directories
    python_files = []
    for check_dir in check_dirs:
        subpath_excludes: list[str] = []
        if check_dir.name == "api":
            subpath_excludes.append("models/silero")

        python_files.extend(find_python_files(check_dir, exclude_subpaths=subpath_excludes))

    # Check all files and collect issues
    all_issues = []
    for filepath in python_files:
        issues = check_file(filepath)
        if issues:
            all_issues.append((filepath, issues))

    # Check for single-use functions
    single_use_functions = check_single_use_functions(check_dirs)

    # Report issues grouped by type
    if all_issues or single_use_functions:
        issue_types = {}
        for filepath, issues in all_issues:
            for issue_type, line_num, message in issues:
                if issue_type not in issue_types:
                    issue_types[issue_type] = []
                issue_types[issue_type].append((filepath, line_num, message))

        # Print issues by type
        exit_code = 0

        if "broad-except" in issue_types:
            print("=" * 70)
            print("BROAD EXCEPTION HANDLING ISSUES:")
            print("=" * 70)
            for filepath, line_num, message in issue_types["broad-except"]:
                print(f"{filepath}:{line_num}: {message}")
            exit_code = 1

        if "pytest-skip" in issue_types:
            print("=" * 70)
            print("PYTEST SKIP ISSUES:")
            print("=" * 70)
            for filepath, line_num, message in issue_types["pytest-skip"]:
                print(f"{filepath}:{line_num}: {message}")
            exit_code = 1

        if "late-import" in issue_types:
            print("=" * 70)
            print("LATE IMPORT ISSUES:")
            print("=" * 70)
            for filepath, line_num, message in issue_types["late-import"]:
                print(f"{filepath}:{line_num}: {message}")
            exit_code = 1

        if single_use_functions:
            print("=" * 70)
            print("SINGLE-USE FUNCTION ISSUES:")
            print("=" * 70)
            print("Functions that are only called once should be inlined.")
            print("Add '# noqa: SINGLE001' to the function def line if this is intentional.")
            print()
            for filepath, func_name, usage_count in single_use_functions:
                print(f"{filepath}: Function '{func_name}' is only used {usage_count} time(s)")
                print(f"  → Consider inlining this function at its call site")
            exit_code = 1

        return exit_code
    else:
        print("✓ All code quality checks passed!")
        return 0


if __name__ == "__main__":
    sys.exit(main())
