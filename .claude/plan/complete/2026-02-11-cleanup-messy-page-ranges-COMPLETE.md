# Plan: Clean Up 18 States with Messy Page Range Data

**Status:** COMPLETE (cleanup done; new extraction BLOCKED — see note below)
**Priority:** High
**Estimated Time:** 3-4 hours
**Completed:** 2026-02-11

## Completion Note

Cleanup portion complete. New grade extraction (Steps 3-4) is BLOCKED:
all state education PDFs return 403 Forbidden to automated access.
Extraction requires MCP browser tools or manual PDF download per docs/LESSONS_LEARNED.md.

Steps completed:
- Step 1 (validate_page_ranges.py): ✅ Done in comprehensive-validation-suite
- Step 2 (prioritize states): ✅ All target PDFs confirmed 403-blocked
- Step 5 (clean messy artifacts): ✅ Complete — 35 changes across states.json
- Step 6 (final validation): ✅ PR001 errors 2→0, all _all keys removed

What was actually fixed:
- HI, MS: plain-string page_range → null (data type corrected)
- NJ, AL, OH, OK, ID: _all multi-grade data promoted → individual grade keys
- 9 states: format field HTML→PDF (DE, DC, HI, MD, NM, GA, IN, MN + AR)
- 13 states: scattered/artifact K ranges removed
- CA, AR, IL, KY, MT, PA: cascading K ranges consolidated
**Dependencies:** None

## Overview

Clean up and re-extract page ranges for 18 states that have partial, incomplete, or messy data from automated parser artifacts. These states need manual re-extraction using proven methods (TOC extraction, manual download + parsing, or MCP browser tools).

## Problem Statement

Current data/states.json has 18 states with low-quality page range extractions:
- **Only Kindergarten extracted:** AR, CA, IL, MT, PA, TX (6 states)
- **Missing grades:** AK (only K,5), AL (only K-8), ND (only K-6), NV (spotty K,1,6,8,12)
- **Messy/overlapping ranges:** Multiple states with automated parser artifacts

These need to be re-extracted with high-quality manual methods to match the 10 states that have clean, production-ready data (AZ, SC, TN, WY, WA, MI, OK, OH, UT, OR).

## Prerequisites

- [x] Comprehensive analysis of current page range data completed
- [x] Identified 18 states needing cleanup
- [x] docs/LESSONS_LEARNED.md has proven extraction methods
- [x] Previous manual extraction experience documented

## Implementation Steps

### Step 1: Create Data Quality Validation Script (30 min)

**Goal:** Automated detection of incomplete/messy page ranges

**Actions:**
1. Create `scripts/validation/validate_page_ranges.py`
2. Implement checks:
   - Detect incomplete K-12 coverage (missing grade 8 is common)
   - Flag overlapping page ranges
   - Identify states with only K extracted
   - Check for unreasonably long page range strings (parser artifacts)
3. Generate report of issues found
4. Test on current data/states.json

**Test:**
```bash
cd scripts/validation
uv run validate_page_ranges.py
# Should identify the 18 problematic states
```

**Commit:** `feat(validation): add page range quality validation script`

### Step 2: Prioritize States by Extraction Method (15 min)

**Goal:** Group states by best extraction approach

**Actions:**
1. Review each of the 18 states' documents
2. Categorize by method:
   - **TOC extraction:** States with clear table of contents
   - **Manual download + parsing:** 403 Forbidden or bot-protected
   - **Remote parsing with fixes:** Parser needs better pattern matching
3. Document extraction strategy in progress.txt
4. Create extraction order (easiest first)

**Output:** Priority list in progress.txt

**Commit:** `docs(extraction): prioritize 18 states for cleanup`

### Step 3: Re-extract High Priority States (6 states, 90 min)

**Goal:** Clean re-extraction of states with only K data

**Target States:** AR, CA, IL, MT, PA, TX

**Actions:**
For each state:
1. Download PDF manually if needed (bypass bot protection)
2. Identify document structure (by grade or by topic)
3. Use appropriate extraction method:
   - TOC extraction if available
   - Text search with improved patterns
   - Manual page counting if needed
4. Create clean page_range dict with all K-12 grades
5. Update states.json
6. Validate with CLI: `python state_science_standards_system.py sections <STATE>`

**Test per state:**
```bash
python state_science_standards_system.py state AR
python state_science_standards_system.py sections AR
# Should show all grades K-12 with clean page ranges
```

**Commit after each state:** `fix(data): re-extract <STATE> page ranges - complete K-12`

### Step 4: Fix States with Missing Grades (4 states, 60 min)

**Goal:** Complete grade coverage for partially extracted states

**Target States:** AK (add 1-12), AL (add 9-12), ND (add 7-12), NV (fill gaps)

**Actions:**
For each state:
1. Read existing page_range data
2. Identify missing grades
3. Use same PDF/document as before
4. Extract only the missing grade ranges
5. Merge with existing data
6. Validate complete K-12 coverage

**Test per state:**
```bash
python state_science_standards_system.py range AK
# Should show complete K-12 coverage visualization
```

**Commit after each state:** `fix(data): complete <STATE> page ranges - add missing grades`

### Step 5: Clean Up Messy Automated Artifacts (8 states, 60 min)

**Goal:** Re-extract states with overlapping or messy ranges

**Target States:** IA, ID, KY, MA, NJ, NY, WI, and any others flagged

**Actions:**
For each state:
1. Review current page_range data
2. Identify specific issues (overlaps, duplicates, unrealistic ranges)
3. Re-extract from scratch using manual methods
4. Ensure clean, non-overlapping ranges
5. Update states.json
6. Validate with validation script

**Test per state:**
```bash
cd scripts/validation
uv run validate_page_ranges.py --state MA
# Should pass all validation checks
```

**Commit after each state:** `fix(data): clean up <STATE> page ranges - remove artifacts`

### Step 6: Final Validation & Documentation (30 min)

**Goal:** Verify all 18 states now have high-quality data

**Actions:**
1. Run full validation script on all 18 states
2. Generate before/after comparison report
3. Update features.txt with completion status
4. Update README.md with new coverage statistics
5. Document any remaining edge cases or special structures

**Test:**
```bash
cd scripts/validation
uv run validate_page_ranges.py --verbose
# All 18 states should pass quality checks

python state_science_standards_system.py list
# Should show 28 states with clean page range data
```

**Commit:** `docs(cleanup): complete page range cleanup - 18 states fixed`

## Success Criteria

- [ ] All 18 states have complete K-12 or K-8 grade coverage
- [ ] No overlapping page ranges
- [ ] No parser artifacts or messy data
- [ ] Validation script passes for all 18 states
- [ ] Total states with clean page ranges: 28 (up from 10)
- [ ] Documentation updated with new coverage stats

## Rollback Plan

If issues discovered during cleanup:
1. Keep backup of original states.json
2. Can revert individual states if re-extraction fails
3. Original messy data preserved in git history
4. Can fall back to "needs manual review" flag if uncertain

## Notes

- Focus on quality over speed - manual methods are proven reliable
- Use docs/LESSONS_LEARNED.md patterns for each extraction
- Commit after each state to enable easy rollback
- Test each state immediately after extraction
- Document any new document structures discovered

## Related Work

- Previous manual extraction: 18 states, 94% success rate
- docs/LESSONS_LEARNED.md: Complete method documentation
- scripts/parsing/parse_standards.py: Automated parser (for reference)
- 10 states already have production-ready data
