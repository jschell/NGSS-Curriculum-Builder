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
| `page_range` | str \| null | **Grade-specific page ranges** (NEW) | `"K:16-18, 1:19-20, 2:21-26"` or `null` |
| `notes` | str \| null | Additional notes about the document | "Based on Framework for K-12 Science Education" |
| `url_source` | str \| null | Where URL was found | "https://www.alabamaachieves.org/acad-standards/" |
| `last_verified` | str \| null | Last URL verification date (YYYY-MM-DD) | "2026-02-04" |

### page_range Field (NEW)

The `page_range` field stores grade-specific page ranges for multi-grade documents. This helps users navigate to specific grade content within large PDFs.

**Format:** Comma-separated list of grade:range pairs

**Example:**
```json
"page_range": "K:16-18, 1:19-20, 2:21-26, 3:27-31, 4:32-36, 5:37-44"
```

**Structure:**
- Each entry: `<grade>:<start_page>-<end_page>`
- Entries separated by comma (`,`)
- Grades can be: `K`, `1`, `2`, ..., `12`
- Page numbers are 1-indexed (first page = page 1)

**When to use:**
- **Use page_range** for multi-grade documents where different grades appear on different page ranges
- **Use null** for:
  - Single-grade documents (entire document is for one grade)
  - Documents without clear grade-based organization
  - Documents where grades are interleaved throughout

**Examples:**

1. **Multi-grade K-8 document:**
   ```json
   {
     "title": "Ohio's Learning Standards for Science",
     "grade_levels": ["K", "1", "2", "3", "4", "5", "6", "7", "8"],
     "page_range": "K:17-32, 1:33-47, 2:48-62, 3:63-86, 4:87-106, 5:107-124, 6:125-152, 7:153-180, 8:181-387"
   }
   ```

2. **Single-grade document (page_range = null):**
   ```json
   {
     "title": "Kindergarten Science TEKS",
     "grade_levels": ["K"],
     "page_range": null
   }
   ```

3. **Complete K-12 with only K extracted:**
   ```json
   {
     "title": "Hawaii NGSS Standards K-12",
     "grade_levels": ["K", "1", "2", ..., "12"],
     "page_range": "K:3-533"
   }
   ```

**Note:** The example above shows a case where only Kindergarten page range was extracted from the table of contents. Other grades (1-12) may exist but weren't automatically extracted.

## Using page_range

### CLI Display

The CLI automatically displays page_range when viewing state information:

```bash
python state_science_standards_system.py state OH
```

Output includes:
```
1. Ohio's Learning Standards for Science and Model Curriculum
   URL: https://education.ohio.gov/...
   Covers Grades: K, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12
   Format: PDF
   Pages: K:17-32, 1:33-47, 2:48-62, 3:63-86, ...
```

### Efficient Parsing

The `parse_by_page_range.py` script demonstrates how to use page_range for efficient grade-specific parsing:

```bash
# Parse only Kindergarten pages (16-18) instead of entire 120-page PDF
python parse_by_page_range.py AL K
```

This approach:
- Downloads only the specified pages (faster)
- Reduces processing time
- Provides grade-specific content extraction

### Parsing page_range String

To parse the page_range string programmatically:

```python
def parse_page_range(page_range_str: str) -> dict:
    """Parse page_range string into structured format"""
    if not page_range_str:
        return {}

    result = {}
    pairs = page_range_str.split(',')

    for pair in pairs:
        grade, range_str = pair.strip().split(':')
        start, end = range_str.split('-')
        result[grade] = (int(start), int(end))

    return result

# Example
ranges = parse_page_range("K:16-18, 1:19-20")
# returns: {"K": (16, 18), "1": (19, 20)}
```

## Current Coverage

As of 2026-02-05:

- **Total documents:** 80
- **With page_range:** 14 (17.5%)
- **Single-grade (null):** 30 (37.5%)
- **URL errors (cannot extract):** 36 (45%)

**States with page_range data:**
- Alabama (K-8): 9 grades extracted
- Idaho (K-5): 6 grades extracted
- New Jersey K-5: 6 grades extracted
- Ohio (K-8): 9 grades extracted
- Oklahoma (K-8): 9 grades extracted
- Hawaii, Iowa, Mississippi, Montana (2 docs), North Dakota, Pennsylvania, South Dakota, Utah: Kindergarten only

## Future Enhancements

1. **Increase coverage:** Re-run extraction when more URLs are fixed
2. **Enhanced patterns:** Add patterns for "High School Biology", "Chemistry", etc.
3. **Larger TOC search:** Expand from 30 to 50 pages to find more grades
4. **Manual review:** Manually verify Kindergarten-only extractions for missing grades
5. **Integration:** Integrate page_range-based parsing into main parser workflow

## Related Scripts

- `scripts/extract_page_ranges.py` - Extract page ranges from PDFs
- `scripts/merge_page_ranges.py` - Merge extracted ranges into states.json
- `parse_by_page_range.py` - Efficient grade-specific parsing using page_range
