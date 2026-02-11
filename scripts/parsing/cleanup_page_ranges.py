#!/usr/bin/env python3
"""
Page Range Cleanup Script

Repairs the following artifacts in data/states.json without network access:

1. _all keys that encode multi-grade data (e.g. "K:14-25, 1:26-35, ...")
   → Parse and promote each grade to its own key, then delete _all.

2. _all keys that just store a whole-document range (e.g. "K:16-248")
   → Delete the _all key.

3. Plain-string page_range values (HI, MS)
   → Convert to null (can't be parsed without the document).

4. HI format field is HTML but URL is a PDF
   → Fix to PDF.

5. Cascading K ranges (parser captured each page: 2-6,6-8,8-10...)
   → Consolidate to single span.

6. Scattered K ranges spanning whole document (topic-organized artifact)
   → Remove K from page_range (data is unreliable).

Usage:
    python cleanup_page_ranges.py [--dry-run]
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def parse_spans(value: str) -> List[Tuple[int, int]]:
    """Parse 'N-M' comma-separated string into list of (start,end) tuples."""
    spans = []
    for token in value.split(","):
        token = token.strip()
        m = re.fullmatch(r"(\d+)-(\d+)", token)
        if m:
            spans.append((int(m.group(1)), int(m.group(2))))
        else:
            m = re.fullmatch(r"(\d+)", token)
            if m:
                p = int(m.group(1))
                spans.append((p, p))
    return spans


def merge_spans(spans: List[Tuple[int, int]]) -> List[Tuple[int, int]]:
    """Merge overlapping/adjacent spans."""
    if not spans:
        return []
    srt = sorted(spans)
    merged = [srt[0]]
    for s, e in srt[1:]:
        if s <= merged[-1][1] + 1:
            merged[-1] = (merged[-1][0], max(merged[-1][1], e))
        else:
            merged.append((s, e))
    return merged


def fmt_spans(spans: List[Tuple[int, int]]) -> str:
    return ", ".join(f"{s}-{e}" if s != e else str(s) for s, e in spans)


def is_cascading(spans: List[Tuple[int, int]]) -> bool:
    """
    Returns True if most consecutive segments share an endpoint
    (parser captured each page of a section individually).
    Pattern: (2,6), (6,8), (8,10) → adjacent at 6, 8
    """
    if len(spans) < 3:
        return False
    adjacent = sum(
        1 for i in range(1, len(spans))
        if abs(spans[i][0] - spans[i - 1][1]) <= 1
    )
    return adjacent >= len(spans) * 0.55


def is_scattered(spans: List[Tuple[int, int]], total_doc_pages: int = 300) -> bool:
    """
    Returns True if the spans are scattered across a large portion of the document
    (topic-organized artifact: K mentioned throughout the doc).
    """
    if not spans:
        return False
    overall_start = min(s for s, e in spans)
    overall_end = max(e for s, e in spans)
    span_coverage = overall_end - overall_start
    # Scattered if: covers more than 50 pages OR more than 15 non-adjacent segments
    return span_coverage > 50 or len(spans) > 15


# ---------------------------------------------------------------------------
# _all key parser
# ---------------------------------------------------------------------------

# Format: "K:14-25, 1:26-35, 2:36-47, ..."
ALL_ENTRY_PATTERN = re.compile(
    r"(K|\d{1,2})\s*:\s*([\d,\s\-]+?)(?=,\s*(?:K|\d{1,2})\s*:|$)"
)


def parse_all_value(all_value: str) -> Optional[Dict[str, str]]:
    """
    Try to parse an _all value like "K:14-25, 1:26-35, 2:36-47, ..."
    into a dict {grade: range_string}.
    Returns None if it doesn't match the multi-grade format.
    """
    matches = ALL_ENTRY_PATTERN.findall(all_value)
    if len(matches) < 2:
        return None
    result = {}
    for grade, ranges_str in matches:
        ranges_str = ranges_str.strip().rstrip(",")
        if ranges_str:
            result[grade] = ranges_str
    if len(result) < 2:
        return None
    return result


# ---------------------------------------------------------------------------
# Main cleanup logic
# ---------------------------------------------------------------------------

def cleanup_doc(abbr: str, doc: dict, dry_run: bool) -> List[str]:
    """
    Apply all cleanup rules to a single document. Returns list of change messages.
    Modifies doc in-place if not dry_run.
    """
    changes = []
    pr = doc.get("page_range")
    title = doc.get("title", "untitled")[:50]

    # ----------------------------------------------------------------
    # Rule: plain-string page_range → null
    # ----------------------------------------------------------------
    if isinstance(pr, str):
        changes.append(f"[{abbr}] '{title}': plain string '{pr[:40]}' → null")
        if not dry_run:
            doc["page_range"] = None
        return changes  # nothing else to do

    if not isinstance(pr, dict):
        return changes

    # Work on a copy we'll assign back
    new_pr = dict(pr)

    # ----------------------------------------------------------------
    # Rule: _all key
    # ----------------------------------------------------------------
    if "_all" in new_pr:
        all_val = new_pr["_all"]
        parsed = parse_all_value(str(all_val))

        if parsed:
            # Contains grade breakdown — promote all grades, remove _all.
            # Always use _all's clean values (they are more authoritative than
            # noisy individually-extracted values for the same grade).
            promoted = []
            for grade, range_str in parsed.items():
                new_pr[grade] = range_str
                promoted.append(grade)
            del new_pr["_all"]
            changes.append(
                f"[{abbr}] '{title}': _all promoted {promoted} → individual keys; _all removed"
            )
        else:
            # Just a whole-doc placeholder — delete it
            del new_pr["_all"]
            changes.append(f"[{abbr}] '{title}': _all='{all_val[:40]}' deleted (whole-doc placeholder)")

    # ----------------------------------------------------------------
    # Rule: messy K range
    # ----------------------------------------------------------------
    if "K" in new_pr:
        k_val = new_pr["K"]
        if isinstance(k_val, str):
            spans = parse_spans(k_val)
            if len(spans) > 8:
                if is_scattered(spans):
                    pass  # handled below
                elif is_cascading(spans):
                    merged = merge_spans(spans)
                    # Even after consolidation, check the total span isn't too wide
                    total_span = max(e for _, e in merged) - min(s for s, _ in merged)
                    if total_span > 50:
                        # Still spans too much of the document — treat as scattered
                        del new_pr["K"]
                        changes.append(
                            f"[{abbr}] '{title}': K cascading but wide span "
                            f"({total_span} pages) → removed"
                        )
                    else:
                        new_k = fmt_spans(merged)
                        changes.append(
                            f"[{abbr}] '{title}': K cascading ({len(spans)} segs) "
                            f"→ consolidated '{new_k}'"
                        )
                        new_pr["K"] = new_k
                if is_scattered(spans) and "K" in new_pr and new_pr["K"] == k_val:
                    del new_pr["K"]
                    changes.append(
                        f"[{abbr}] '{title}': K scattered ({len(spans)} segs spanning "
                        f"{min(s for s,e in spans)}-{max(e for s,e in spans)}) → removed"
                    )

    # ----------------------------------------------------------------
    # Apply changes
    # ----------------------------------------------------------------
    if new_pr != pr:
        if not dry_run:
            doc["page_range"] = new_pr if new_pr else None

    return changes


def cleanup_state_fields(abbr: str, state: dict, dry_run: bool) -> List[str]:
    """Fix state-level field issues."""
    changes = []
    for doc in state.get("documents", []):
        url = doc.get("url", "")
        fmt = doc.get("format", "")
        # HI: format=HTML but URL is a PDF file
        if fmt == "HTML" and url.lower().endswith(".pdf"):
            changes.append(f"[{abbr}] '{doc['title'][:40]}': format HTML→PDF (URL ends in .pdf)")
            if not dry_run:
                doc["format"] = "PDF"
    return changes


def main() -> int:
    dry_run = "--dry-run" in sys.argv

    states_path = Path("data/states.json")
    if not states_path.exists():
        states_path = Path("../../data/states.json")
    data = json.loads(states_path.read_text(encoding="utf-8"))

    all_changes = []

    for abbr, state in data.items():
        # State-level field fixes
        all_changes.extend(cleanup_state_fields(abbr, state, dry_run))
        # Document-level cleanup
        for doc in state.get("documents", []):
            all_changes.extend(cleanup_doc(abbr, doc, dry_run))

    if all_changes:
        print(f"{'DRY RUN — ' if dry_run else ''}Changes ({len(all_changes)}):")
        for c in all_changes:
            print(f"  {c}")
        if not dry_run:
            states_path.write_text(
                json.dumps(data, indent=2, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )
            print(f"\nSaved to {states_path}")
    else:
        print("No changes needed.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
