# Data Schema Documentation

## Overview

The NGSS Curriculum Builder uses a JSON-based data structure to track science standards across all 50 US states + District of Columbia. This document describes the schema used in `data/states.json`.

## StandardsDocument

Represents a single standards document (PDF, HTML, or interactive).

### Fields

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `title` | str | Document title | "2023 Alabama Course of Study: Science" |
| `url` | str | URL to the document | "https://example.com/standards.pdf" |
| `grade_levels` | List[str] | Grades covered by this document | `["K", "1", "2"]` or `["K", "1", "2", ..., "12"]` |
| `document_type` | str | Type of document organization | `"complete_k12"`, `"grade_specific"`, `"grade_band"` |
| `format` | str | Document format | `"PDF"`, `"HTML"`, `"Interactive"` |
| `page_range` | dict \| null | **DEPRECATED** — grade page ranges (legacy) | `{"K": "4-7", "1": "8-11"}` or `null` |
| `grade_sections` | dict \| {} | **Rich page/section metadata** (preferred) | See below |
| `notes` | str \| null | Additional notes about the document | "Based on Framework for K-12 Science Education" |
| `url_source` | str \| null | Where URL was found | "https://www.alabamaachieves.org/acad-standards/" |
| `last_verified` | str \| null | Last URL verification date (YYYY-MM-DD) | "2026-02-04" |

### grade_sections Field (Preferred)

The `grade_sections` field stores rich metadata about grade-specific page locations within a document. It supersedes the legacy `page_range` dict format.

**Structure:**
```json
"grade_sections": {
  "K": {
    "page_ranges": [[4, 7]],
    "section_ids": [],
    "confidence": "high",
    "notes": "Extracted via manual_verified",
    "needs_review": false
  },
  "1": {
    "page_ranges": [[8, 11]],
    "section_ids": [],
    "confidence": "high",
    "notes": "Extracted via manual_verified",
    "needs_review": false
  }
}
```

**Fields per grade entry:**

| Field | Type | Description |
|-------|------|-------------|
| `page_ranges` | `[[start, end], ...]` | List of page spans (1-indexed) |
| `section_ids` | `[str, ...]` | Reserved for future section ID mapping |
| `confidence` | `"high" \| "medium" \| "low"` | Quality of the extraction |
| `notes` | str | Extraction method description |
| `needs_review` | bool | True if manual verification is recommended |

**Confidence levels:**

| Level | Meaning | When assigned |
|-------|---------|---------------|
| `high` | Verified extraction | Manual download, MCP tools, or manual verification |
| `medium` | Automated extraction | Remote fetch without cross-checking |
| `low` | Uncertain data | URL broken, or data known to be incomplete |

**Multi-range example (grade spans two page blocks):**
```json
"9-12": {
  "page_ranges": [[54, 64], [65, 95]],
  "section_ids": [],
  "confidence": "high",
  "notes": "Extracted via mcp_tools",
  "needs_review": false
}
```

**When grade_sections is null/empty:**
- Single-grade documents (entire doc covers one grade) → `grade_sections: {}`
- Documents where page layout does not separate by grade → `grade_sections: {}`

---

### page_range Field (DEPRECATED)

> **⚠ Deprecated as of 2026-02-15.** Use `grade_sections` instead.
> `page_range` is preserved alongside `grade_sections` during the transition period.
> It will be removed in a future major release.

**Legacy format:**
```json
"page_range": {
  "K": "4-7",
  "1": "8-11",
  "2": "12-16"
}
```

**Deprecation timeline:**
- 2026-02-15: `grade_sections` added alongside `page_range` (additive migration)
- 2026-Q2: CLI reads `grade_sections` only; `page_range` retained in JSON
- 2026-Q3: `page_range` removed from `data/states.json`

**Migration:** Run `scripts/migration/migrate_to_grade_sections.py --dry-run` to preview or `--execute` to apply.

---

## Using grade_sections

### CLI Display

The CLI automatically uses `grade_sections` when showing state information:

```bash
# Show all docs for a state — compact section summary
python state_science_standards_system.py state WA
# Output: Pages: Sections: K:4-7 | 1:8-11 | 2:12-16 | ...

# Filter by grade — shows grade-specific pages with confidence
python state_science_standards_system.py state WA 5
# Output: Pages: pp. 27-53 (confidence: high)

# Show detailed grade sections
python state_science_standards_system.py sections WA
python state_science_standards_system.py sections WA 5
python state_science_standards_system.py sections WA --show-confidence
```

### Programmatic Access

```python
import json

data = json.load(open("data/states.json"))
wa_doc = data["WA"]["documents"][0]
gs = wa_doc.get("grade_sections", {})

# Get page ranges for grade 5
grade5 = gs.get("5", {})
for start, end in grade5.get("page_ranges", []):
    print(f"Grade 5: pages {start}–{end}")
    print(f"Confidence: {grade5['confidence']}")
    print(f"Needs review: {grade5['needs_review']}")
```

## Current Coverage

As of 2026-02-15:

- **Total documents:** 93
- **With grade_sections:** 52 (56%)
- **Without section data (null page_range):** 41 (44%) — single-grade or no data

**Confidence distribution (238 grade entries across 52 documents):**
- `high`: 144 (60%) — manual downloads, MCP tools, manual verification
- `medium`: 94 (39%) — remote automated extraction
- `low`: 0 (0%)
- `needs_review`: 3 (1%) — NJ grade 5, WV grades 1 and 4

**States with full K-12 grade_sections:** AL, AZ, HI, MA, OH, OK, SC, TN, WY
**States with partial grade_sections:** WA (K-5, 9-12), IA, NV, WI, WV, ...
**States with no section data (empty):** CT, DE, FL, GA, IN, KS, LA, MD, ME, MO, NC, NH, NM, RI, VA, VT, MS

## Future Enhancements

1. **Remove page_range** (deprecated): After Q2 2026 transition period
2. **Fill missing 17 states**: CT, DE, FL, GA, IN, KS, LA, MD, ME, MO, NC, NH, NM, RI, VA, VT, MS need grade_sections data
3. **Upgrade medium → high**: Re-extract with verification for 94 medium-confidence grades
4. **Add section_ids**: Map standards sections to specific identifiers for direct linking
5. **TX grades 9-12**: Complete Texas high school TEKS section data

## Related Scripts

- `scripts/migration/migrate_to_grade_sections.py` - Migrate page_range to grade_sections
- `scripts/migration/extraction_methods.json` - Per-state extraction method registry
- `scripts/validation/validate_page_ranges.py` - Validate page ranges + confidence quality
- `scripts/parsing/extract_grade_ranges.py` - Extract page ranges from PDFs
- `parse_by_page_range.py` - Efficient grade-specific parsing using page ranges
