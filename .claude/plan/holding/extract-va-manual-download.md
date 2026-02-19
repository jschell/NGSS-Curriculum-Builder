# Plan: Extract Virginia Page Ranges via Manual Download

**Status:** Active
**Priority:** High
**Estimated Time:** 20-30 minutes
**Dependencies:** None (can run independently)

## Overview

Virginia is the only state where a combined K-12 PDF exists but page ranges couldn't be extracted due to Akamai CDN bot protection. The PDF must be manually downloaded via browser, then parsed locally.

## Problem Statement

- **State:** Virginia (VA)
- **Document:** 2018 Virginia Science Standards of Learning (44 pages)
- **URL:** `https://www.doe.virginia.gov/home/showpublisheddocument/23723/638043832157670000`
- **Blocker:** Akamai CDN serves an HTML wrapper (`<embed src='about:blank'>`) to automated tools. The actual PDF bytes are only accessible via Chrome's native PDF viewer.
- **Archive.org:** Returns 520 (Akamai blocks all crawlers)

## Prerequisites

- [x] URL confirmed working in browser (documented in extraction plan)
- [x] pypdf available via UV inline deps
- [x] Proven extraction workflow in docs/LESSONS_LEARNED.md

## Implementation Steps

### Step 1: Manual browser download (5 min)

**Goal:** Get the PDF file onto local disk

**Actions:**
1. Open URL in Chrome: `https://www.doe.virginia.gov/home/showpublisheddocument/23723/638043832157670000`
2. Wait for PDF to render in Chrome's built-in viewer
3. Click the download icon (↓) in the PDF viewer toolbar
4. Save as `cached_va_2018.pdf` in the project root directory
5. Verify file size is reasonable (should be ~500KB-2MB for a 44-page PDF)

**Test:**
```bash
ls -la cached_va_2018.pdf
# Should exist and be > 100KB
file cached_va_2018.pdf
# Should report "PDF document"
```

### Step 2: Extract page ranges from PDF (10 min)

**Goal:** Parse the TOC and find grade-level page boundaries

**Actions:**
1. Run the existing extraction script:
   ```bash
   uv run --with pypdf python scripts/parsing/extract_grade_ranges.py cached_va_2018.pdf
   ```
2. If the script doesn't find grades, fall back to manual text search:
   ```python
   import pypdf
   pdf = pypdf.PdfReader("cached_va_2018.pdf")
   # Check TOC pages (typically pages 2-5)
   for i in range(min(10, len(pdf.pages))):
       text = pdf.pages[i].extract_text()
       print(f"--- Page {i+1} ---")
       print(text[:500])
   ```
3. Identify grade markers: look for "Kindergarten", "Grade 1" through "Grade 8", plus high school subjects
4. Record start and end page for each grade section
5. Create a `page_range` dict:
   ```json
   {
     "K": "X-Y",
     "1": "X-Y",
     "2": "X-Y",
     ...
     "9-12": "X-Y"
   }
   ```

**Virginia-specific notes:**
- 44 pages total — expect compact grade sections (2-4 pages each)
- Virginia uses "Standards of Learning" (SOL) naming
- May organize by grade bands (K-2, 3-5, 6-8, 9-12) rather than individual grades
- High school likely organized by subject (Biology, Chemistry, Physics, Earth Science)

**Test:**
```bash
python -c "
import json
data = json.load(open('data/states.json'))
va = data['VA']
for doc in va['documents']:
    print(doc.get('page_range'))
"
# Should show extracted grade ranges
```

### Step 3: Apply to states.json and validate (5 min)

**Goal:** Update the data file and confirm CLI works

**Actions:**
1. Update VA's document entry in `data/states.json` with the extracted `page_range`
2. Set `verified` date to today
3. Run CLI tests
4. Clean up: remove `cached_va_2018.pdf` from project root

**Test:**
```bash
python state_science_standards_system.py state VA
# Should display page ranges

python state_science_standards_system.py state VA 5
# Should show grade 5 section info

python -c "import json; data=json.load(open('data/states.json')); print(len(data))"
# Should still be 51
```

**Commit:** `feat(extraction): extract VA page ranges via manual download`

### Step 4: Clean up (2 min)

**Actions:**
1. Delete `cached_va_2018.pdf`
2. Verify git status is clean except for states.json change

```bash
rm cached_va_2018.pdf
git status
```

## Success Criteria

- [ ] VA has complete page_range data in states.json
- [ ] Grade coverage spans K through high school
- [ ] CLI displays VA page ranges correctly
- [ ] cached PDF removed from project
- [ ] Data integrity preserved (51 states, JSON valid)

## Rollback Plan

- VA's previous data (null page_range) is in git history
- Can revert states.json change with `git checkout HEAD -- data/states.json`
- No other files affected
