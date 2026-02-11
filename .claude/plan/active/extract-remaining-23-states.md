# Plan: Extract Page Ranges for Remaining States

**Status:** Active — Partial progress 2026-02-11
**Priority:** High
**Estimated Time:** 2-3 hours remaining
**Dependencies:** None

## Progress Summary (2026-02-11)

**Started with**: 21 states needing page_range data (HI and MS were already done, not 23)
**Completed this session**:
- NE: Full K-8 + HS-by-subject extracted via browser TOC
- DC: Full grade-band structure extracted via browser TOC
- CO: Grade-band page ranges applied from CDE documentation (P-5/6-8/9-12)
- 18 broken/wrong URLs fixed for CT, GA, IN, KS, LA, MD, ME, MN, MO, NC, NH, NM, RI, VA, VT, WV, DE notes

**Current state**: 33/51 states have page_range data (up from 30)

## Remaining Work

### States Without page_range (18) — Classified by Blocker

**Direct NGSS adoption (no single K-12 PDF):**
- CT, KS, MD, NH, NM, RI, VT — Use NGSS directly; page_ranges N/A

**HTML/interactive standards (no extractable PDF):**
- FL — CPALMS interactive database
- GA — Grade-band PDFs per course (K-5, 6-8, 9-12 sections)
- IN — 2023 grade/course-specific individual PDFs
- LA — Individual grade PDFs (K-12 in ZIP archive)
- ME — Grade-band PDFs (K-2, 3-5, 6-8, 9-12)
- MO — Separate K-5 and 6-12 PDFs
- NC — 2023 grade/course-specific PDFs
- VA — Grade-specific PDFs per course
- WV — Policy 2520.3C PDF (needs browser to access)

**Needs MN PDF TOC read:**
- MN — 104-page PDF accessible but downloads automatically; needs manual read

**Needs DE structure analysis:**
- DE — Topical (not grade-organized) arrangement of NGSS

## Overview

Extract grade-level page ranges for the remaining states. Use the proven multi-phase approach: remote parsing, MCP browser tools, manual download, and TOC extraction.

## Problem Statement (Updated)

21 states still need page range extraction (HI and MS already had data):
CO, CT, DC, DE, FL, GA, IN, KS, LA, MD, ME, MN, MO, NC, NE, NH, NM, RI, VA, VT, WV

After session work (2026-02-11): 18 states remain at null page_range.

## Prerequisites

- [x] docs/LESSONS_LEARNED.md with proven extraction methods
- [x] scripts/parsing/parse_standards.py working
- [x] MCP browser tools available
- [x] Previous extraction batches completed successfully

## Implementation Steps

### Step 1: Automated Remote Parsing Attempt (60 min)

**Goal:** Extract as many states as possible with automated parser

**Actions:**
1. Run parse_standards.py on all 23 states
2. Review extraction results
3. Identify successful extractions (likely 60-70% success rate)
4. Apply successful extractions to states.json
5. Document which states failed and why

**Test:**
```bash
cd scripts/parsing
uv run parse_standards.py parse --states CO,CT,DC,DE,FL,GA,HI,IN,KS,LA,MD,ME,MN,MO,MS,NC,NE,NH,NM,RI,VA,VT,WV
```

**Expected:** ~14-16 states successfully extracted

**Commit:** `feat(extraction): automated extraction for remaining states - batch 1`

### Step 2: Research Failed URLs with MCP Tools (45 min)

**Goal:** Find working URLs for states that returned 404 or 403

**Actions:**
1. Identify states with failed HTTP requests
2. Use brave_web_search to find alternative URLs
3. Use browser_navigate to verify PDFs load
4. Take screenshots for confirmation
5. Update states.json with working URLs
6. Retry parsing with new URLs

**Test per state:**
```bash
# Research example
mcp__MCP_DOCKER__brave_web_search("Connecticut science standards 2024 PDF site:ct.gov")
browser_navigate(found_url)
browser_take_screenshot("ct_verify.png")
```

**Commit:** `fix(data): update URLs for states with 404/403 errors`

### Step 3: Manual Download for Bot-Protected Sites (60 min)

**Goal:** Extract states blocked by Cloudflare or aggressive bot detection

**Actions:**
For each bot-protected state:
1. User opens PDF in browser
2. User downloads via browser's download button
3. Save to project directory (e.g., `cached/CT_standards.pdf`)
4. Run local parsing:
   ```python
   import pypdf
   pdf = pypdf.PdfReader("cached/CT_standards.pdf")
   # Extract page ranges
   ```
5. Create clean page_range dict
6. Update states.json
7. Remove cached PDF after extraction

**Test per state:**
```bash
python state_science_standards_system.py sections CT
# Should show all extracted grades
```

**Commit after each state:** `feat(extraction): manual extraction for <STATE>`

### Step 4: TOC Extraction for Complex Structures (45 min)

**Goal:** Handle states with non-standard organization

**Actions:**
For states with complex structure (like Wyoming was):
1. Download PDF
2. Locate table of contents page
3. Extract TOC text:
   ```python
   toc_text = pdf.pages[TOC_PAGE].extract_text()
   ```
4. Parse grade levels and page numbers from TOC
5. Create structured page_range dict
6. Add notes about organization (by subject, by grade band, etc.)
7. Update states.json

**Test per state:**
```bash
python state_science_standards_system.py range <STATE>
# Should show complete coverage based on TOC structure
```

**Commit after each state:** `feat(extraction): TOC-based extraction for <STATE>`

### Step 5: Handle Special Document Structures (30 min)

**Goal:** Document states with grade-specific or multi-document structures

**Actions:**
For states like ME (separate PDFs per grade):
1. Identify document organization pattern
2. Add `special_structure` field to document metadata
3. Add detailed notes explaining structure
4. Update CLI to handle special structures appropriately
5. Document in README

**Example:**
```json
{
  "special_structure": "grade_specific_documents",
  "notes": "Each grade has separate PDF (K-ESS2.pdf, 1-LS1.pdf, etc.)"
}
```

**Commit:** `feat(data): document special structures for <STATE> standards`

### Step 6: Validation & Quality Check (30 min)

**Goal:** Ensure all 23 states have usable data

**Actions:**
1. Run validation script on all newly extracted states
2. Check for:
   - Complete K-12 coverage (or documented special structure)
   - No overlapping ranges
   - Clean, readable page range format
   - All states have at least basic coverage
3. Generate extraction summary report
4. Update features.txt and README.md

**Test:**
```bash
cd scripts/validation
uv run validate_page_ranges.py --states CO,CT,DC,DE,FL,GA,HI,IN,KS,LA,MD,ME,MN,MO,MS,NC,NE,NH,NM,RI,VA,VT,WV
# All should pass or be documented as special structure
```

**Commit:** `docs(extraction): complete remaining 23 states - 100% coverage achieved`

## Success Criteria

- [ ] All 23 states have page range data or documented special structure
- [ ] Total coverage: 51/51 states (100%)
- [ ] Automated extraction: ~60-70% success rate
- [ ] Manual methods: 100% success rate
- [ ] Validation passing for all states
- [ ] README updated with final statistics

## Rollback Plan

If issues discovered:
1. Backup states.json before each batch
2. Can revert individual states if extraction incorrect
3. Mark problematic states with `needs_review: true`
4. Can defer complex special structures for later manual review

## Extraction Method Priority

**Phase 1: Remote Automated (try first)**
- Fastest method
- ~60-70% success rate
- Zero manual work

**Phase 2: MCP Browser Tools (for 404/403)**
- Find alternative URLs
- Bypass bot protection for viewing
- Visual confirmation before extraction

**Phase 3: Manual Download (for aggressive protection)**
- 100% success rate
- User downloads via browser
- Parse locally with pypdf

**Phase 4: TOC Extraction (for complex structures)**
- Last resort for non-standard organization
- Extract from table of contents
- Manual page mapping

## Notes

- Prioritize speed: try automated first
- Document failures: helps identify patterns
- Commit frequently: each state or small batch
- Test immediately: catch issues early
- Use proven patterns from docs/LESSONS_LEARNED.md

## Related Work

- Previous extraction batches: 28 states completed
- docs/LESSONS_LEARNED.md: Method documentation
- cleanup-messy-page-ranges.md: Cleanup plan for existing data
- Goal: Complete 51/51 states (100% coverage)
