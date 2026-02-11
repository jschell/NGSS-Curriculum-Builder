# NGSS Curriculum Builder — Validation Suite

Comprehensive automated quality assurance for `data/states.json`.

## Quick Start

```bash
# Run full validation (all checks including URL network requests)
uv run scripts/validation/validate_all.py

# Fast local-only check (no network, <1 second)
uv run scripts/validation/validate_all.py --quick

# Errors only
uv run scripts/validation/validate_all.py --quick --severity ERROR

# Single state
uv run scripts/validation/validate_all.py --quick --state WA

# Save HTML report
uv run scripts/validation/validate_all.py --quick --report report.html

# Save Markdown report (useful for GitHub PR comments)
uv run scripts/validation/validate_all.py --quick --report report.md
```

---

## Validators

### `validation_framework.py` — Base Infrastructure
Shared classes used by all validators. Not run directly.

| Class | Purpose |
|-------|---------|
| `Validator` | Base class; subclass and implement `validate(data)` |
| `ValidationRunner` | Runs multiple validators, aggregates issues |
| `Issue` | Single finding: severity, code, state, message, suggestion |
| `Severity` | `ERROR` / `WARNING` / `INFO` |
| `load_states()` | Locates and loads `data/states.json` |

---

### `validate_urls.py` — URL Validation (Step 2)

Validates all document URLs in `states.json`. Requires network access.

```bash
uv run scripts/validation/validate_urls.py
uv run scripts/validation/validate_urls.py --verbose
uv run scripts/validation/validate_urls.py --state WA,OR
uv run scripts/validation/validate_urls.py --severity ERROR
```

| Code | Severity | Description |
|------|----------|-------------|
| U001 | ERROR    | URL typo (`htpp://`, missing `//`, whitespace) |
| U002 | WARNING  | HTTP used where HTTPS is available |
| U003 | WARNING  | URL uses a deprecated domain |
| U004 | ERROR    | HTTP error (4xx / 5xx / network failure) |
| U005 | INFO     | Redirect chain detected |
| U006 | WARNING  | SSL certificate invalid or expired |
| U007 | WARNING  | Response is HTML, not a document/PDF |

---

### `validate_page_ranges.py` — Page Range Quality (Step 3)

Checks completeness, format, and consistency of `page_range` data.

```bash
uv run scripts/validation/validate_page_ranges.py
uv run scripts/validation/validate_page_ranges.py --state TX
uv run scripts/validation/validate_page_ranges.py --severity WARNING
```

| Code | Severity | Description |
|------|----------|-------------|
| PR001 | ERROR   | `page_range` is a plain string instead of a dict |
| PR002 | WARNING | Grade in `grade_levels` is missing from `page_range` |
| PR003 | INFO    | Grade sequence gap (e.g. K,1,2,4 — missing 3) |
| PR004 | WARNING | `complete_k12` document missing full K-12 coverage |
| PR005 | WARNING | Only 1 grade extracted from a multi-grade document |
| PR006 | WARNING | Overlapping page ranges between consecutive grades |
| PR007 | WARNING | >12 comma segments (likely parser artifact) |
| PR008 | ERROR   | Malformed range token (can't parse as `N` or `N-M`) |
| PR009 | ERROR   | Negative/zero-length range (start > end) |

**Known issues detected:**
- `HI` — `page_range` is a plain string `'K:3-533'` (PR001)
- `MS` — `page_range` is a plain string `'K:20-133'` (PR001)
- `WA` — Grades 6-8 missing from main document (PR002)

---

### `validate_data_integrity.py` — Data Integrity (Step 4)

Checks overall structure, required fields, type consistency.

```bash
uv run scripts/validation/validate_data_integrity.py
uv run scripts/validation/validate_data_integrity.py --state CA
```

| Code | Severity | Description |
|------|----------|-------------|
| DI001 | ERROR   | Required state field missing or empty |
| DI002 | ERROR   | Required document field missing or empty |
| DI003 | ERROR   | Invalid `ngss_status` value |
| DI004 | ERROR   | Invalid `document_type` value |
| DI005 | ERROR   | `grade_levels` is empty |
| DI006 | WARNING | `page_range` keys not present in `grade_levels` |
| DI007 | WARNING | Duplicate URL used by multiple states |
| DI008 | WARNING | Adoption date is in the future |
| DI009 | ERROR   | `state_abbrev` field doesn't match dict key |
| DI010 | WARNING | Unusually high document count (>10) |
| DI011 | ERROR   | Document has no URL |
| DI012 | INFO    | `last_verified` date is over 2 years old |
| DI013 | WARNING | Unrecognised grade identifier in `grade_levels` |
| DI014 | ERROR   | Field type mismatch (e.g. list expected, got string) |

---

### `validate_special_structures.py` — Special Structures (Step 5)

Validates states with non-standard document organisation.

```bash
uv run scripts/validation/validate_special_structures.py
uv run scripts/validation/validate_special_structures.py --state TX,ME,NY
```

| Code | Severity | Description |
|------|----------|-------------|
| SS001 | INFO    | Multiple `grade_specific` docs without explanatory notes |
| SS002 | INFO    | `grade_band` docs without band organisation notes |
| SS003 | INFO    | `page_range` uses compound band keys (`6-8`, `9-12`) |
| SS004 | WARNING | `grade_band` doc covers only subset of declared grades |
| SS005 | WARNING | `grade_specific` doc declares multiple grade levels |
| SS006 | INFO    | Mixed document types without state notes |

---

### `validate_all.py` — Master Script (Step 6)

Orchestrates all validators. Use this for routine quality checks.

```bash
uv run scripts/validation/validate_all.py [options]
```

| Option | Description |
|--------|-------------|
| `--quick` | Skip URL network checks |
| `--state WA,OR` | Limit to specific states |
| `--severity LEVEL` | Show only `ERROR`, `WARNING`, or `INFO` and above |
| `--report FILE` | Save `.html` or `.md` report |
| `--verbose` | Show per-URL progress |

---

## Interpreting Results

**Errors** must be fixed before the data is considered reliable:
- Plain-string `page_range` values (HI, MS) — re-parse source documents
- Missing required fields — populate before publishing

**Warnings** indicate quality issues worth investigating:
- Missing grades in `page_range` — may require additional document parsing
- HTTP-only URLs — update to HTTPS where available
- Stale `last_verified` dates — re-check documents

**Info** is informational and generally does not require action:
- Redirect chains — consider updating to final URL for speed
- Compound band keys — verify intentional and add notes

---

## Adding a New Validator

1. Create `scripts/validation/validate_<name>.py`
2. Import and subclass `Validator` from `validation_framework`
3. Implement `validate(self, data) -> List[Issue]`
4. Add issue codes with docstring (e.g. `XX001`)
5. Add to `validate_all.py`'s `ValidationRunner`
6. Document in this README

```python
from validation_framework import Issue, Severity, Validator

class MyValidator(Validator):
    name = "MyValidator"

    def validate(self, data):
        issues = []
        for state_abbrev, state_data in data.items():
            # ... your checks ...
            issues.append(Issue(
                severity=Severity.WARNING,
                code="MY001",
                state=state_abbrev,
                message="Something looks off",
                suggestion="Fix it like this",
            ))
        return issues
```
