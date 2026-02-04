# Grade-Specific Section Mapping System

**Date:** 2026-02-04
**Status:** COMPLETE ✅  
**Overview:** Add grade-specific page/section mapping to state science standards tracker using UV inline dependencies

---

## Problem Statement

The current NGSS Curriculum Builder tracks which states have standards for each grade, but cannot identify specific pages or sections within documents that contain those standards. This makes it difficult for users to:
- Navigate directly to relevant sections in K-12 documents
- Extract grade-specific content programmatically
- Link curriculum materials to specific standards locations

**Current State:**
- 21 states have only complete K-12 documents (WA, AR, CT, DE, DC, HI, IL, IA, KS, KY, ME, MD, MI, NV, etc.)
- These documents span multiple grades but lack per-grade page/section mappings
- 21 other documents are already grade-specific (e.g., Texas has separate PDFs per grade)

---

## Solution Overview

Implement a comprehensive grade-specific section mapping system with:

1. **Data Structure Updates** - Add `grade_sections` field to track page ranges and section IDs per grade
2. **PDF/HTML Parser Utility** - Auto-detect grade sections in complete K-12 documents
3. **Hybrid Detection** - Auto-detect patterns with manual review flags for ambiguous cases
4. **Multiple Section Support** - Handle topic-organized docs where grades appear in multiple places
5. **UV Inline Dependencies** - Modern, self-contained script approach

---

## Technical Approach

### 1. Inline Dependency Management (UV)

Both main CLI and parser utility will use UV's inline dependency format:

```python
# /// script
# requires-python = ">=3.10"
# dependencies = ["pydantic>=2.5.0", "pypdf>=5.0.0", ...]
# ///
```

**Benefits:**
- Self-contained scripts
- No separate config files
- Easy execution: `uv run script.py`
- Clear dependency visibility

### 2. Data Model Updates (Pydantic)

Replace stdlib dataclasses with Pydantic for type safety:

```python
class GradeSection(BaseModel):
    page_ranges: List[Tuple[int, int]] = Field(default_factory=list)
    section_ids: List[str] = Field(default_factory=list)
    confidence: str = Field(default="high")
    notes: Optional[str] = None
    needs_review: bool = Field(default=False)

class StandardsDocument(BaseModel):
    # ... existing fields ...
    grade_sections: Dict[str, GradeSection] = Field(default_factory=dict)
```

**Key Features:**
- Support multiple page ranges per grade (for topic-based docs)
- Confidence scoring (high/medium/low)
- Manual review flag
- Backward compatible with existing JSON

### 3. Parser Architecture

**Libraries:**
- `pypdf>=5.0.0` - PDF text extraction
- `pikepdf>=8.0.0` - PDF metadata and structure
- `pdfplumber>=0.10.3` - Complex layout extraction
- `httpx>=0.26.0` - Async HTTP client
- `beautifulsoup4>=4.12.2` - HTML parsing
- `orjson>=3.9.0` - Fast JSON serialization

**Core Functions:**
- `detect_organization()` - Identify if PDF organized by grade or topic
- `extract_grade_sections_by_grade()` - Sequential grade extraction
- `extract_grade_sections_by_topic()` - Multi-range extraction
- `parse_all_states()` - Async batch processing
- `generate_json_patch()` - Create update files
- `generate_markdown_report()` - Human-readable documentation

**Detection Patterns (Regex):**
```python
Grade Patterns:
- r"\bKindergarten\b"
- r"\bGrade\s+3\b"
- r"\b3rd\s+Grade\b"

Topic Patterns:
- r"\bPhysical\s+Science\b"
- r"\bLife\s+Science\b"
- r"\bEarth\s+and\s+Space\s+Science\b"
```

### 4. JSON Schema Enhancement

Existing documents get `grade_sections` mapping:

```json
{
  "documents": [
    {
      "title": "Washington State K-12 Science Learning Standards",
      "grade_levels": ["K", "1", "2", "3", ...],
      "grade_sections": {
        "3": {
          "page_ranges": [[22, 28]],
          "section_ids": [],
          "confidence": "high",
          "needs_review": false
        }
      }
    }
  ]
}
```

**For topic-based documents:**
```json
{
  "grade_sections": {
    "3": {
      "page_ranges": [[18, 24], [52, 56], [89, 93]],
      "notes": "Physical Science: p18-24, Life Science: p52-56, Earth Science: p89-93",
      "confidence": "medium"
    }
  }
}
```

---

## Implementation Phases

### Phase 1: Core Data Structure Updates
**File:** `state_science_standards_system.py`

1. Add UV inline dependencies block
2. Import Pydantic and orjson
3. Define `GradeSection` and update `StandardsDocument` models
4. Add `grade_sections` field to existing dataclass (backward compatible)
5. Update `load_states_data()` to parse `grade_sections`
6. Add new CLI command: `cmd_sections(state_abbrev, grade=None)`
7. Update `get_documents_for_grade()` to include section info

### Phase 2: Create Parser Utility
**File:** `parse_standards.py` (NEW)

1. Add UV inline dependencies block
2. Import async libraries (httpx, asyncio)
3. Define Pydantic models: `GradeSection`, `DocumentParseResult`
4. Implement HTTP client with connection pooling
5. Implement PDF fetching and caching
6. Implement text extraction (pypdf + pdfplumber fallback)
7. Implement organization detection algorithm
8. Implement grade section extraction (by_grade and by_topic)
9. Implement async batch processing
10. Implement JSON patch generation
11. Implement Markdown report generation
12. Add CLI interface

### Phase 3: Testing and Validation
**Actions:**

1. Test parser on known states:
   - Washington (grade-organized, complete K-12)
   - California (has both complete and grade-specific)
   - Texas (all grade-specific, should parse cleanly)

2. Validate detection accuracy:
   - Compare auto-detected page ranges with manual spot-check
   - Verify confidence scoring logic
   - Identify edge cases for manual review

3. Generate initial patches:
   - Parse 21 states with complete K-12 documents
   - Review reports for flagged items
   - Apply patches to `data/states.json`

### Phase 4: Documentation and Examples
**Actions:**

1. Update `GRADE_FILTERING_EXPLAINED.md` with section mapping info
2. Add usage examples to README
3. Create quick start guide for parsing
4. Document manual review workflow

### Phase 5: Integration and Polish
**Actions:**

1. Update `.gitignore` to exclude cached PDFs
2. Ensure backward compatibility with existing JSON data
3. Add error handling for malformed documents
4. Optimize concurrent fetching rate limits
5. Add progress indicators for long-running parses

---

## Directory Structure

```
NGSS-Curriculum-Builder/
├── state_science_standards_system.py  # Updated with Pydantic + sections command
├── parse_standards.py                  # NEW: Parser with UV inline deps
├── data/
│   └── states.json                     # Updated with grade_sections
├── reports/                           # NEW: Generated analysis reports
│   └── grade_sections_analysis.md
├── patches/                           # NEW: JSON update patches
│   └── grade_sections_patch.json
├── cached/                            # NEW: Downloaded PDFs/HTMLs
│   ├── WA_abc123.pdf
│   └── CA_def456.pdf
├── .claude/
│   └── plan/
│       └── active/
│           └── 2026-02-04-grade-specific-section-mapping.md
└── .gitignore                         # Updated to exclude cached/
```

---

## Usage Examples

### Parse States
```bash
# Parse specific states
uv run parse_standards.py parse --states WA,CA,OR

# Parse all states
uv run parse_standards.py parse --all

# Generate report from existing patch
uv run parse_standards.py report patches/grade_sections.json
```

### Query Grade Sections
```bash
# Show Grade 3 sections for Washington
uv run state_science_standards_system.py sections WA 3

# Show all sections for a state
uv run state_science_standards_system.py sections WA

# List all states with sections data
uv run state_science_standards_system.py list
```

### Expected Output

**Query: `sections WA 3`**
```
================================================================================
Washington (WA) - GRADE-SPECIFIC SECTIONS
================================================================================

Grade 3 sections:

Document: Washington State K-12 Science Learning Standards
  URL: https://ospi.k12.wa.us/sites/default/files/...pdf
  Pages: 22-28
  Confidence: High

Document: WSSLS DCI Arrangement
  URL: https://ospi.k12.wa.us/sites/default/files/...pdf
  Pages: 18-24 (Physical Science), 52-56 (Life Science), 89-93 (Earth Science)
  Confidence: Medium
  Notes: Multiple sections due to topic organization
```

---

## Success Criteria

- [x] Pydantic models defined and backward compatible
- [x] UV inline dependencies configured in both scripts
- [x] Parser utility successfully extracts grade sections
- [x] JSON patch generation works correctly
- [x] Markdown reports generated with human-readable format
- [x] `sections` CLI command functional
- [x] Backward compatibility maintained with existing `states.json`
- [x] All 21 complete K-12 states parsed successfully
- [x] Documentation updated
- [x] Manual review workflow established

---

## Risk Mitigation

| Risk | Mitigation |
|------|------------|
| PDF parsing errors | Fallback to multiple parsers (pypdf → pdfplumber) |
| Incorrect section detection | Confidence scoring + manual review flags |
| Network timeout/failure | Connection pooling + retry logic |
| Large PDF memory issues | Page-by-page streaming extraction |
| Ambiguous patterns | Pattern scoring thresholds + hybrid approach |

---

## Implementation Summary

**All phases completed successfully:**
- ✅ Phase 1: Core Data Structure Updates (Feb 4, 2026)
- ✅ Phase 2: Parser Utility Created (Feb 4, 2026)
- ✅ Phase 3: Testing and Validation (Feb 4, 2026)
- ✅ Phase 4: Documentation and Examples (Feb 4, 2026)
- ✅ Phase 5: Integration and Polish (Feb 4, 2026)

**See `docs/IMPLEMENTATION_SUMMARY.md` for detailed completion report.**

---

**Created:** 2026-02-04
**Last Updated:** 2026-02-04 (Status updated to COMPLETE)
**Next Phase:** Data Validation - See `docs/DATA_VALIDATION_PLAN.md`
