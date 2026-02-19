# Plan: Complete Texas High School Standards (Grades 9-12)

**Status:** Active
**Priority:** Medium
**Estimated Time:** 1-2 hours
**Dependencies:** None (can run independently)

## Overview

Texas is the only state with an explicitly known data gap: grades 9-12 are missing from the dataset. Texas uses the TEKS (Texas Essential Knowledge and Skills) framework with separate documents per grade level and per high school subject. This plan researches, catalogs, and adds the missing high school science standards documents.

## Problem Statement

- Texas currently covers **K-8 only** in `states.json`
- Texas high school science uses subject-specific TEKS documents:
  - Biology
  - Chemistry
  - Physics
  - Integrated Physics and Chemistry (IPC)
  - Environmental Systems
  - Aquatic Science
  - Astronomy
  - Earth and Space Science
- These are separate PDFs hosted on the Texas Education Agency (TEA) website
- The state is already marked with `special_structure: "level_specific_documents"` — high school docs need to be added to this structure

## Prerequisites

- [x] Texas K-8 data already in states.json
- [x] Texas marked as `framework_based` (TEKS, not NGSS)
- [x] special_structure field already set
- [x] TEA website structure known from prior research

## Implementation Steps

### Step 1: Research current TEA high school science URLs (20 min)

**Goal:** Find the current TEKS documents for all high school science subjects

**Actions:**
1. Search for the TEA TEKS page:
   - Primary: `https://tea.texas.gov/academics/curriculum-standards/teks/texas-essential-knowledge-and-skills`
   - Science TEKS section specifically
2. Identify high school science subjects and their PDF URLs
3. For each subject, record:
   - Title (e.g., "Biology TEKS")
   - URL to PDF or HTML document
   - Format (PDF, HTML)
   - Page count (if PDF)
   - Grade level designation ("9-12" or specific course)
4. Note if TEA has switched to a new format or reorganized since last check

**Key subjects to find:**
| Subject | TEKS Chapter | Expected |
|---|---|---|
| Biology | §112.34 | Core, required |
| Chemistry | §112.35 | Core, required |
| Physics | §112.39 | Core, required |
| IPC | §112.38 | Alternative to Chem+Physics |
| Environmental Systems | §112.37 | Elective |
| Aquatic Science | §112.36 | Elective |
| Astronomy | §112.40 | Elective |
| Earth and Space Science | §112.41 | Elective |

**Test:**
```bash
# Verify at least the core subjects are found
# Should have working URLs for Biology, Chemistry, Physics at minimum
```

### Step 2: Validate discovered URLs (10 min)

**Goal:** Confirm all URLs are accessible and return correct content

**Actions:**
1. Test each URL:
   ```bash
   uv run --with httpx python -c "
   import httpx
   urls = {
       'Biology': 'URL_HERE',
       'Chemistry': 'URL_HERE',
       # ...
   }
   for name, url in urls.items():
       try:
           r = httpx.head(url, follow_redirects=True, timeout=15)
           print(f'{name}: {r.status_code} ({r.headers.get(\"content-type\", \"unknown\")})')
       except Exception as e:
           print(f'{name}: ERROR - {e}')
   "
   ```
2. Note any 403/404 errors — TEA may use Cloudflare or bot protection
3. If URLs return HTML instead of PDF, check if it's a landing page with embedded PDF viewer
4. Record final verified URLs

### Step 3: Add high school documents to states.json (20 min)

**Goal:** Add the high school science documents to Texas's data

**Actions:**
1. Decide on document representation:
   - **Option A:** One document per high school subject (Biology, Chemistry, etc.)
   - **Option B:** One combined "High School Science TEKS" entry with notes
   - **Recommended:** Option A — consistent with Texas's `level_specific_documents` structure
2. For each subject, add a document entry:
   ```json
   {
     "title": "Biology TEKS (§112.34)",
     "url": "https://...",
     "format": "PDF",
     "grades": ["9-12"],
     "page_range": null,
     "page_range_status": null,
     "notes": "High school Biology - Texas Essential Knowledge and Skills"
   }
   ```
3. Ensure the `grades` field includes appropriate grade levels
4. Keep existing K-8 documents unchanged

**Grade mapping for high school subjects:**
- Core subjects (Biology, Chemistry, Physics): grades `["9", "10", "11", "12"]`
- IPC: grades `["9", "10"]` (typically taken instead of separate Chem/Physics)
- Electives: grades `["9", "10", "11", "12"]` (available at any HS level)

**Test:**
```bash
python -c "
import json
data = json.load(open('data/states.json'))
tx = data['TX']
print(f'TX documents: {len(tx[\"documents\"])}')
for doc in tx['documents']:
    print(f'  - {doc[\"title\"][:50]} | grades: {doc.get(\"grades\")}')
"
```

### Step 4: Update CLI grade coverage display (10 min)

**Goal:** Verify Texas now shows K-12 coverage

**Actions:**
1. Run coverage check:
   ```bash
   python state_science_standards_system.py range TX
   ```
2. Should now show coverage for K-12 (previously only K-8)
3. Test grade-specific query:
   ```bash
   python state_science_standards_system.py state TX 10
   # Should show high school documents
   ```
4. If the CLI `range` command doesn't handle `"9-12"` grade ranges properly, fix the grade expansion logic

### Step 5: Extract page ranges for high school PDFs (15 min)

**Goal:** If the high school docs are multi-page PDFs, extract page ranges

**Actions:**
1. For each high school PDF that's accessible:
   ```bash
   uv run --with pypdf,httpx python -c "
   import httpx, pypdf, io
   url = 'URL_HERE'
   r = httpx.get(url, follow_redirects=True, timeout=30)
   if r.status_code == 200:
       pdf = pypdf.PdfReader(io.BytesIO(r.content))
       print(f'Pages: {len(pdf.pages)}')
       # Check for grade/topic sections
   "
   ```
2. Most TEKS documents are single-subject — `page_range` will likely be `null` (entire document is one subject)
3. If any document covers multiple grades within the subject, extract those sections
4. Update states.json with any page ranges found

**Commit:** `feat(data): add Texas high school science standards (grades 9-12)`

### Step 6: Validate and document (10 min)

**Goal:** Ensure data integrity and update project docs

**Actions:**
1. Full data integrity check:
   ```bash
   python -c "import json; data=json.load(open('data/states.json')); print(f'States: {len(data)}')"
   python -c "import json; data=json.load(open('data/states.json')); print(f'Docs: {sum(len(s[\"documents\"]) for s in data.values())}')"
   # Documents count will increase from 93
   ```
2. Run CLI tests:
   ```bash
   python state_science_standards_system.py list
   python state_science_standards_system.py state TX
   python state_science_standards_system.py range TX
   python state_science_standards_system.py search 10
   # TX should appear in grade 10 search results
   ```
3. Update CLAUDE.md known issues: remove "Texas: Only K-8, missing grades 9-12"
4. Update features.txt: move TX high school to Done

**Commit:** `docs: update project status after TX high school addition`

## Success Criteria

- [ ] At least 3 core high school subjects added (Biology, Chemistry, Physics)
- [ ] All added URLs verified accessible (or documented as blocked)
- [ ] Texas shows K-12 coverage in `range` command
- [ ] Grade 10 search includes Texas
- [ ] Data integrity preserved (51 states, valid JSON)
- [ ] CLAUDE.md known issue resolved

## Rollback Plan

- All changes are additive (new documents added)
- Can remove documents individually if URLs break
- Existing K-8 data untouched
- Git history preserves previous state

## Notes

- TEA reorganizes their website periodically — URLs may have changed since last research
- TEA may use Cloudflare bot protection — be prepared for 403 errors
- If all URLs are blocked, document the subjects/chapter numbers and mark URLs as "needs_research"
- Texas has more high school science subjects than most states due to TEKS breadth
- Focus on the 3 core subjects (Bio, Chem, Physics) if time is limited
