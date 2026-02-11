#!/usr/bin/env python3
# /// script
# dependencies = [
#     "httpx>=0.27.0",
#     "pypdf>=5.0.0",
# ]
# ///
"""
Grade Range Extractor - improved TOC-first approach.

Strategy (in priority order):
  1. PDF bookmarks/outlines  — most reliable, explicit document structure
  2. Dedicated section-header pages — page where grade heading is the first
     substantive line (not just any mention of a grade word)
  3. Skip — leave existing data and report need for manual review

Usage:
    uv run extract_grade_ranges.py --states HI,MS,AR,IL
    uv run extract_grade_ranges.py --states ALL --dry-run
    uv run extract_grade_ranges.py --states AK,AL,ND,NV --merge   # merge with existing
"""

from __future__ import annotations

import io
import json
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import httpx
from pypdf import PdfReader

# ---------------------------------------------------------------------------
# Grade patterns — match section HEADERS, not body text occurrences.
# Only match when the grade label appears within the first ~200 chars of a page,
# or when the entire page text is short (likely a divider page).
# ---------------------------------------------------------------------------

HEADER_PATTERNS: Dict[str, List[re.Pattern]] = {
    "K": [
        re.compile(r"^(kindergarten|grade\s*k\b)", re.IGNORECASE | re.MULTILINE),
        re.compile(r"^\s*(kindergarten|grade\s+k)\s*$", re.IGNORECASE | re.MULTILINE),
    ],
    **{
        str(g): [
            re.compile(rf"^(grade\s*{g}\b|\b{g}(st|nd|rd|th)?\s+grade\b)", re.IGNORECASE | re.MULTILINE),
            re.compile(rf"^\s*grade\s+{g}\s*$", re.IGNORECASE | re.MULTILINE),
        ]
        for g in range(1, 13)
    },
}

CANONICAL = ["K", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12"]


def _fmt_range(start: int, end: int) -> str:
    """Format a 0-based [start, end) page range as 1-based 'S-E' string."""
    s = start + 1
    e = end  # end is exclusive, so last page = end (0-based) → end (1-based)
    if s == e:
        return str(s)
    return f"{s}-{e}"


def _merge_ranges(ranges: List[Tuple[int, int]]) -> List[Tuple[int, int]]:
    """Merge overlapping/adjacent 0-based ranges."""
    if not ranges:
        return []
    srt = sorted(ranges)
    merged = [srt[0]]
    for start, end in srt[1:]:
        if start <= merged[-1][1] + 1:
            merged[-1] = (merged[-1][0], max(merged[-1][1], end))
        else:
            merged.append((start, end))
    return merged


# ---------------------------------------------------------------------------
# Method 1: PDF bookmarks / outline
# ---------------------------------------------------------------------------

def extract_via_bookmarks(reader: PdfReader) -> Optional[Dict[str, str]]:
    """
    Walk the PDF outline (bookmarks). Return grade→page_range dict
    if we can find entries for at least 3 canonical grades.
    """
    outline = reader.outline
    if not outline:
        return None

    result: Dict[str, int] = {}  # grade → 0-based first page

    def _walk(items):
        for item in items:
            if isinstance(item, list):
                _walk(item)
                continue
            title = getattr(item, "title", "") or ""
            page_obj = None
            try:
                page_obj = reader.get_destination_page_number(item)
            except Exception:
                pass
            if page_obj is None:
                continue
            for grade in CANONICAL:
                patterns = HEADER_PATTERNS[grade]
                for pat in patterns:
                    if pat.search(title):
                        if grade not in result:
                            result[grade] = page_obj
                        break

    _walk(outline)

    if len(result) < 3:
        return None

    # Build ranges: each grade goes from its page to the next grade's page - 1
    sorted_grades = sorted(result.items(), key=lambda x: x[1])
    num_pages = len(reader.pages)
    grade_ranges: Dict[str, str] = {}
    for i, (grade, start_page) in enumerate(sorted_grades):
        if i + 1 < len(sorted_grades):
            end_page = sorted_grades[i + 1][1]
        else:
            end_page = num_pages
        grade_ranges[grade] = _fmt_range(start_page, end_page)

    return grade_ranges


# ---------------------------------------------------------------------------
# Method 2: Section-header page detection
# ---------------------------------------------------------------------------

def _is_section_header_page(page_text: str, grade: str) -> bool:
    """
    Returns True if the page appears to be a dedicated grade section header.
    Criteria: grade pattern matches in first 300 chars OR page is short (<300 chars total).
    """
    stripped = page_text.strip()
    if not stripped:
        return False
    head = stripped[:300]
    patterns = HEADER_PATTERNS[grade]
    for pat in patterns:
        if pat.search(head):
            return True
    # Also match if whole page is short and contains grade marker
    if len(stripped) < 400:
        for pat in patterns:
            if pat.search(stripped):
                return True
    return False


def extract_via_section_headers(
    pages_text: List[str],
) -> Optional[Dict[str, str]]:
    """
    Walk pages in order. When we encounter a dedicated section-header page,
    record the grade transition. This gives spans like grade K: pages 4-7.
    Requires at least 3 grades to be detected.
    """
    transitions: List[Tuple[int, str]] = []  # (0-based page, grade)

    for page_idx, text in enumerate(pages_text):
        for grade in CANONICAL:
            if _is_section_header_page(text, grade):
                # Don't record duplicate consecutive grade
                if transitions and transitions[-1][1] == grade:
                    continue
                transitions.append((page_idx, grade))
                break  # one grade per page

    if len(transitions) < 3:
        return None

    grade_ranges: Dict[str, str] = {}
    num_pages = len(pages_text)
    for i, (start_page, grade) in enumerate(transitions):
        if i + 1 < len(transitions):
            end_page = transitions[i + 1][0]
        else:
            end_page = num_pages
        grade_ranges[grade] = _fmt_range(start_page, end_page)

    return grade_ranges


# ---------------------------------------------------------------------------
# Download
# ---------------------------------------------------------------------------

def download_pdf(url: str, timeout: int = 45) -> Optional[bytes]:
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        ),
        "Accept": "application/pdf,*/*",
    }
    try:
        resp = httpx.get(url, headers=headers, timeout=timeout, follow_redirects=True)
        if resp.status_code == 200:
            ct = resp.headers.get("content-type", "")
            if "pdf" in ct.lower() or resp.content[:4] == b"%PDF":
                return resp.content
        print(f"    HTTP {resp.status_code} — content-type: {resp.headers.get('content-type','?')}")
    except Exception as e:
        print(f"    Download error: {e}")
    return None


# ---------------------------------------------------------------------------
# Extract for a single document
# ---------------------------------------------------------------------------

def extract_for_document(doc: dict) -> Tuple[Optional[Dict[str, str]], str]:
    """
    Returns (grade_range_dict or None, method_used).
    method_used is one of: 'bookmarks', 'section_headers', 'failed'.
    """
    url = doc.get("url", "")
    fmt = doc.get("format", "PDF").upper()

    if fmt != "PDF":
        return None, "skipped_not_pdf"

    print(f"    Downloading: {url[:70]}...")
    data = download_pdf(url)
    if not data:
        return None, "download_failed"

    try:
        reader = PdfReader(io.BytesIO(data))
        num_pages = len(reader.pages)
        print(f"    PDF loaded: {num_pages} pages")
    except Exception as e:
        print(f"    PDF parse error: {e}")
        return None, "parse_error"

    # Method 1: bookmarks
    result = extract_via_bookmarks(reader)
    if result:
        print(f"    Bookmarks: found {len(result)} grades: {sorted(result.keys())}")
        return result, "bookmarks"

    # Method 2: section headers
    pages_text = []
    for page in reader.pages:
        try:
            pages_text.append(page.extract_text() or "")
        except Exception:
            pages_text.append("")

    result = extract_via_section_headers(pages_text)
    if result:
        print(f"    Section headers: found {len(result)} grades: {sorted(result.keys())}")
        return result, "section_headers"

    print(f"    Could not extract grade sections automatically")
    return None, "failed"


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def load_states() -> dict:
    for candidate in [Path("data/states.json"), Path("../../data/states.json")]:
        if candidate.exists():
            return json.loads(candidate.read_text(encoding="utf-8"))
    raise FileNotFoundError("Cannot find data/states.json")


def save_states(data: dict):
    for candidate in [Path("data/states.json"), Path("../../data/states.json")]:
        if candidate.exists():
            candidate.write_text(
                json.dumps(data, indent=2, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )
            return
    raise FileNotFoundError("Cannot find data/states.json to save")


def parse_args(argv: List[str]) -> dict:
    args = {"states": [], "dry_run": False, "merge": False}
    i = 0
    while i < len(argv):
        a = argv[i]
        if a == "--dry-run":
            args["dry_run"] = True
        elif a == "--merge":
            args["merge"] = True
        elif a == "--states" and i + 1 < len(argv):
            val = argv[i + 1]
            args["states"] = (
                [] if val.upper() == "ALL"
                else [s.strip().upper() for s in val.split(",")]
            )
            i += 1
        i += 1
    return args


def main() -> int:
    args = parse_args(sys.argv[1:])
    if not args.get("states") and "--states" not in sys.argv:
        # Default: all target states from the plan
        args["states"] = [
            "HI", "MS",                          # plain string errors
            "AR", "IL", "MT", "PA",              # only K extracted
            "AK", "AL", "KY", "ND", "NV", "WI", # partial
            "IA", "MA",                           # messy K
        ]

    data = load_states()
    target_abbrevs = args["states"] if args["states"] else list(data.keys())
    dry_run = args["dry_run"]
    merge = args["merge"]

    print(f"Extracting page ranges for: {target_abbrevs}")
    print(f"Mode: {'DRY RUN' if dry_run else 'LIVE'} | merge={merge}")
    print()

    results_summary = []

    for abbr in target_abbrevs:
        if abbr not in data:
            print(f"{abbr}: NOT FOUND in states.json")
            continue

        state = data[abbr]
        print(f"\n{'='*60}")
        print(f"{abbr}: {state.get('state_name', '')}")

        for doc_idx, doc in enumerate(state.get("documents", [])):
            doc_type = doc.get("document_type", "")
            title = doc.get("title", "")[:50]
            existing_pr = doc.get("page_range")

            print(f"\n  [{doc_type}] {title}")

            # Fix plain-string page_range first (HI, MS)
            if isinstance(existing_pr, str):
                print(f"  Current: PLAIN STRING '{existing_pr}' — needs re-extraction")

            # Skip if already has good data (dict with 8+ grades) and not merging
            if isinstance(existing_pr, dict) and len(existing_pr) >= 8 and not merge:
                print(f"  Current: {len(existing_pr)} grades — skipping (use --merge to re-extract)")
                continue

            result, method = extract_for_document(doc)

            if result:
                if merge and isinstance(existing_pr, dict):
                    # Merge: add new grades, keep existing ones that aren't in result
                    merged = {**result, **{k: v for k, v in existing_pr.items()
                                          if k not in result and k != "_all"}}
                    # Remove _all artifact
                    merged.pop("_all", None)
                    result = merged

                # Remove _all artifact even without merge
                if isinstance(result, dict):
                    result.pop("_all", None)

                print(f"  Result ({method}): {len(result)} grades: {sorted(result.keys())}")
                if not dry_run:
                    data[abbr]["documents"][doc_idx]["page_range"] = result
                results_summary.append((abbr, title, len(result), method, "success"))
            else:
                print(f"  Result: FAILED ({method}) — no changes made")
                results_summary.append((abbr, title, 0, method, "failed"))

    print(f"\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")
    success = [r for r in results_summary if r[4] == "success"]
    failed = [r for r in results_summary if r[4] == "failed"]
    print(f"Successful: {len(success)}")
    for abbr, title, grades, method, _ in success:
        print(f"  {abbr}: {grades} grades via {method}")
    if failed:
        print(f"Failed/skipped: {len(failed)}")
        for abbr, title, _, method, _ in failed:
            print(f"  {abbr}: {method}")

    if not dry_run and success:
        save_states(data)
        print(f"\nSaved {len(success)} state(s) to data/states.json")

    return 0 if not failed else 1


if __name__ == "__main__":
    sys.exit(main())
