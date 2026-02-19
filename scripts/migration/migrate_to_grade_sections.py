#!/usr/bin/env python3
"""
Migrate page_range dict format to grade_sections rich metadata format.

Usage:
    python migrate_to_grade_sections.py --dry-run   # Preview without modifying
    python migrate_to_grade_sections.py --execute   # Apply migration

The migration is ADDITIVE: grade_sections is added alongside page_range.
page_range is NOT removed, allowing a gradual transition period.

grade_sections format:
{
  "grade_sections": {
    "K": {
      "page_ranges": [[4, 7]],
      "section_ids": [],
      "confidence": "high" | "medium" | "low",
      "notes": "Extracted via <method>",
      "needs_review": false
    }
  }
}
"""

import json
import re
import shutil
import sys
from datetime import datetime
from pathlib import Path

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
ROOT = Path(__file__).resolve().parents[2]
DATA_FILE = ROOT / "data" / "states.json"
BACKUP_FILE = ROOT / "data" / "states.json.backup"

# ---------------------------------------------------------------------------
# Extraction method registry
# Built from commit history analysis (see Step 2 / docs in plan)
# ---------------------------------------------------------------------------
EXTRACTION_METHODS: dict[str, dict[str, str]] = {
    # Key: state abbreviation, Value: {method, confidence}
    # toc_extraction = parsed from PDF table of contents automatically
    # manual_download = user manually downloaded PDF, then automated parse
    # remote_automated = fetched and parsed remotely without user intervention
    # mcp_tools = extracted with browser/MCP tool assistance
    # manual_verified = re-extracted in cleanup phase, high confidence
    "AK": {"method": "remote_automated", "confidence": "medium"},
    "AL": {"method": "remote_automated", "confidence": "high"},
    "AR": {"method": "remote_automated", "confidence": "medium"},
    "AZ": {"method": "manual_download", "confidence": "high"},
    "CA": {"method": "remote_automated", "confidence": "medium"},
    "CO": {"method": "remote_automated", "confidence": "medium"},
    "CT": {"method": "remote_automated", "confidence": "medium"},
    "DC": {"method": "remote_automated", "confidence": "medium"},
    "DE": {"method": "remote_automated", "confidence": "medium"},
    "FL": {"method": "remote_automated", "confidence": "medium"},
    "GA": {"method": "remote_automated", "confidence": "medium"},
    "HI": {"method": "manual_verified", "confidence": "high"},
    "IA": {"method": "remote_automated", "confidence": "medium"},
    "ID": {"method": "remote_automated", "confidence": "high"},
    "IL": {"method": "remote_automated", "confidence": "medium"},
    "IN": {"method": "remote_automated", "confidence": "medium"},
    "KS": {"method": "remote_automated", "confidence": "medium"},
    "KY": {"method": "remote_automated", "confidence": "high"},
    "LA": {"method": "remote_automated", "confidence": "medium"},
    "MA": {"method": "remote_automated", "confidence": "high"},
    "MD": {"method": "remote_automated", "confidence": "medium"},
    "ME": {"method": "remote_automated", "confidence": "medium"},
    "MI": {"method": "mcp_tools", "confidence": "high"},
    "MN": {"method": "remote_automated", "confidence": "medium"},
    "MO": {"method": "remote_automated", "confidence": "medium"},
    "MS": {"method": "remote_automated", "confidence": "low"},
    "MT": {"method": "remote_automated", "confidence": "high"},
    "NC": {"method": "remote_automated", "confidence": "medium"},
    "ND": {"method": "remote_automated", "confidence": "high"},
    "NE": {"method": "remote_automated", "confidence": "medium"},
    "NH": {"method": "remote_automated", "confidence": "medium"},
    "NJ": {"method": "remote_automated", "confidence": "high"},
    "NM": {"method": "remote_automated", "confidence": "medium"},
    "NV": {"method": "remote_automated", "confidence": "medium"},
    "NY": {"method": "remote_automated", "confidence": "medium"},
    "OH": {"method": "remote_automated", "confidence": "high"},
    "OK": {"method": "remote_automated", "confidence": "high"},
    "OR": {"method": "remote_automated", "confidence": "medium"},
    "PA": {"method": "remote_automated", "confidence": "high"},
    "RI": {"method": "remote_automated", "confidence": "medium"},
    "SC": {"method": "manual_download", "confidence": "high"},
    "SD": {"method": "remote_automated", "confidence": "high"},
    "TN": {"method": "manual_download", "confidence": "high"},
    "TX": {"method": "toc_extraction", "confidence": "medium"},
    "UT": {"method": "remote_automated", "confidence": "high"},
    "VA": {"method": "remote_automated", "confidence": "medium"},
    "VT": {"method": "remote_automated", "confidence": "medium"},
    "WA": {"method": "mcp_tools", "confidence": "high"},
    "WI": {"method": "remote_automated", "confidence": "high"},
    "WV": {"method": "remote_automated", "confidence": "medium"},
    "WY": {"method": "toc_extraction", "confidence": "high"},
}


# ---------------------------------------------------------------------------
# Core conversion helpers
# ---------------------------------------------------------------------------

def parse_range_string(range_str: str) -> list[list[int]]:
    """
    Convert human-readable page range string to list of [start, end] pairs.

    Examples:
        "4-7"        -> [[4, 7]]
        "4-7, 8-11"  -> [[4, 7], [8, 11]]
        "16"         -> [[16, 16]]
        "16-18"      -> [[16, 18]]
    """
    ranges = []
    parts = re.split(r",\s*", range_str.strip())
    for part in parts:
        part = part.strip()
        if not part:
            continue
        m = re.match(r"^(\d+)-(\d+)$", part)
        if m:
            ranges.append([int(m.group(1)), int(m.group(2))])
        elif re.match(r"^\d+$", part):
            page = int(part)
            ranges.append([page, page])
        else:
            # Unknown format - store as single-item string note, skip numeric
            pass
    return ranges


def determine_confidence(state: str, extraction_method: str, page_ranges: list) -> str:
    """Return confidence based on state registry and data quality."""
    # Look up state-level override first
    state_info = EXTRACTION_METHODS.get(state, {})
    base_confidence = state_info.get("confidence", "medium")

    # Downgrade if extraction is a single-page entry (start == end)
    if page_ranges and all(r[0] == r[1] for r in page_ranges):
        if base_confidence == "high":
            return "medium"

    return base_confidence


def needs_manual_review(page_ranges: list, confidence: str) -> bool:
    """Flag entries that should be manually reviewed."""
    if confidence == "low":
        return True
    # Single-page ranges are suspicious (may be TOC mentions, not section starts)
    if page_ranges and all(r[0] == r[1] for r in page_ranges):
        return True
    return False


def convert_page_range_to_sections(
    page_range_dict: dict,
    state: str,
    doc_title: str,
) -> dict:
    """Convert a simple page_range dict to grade_sections format."""
    state_info = EXTRACTION_METHODS.get(state, {})
    extraction_method = state_info.get("method", "automated")
    sections = {}

    for grade, range_val in page_range_dict.items():
        if grade == "_all":
            continue
        if range_val is None:
            continue

        range_str = str(range_val)
        page_ranges = parse_range_string(range_str)

        if not page_ranges:
            continue

        confidence = determine_confidence(state, extraction_method, page_ranges)
        review = needs_manual_review(page_ranges, confidence)

        sections[grade] = {
            "page_ranges": page_ranges,
            "section_ids": [],
            "confidence": confidence,
            "notes": f"Extracted via {extraction_method}",
            "needs_review": review,
        }

    return sections


# ---------------------------------------------------------------------------
# Migration runner
# ---------------------------------------------------------------------------

def migrate(data: dict, dry_run: bool) -> tuple[dict, list[dict]]:
    """
    Walk all documents and convert page_range -> grade_sections.

    Returns:
        (updated_data, report_lines)
    """
    report = []
    total_docs = 0
    migrated_docs = 0
    skipped_null = 0
    already_migrated = 0

    for state_abbr, state_data in data.items():
        for doc in state_data.get("documents", []):
            total_docs += 1
            title = doc.get("title", "Unknown")
            page_range = doc.get("page_range")

            if page_range is None:
                skipped_null += 1
                continue

            if not isinstance(page_range, dict):
                report.append({
                    "state": state_abbr,
                    "doc": title,
                    "status": "SKIP",
                    "reason": f"page_range is not a dict: {type(page_range).__name__}",
                })
                skipped_null += 1
                continue

            if doc.get("grade_sections"):
                already_migrated += 1
                report.append({
                    "state": state_abbr,
                    "doc": title,
                    "status": "ALREADY_MIGRATED",
                    "grades": list(doc["grade_sections"].keys()),
                })
                continue

            # Convert
            grade_sections = convert_page_range_to_sections(page_range, state_abbr, title)

            if not grade_sections:
                report.append({
                    "state": state_abbr,
                    "doc": title,
                    "status": "SKIP",
                    "reason": "page_range dict had no parseable entries",
                })
                continue

            migrated_docs += 1
            report.append({
                "state": state_abbr,
                "doc": title,
                "status": "CONVERTED",
                "grades": list(grade_sections.keys()),
                "confidence_distribution": {
                    conf: sum(1 for g in grade_sections.values() if g["confidence"] == conf)
                    for conf in ("high", "medium", "low")
                },
                "needs_review_count": sum(1 for g in grade_sections.values() if g["needs_review"]),
                "preview": {k: v for k, v in list(grade_sections.items())[:2]},
            })

            if not dry_run:
                doc["grade_sections"] = grade_sections

    summary = {
        "state": "_SUMMARY_",
        "doc": "",
        "status": "SUMMARY",
        "total_docs": total_docs,
        "migrated": migrated_docs,
        "skipped_null": skipped_null,
        "already_migrated": already_migrated,
    }
    report.append(summary)
    return data, report


def print_report(report: list[dict], dry_run: bool) -> None:
    mode = "DRY RUN" if dry_run else "EXECUTE"
    print(f"\n{'='*70}")
    print(f"  MIGRATION REPORT [{mode}] - {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"{'='*70}\n")

    for entry in report:
        status = entry["status"]
        if status == "SUMMARY":
            print(f"\n{'─'*70}")
            print("SUMMARY")
            print(f"  Total documents:    {entry['total_docs']}")
            print(f"  Migrated:           {entry['migrated']}")
            print(f"  Skipped (null):     {entry['skipped_null']}")
            print(f"  Already migrated:   {entry['already_migrated']}")
        elif status == "CONVERTED":
            print(f"[CONVERT] {entry['state']}: {entry['doc'][:55]}")
            print(f"          Grades: {', '.join(entry['grades'])}")
            dist = entry["confidence_distribution"]
            print(f"          Confidence: high={dist['high']} medium={dist['medium']} low={dist['low']}")
            if entry["needs_review_count"]:
                print(f"          ⚠ Needs review: {entry['needs_review_count']} grade(s)")
        elif status == "ALREADY_MIGRATED":
            print(f"[SKIP] {entry['state']}: already has grade_sections ({len(entry['grades'])} grades)")
        elif status == "SKIP":
            print(f"[SKIP] {entry['state']}: {entry['doc'][:40]} — {entry['reason']}")
    print()


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> None:
    dry_run = "--dry-run" in sys.argv
    execute = "--execute" in sys.argv

    if not dry_run and not execute:
        print("Usage:")
        print("  python migrate_to_grade_sections.py --dry-run")
        print("  python migrate_to_grade_sections.py --execute")
        sys.exit(1)

    print(f"Loading {DATA_FILE} ...")
    data = json.loads(DATA_FILE.read_text())

    if execute:
        print(f"Backing up to {BACKUP_FILE} ...")
        shutil.copy2(DATA_FILE, BACKUP_FILE)

    updated_data, report = migrate(data, dry_run=dry_run)
    print_report(report, dry_run=dry_run)

    if execute:
        print(f"Writing updated data to {DATA_FILE} ...")
        DATA_FILE.write_text(json.dumps(updated_data, indent=2, ensure_ascii=False) + "\n")
        print("Migration complete. Backup preserved at data/states.json.backup")
    else:
        print("Dry run complete. No files modified. Run with --execute to apply.")


if __name__ == "__main__":
    main()
