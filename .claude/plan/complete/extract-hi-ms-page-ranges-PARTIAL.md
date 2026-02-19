# Plan: Re-extract Hawaii and Mississippi Page Ranges

**Status:** Complete (partial — HI done, MS blocked)
**Completed:** 2026-02-15
**Priority:** High
**Estimated Time:** 30-45 minutes
**Dependencies:** None (can run independently)

## Overview

Hawaii (HI) and Mississippi (MS) had page_range data that was corrected to `null` during the 2026-02-11 cleanup session (plain-string values were invalid format). They need fresh extraction since both have combined K-12 PDFs that should yield real page ranges.

## Problem Statement

- **Root cause:** The cleanup plan (`2026-02-11-cleanup-messy-page-ranges-COMPLETE.md`) found HI and MS had plain-string `page_range` values instead of the expected dict format. These were set to `null` as a data type fix — but the underlying page ranges were never re-extracted.
- **Current state:** Both states show `page_range: None` for their primary documents
- **Both states have working URLs** with combined K-12 PDFs that should be parseable

### Hawaii
- **Document:** Hawaii NGSS Standards K-12
- **URL:** `https://manoa.hawaii.edu/sealearning/sites/default/files/NGSSReduced.pdf`
- **Format:** PDF
- **Expected:** Multi-grade document, should have K-12 grade sections

### Mississippi
- **Document:** 2018 MS College- and Career-Readiness Standards for Science
- **URL:** `https://www.mdek12.org/sites/default/files/documents/Secondary%20Ed/2018-ms_ccrs-science_final.pdf`
- **Format:** PDF
- **Expected:** Multi-grade document, should have K-12 grade sections

## Prerequisites

- [x] URLs confirmed in states.json
- [x] pypdf available via UV inline deps
- [x] Extraction scripts in scripts/parsing/
- [x] Proven extraction patterns in docs/LESSONS_LEARNED.md

## Implementation Steps

### Step 1: Attempt remote automated extraction (10 min)

**Goal:** Try the fastest method first — direct download and parse

**Actions:**
1. Attempt to fetch and parse HI PDF:
   ```bash
   uv run --with pypdf,httpx python -c "
   import httpx, pypdf, io
   r = httpx.get('https://manoa.hawaii.edu/sealearning/sites/default/files/NGSSReduced.pdf', follow_redirects=True, timeout=30)
   print(f'HI: {r.status_code}, {len(r.content)} bytes')
   if r.status_code == 200:
       pdf = pypdf.PdfReader(io.BytesIO(r.content))
       print(f'Pages: {len(pdf.pages)}')
       for i in range(min(8, len(pdf.pages))):
           text = pdf.pages[i].extract_text()[:300]
           print(f'--- Page {i+1} ---')
           print(text)
   "
   ```
2. Repeat for MS PDF:
   ```bash
   uv run --with pypdf,httpx python -c "
   import httpx, pypdf, io
   r = httpx.get('https://www.mdek12.org/sites/default/files/documents/Secondary%20Ed/2018-ms_ccrs-science_final.pdf', follow_redirects=True, timeout=30)
   print(f'MS: {r.status_code}, {len(r.content)} bytes')
   if r.status_code == 200:
       pdf = pypdf.PdfReader(io.BytesIO(r.content))
       print(f'Pages: {len(pdf.pages)}')
       for i in range(min(8, len(pdf.pages))):
           text = pdf.pages[i].extract_text()[:300]
           print(f'--- Page {i+1} ---')
           print(text)
   "
   ```
3. If either returns 403/404, note it and proceed to Step 2 (manual download)

**Expected outcomes:**
- Success (200 + PDF parseable): proceed to grade extraction
- 403 Forbidden: need manual browser download (Step 2 fallback)
- 404 Not Found: need URL research (separate concern)

### Step 2: Extract grade-level page ranges (15 min)

**Goal:** Find grade boundaries in each PDF

**Actions for each state:**
1. Search PDF text for grade markers using these patterns (in order of specificity):
   - `"Kindergarten"`, `"Grade 1"` through `"Grade 12"`
   - `"Grade K"`, `"Grade One"` through `"Grade Twelve"`
   - `"K-2"`, `"3-5"`, `"6-8"`, `"9-12"` (grade bands)
   - State-specific: `"Biology"`, `"Chemistry"`, `"Physics"` (high school subjects)
2. Record the page number where each grade section starts
3. Calculate end pages (start of next grade minus 1)
4. Build `page_range` dict

**Extraction script pattern:**
```python
import pypdf, re

def extract_grades(pdf_path_or_bytes):
    pdf = pypdf.PdfReader(pdf_path_or_bytes)
    grades = {}
    patterns = [
        (r'\bKindergarten\b', 'K'),
        (r'\bGrade\s+1\b', '1'),
        (r'\bGrade\s+2\b', '2'),
        # ... through Grade 12
        (r'\bGrade\s+12\b', '12'),
    ]
    for page_num, page in enumerate(pdf.pages):
        text = page.extract_text() or ''
        for pattern, grade in patterns:
            if re.search(pattern, text) and grade not in grades:
                grades[grade] = page_num + 1  # 1-indexed
    return grades
```

3. Calculate page ranges from start pages:
   - Sort grades by page number
   - End page = next grade's start page - 1 (or total pages for last grade)
   - Format as `"start-end"` strings

**Hawaii-specific notes:**
- NGSS-based, likely organized by Disciplinary Core Ideas + grade
- May use Performance Expectations (PE) numbering: K-PS2-1, 1-LS1-1, etc.
- "Reduced" in filename may mean abbreviated — could be shorter than typical

**Mississippi-specific notes:**
- "College- and Career-Readiness Standards" — Mississippi's own framework
- 2018 document — may have K-12 comprehensive coverage
- Check for grade bands vs individual grades

### Step 3: Apply to states.json and validate (10 min)

**Goal:** Update both states and confirm data integrity

**Actions:**
1. Update HI document's `page_range` in `data/states.json`
2. Update MS document's `page_range` in `data/states.json`
3. Run validation:
   ```bash
   python state_science_standards_system.py state HI
   python state_science_standards_system.py state MS

   # Data integrity
   python -c "import json; data=json.load(open('data/states.json')); print(len(data))"
   # Expected: 51
   ```
4. Verify page ranges look reasonable (no single-page grades, no overlaps)

**Commit:** `fix(data): re-extract HI and MS page ranges (cleaned to null in prior session)`

## Fallback: Manual Download

If remote fetch fails (403/404), use this procedure:

1. Open PDF URL in Chrome
2. Download via browser's PDF viewer download button
3. Save to project root as `cached_hi.pdf` or `cached_ms.pdf`
4. Parse locally with pypdf
5. Delete cached file after extraction

## Success Criteria

- [x] HI has `page_range` dict with grade sections (not null)
- [ ] MS has `page_range` dict with grade sections (not null) — BLOCKED: PDF URL 404
- [x] Both display correctly in CLI (HI verified)
- [x] Data integrity: 51 states, valid JSON
- [ ] Total states with page ranges increases from 33 to 35 — only reached 34 (HI only)

## Rollback Plan

- Previous null values in git history
- Additive change only — no risk of data loss
- Can set back to null if extraction quality is poor
