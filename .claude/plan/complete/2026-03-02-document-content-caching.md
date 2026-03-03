# Plan: Implement Document Content Caching

**Status:** Not Started
**Created:** 2026-03-02
**Estimated Duration:** 2-3 hours
**Priority:** Medium
**Feature:** `features.txt` → Other Features → "Implement document content caching"

---

## Context

Each call to `scripts/parsing/parse_standards.py` re-fetches and re-parses PDF/HTML
documents from state education websites. This costs 1-5 seconds per document and
~195 seconds for a full database parse. Repeated queries (research workflows, CI,
batch export) waste bandwidth and hammer state websites.

A disk-based content cache stores parsed `grade_sections` results keyed by URL.
Subsequent parses skip the network fetch entirely, returning cached JSON in <5ms.
Cache is lazily populated (warm on demand) and never loaded at CLI startup, so
metadata query performance is unaffected.

---

## Prerequisites

- [x] `data/states.json` with 101 documents catalogued
- [x] `scripts/parsing/parse_standards.py` functional (async httpx + pypdf/BS4)
- [x] UV available for running inline-dependency scripts
- [x] All baseline CLI commands passing

**Verification:**
```bash
python -c "import json; data=json.load(open('data/states.json')); print(len(data), 'states')"
# Expected: 51 states

python state_science_standards_system.py list | tail -3
# Expected: "Total: 51 states", no errors

python --version
# Expected: Python 3.10+
```

---

## Implementation Steps

### Step 1: Design cache directory layout and data schema

**Action:** Create `data/cache/` directory and document the cache format. No code yet —
just the directory and a `README.md` describing the schema. This anchors the contract
that all subsequent steps implement.

**Files to create:**
- `data/cache/.gitkeep` — keeps empty directory in version control
- `data/cache/README.md` — cache schema documentation

**Cache file naming convention:**
```
data/cache/<sha256_of_url>.json
```

**Cache file JSON schema:**
```json
{
  "schema_version": 1,
  "url": "https://...",
  "document_title": "...",
  "state_abbrev": "WA",
  "fetched_at": "2026-03-02T14:30:00Z",
  "ttl_days": 30,
  "format_type": "PDF",
  "grade_sections": {
    "K": {"page_ranges": [[4, 7]], "section_ids": [], "confidence": "high", "notes": "...", "needs_review": false},
    "1": {"page_ranges": [[8, 11]], ...}
  },
  "parse_errors": [],
  "cache_hit_count": 0
}
```

**Files to modify:** None

**Tests required:** None for this step (no code)

**Validation:**
```bash
ls data/cache/
# Expected: .gitkeep README.md
```

**Commit message:** `feat(cache): add data/cache/ directory with schema documentation`

---

### Step 2: Create `scripts/parsing/document_cache.py` cache module

**Action:** Implement a standalone stdlib-only cache module (no UV deps needed) with
read, write, invalidate, and status operations. All functions take `cache_dir` as a
parameter for testability.

**Files to create:** `scripts/parsing/document_cache.py`

**Key functions:**
```python
import hashlib, json, os
from datetime import datetime, timezone
from typing import Optional, Dict

CACHE_DIR = os.path.join(os.path.dirname(__file__), "../../data/cache")
DEFAULT_TTL_DAYS = 30

def _url_to_cache_key(url: str) -> str:
    """SHA-256 of URL → hex filename."""
    return hashlib.sha256(url.encode()).hexdigest()

def get_cached(url: str, cache_dir: str = CACHE_DIR, ttl_days: int = DEFAULT_TTL_DAYS) -> Optional[dict]:
    """Return cached parse result or None if missing/expired."""

def write_cache(url: str, result: dict, cache_dir: str = CACHE_DIR) -> str:
    """Serialize result to cache file. Returns cache file path."""

def invalidate(url: str, cache_dir: str = CACHE_DIR) -> bool:
    """Delete cache entry for URL. Returns True if entry existed."""

def invalidate_all(cache_dir: str = CACHE_DIR) -> int:
    """Clear entire cache. Returns count of deleted entries."""

def cache_status(cache_dir: str = CACHE_DIR) -> dict:
    """Return stats: total entries, expired entries, total_size_kb, oldest/newest."""
```

**Expiry logic:** Compare `fetched_at` ISO timestamp against `datetime.now(timezone.utc)`.
If age > `ttl_days` × 86400 seconds → return None (expired).

**Files to modify:** None

**Tests required:**
```bash
# Inline test at module level (python -c):
python -c "
import sys; sys.path.insert(0, 'scripts/parsing')
from document_cache import write_cache, get_cached, cache_status
import tempfile, os

with tempfile.TemporaryDirectory() as tmp:
    result = {'grade_sections': {'K': {'page_ranges': [[4,7]], 'section_ids': [], 'confidence': 'high', 'notes': None, 'needs_review': False}}, 'parse_errors': []}
    path = write_cache('https://example.com/test.pdf', result, cache_dir=tmp)
    print('Written to:', path)
    hit = get_cached('https://example.com/test.pdf', cache_dir=tmp)
    assert hit is not None, 'Expected cache hit'
    assert hit['grade_sections']['K']['page_ranges'] == [[4, 7]]
    miss = get_cached('https://example.com/nonexistent.pdf', cache_dir=tmp)
    assert miss is None, 'Expected cache miss'
    stats = cache_status(cache_dir=tmp)
    assert stats['total_entries'] == 1
    print('All cache module tests passed')
"
```

**Commit message:** `feat(cache): implement document_cache.py with read/write/invalidate/status`

---

### Step 3: Integrate cache into `scripts/parsing/parse_standards.py`

**Action:** Add cache lookup before any network fetch. If cache hit, return cached
`grade_sections` immediately. If cache miss, parse as normal then write result to cache.

**Files to modify:** `scripts/parsing/parse_standards.py`

**Integration pattern:**
```python
# At top of file (add import):
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from document_cache import get_cached, write_cache

# In the async parse function, before fetching:
async def parse_document(url: str, ...) -> DocumentParseResult:
    cached = get_cached(url)
    if cached is not None:
        return DocumentParseResult(
            ...,
            grade_sections=_deserialize_grade_sections(cached["grade_sections"]),
            from_cache=True
        )
    # ... existing fetch + parse logic ...
    write_cache(url, result_dict)
    return result
```

**Add `from_cache: bool = False`** field to `DocumentParseResult` dataclass so callers
can see whether result came from cache or live fetch.

**Preserve existing behavior entirely** — if cache module import fails for any reason,
log a warning and continue with live fetch (don't break the parser).

**Tests required:**
```bash
# Run the parser against one document and verify cache file is created:
# (Using a known-good, small PDF)
python -c "
import asyncio, sys, os, glob
sys.path.insert(0, 'scripts/parsing')

# Verify cache module integrates without import error:
import parse_standards
print('parse_standards imported OK')

# Verify data/cache/ gets populated after a parse run
# (we can't run full async test without UV deps, so just verify import chain)
print('Integration check passed')
"
```

**Validation (with UV):**
```bash
# Count cache files before:
ls data/cache/*.json 2>/dev/null | wc -l

# Run parser on first document of a known state:
uv run scripts/parsing/parse_standards.py --state WA --max-docs 1 2>&1 | head -20

# Count cache files after (should be +1):
ls data/cache/*.json 2>/dev/null | wc -l
```

**Commit message:** `feat(cache): integrate cache lookup into parse_standards.py`

---

### Step 4: Create `scripts/parsing/warmup_cache.py` batch warmup script

**Action:** Create a standalone UV script that iterates all 101 documents in
`data/states.json` and warms the cache by parsing each uncached document.
Skips already-cached URLs. Provides progress output and a final summary report.

**Files to create:** `scripts/parsing/warmup_cache.py`

**Script structure:**
```python
#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "pypdf>=5.0.0",
#     "httpx>=0.26.0",
#     "beautifulsoup4>=4.12.2",
#     "lxml>=4.9.3",
#     "aiofiles>=23.2.0",
# ]
# ///

"""
Cache warmup script — pre-fetches and caches all 101 standards documents.

Usage:
    uv run scripts/parsing/warmup_cache.py [--state TX] [--force] [--dry-run]

Options:
    --state ST   Only warm cache for one state
    --force      Re-fetch even if already cached (refreshes TTL)
    --dry-run    Show what would be fetched without actually fetching
"""
```

**Key behavior:**
- Loads `data/states.json` directly (stdlib json, no import of main CLI)
- For each document: call `get_cached(url)` — if hit AND not `--force`, skip
- Concurrent fetching with `asyncio.gather` (max 5 concurrent to avoid rate limiting)
- Progress: `[12/101] WA: Washington K-12 Standards... (cached)`
- Summary: `Warmed: 43 | Skipped (cached): 58 | Failed: 0 | Duration: 2m 14s`
- Writes cache entries using `write_cache(url, result)` from `document_cache.py`
- Exit code 0 on success, 1 if >5 failures

**Tests required:**
```bash
# Dry run (no network):
uv run scripts/parsing/warmup_cache.py --dry-run
# Expected: lists 101 documents with "would fetch" / "cached" status, no network calls

# Single-state warmup:
uv run scripts/parsing/warmup_cache.py --state WA
# Expected: fetches WA documents, writes cache entries, reports success

# Verify cache entries created:
ls data/cache/*.json | wc -l
# Expected: >= number of WA documents
```

**Commit message:** `feat(cache): add warmup_cache.py for batch cache population`

---

### Step 5: Add `cache` command to main CLI

**Action:** Add a `cache` subcommand to `state_science_standards_system.py` (stdlib
only, no UV deps) for cache status and cache clearing. This gives users a way to
manage the cache without writing scripts.

**Files to modify:** `state_science_standards_system.py`

**New subcommand:**
```
python state_science_standards_system.py cache status
python state_science_standards_system.py cache clear [--state TX]
```

**`cache status` output:**
```
================================================================================
DOCUMENT CONTENT CACHE STATUS
================================================================================

Cache directory: data/cache/
Total entries:   43 documents cached
Expired entries: 2 (TTL: 30 days)
Cache size:      1.2 MB
Oldest entry:    2026-02-15 (WA K-12 Standards)
Newest entry:    2026-03-02 (TX Biology)

Coverage: 43/101 documents cached (43%)

Run 'uv run scripts/parsing/warmup_cache.py' to warm remaining 58 documents.
================================================================================
```

**`cache clear` behavior:**
- Without `--state`: prompts "Clear all 43 cache entries? [y/N]" then deletes
- With `--state TX`: deletes only entries for TX document URLs
- Prints count of deleted entries

**Implementation:** The `cache` command in the main CLI imports `document_cache`
from a computed relative path (no UV needed since `document_cache.py` uses stdlib only).

**Files to modify:**
- `state_science_standards_system.py` — add `cmd_cache()`, dispatch in `main()`
- `print_usage()` — add cache command docs

**Tests required:**
```bash
# Status command:
python state_science_standards_system.py cache status
# Expected: shows cache stats, no errors

# Clear command (dry run via 'n' response):
echo "n" | python state_science_standards_system.py cache clear
# Expected: "Aborted." message

# Verify existing commands unaffected:
python state_science_standards_system.py list | tail -3
python state_science_standards_system.py state WA 5
```

**Commit message:** `feat(cli): add cache status and cache clear commands`

---

### Step 6: Run full validation and update documentation

**Action:** Run all baseline CLI tests to confirm no regressions. Measure cache speedup.
Update CLAUDE.md, features.txt, and add a quick note to the CLI help.

**Files to modify:**
- `features.txt` — move "Implement document content caching" to Done
- `.claude/CLAUDE.md` — update "Current State" and "Known Issues" sections
- `state_science_standards_system.py` — update `print_usage()` cache docs

**Full test suite:**
```bash
# --- Data integrity ---
python -c "import json; json.load(open('data/states.json'))"
python -c "import json; print(len(json.load(open('data/states.json'))), 'states')"
# Expected: 51 states

# --- Baseline CLI commands ---
python state_science_standards_system.py list | grep "Total: 51"
python state_science_standards_system.py search 5 | grep "Found"
python state_science_standards_system.py state WA | grep "Washington"
python state_science_standards_system.py state CA 8 | grep "Grade 8"
python state_science_standards_system.py range TX | grep "Complete"
python state_science_standards_system.py compare 3 | grep "Grade 3"
python state_science_standards_system.py queries NY 6 | grep "Suggested"
python state_science_standards_system.py sections WA | grep "Grade"
python state_science_standards_system.py ngss 4 | grep "Grade 4"

# --- New cache commands ---
python state_science_standards_system.py cache status
# Expected: no errors, shows cache stats

# --- Performance measurement ---
time uv run scripts/parsing/warmup_cache.py --state WA
# First run (cold): should fetch from network
time uv run scripts/parsing/warmup_cache.py --state WA
# Second run (warm): should report "all cached", near-instant
```

**Commit message:** `docs: update CLAUDE.md and features.txt for document content caching`

---

## Validation Strategy

**After each step:**
- Run `python state_science_standards_system.py list | tail -3` — must show 51 states
- Run `python -c "import json; json.load(open('data/states.json'))"` — must parse cleanly

**Final validation:**
```bash
# All baseline CLI tests (see Step 6)
python state_science_standards_system.py list | grep "Total: 51"
python state_science_standards_system.py cache status
uv run scripts/parsing/warmup_cache.py --dry-run
```

---

## Success Criteria

- [ ] `data/cache/` directory exists with schema README
- [ ] `document_cache.py` passes all inline unit tests
- [ ] `parse_standards.py` checks cache before fetching; writes to cache after parse
- [ ] `warmup_cache.py --dry-run` lists 101 documents without network calls
- [ ] `warmup_cache.py --state WA` warms WA documents and writes cache entries
- [ ] Second run of `warmup_cache.py --state WA` shows all entries as "cached" (< 1s)
- [ ] `cache status` CLI command reports correct cache stats
- [ ] `cache clear` CLI command removes cache entries with confirmation prompt
- [ ] All 9 baseline CLI commands still pass (no regressions)
- [ ] `data/states.json` unchanged (51 states, 101 docs, valid JSON)
- [ ] Main CLI remains dependency-free (no new imports at module level)
- [ ] All commits follow conventional commit format

---

## Rollback Plan

**If execution fails at any step:**
```bash
# The cache system is purely additive — no existing files are modified until Step 3
# For Steps 1-2: delete new files only
rm -rf data/cache/
rm scripts/parsing/document_cache.py

# For Step 3 (parse_standards.py integration):
git revert HEAD  # Reverts parse_standards.py changes

# For Step 5 (CLI changes):
git revert HEAD  # Reverts state_science_standards_system.py changes

# Full rollback of all cache work:
git revert HEAD~N..HEAD  # N = number of commits made
```

**Files to restore manually (if needed):**
- `state_science_standards_system.py` — restore from `git show HEAD~N:state_science_standards_system.py`
- `scripts/parsing/parse_standards.py` — restore from git

**No data changes** — `data/states.json` is never written by this feature.

---

## Potential Blockers

- [ ] **Bot protection (403/429):** State education websites may block automated fetching
  during cache warmup. Mitigation: 5-concurrent limit + exponential backoff in warmup script.
  Stop condition: if >10 fetch failures, stop and report.

- [ ] **Large PDFs:** Some PDFs are >10 MB (e.g. comprehensive K-12 documents).
  Mitigation: stream download with `httpx` streaming mode; add file size cap (50 MB max).

- [ ] **parse_standards.py CLI interface:** Step 3 validates with `--state WA --max-docs 1`
  flags. If the script doesn't support those flags, integration test must be adjusted.
  Read the script's argparse setup first to confirm flag names.

- [ ] **Cache storage size:** 101 documents × average 50 KB JSON ≈ 5 MB. Acceptable.
  If parsed content is unexpectedly large, add a per-entry size limit check.

**Stop conditions:**
- If modifying `parse_standards.py` causes 3+ test failures → stop, revert, ask human
- If cache entries exceed 50 MB total during warmup → stop, review size strategy
- If >10 state education websites return 403 during warmup → stop, document blocked states

---

## Notes

- **Document cache does NOT affect metadata queries.** `load_states_data()` in main CLI
  is unchanged. Cache is only used when `scripts/parsing/parse_standards.py` runs.

- **Cache format version:** `schema_version: 1` in each cache file. Future schema changes
  can bump this and invalidate older entries cleanly.

- **Git tracking:** `data/cache/` is included in version control as an empty directory
  (via `.gitkeep`). Cache files themselves should be added to `.gitignore` so cached
  content isn't committed. Add `data/cache/*.json` to `.gitignore` in Step 1.

- **Relationship to CSV/Excel export:** When export is implemented, it will benefit from
  the cache too (export can optionally include parsed content fields).

- **Reference plan:** `.claude/plan/holding/csv-excel-export.md` for UV script pattern.
