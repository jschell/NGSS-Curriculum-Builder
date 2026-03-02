# Document Content Cache

Parsed document results are stored here as JSON files, keyed by SHA-256 of the
source URL. Cache files are excluded from version control (see `.gitignore`).

## Purpose

Avoid re-fetching and re-parsing PDF/HTML documents on every query. A cold parse
takes 1-5 seconds per document; a cache hit returns in <5ms.

## File Naming

```
data/cache/<sha256_of_url>.json
```

Example: `data/cache/3b4f8a2e1c9d7f6a...json` → cached parse of a document URL.

## Schema (version 1)

```json
{
  "schema_version": 1,
  "url": "https://...",
  "document_title": "Washington K-12 Science Standards",
  "state_abbrev": "WA",
  "fetched_at": "2026-03-02T14:30:00Z",
  "ttl_days": 30,
  "format_type": "PDF",
  "grade_sections": {
    "K": {
      "page_ranges": [[4, 7]],
      "section_ids": [],
      "confidence": "high",
      "notes": "Extracted via TOC parsing",
      "needs_review": false
    },
    "1": {
      "page_ranges": [[8, 11]],
      "section_ids": [],
      "confidence": "high",
      "notes": null,
      "needs_review": false
    }
  },
  "parse_errors": [],
  "cache_hit_count": 0
}
```

## Field Reference

| Field | Type | Description |
|-------|------|-------------|
| `schema_version` | int | Format version (currently 1) |
| `url` | str | Canonical document URL |
| `document_title` | str | Human-readable title from states.json |
| `state_abbrev` | str | Two-letter state code |
| `fetched_at` | str | ISO 8601 UTC timestamp of when document was fetched |
| `ttl_days` | int | Cache validity in days (default: 30) |
| `format_type` | str | "PDF", "HTML", or "Interactive" |
| `grade_sections` | dict | Grade → section mapping (same structure as states.json) |
| `parse_errors` | list | Any non-fatal errors encountered during parsing |
| `cache_hit_count` | int | Number of times this entry has been read from cache |

## Cache Expiry

An entry is considered expired when:
```
now_utc - fetched_at > ttl_days * 86400 seconds
```

Expired entries are not deleted automatically. Run `cache clear --expired` or
`python state_science_standards_system.py cache clear` to remove them.

## Management

```bash
# View cache status
python state_science_standards_system.py cache status

# Clear all cache entries
python state_science_standards_system.py cache clear

# Warm the cache (pre-fetch all documents)
uv run scripts/parsing/warmup_cache.py

# Warm cache for a single state
uv run scripts/parsing/warmup_cache.py --state WA

# Dry run (see what would be fetched)
uv run scripts/parsing/warmup_cache.py --dry-run
```
