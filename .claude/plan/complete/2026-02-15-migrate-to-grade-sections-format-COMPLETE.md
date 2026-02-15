# Plan: Migrate to grade_sections Metadata Format

**Status:** Active
**Priority:** Medium
**Estimated Time:** 2-3 hours
**Dependencies:** cleanup-messy-page-ranges.md (complete), extract-remaining-23-states.md (complete 2026-02-15)

## Overview

Migrate from the simple `page_range` dictionary format to the documented `grade_sections` metadata structure with confidence scoring, section IDs, and review flags. This provides better data quality tracking and supports more complex document structures.

## Problem Statement

Current format is simple but lacks metadata:
```json
{
  "page_range": {
    "K": "4-7",
    "1": "8-11"
  }
}
```

Documented format provides richer metadata:
```json
{
  "grade_sections": {
    "K": {
      "page_ranges": [[4, 7]],
      "section_ids": [],
      "confidence": "high",
      "notes": "Extracted via text search",
      "needs_review": false
    }
  }
}
```

## Prerequisites

- [x] All states have clean page_range data (from cleanup and extraction plans)
- [x] StandardsDocument dataclass supports grade_sections field
- [x] CLI can read grade_sections format
- [ ] Migration script created and tested

## Implementation Steps

### Step 1: Create Migration Script (45 min)

**Goal:** Automated conversion from page_range to grade_sections

**Actions:**
1. Create `scripts/migration/migrate_to_grade_sections.py`
2. Implement conversion logic:
   - Parse page_range string format (e.g., "4-7" → [[4, 7]])
   - Handle multi-range format (e.g., "4-7, 8-11" → [[4, 7], [8, 11]])
   - Assign confidence levels:
     - "high" for manually verified extractions
     - "medium" for automated with validation
     - "low" for automated without validation
   - Preserve extraction method in notes
   - Set needs_review based on data quality
3. Add dry-run mode for testing
4. Create backup before migration

**Script structure:**
```python
#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.10"
# dependencies = ["pydantic>=2.5.0"]
# ///

def convert_page_range_to_sections(page_range_dict, extraction_method="automated"):
    """Convert simple page_range dict to grade_sections format."""
    sections = {}
    for grade, range_str in page_range_dict.items():
        if grade == "_all":
            continue

        # Parse range string
        page_ranges = parse_range_string(range_str)

        sections[grade] = {
            "page_ranges": page_ranges,
            "section_ids": [],
            "confidence": determine_confidence(extraction_method, range_str),
            "notes": f"Extracted via {extraction_method}",
            "needs_review": needs_manual_review(page_ranges)
        }

    return sections
```

**Test:**
```bash
cd scripts/migration
uv run migrate_to_grade_sections.py --dry-run
# Should show preview of conversion
```

**Commit:** `feat(migration): create page_range to grade_sections migration script`

### Step 2: Tag Extraction Methods in Current Data (30 min)

**Goal:** Track how each state's data was extracted for confidence scoring

**Actions:**
1. Review git history for extraction commits
2. Create mapping of states to extraction methods:
   - "toc_extraction": WY
   - "manual_download": TN, AZ, SC
   - "remote_automated": AL, AR, CT, DE, GA, ID, KY, MT, NC, OK, PA
   - "mcp_tools": MI, WA
   - "manual_verified": States re-extracted in cleanup phase
3. Add extraction method metadata to states.json temporarily
4. Will be used by migration script for confidence assignment

**Commit:** `docs(migration): tag states with extraction methods`

### Step 3: Run Migration in Dry-Run Mode (15 min)

**Goal:** Validate migration without modifying data

**Actions:**
1. Run migration script with --dry-run flag
2. Review output for each state
3. Check that:
   - All page ranges parsed correctly
   - Confidence levels assigned appropriately
   - No data loss during conversion
   - needs_review flagged for uncertain data
4. Save dry-run output as migration preview

**Test:**
```bash
cd scripts/migration
uv run migrate_to_grade_sections.py --dry-run > migration_preview.txt
cat migration_preview.txt
# Review all conversions
```

**Commit:** `docs(migration): generate migration preview for review`

### Step 4: Execute Migration (15 min)

**Goal:** Convert all page_range data to grade_sections format

**Actions:**
1. Backup current states.json: `cp data/states.json data/states.json.backup`
2. Run migration script without dry-run:
   ```bash
   cd scripts/migration
   uv run migrate_to_grade_sections.py --execute
   ```
3. Verify migration success:
   - Check states.json file size (should be larger)
   - Validate JSON structure
   - Count grade_sections vs old page_range
4. Keep both formats temporarily for transition period

**Migration approach:**
- Add grade_sections alongside page_range (don't remove yet)
- Allows gradual transition
- CLI reads grade_sections first, falls back to page_range

**Test:**
```bash
python -c "import json; data=json.load(open('data/states.json')); print(sum(1 for s in data.values() for d in s['documents'] if d.get('grade_sections')))"
# Should equal number of states with page_range data
```

**Commit:** `feat(migration): migrate all page_range data to grade_sections format`

### Step 5: Update CLI to Use grade_sections (30 min)

**Goal:** Make CLI prefer grade_sections over page_range

**Actions:**
1. Update `state_science_standards_system.py`:
   - Modify `get_grade_page_range()` to check grade_sections first
   - Fall back to page_range if grade_sections not available
   - Display confidence level in output
   - Show section_ids if present
2. Update `sections` command to show metadata
3. Add `--show-confidence` flag for verbose output

**Example output:**
```
Washington (WA) - GRADE-SPECIFIC SECTIONS

Grade K sections:
  Document: Washington State K-12 Science Learning Standards
  URL: https://...
  Pages: 4-7
  Confidence: High ✓
  Method: Manual verification
```

**Test:**
```bash
python state_science_standards_system.py sections WA
python state_science_standards_system.py sections WA --show-confidence
python state_science_standards_system.py state TN 5
```

**Commit:** `feat(cli): update to use grade_sections with confidence display`

### Step 6: Add Confidence Level Validation (30 min)

**Goal:** Automated quality checks based on confidence levels

**Actions:**
1. Update `scripts/validation/validate_page_ranges.py`
2. Add confidence-based checks:
   - "low" confidence → flag for manual review
   - Missing confidence → default to "medium"
   - "high" confidence → skip some validation checks
3. Generate quality report by confidence level
4. Suggest states for re-extraction based on confidence

**Test:**
```bash
cd scripts/validation
uv run validate_page_ranges.py --confidence-report
# Should show breakdown by confidence level
```

**Commit:** `feat(validation): add confidence-level quality checks`

### Step 7: Documentation & Deprecation Plan (20 min)

**Goal:** Update docs and plan page_range deprecation

**Actions:**
1. Update README.md with grade_sections structure
2. Update DATA_SCHEMA.md with full field documentation
3. Mark page_range as deprecated in documentation
4. Set timeline for page_range removal (e.g., after next major release)
5. Update features.txt with completion status

**Deprecation plan:**
- Keep both formats for 2-3 months
- Remove page_range in next major version
- Update all scripts to use grade_sections only

**Commit:** `docs(schema): document grade_sections format and deprecation plan`

## Success Criteria

- [ ] Migration script created and tested
- [ ] All states with page_range data converted to grade_sections
- [ ] CLI uses grade_sections format
- [ ] Confidence levels assigned to all extractions
- [ ] Validation script checks confidence levels
- [ ] Documentation updated
- [ ] Both formats coexist during transition period

## Rollback Plan

If migration causes issues:
1. Restore from data/states.json.backup
2. Keep page_range as primary format
3. Make grade_sections optional enhancement
4. Continue using simple format if complex format problematic

## Data Quality Improvements

**Before (simple format):**
- Just page ranges
- No quality indicators
- No extraction method tracking
- Hard to identify issues

**After (rich metadata):**
- Page ranges + confidence
- Extraction method documented
- Manual review flags
- Section IDs for complex structures
- Better validation capabilities

## Notes

- Migration is additive: both formats coexist during transition
- CLI should handle both formats gracefully
- Focus on data quality improvement, not breaking changes
- Confidence levels help prioritize future work
- section_ids support complex document structures (by topic, by subject)

## Related Work

- Current format uses simple page_range dict
- Documented format is grade_sections (see DATA_SCHEMA.md)
- StandardsDocument dataclass already supports grade_sections
- This migration aligns code with documentation
