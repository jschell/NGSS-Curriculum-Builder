#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "pypdf>=5.0.0",
#     "pikepdf>=8.0.0",
#     "pdfplumber>=0.10.3",
#     "beautifulsoup4>=4.12.2",
#     "lxml>=4.9.3",
#     "httpx>=0.26.0",
#     "aiofiles>=23.2.0",
#     "orjson>=3.9.0",
# ]
# ///

"""
Cache warmup script — pre-fetches and parses standards documents, writing
grade_sections results to data/cache/ so subsequent queries skip the network.

Usage:
    uv run scripts/parsing/warmup_cache.py [options]

Options:
    --state ST      Only warm cache for one state (e.g. --state WA)
    --force         Re-fetch even if already cached (refreshes TTL)
    --dry-run       List documents without fetching or parsing
    --max-concurrent N  Max concurrent fetches (default: 5)
"""

import asyncio
import json
import os
import sys
import time
from pathlib import Path
from typing import Optional

# ── Resolve project root ──────────────────────────────────────────────────────
_THIS_DIR = Path(__file__).resolve().parent
_PROJECT_ROOT = _THIS_DIR.parent.parent
sys.path.insert(0, str(_THIS_DIR))

from document_cache import get_cached, write_cache, CACHE_DIR  # noqa: E402
from parse_standards import (  # noqa: E402
    parse_document,
    _grade_sections_to_dict,
    GradeSection,
)

STATES_JSON = _PROJECT_ROOT / "data" / "states.json"

# Formats that can actually be parsed (skip interactive/unknown)
PARSEABLE_FORMATS = {"PDF", "HTML"}

# Statuses that mean no document to fetch
SKIP_STATUSES = {
    "not_applicable_ngss_reference",
    "not_applicable_multi_document",
    "not_applicable_interactive_database",
}


# ── Helpers ───────────────────────────────────────────────────────────────────


def _load_documents(state_filter: Optional[str]) -> list[dict]:
    """Return flat list of document dicts (with state_abbrev injected) to process."""
    data = json.loads(STATES_JSON.read_text(encoding="utf-8"))
    docs = []
    for abbrev, state in data.items():
        if state_filter and abbrev.upper() != state_filter.upper():
            continue
        for doc in state.get("documents", []):
            # Skip non-parseable formats
            fmt = doc.get("format", "PDF")
            if fmt not in PARSEABLE_FORMATS:
                continue
            # Skip documents explicitly marked N/A
            if doc.get("page_range_status") in SKIP_STATUSES:
                continue
            doc_copy = dict(doc)
            doc_copy["state_abbrev"] = abbrev
            docs.append(doc_copy)
    return docs


def _fmt_duration(seconds: float) -> str:
    if seconds < 60:
        return f"{seconds:.0f}s"
    m, s = divmod(int(seconds), 60)
    return f"{m}m {s:02d}s"


# ── Core async logic ──────────────────────────────────────────────────────────


async def warm_one(
    doc: dict,
    semaphore: asyncio.Semaphore,
    download_dir: Path,
    force: bool,
) -> dict:
    """
    Warm cache for one document.

    Returns a result dict with keys:
        url, title, state_abbrev, status  ("cached"|"warmed"|"skipped"|"failed")
        grades_found (int), error (str|None)
    """
    url = doc.get("url", "")
    title = doc.get("title", url)
    state_abbrev = doc.get("state_abbrev", "")

    if not url:
        return {"url": url, "title": title, "state_abbrev": state_abbrev,
                "status": "skipped", "grades_found": 0, "error": "no URL"}

    # Check cache (unless --force)
    if not force:
        cached = get_cached(url)
        if cached is not None:
            return {"url": url, "title": title, "state_abbrev": state_abbrev,
                    "status": "cached", "grades_found": len(cached.get("grade_sections", {})),
                    "error": None}

    async with semaphore:
        try:
            result = await parse_document(doc, download_dir)

            if result.parse_errors and not result.grade_sections:
                return {"url": url, "title": title, "state_abbrev": state_abbrev,
                        "status": "failed", "grades_found": 0,
                        "error": "; ".join(result.parse_errors)}

            # write_cache is called inside parse_document automatically;
            # but if --force, we need to overwrite explicitly.
            if force and result.grade_sections:
                write_cache(
                    url=url,
                    result={
                        "grade_sections": _grade_sections_to_dict(result.grade_sections),
                        "parse_errors": result.parse_errors,
                    },
                    document_title=title,
                    state_abbrev=state_abbrev,
                    format_type=doc.get("format", "PDF"),
                )

            grades = len(result.grade_sections)
            return {"url": url, "title": title, "state_abbrev": state_abbrev,
                    "status": "warmed", "grades_found": grades, "error": None}

        except Exception as exc:  # noqa: BLE001
            return {"url": url, "title": title, "state_abbrev": state_abbrev,
                    "status": "failed", "grades_found": 0, "error": str(exc)}


async def run_warmup(
    docs: list[dict],
    force: bool,
    max_concurrent: int,
    dry_run: bool,
) -> list[dict]:
    """Run warmup for all documents, respecting concurrency limit."""
    total = len(docs)
    results = []

    if dry_run:
        for i, doc in enumerate(docs, 1):
            url = doc.get("url", "")
            cached = get_cached(url)
            status = "cached" if cached else "would fetch"
            grades = len(cached.get("grade_sections", {})) if cached else "?"
            print(f"[{i:3d}/{total}] {doc['state_abbrev']:2s}  {status:12s}  "
                  f"grades={grades:>3}  {doc.get('title', '')[:60]}")
        return []

    semaphore = asyncio.Semaphore(max_concurrent)
    download_dir = _PROJECT_ROOT / "cached"
    download_dir.mkdir(exist_ok=True)

    tasks = [warm_one(doc, semaphore, download_dir, force) for doc in docs]

    completed = 0
    for coro in asyncio.as_completed(tasks):
        result = await coro
        completed += 1
        status_icon = {"cached": "·", "warmed": "✓", "skipped": "–", "failed": "✗"}.get(
            result["status"], "?"
        )
        print(
            f"[{completed:3d}/{total}] {result['state_abbrev']:2s}  "
            f"{status_icon} {result['status']:8s}  "
            f"grades={result['grades_found']:>3}  "
            f"{result['title'][:55]}"
            + (f"  ERR: {result['error'][:40]}" if result["error"] else "")
        )
        results.append(result)

    return results


# ── CLI ───────────────────────────────────────────────────────────────────────


def parse_args() -> dict:
    args = {"state": None, "force": False, "dry_run": False, "max_concurrent": 5}
    argv = sys.argv[1:]
    i = 0
    while i < len(argv):
        arg = argv[i]
        if arg == "--state" and i + 1 < len(argv):
            args["state"] = argv[i + 1].upper()
            i += 2
        elif arg == "--force":
            args["force"] = True
            i += 1
        elif arg == "--dry-run":
            args["dry_run"] = True
            i += 1
        elif arg == "--max-concurrent" and i + 1 < len(argv):
            args["max_concurrent"] = int(argv[i + 1])
            i += 2
        else:
            print(f"Unknown argument: {arg}")
            print(__doc__)
            sys.exit(1)
    return args


async def main() -> int:
    args = parse_args()

    docs = _load_documents(args["state"])
    if not docs:
        print("No documents found matching criteria.")
        return 0

    scope = f"state={args['state']}" if args["state"] else "all states"
    mode = "DRY RUN" if args["dry_run"] else ("FORCE REFRESH" if args["force"] else "normal")
    print(f"\nCache warmup — scope: {scope}, mode: {mode}")
    print(f"Documents to process: {len(docs)}")
    print(f"Cache dir: {CACHE_DIR}")
    print()

    start = time.monotonic()
    results = await run_warmup(
        docs,
        force=args["force"],
        max_concurrent=args["max_concurrent"],
        dry_run=args["dry_run"],
    )
    elapsed = time.monotonic() - start

    if not args["dry_run"]:
        warmed = sum(1 for r in results if r["status"] == "warmed")
        cached = sum(1 for r in results if r["status"] == "cached")
        failed = sum(1 for r in results if r["status"] == "failed")
        skipped = sum(1 for r in results if r["status"] == "skipped")

        print()
        print("=" * 60)
        print(f"Warmup complete — {_fmt_duration(elapsed)}")
        print(f"  Warmed (new):   {warmed}")
        print(f"  Already cached: {cached}")
        print(f"  Failed:         {failed}")
        print(f"  Skipped:        {skipped}")
        print("=" * 60)

        if failed > 10:
            print(f"\nWARNING: {failed} failures — check network/bot-protection issues.")
            return 1

    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
