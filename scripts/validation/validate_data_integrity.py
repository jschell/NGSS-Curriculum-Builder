#!/usr/bin/env python3
"""
Data Integrity Validator - Step 4 of Comprehensive Validation Suite

Checks performed
----------------
DI001  Required top-level field missing or empty
DI002  Required document field missing or empty
DI003  Invalid ngss_status value
DI004  Invalid document_type value
DI005  grade_levels is empty or missing
DI006  page_range dict keys not a subset of grade_levels (orphan keys)
DI007  Duplicate URL found across states
DI008  Adoption date appears to be in the future
DI009  State abbreviation in data doesn't match dict key
DI010  Document count outlier (>5 documents for a single state)
DI011  Document has no URL
DI012  last_verified date is very old (>2 years) — may be stale
DI013  grade_levels contains unrecognised grade identifier
DI014  Field type mismatch (e.g. grade_levels is a string not a list)

Usage
-----
    uv run validate_data_integrity.py [--state WA,OR] [--severity ERROR|WARNING|INFO]
"""

from __future__ import annotations

import re
import sys
from datetime import date, datetime
from pathlib import Path
from typing import Any, Dict, List

sys.path.insert(0, str(Path(__file__).resolve().parent))
from validation_framework import Issue, Severity, Validator, ValidationRunner, load_states

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

VALID_NGSS_STATUSES = {"direct_adoption", "framework_based"}
VALID_DOC_TYPES = {"complete_k12", "grade_band", "grade_specific"}
VALID_FORMATS = {"PDF", "HTML", "Excel", "Word"}

# All recognisable grade identifiers (individual + compound bands)
GRADE_PATTERN = re.compile(
    r"^(K|\d{1,2}|\d{1,2}-\d{1,2}|K-\d{1,2})$"
)

REQUIRED_STATE_FIELDS = [
    "state_name", "state_abbrev", "ngss_status", "standards_name",
    "website", "documents",
]
REQUIRED_DOC_FIELDS = ["title", "url", "document_type", "grade_levels", "format"]

TODAY = date.today()


# ---------------------------------------------------------------------------
# Validator
# ---------------------------------------------------------------------------

class DataIntegrityValidator(Validator):
    name = "DataIntegrityValidator"

    def validate(self, data: Dict[str, Any]) -> List[Issue]:
        issues: List[Issue] = []
        seen_urls: Dict[str, str] = {}   # url -> "STATE/title"

        for state_abbrev, state_data in data.items():
            issues.extend(self._check_state(state_abbrev, state_data, seen_urls))

        return issues

    # ------------------------------------------------------------------
    # State-level checks
    # ------------------------------------------------------------------

    def _check_state(
        self, abbr: str, s: dict, seen_urls: Dict[str, str]
    ) -> List[Issue]:
        issues: List[Issue] = []

        # DI001: required top-level fields
        for field in REQUIRED_STATE_FIELDS:
            val = s.get(field)
            if val is None or val == "" or val == []:
                issues.append(Issue(
                    severity=Severity.ERROR,
                    code="DI001",
                    state=abbr,
                    field=field,
                    message=f"Required field '{field}' is missing or empty",
                    suggestion=f"Populate '{field}' for {abbr}",
                ))

        # DI003: invalid ngss_status
        status = s.get("ngss_status")
        if status and status not in VALID_NGSS_STATUSES:
            issues.append(Issue(
                severity=Severity.ERROR,
                code="DI003",
                state=abbr,
                field="ngss_status",
                message=f"Invalid ngss_status '{status}', expected one of {VALID_NGSS_STATUSES}",
                suggestion="Set to 'direct_adoption' or 'framework_based'",
            ))

        # DI009: state_abbrev in data matches dict key
        data_abbrev = s.get("state_abbrev", "")
        if data_abbrev and data_abbrev != abbr:
            issues.append(Issue(
                severity=Severity.ERROR,
                code="DI009",
                state=abbr,
                field="state_abbrev",
                message=f"state_abbrev field '{data_abbrev}' doesn't match dict key '{abbr}'",
                suggestion=f"Set state_abbrev to '{abbr}'",
            ))

        # DI008: adoption_date in future
        adoption_date = s.get("adoption_date", "")
        if adoption_date:
            year_match = re.search(r"\b(20\d{2})\b", str(adoption_date))
            if year_match:
                year = int(year_match.group(1))
                if year > TODAY.year:
                    issues.append(Issue(
                        severity=Severity.WARNING,
                        code="DI008",
                        state=abbr,
                        field="adoption_date",
                        message=f"adoption_date '{adoption_date}' appears to be in the future",
                        suggestion="Verify the adoption date",
                    ))

        # DI010: document count outlier
        docs = s.get("documents", [])
        if isinstance(docs, list) and len(docs) > 10:
            issues.append(Issue(
                severity=Severity.WARNING,
                code="DI010",
                state=abbr,
                field="documents",
                message=f"Unusually high document count: {len(docs)} documents",
                suggestion="Verify all documents are distinct and needed",
            ))

        # DI014: documents field type
        if not isinstance(docs, list):
            issues.append(Issue(
                severity=Severity.ERROR,
                code="DI014",
                state=abbr,
                field="documents",
                message=f"'documents' should be a list, got {type(docs).__name__}",
                suggestion="Fix data structure",
            ))
            return issues

        # Per-document checks
        for doc in docs:
            issues.extend(self._check_doc(abbr, doc, seen_urls))

        return issues

    # ------------------------------------------------------------------
    # Document-level checks
    # ------------------------------------------------------------------

    def _check_doc(
        self, state: str, doc: dict, seen_urls: Dict[str, str]
    ) -> List[Issue]:
        issues: List[Issue] = []
        title = doc.get("title", "untitled")[:60]

        # DI002: required document fields
        for field in REQUIRED_DOC_FIELDS:
            val = doc.get(field)
            if val is None or val == "" or val == []:
                issues.append(Issue(
                    severity=Severity.ERROR,
                    code="DI002",
                    state=state,
                    field=f"{title}: {field}",
                    message=f"Required document field '{field}' missing or empty",
                    suggestion=f"Populate '{field}' for document '{title}'",
                ))

        # DI011: document URL missing
        url = doc.get("url", "").strip()
        if not url:
            issues.append(Issue(
                severity=Severity.ERROR,
                code="DI011",
                state=state,
                field=title,
                message="Document has no URL",
                suggestion="Add the document URL",
            ))

        # DI007: duplicate URL across states
        if url:
            key = f"{state}/{title}"
            if url in seen_urls and seen_urls[url] != key:
                issues.append(Issue(
                    severity=Severity.WARNING,
                    code="DI007",
                    state=state,
                    field=title,
                    message=f"Duplicate URL also used by '{seen_urls[url]}': {url}",
                    suggestion="Verify this is intentional (shared document) or fix URL",
                ))
            else:
                seen_urls[url] = key

        # DI004: invalid document_type
        doc_type = doc.get("document_type")
        if doc_type and doc_type not in VALID_DOC_TYPES:
            issues.append(Issue(
                severity=Severity.ERROR,
                code="DI004",
                state=state,
                field=title,
                message=f"Invalid document_type '{doc_type}', expected one of {VALID_DOC_TYPES}",
                suggestion="Set document_type to 'complete_k12', 'grade_band', or 'grade_specific'",
            ))

        # DI005 + DI014: grade_levels type and emptiness
        grade_levels = doc.get("grade_levels")
        if not isinstance(grade_levels, list):
            issues.append(Issue(
                severity=Severity.ERROR,
                code="DI014",
                state=state,
                field=title,
                message=f"'grade_levels' should be a list, got {type(grade_levels).__name__}",
                suggestion="Fix grade_levels to be a list of grade strings",
            ))
            grade_levels = []
        elif len(grade_levels) == 0:
            issues.append(Issue(
                severity=Severity.ERROR,
                code="DI005",
                state=state,
                field=title,
                message="'grade_levels' is empty",
                suggestion="Add grade levels covered by this document",
            ))

        # DI013: unrecognised grade identifiers
        for g in grade_levels:
            if not GRADE_PATTERN.match(str(g)):
                issues.append(Issue(
                    severity=Severity.WARNING,
                    code="DI013",
                    state=state,
                    field=title,
                    message=f"Unrecognised grade identifier '{g}' in grade_levels",
                    suggestion="Use K, 1-12, or band notation like '9-12'",
                ))

        # DI006: page_range keys not in grade_levels
        pr = doc.get("page_range")
        if isinstance(pr, dict) and grade_levels:
            orphans = [k for k in pr.keys() if k not in grade_levels]
            if orphans:
                issues.append(Issue(
                    severity=Severity.WARNING,
                    code="DI006",
                    state=state,
                    field=title,
                    message=f"page_range has keys not in grade_levels: {orphans}",
                    suggestion="Add missing grades to grade_levels or remove orphan page_range keys",
                ))

        # DI012: stale last_verified
        last_verified = doc.get("last_verified", "")
        if last_verified:
            try:
                verified_date = datetime.strptime(last_verified, "%Y-%m-%d").date()
                age_days = (TODAY - verified_date).days
                if age_days > 730:  # 2 years
                    issues.append(Issue(
                        severity=Severity.INFO,
                        code="DI012",
                        state=state,
                        field=title,
                        message=f"last_verified is {age_days // 365} year(s) old ({last_verified})",
                        suggestion="Re-verify URL and document content",
                    ))
            except ValueError:
                issues.append(Issue(
                    severity=Severity.WARNING,
                    code="DI012",
                    state=state,
                    field=title,
                    message=f"last_verified has invalid date format '{last_verified}'",
                    suggestion="Use YYYY-MM-DD format",
                ))

        return issues


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def parse_args(argv: List[str]) -> dict:
    args = {"states": None, "severity": "INFO"}
    i = 0
    while i < len(argv):
        a = argv[i]
        if a == "--state" and i + 1 < len(argv):
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

    validator = DataIntegrityValidator()
    runner = ValidationRunner()
    runner.add_validator(validator)

    issues = runner.run(data, states=args["states"], min_severity=min_severity)
    print(runner.report(issues))

    # Print summary statistics
    total_docs = sum(len(s.get("documents", [])) for s in data.values())
    total_with_pr = sum(
        1 for s in data.values()
        for doc in s.get("documents", [])
        if isinstance(doc.get("page_range"), dict)
    )
    print(f"\nStatistics: {len(data)} states, {total_docs} documents, "
          f"{total_with_pr} documents with page_range data")

    errors = [i for i in issues if i.severity == Severity.ERROR]
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
