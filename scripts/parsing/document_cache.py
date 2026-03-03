"""
Document content cache for NGSS Curriculum Builder.

Stores parsed grade_sections results on disk, keyed by SHA-256 of the document URL.
All operations are stdlib-only (no UV dependencies required).

Cache file location: data/cache/<sha256_of_url>.json
"""

import hashlib
import json
import os
from datetime import datetime, timezone
from typing import Optional

# Default cache directory relative to this file (scripts/parsing/ -> ../../data/cache)
_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
CACHE_DIR = os.path.normpath(os.path.join(_THIS_DIR, "..", "..", "data", "cache"))

DEFAULT_TTL_DAYS = 30
SCHEMA_VERSION = 1


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _url_to_cache_key(url: str) -> str:
    """Return SHA-256 hex digest of URL — used as cache filename."""
    return hashlib.sha256(url.encode("utf-8")).hexdigest()


def _cache_path(url: str, cache_dir: str) -> str:
    return os.path.join(cache_dir, _url_to_cache_key(url) + ".json")


def _is_expired(entry: dict, ttl_days: int) -> bool:
    """Return True if the cache entry is older than ttl_days."""
    try:
        fetched_at = datetime.fromisoformat(entry["fetched_at"].replace("Z", "+00:00"))
        age_seconds = (datetime.now(timezone.utc) - fetched_at).total_seconds()
        return age_seconds > ttl_days * 86400
    except (KeyError, ValueError):
        return True  # Treat malformed entries as expired


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def get_cached(
    url: str,
    cache_dir: str = CACHE_DIR,
    ttl_days: int = DEFAULT_TTL_DAYS,
) -> Optional[dict]:
    """
    Return a cached parse result for *url*, or None if missing/expired.

    The returned dict has keys: grade_sections, parse_errors, fetched_at,
    document_title, state_abbrev, format_type, cache_hit_count.

    Side-effect: increments cache_hit_count on a cache hit.
    """
    path = _cache_path(url, cache_dir)
    if not os.path.exists(path):
        return None

    try:
        with open(path, "r", encoding="utf-8") as f:
            entry = json.load(f)
    except (OSError, json.JSONDecodeError):
        return None

    if _is_expired(entry, ttl_days):
        return None

    # Bump hit counter (best-effort; ignore write errors)
    try:
        entry["cache_hit_count"] = entry.get("cache_hit_count", 0) + 1
        with open(path, "w", encoding="utf-8") as f:
            json.dump(entry, f, indent=2)
    except OSError:
        pass

    return entry


def write_cache(
    url: str,
    result: dict,
    cache_dir: str = CACHE_DIR,
    ttl_days: int = DEFAULT_TTL_DAYS,
    document_title: str = "",
    state_abbrev: str = "",
    format_type: str = "PDF",
) -> str:
    """
    Persist *result* to the cache for *url*.

    *result* must contain at minimum:
        - "grade_sections": dict mapping grade strings to section dicts
        - "parse_errors": list of error strings (may be empty)

    Returns the path of the written cache file.
    """
    os.makedirs(cache_dir, exist_ok=True)
    path = _cache_path(url, cache_dir)

    entry = {
        "schema_version": SCHEMA_VERSION,
        "url": url,
        "document_title": document_title,
        "state_abbrev": state_abbrev,
        "fetched_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "ttl_days": ttl_days,
        "format_type": format_type,
        "grade_sections": result.get("grade_sections", {}),
        "parse_errors": result.get("parse_errors", []),
        "cache_hit_count": 0,
    }

    with open(path, "w", encoding="utf-8") as f:
        json.dump(entry, f, indent=2)

    return path


def invalidate(url: str, cache_dir: str = CACHE_DIR) -> bool:
    """
    Delete the cache entry for *url*.

    Returns True if an entry existed and was deleted, False if no entry found.
    """
    path = _cache_path(url, cache_dir)
    if os.path.exists(path):
        os.remove(path)
        return True
    return False


def invalidate_all(cache_dir: str = CACHE_DIR) -> int:
    """
    Delete all cache entries (.json files) in *cache_dir*.

    Returns the count of deleted files.
    """
    if not os.path.isdir(cache_dir):
        return 0
    count = 0
    for fname in os.listdir(cache_dir):
        if fname.endswith(".json"):
            try:
                os.remove(os.path.join(cache_dir, fname))
                count += 1
            except OSError:
                pass
    return count


def cache_status(cache_dir: str = CACHE_DIR, ttl_days: int = DEFAULT_TTL_DAYS) -> dict:
    """
    Return statistics about the current cache.

    Returned dict keys:
        total_entries   int   Total .json files in cache_dir
        expired_entries int   Entries older than ttl_days
        total_size_kb   float Combined size of all cache files in KB
        oldest_entry    dict | None   {url, fetched_at, document_title}
        newest_entry    dict | None   {url, fetched_at, document_title}
        cache_dir       str   Absolute path to cache directory
    """
    stats = {
        "total_entries": 0,
        "expired_entries": 0,
        "total_size_kb": 0.0,
        "oldest_entry": None,
        "newest_entry": None,
        "cache_dir": os.path.abspath(cache_dir),
    }

    if not os.path.isdir(cache_dir):
        return stats

    entries = []
    for fname in os.listdir(cache_dir):
        if not fname.endswith(".json"):
            continue
        fpath = os.path.join(cache_dir, fname)
        try:
            size = os.path.getsize(fpath)
            stats["total_size_kb"] += size / 1024
            with open(fpath, "r", encoding="utf-8") as f:
                entry = json.load(f)
            entries.append(entry)
            stats["total_entries"] += 1
            if _is_expired(entry, ttl_days):
                stats["expired_entries"] += 1
        except (OSError, json.JSONDecodeError):
            stats["total_entries"] += 1  # Count even if unreadable

    if entries:
        def _ts(e):
            try:
                return datetime.fromisoformat(e["fetched_at"].replace("Z", "+00:00"))
            except (KeyError, ValueError):
                return datetime.min.replace(tzinfo=timezone.utc)

        entries_sorted = sorted(entries, key=_ts)
        oldest = entries_sorted[0]
        newest = entries_sorted[-1]
        stats["oldest_entry"] = {
            "url": oldest.get("url", ""),
            "fetched_at": oldest.get("fetched_at", ""),
            "document_title": oldest.get("document_title", ""),
        }
        stats["newest_entry"] = {
            "url": newest.get("url", ""),
            "fetched_at": newest.get("fetched_at", ""),
            "document_title": newest.get("document_title", ""),
        }

    stats["total_size_kb"] = round(stats["total_size_kb"], 1)
    return stats
