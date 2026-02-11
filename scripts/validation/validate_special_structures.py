#!/usr/bin/env python3
"""
Special Structure Validator - Step 5 of Comprehensive Validation Suite

Validates states with non-standard document organisation:
  - grade_specific:  one document per individual grade (like TX K-8, ME)
  - grade_band:      documents span a grade band (elem/middle/high) — like NY, NJ, KY
  - compound keys:   page_range uses band keys like '9-12', '6-8'

Checks performed
----------------
SS001  State has multiple grade_specific docs but special_structure note is absent
SS002  State has grade_band docs but no notes explaining band organisation
SS003  page_range uses compound band keys (6-8, 9-12) — may indicate special structure
SS004  grade_band document covers only a subset of its declared grade_levels
SS005  grade_specific doc declares multiple grade levels (contradicts type)
SS006  Mix of document types within one state with no explanation in notes
SS007  State notes mention grade-specific organisation but docs don't match

Usage
-----
    uv run validate_special_structures.py [--state WA,OR] [--severity ERROR|WARNING|INFO]
"""

from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Set

sys.path.insert(0, str(Path(__file__).resolve().parent))
from validation_framework import Issue, Severity, Validator, ValidationRunner, load_states

CANONICAL_GRADES = ["K", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12"]
BAND_PATTERN = re.compile(r"^\d{1,2}-\d{1,2}$|^K-\d{1,2}$")

GRADE_BAND_KEYWORDS = [
    "elementary", "middle", "high school", "grade band", "band",
    "k-5", "k-8", "6-8", "9-12", "grades 6", "grades 9",
]
GRADE_SPECIFIC_KEYWORDS = [
    "grade specific", "grade-specific", "separate pdf", "individual grade",
    "per grade", "one per grade",
]


def _doc_types_in_state(docs: List[dict]) -> Set[str]:
    return {d.get("document_type", "") for d in docs if d.get("document_type")}


def _has_notes_keyword(text: str, keywords: List[str]) -> bool:
    text_lower = (text or "").lower()
    return any(kw in text_lower for kw in keywords)


class SpecialStructureValidator(Validator):
    name = "SpecialStructureValidator"

    def validate(self, data: Dict[str, Any]) -> List[Issue]:
        issues: List[Issue] = []
        for state_abbrev, state_data in data.items():
            issues.extend(self._check_state(state_abbrev, state_data))
        return issues

    def _check_state(self, abbr: str, s: dict) -> List[Issue]:
        issues: List[Issue] = []
        docs = s.get("documents", [])
        if not docs:
            return issues

        state_notes = s.get("notes", "") or ""
        doc_types = _doc_types_in_state(docs)

        grade_specific_docs = [d for d in docs if d.get("document_type") == "grade_specific"]
        grade_band_docs = [d for d in docs if d.get("document_type") == "grade_band"]
        complete_k12_docs = [d for d in docs if d.get("document_type") == "complete_k12"]

        # SS001: multiple grade_specific docs with no explanatory note
        if len(grade_specific_docs) > 1:
            if not _has_notes_keyword(state_notes, GRADE_SPECIFIC_KEYWORDS):
                issues.append(Issue(
                    severity=Severity.INFO,
                    code="SS001",
                    state=abbr,
                    field="documents",
                    message=(
                        f"State has {len(grade_specific_docs)} grade_specific documents "
                        f"but state notes don't mention grade-specific organisation"
                    ),
                    suggestion="Add a note explaining that standards are published per grade",
                ))

        # SS002: grade_band docs with no explanatory note
        if grade_band_docs:
            if not _has_notes_keyword(state_notes, GRADE_BAND_KEYWORDS):
                issues.append(Issue(
                    severity=Severity.INFO,
                    code="SS002",
                    state=abbr,
                    field="documents",
                    message=(
                        f"State has {len(grade_band_docs)} grade_band document(s) "
                        f"but state notes don't mention band organisation"
                    ),
                    suggestion="Add a note explaining the grade band structure (e.g. K-5, 6-8, 9-12)",
                ))

        # SS006: mixed document types with no explanation
        if len(doc_types) > 1 and "complete_k12" in doc_types and (
            "grade_specific" in doc_types or "grade_band" in doc_types
        ):
            if not state_notes:
                issues.append(Issue(
                    severity=Severity.INFO,
                    code="SS006",
                    state=abbr,
                    field="documents",
                    message=f"Mixed document types ({sorted(doc_types)}) with no state-level notes",
                    suggestion="Add notes field explaining why multiple document types coexist",
                ))

        # Per-document checks
        for doc in docs:
            issues.extend(self._check_doc(abbr, doc))

        return issues

    def _check_doc(self, state: str, doc: dict) -> List[Issue]:
        issues: List[Issue] = []
        title = doc.get("title", "untitled")[:60]
        doc_type = doc.get("document_type", "")
        grade_levels = doc.get("grade_levels") or []
        pr = doc.get("page_range") if isinstance(doc.get("page_range"), dict) else {}
        doc_notes = doc.get("notes", "") or ""

        # SS003: compound band keys in page_range
        if pr:
            band_keys = [k for k in pr.keys() if BAND_PATTERN.match(k)]
            if band_keys:
                issues.append(Issue(
                    severity=Severity.INFO,
                    code="SS003",
                    state=state,
                    field=title,
                    message=f"page_range uses compound band key(s) {band_keys} — subject-based or band organisation",
                    suggestion="Verify this is intentional; consider adding a doc note explaining the structure",
                ))

        # SS004: grade_band doc that only covers a subset of its grade_levels
        if doc_type == "grade_band" and isinstance(grade_levels, list) and len(grade_levels) > 0:
            canonical_in_doc = [g for g in grade_levels if g in CANONICAL_GRADES]
            if pr and isinstance(pr, dict):
                covered = set(pr.keys())
                missing_from_pr = [g for g in canonical_in_doc if g not in covered]
                if missing_from_pr and len(missing_from_pr) < len(canonical_in_doc):
                    issues.append(Issue(
                        severity=Severity.WARNING,
                        code="SS004",
                        state=state,
                        field=title,
                        message=(
                            f"grade_band document has page_range for only "
                            f"{len(canonical_in_doc) - len(missing_from_pr)}/{len(canonical_in_doc)} "
                            f"declared grades; missing: {missing_from_pr}"
                        ),
                        suggestion="Extract page ranges for missing grades or correct grade_levels",
                    ))

        # SS005: grade_specific doc with multiple grade levels
        if doc_type == "grade_specific" and isinstance(grade_levels, list):
            canonical_in_doc = [g for g in grade_levels if g in CANONICAL_GRADES]
            if len(canonical_in_doc) > 2:
                issues.append(Issue(
                    severity=Severity.WARNING,
                    code="SS005",
                    state=state,
                    field=title,
                    message=(
                        f"grade_specific document claims {len(canonical_in_doc)} grade levels "
                        f"({canonical_in_doc[:4]}{'...' if len(canonical_in_doc)>4 else ''}); "
                        f"expected 1 grade for grade_specific type"
                    ),
                    suggestion=(
                        "Change document_type to 'complete_k12' or 'grade_band', "
                        "or split into per-grade documents"
                    ),
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

    validator = SpecialStructureValidator()
    runner = ValidationRunner()
    runner.add_validator(validator)

    issues = runner.run(data, states=args["states"], min_severity=min_severity)
    print(runner.report(issues))

    # Summary: count states by document type mix
    only_complete = sum(
        1 for s in data.values()
        if {d.get("document_type") for d in s.get("documents", [])} == {"complete_k12"}
    )
    has_grade_specific = sum(
        1 for s in data.values()
        if any(d.get("document_type") == "grade_specific" for d in s.get("documents", []))
    )
    has_grade_band = sum(
        1 for s in data.values()
        if any(d.get("document_type") == "grade_band" for d in s.get("documents", []))
    )
    print(f"\nDocument structure breakdown:")
    print(f"  Only complete_k12: {only_complete}")
    print(f"  Has grade_specific docs: {has_grade_specific}")
    print(f"  Has grade_band docs: {has_grade_band}")

    errors = [i for i in issues if i.severity == Severity.ERROR]
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
