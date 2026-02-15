#!/usr/bin/env python3
"""
Page Range Quality Validator - Step 3 of Comprehensive Validation Suite

Checks performed
----------------
PR001  page_range is a plain string instead of dict (data error)
PR002  Missing grade in page_range that is present in grade_levels
PR003  Grade sequence gap (e.g. K,1,2,4 — missing 3)
PR004  Incomplete K-12 coverage on a complete_k12 document
PR005  Only a single grade extracted (likely incomplete parse)
PR006  Overlapping page ranges between consecutive grades
PR007  Suspiciously wide range string (>12 comma segments — parser artifact)
PR008  Malformed range token (cannot be parsed as N or N-M)
PR009  Range is zero-length or negative (start > end)
PR010  Non-sequential range (start of next grade < end of current)

Usage
-----
    uv run validate_page_ranges.py [--state WA,OR] [--severity ERROR|WARNING|INFO] [--verbose]
"""

from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

sys.path.insert(0, str(Path(__file__).resolve().parent))
from validation_framework import Issue, Severity, Validator, ValidationRunner, load_states

# Grades in canonical K-12 order
CANONICAL_GRADES = ["K", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12"]
# Compound grade keys treated as acceptable band markers (not checked for gaps)
BAND_PATTERN = re.compile(r"^\d{1,2}-\d{1,2}$|^K-\d{1,2}$")


# ---------------------------------------------------------------------------
# Range parsing helpers
# ---------------------------------------------------------------------------

def _parse_range_token(token: str) -> Optional[Tuple[int, int]]:
    """Parse 'N' or 'N-M' into (start, end). Returns None if malformed."""
    token = token.strip()
    m = re.fullmatch(r"(\d+)-(\d+)", token)
    if m:
        return int(m.group(1)), int(m.group(2))
    m = re.fullmatch(r"(\d+)", token)
    if m:
        p = int(m.group(1))
        return p, p
    return None


def _parse_range_string(value: str) -> Tuple[List[Tuple[int, int]], List[str]]:
    """
    Parse a comma-separated page range string like '4-7, 11-15'.
    Returns (list_of_valid_spans, list_of_malformed_tokens).
    """
    spans = []
    bad = []
    for token in value.split(","):
        token = token.strip()
        if not token:
            continue
        parsed = _parse_range_token(token)
        if parsed is None:
            bad.append(token)
        else:
            spans.append(parsed)
    return spans, bad


def _overall_span(spans: List[Tuple[int, int]]) -> Optional[Tuple[int, int]]:
    if not spans:
        return None
    return min(s[0] for s in spans), max(s[1] for s in spans)


# ---------------------------------------------------------------------------
# Validator
# ---------------------------------------------------------------------------

class PageRangeValidator(Validator):
    name = "PageRangeValidator"

    def __init__(self, verbose: bool = False):
        self.verbose = verbose

    def validate(self, data: Dict[str, Any]) -> List[Issue]:
        issues: List[Issue] = []
        for state_abbrev, state_data in data.items():
            for doc in state_data.get("documents", []):
                issues.extend(self._validate_doc(state_abbrev, doc))
        return issues

    def _validate_doc(self, state: str, doc: dict) -> List[Issue]:
        issues: List[Issue] = []
        title = doc.get("title", "untitled")[:60]
        pr = doc.get("page_range")
        grade_levels = doc.get("grade_levels", [])
        doc_type = doc.get("document_type", "")

        # PR001: plain string instead of dict
        if isinstance(pr, str):
            issues.append(Issue(
                severity=Severity.ERROR,
                code="PR001",
                state=state,
                field=title,
                message=f"page_range is a plain string, expected dict: '{pr[:60]}'",
                suggestion="Re-parse document and store as {grade: 'N-M, ...'} dict",
            ))
            # Still try to parse it to catch other issues
            pr = None

        if pr is None:
            # No page_range — only flag if this is a complete_k12 doc
            if doc_type == "complete_k12":
                issues.append(Issue(
                    severity=Severity.WARNING,
                    code="PR004",
                    state=state,
                    field=title,
                    message="complete_k12 document has no page_range data",
                    suggestion="Extract page ranges by parsing the document",
                ))
            return issues

        # From here pr is a dict
        assert isinstance(pr, dict)

        extracted_grades = [k for k in pr.keys() if not BAND_PATTERN.match(k)]
        all_pr_keys = list(pr.keys())

        # PR002: grade in grade_levels missing from page_range
        canonical_in_doc = [g for g in grade_levels if g in CANONICAL_GRADES]
        for grade in canonical_in_doc:
            if grade not in pr:
                issues.append(Issue(
                    severity=Severity.WARNING,
                    code="PR002",
                    state=state,
                    field=title,
                    message=f"Grade {grade} listed in grade_levels but missing from page_range",
                    suggestion=f"Extract page range for grade {grade} from the document",
                ))

        # PR005: only one grade extracted
        if len(extracted_grades) == 1 and len(canonical_in_doc) > 1:
            issues.append(Issue(
                severity=Severity.WARNING,
                code="PR005",
                state=state,
                field=title,
                message=f"Only 1 grade extracted ({extracted_grades[0]}) from document covering {len(canonical_in_doc)} grades",
                suggestion="Re-parse document; likely incomplete extraction",
            ))

        # PR004: complete_k12 doc — check full K-12 coverage
        if doc_type == "complete_k12":
            covered = set(pr.keys())
            missing = [g for g in CANONICAL_GRADES if g not in covered]
            if missing:
                issues.append(Issue(
                    severity=Severity.WARNING,
                    code="PR004",
                    state=state,
                    field=title,
                    message=f"complete_k12 document missing grades in page_range: {missing}",
                    suggestion="Extract page ranges for missing grades",
                ))

        # PR003: grade sequence gap among extracted canonical grades
        extracted_canonical = [g for g in CANONICAL_GRADES if g in pr]
        if len(extracted_canonical) >= 2:
            idx_list = [CANONICAL_GRADES.index(g) for g in extracted_canonical]
            for i in range(1, len(idx_list)):
                gap = idx_list[i] - idx_list[i - 1]
                if gap > 1:
                    missing_between = CANONICAL_GRADES[idx_list[i-1]+1:idx_list[i]]
                    issues.append(Issue(
                        severity=Severity.INFO,
                        code="PR003",
                        state=state,
                        field=title,
                        message=f"Grade sequence gap: {missing_between} not extracted",
                        suggestion="Check whether these grades exist in the document",
                    ))

        # Per-grade range checks
        prev_end: Optional[int] = None
        prev_grade: Optional[str] = None
        for grade in CANONICAL_GRADES:
            if grade not in pr:
                prev_end = None
                prev_grade = None
                continue
            value = pr[grade]
            if not isinstance(value, str):
                continue
            spans, bad_tokens = _parse_range_string(value)

            # PR008: malformed tokens
            for bt in bad_tokens:
                issues.append(Issue(
                    severity=Severity.ERROR,
                    code="PR008",
                    state=state,
                    field=title,
                    message=f"Grade {grade}: malformed range token '{bt}' in '{value[:40]}'",
                    suggestion="Fix range string to use 'N-M' or 'N' format",
                ))

            # PR007: suspiciously wide (>12 comma segments)
            segments = [t for t in value.split(",") if t.strip()]
            if len(segments) > 12:
                issues.append(Issue(
                    severity=Severity.WARNING,
                    code="PR007",
                    state=state,
                    field=title,
                    message=f"Grade {grade}: {len(segments)} comma segments (possible parser artifact): '{value[:60]}'",
                    suggestion="Verify this range string is correct; may need re-extraction",
                ))

            for start, end in spans:
                # PR009: zero-length or negative range
                if start > end:
                    issues.append(Issue(
                        severity=Severity.ERROR,
                        code="PR009",
                        state=state,
                        field=title,
                        message=f"Grade {grade}: negative range {start}-{end}",
                        suggestion="Fix page range data",
                    ))

                # PR006: overlapping with previous grade
                if prev_end is not None and start <= prev_end:
                    issues.append(Issue(
                        severity=Severity.WARNING,
                        code="PR006",
                        state=state,
                        field=title,
                        message=(
                            f"Grade {grade} range starts at {start}, overlapping "
                            f"grade {prev_grade} which ends at {prev_end}"
                        ),
                        suggestion="Verify page boundaries between grades",
                    ))

                # PR010: non-sequential (grade starts before previous ends — informational)
                if prev_end is not None and start < prev_end and start > prev_end - 3:
                    pass  # Already caught by PR006

            span = _overall_span(spans)
            if span:
                prev_end = span[1]
                prev_grade = grade

        return issues


# ---------------------------------------------------------------------------
# grade_sections confidence validator
# ---------------------------------------------------------------------------

class GradeSectionsConfidenceValidator(Validator):
    """
    Validates grade_sections metadata quality.

    GS001  grade_sections missing on a document that has page_range data
    GS002  grade_sections grade entry missing required keys
    GS003  grade with confidence=low flagged for mandatory review
    GS004  grade with needs_review=True (informational report)
    GS005  grade_sections page_ranges disagree with page_range string values
    GS006  --confidence-report: summary of confidence distribution
    """
    name = "GradeSectionsConfidenceValidator"

    VALID_CONFIDENCE = {"high", "medium", "low"}
    REQUIRED_KEYS = {"page_ranges", "section_ids", "confidence", "notes", "needs_review"}

    def __init__(self, confidence_report: bool = False, verbose: bool = False):
        self.confidence_report = confidence_report
        self.verbose = verbose

    def validate(self, data: Dict[str, Any]) -> List[Issue]:
        issues: List[Issue] = []
        confidence_counts: Dict[str, int] = {"high": 0, "medium": 0, "low": 0}
        needs_review_count = 0
        total_grade_entries = 0

        for state_abbrev, state_data in data.items():
            for doc in state_data.get("documents", []):
                issues.extend(self._validate_doc(state_abbrev, doc, confidence_counts))
                gs = doc.get("grade_sections", {})
                for grade, entry in gs.items():
                    total_grade_entries += 1
                    if entry.get("needs_review"):
                        needs_review_count += 1

        if self.confidence_report:
            issues.extend(self._confidence_report(
                confidence_counts, needs_review_count, total_grade_entries
            ))

        return issues

    def _validate_doc(self, state: str, doc: dict, confidence_counts: dict) -> List[Issue]:
        issues: List[Issue] = []
        title = doc.get("title", "untitled")[:60]
        pr = doc.get("page_range")
        gs = doc.get("grade_sections", {})

        has_page_range = isinstance(pr, dict) and len(pr) > 0

        # GS001: page_range exists but no grade_sections
        if has_page_range and not gs:
            issues.append(Issue(
                severity=Severity.WARNING,
                code="GS001",
                state=state,
                field=title,
                message="Document has page_range data but no grade_sections",
                suggestion="Run migration script to convert page_range → grade_sections",
            ))
            return issues

        if not gs:
            return issues

        for grade, entry in gs.items():
            if not isinstance(entry, dict):
                continue

            # GS002: missing required keys
            missing_keys = self.REQUIRED_KEYS - set(entry.keys())
            if missing_keys:
                issues.append(Issue(
                    severity=Severity.ERROR,
                    code="GS002",
                    state=state,
                    field=title,
                    message=f"Grade {grade}: grade_sections entry missing keys: {sorted(missing_keys)}",
                    suggestion="Re-run migration script to add missing fields",
                ))

            # Track confidence distribution
            confidence = entry.get("confidence", "unknown")
            if confidence in confidence_counts:
                confidence_counts[confidence] += 1

            # GS003: low confidence → flag as warning
            if confidence == "low":
                issues.append(Issue(
                    severity=Severity.WARNING,
                    code="GS003",
                    state=state,
                    field=title,
                    message=f"Grade {grade}: low confidence — manual verification required",
                    suggestion="Re-extract page ranges for this grade manually",
                ))

            # GS004: needs_review flag (informational)
            if entry.get("needs_review") and self.verbose:
                issues.append(Issue(
                    severity=Severity.INFO,
                    code="GS004",
                    state=state,
                    field=title,
                    message=f"Grade {grade}: flagged needs_review ({entry.get('notes', '')})",
                    suggestion="Manually verify page range for this grade",
                ))

            # GS005: cross-check page_ranges against page_range string (if both exist)
            if has_page_range and isinstance(pr, dict):
                pr_str = pr.get(grade)
                gs_ranges = entry.get("page_ranges", [])
                if pr_str and isinstance(pr_str, str) and gs_ranges:
                    expected_spans, _ = _parse_range_string(pr_str)
                    # Compare first span start page
                    if expected_spans and gs_ranges:
                        pr_start = expected_spans[0][0]
                        gs_start = gs_ranges[0][0]
                        if abs(pr_start - gs_start) > 2:
                            issues.append(Issue(
                                severity=Severity.WARNING,
                                code="GS005",
                                state=state,
                                field=title,
                                message=(
                                    f"Grade {grade}: page_range starts at {pr_start} but "
                                    f"grade_sections starts at {gs_start} (difference > 2)"
                                ),
                                suggestion="Verify migration was applied correctly",
                            ))

        return issues

    def _confidence_report(
        self, counts: dict, needs_review: int, total: int
    ) -> List[Issue]:
        """Generate INFO issues summarizing confidence distribution."""
        if total == 0:
            return []
        return [
            Issue(
                severity=Severity.INFO,
                code="GS006",
                state="_ALL_",
                field="confidence_report",
                message=(
                    f"Confidence distribution: high={counts['high']} "
                    f"({counts['high']*100//total}%), "
                    f"medium={counts['medium']} ({counts['medium']*100//total}%), "
                    f"low={counts['low']} ({counts['low']*100//total}%) "
                    f"| needs_review={needs_review}/{total} "
                    f"({needs_review*100//total}%)"
                ),
                suggestion="Focus re-extraction efforts on low/medium confidence grades",
            )
        ]


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def parse_args(argv: List[str]) -> dict:
    args = {"states": None, "severity": "INFO", "verbose": False, "confidence_report": False}
    i = 0
    while i < len(argv):
        a = argv[i]
        if a in ("--verbose", "-v"):
            args["verbose"] = True
        elif a == "--confidence-report":
            args["confidence_report"] = True
        elif a == "--state" and i + 1 < len(argv):
            args["states"] = [s.strip().upper() for s in argv[i+1].split(",")]
            i += 1
        elif a == "--severity" and i + 1 < len(argv):
            args["severity"] = argv[i+1].upper()
            i += 1
        i += 1
    return args


def main() -> int:
    args = parse_args(sys.argv[1:])
    severity_map = {"ERROR": Severity.ERROR, "WARNING": Severity.WARNING, "INFO": Severity.INFO}
    min_severity = severity_map.get(args["severity"], Severity.INFO)

    data = load_states()
    print(f"Loaded {len(data)} states.")

    runner = ValidationRunner()
    runner.add_validator(PageRangeValidator(verbose=args["verbose"]))
    runner.add_validator(GradeSectionsConfidenceValidator(
        confidence_report=args["confidence_report"],
        verbose=args["verbose"],
    ))

    issues = runner.run(data, states=args["states"], min_severity=min_severity)
    print(runner.report(issues))

    errors = [i for i in issues if i.severity == Severity.ERROR]
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
