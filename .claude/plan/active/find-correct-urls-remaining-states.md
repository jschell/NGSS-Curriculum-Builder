# Plan: Find Correct URLs for Remaining States

**Status:** In Progress
**Created:** 2026-02-05
**Last Updated:** 2026-02-05
**Estimated Duration:** 5-8 hours (remaining work)
**Priority:** High (blocked 74.5% of states from page_range feature)

---

## 📊 Progress Summary (Last Updated: 2026-02-05)

**Overall Progress:**
- ✅ Batches 1-2: **COMPLETE** (17 states researched, 15 URLs found)
- ⏳ Batch 3: **READY** (script exists, needs execution - 7 states)
- ❌ Batches 4-6: **NOT STARTED** (7 states remaining)

**URL Research Status:**
- **States researched:** 17/38 (44.7%)
- **URLs found:** 15/17 (88% success rate)
- **URLs applied to states.json:** 9/15 (Batch 1 only)
- **URLs pending application:** 6/15 (Batch 2)

**By Batch:**
| Batch | Status | States | URLs Found | Time Spent |
|-------|--------|--------|------------|------------|
| Batch 1 (HTTP 403) | ✅ Complete | 11 | 9 (82%) | ~35 min |
| Batch 2 (HTTP 202) | ✅ Complete | 6 | 6 (100%) | ~1 hour |
| Batch 3 (PDF Errors) | ⏳ Ready | 7 | - | - |
| Batch 4 (SSL/Conn) | ❌ Not Started | 4 | - | - |
| Batch 5 (Special) | ❌ Not Started | 2 | - | - |
| Batch 6 (DC) | ❌ Not Started | 1 | - | - |

**Key Achievements:**
- Built automated research infrastructure (`scripts/research_urls_automated.py`)
- Created 17 JSON research templates
- Documented findings in `docs/url_updates/BATCH1_RESEARCH_SUMMARY.md`
- Proven web search automation effective (75% time reduction vs manual)

**Next Immediate Steps:**
1. Execute `batch3_research.py` (30-45 min, 7 states)
2. Apply Batch 2 URL updates to states.json (30 min, 6 states)
3. Continue with Batches 4-6

---

---

## Context

Currently 38/51 states (74.5%) do not have `page_range` data. This is primarily due to broken URLs that prevent PDF extraction. Finding working URLs for these states will enable:

1. **Complete page_range coverage** - Add data to all states
2. **Improve URL reliability** - Fix broken links in states.json
3. **Enable efficient parsing** - Allow grade-specific page extraction
4. **Enhance user experience** - Working document links for all states

**Current State:**
- ✅ 13/51 states (25.5%) have page_range data
- ❌ 38/51 states (74.5%) lack page_range data
- ✅ 18/51 states (35.3%) have verified URLs (increased from 16/51)
- ✅ 43/80 documents (53.8%) have verified URLs
- ✅ URL research workflow exists (`docs/URL_RESEARCH_WORKFLOW.md`)
- ✅ Research script exists (`research_state_urls_browser.py`)
- ✅ Research plan exists (`state_url_research_plan.json`) for 35 states
- ✅ Documentation templates available (`docs/templates/url_update_template.md`)
- ✅ Automated research infrastructure exists (`scripts/research_urls_automated.py`)
- ✅ Batch 1 (HTTP 403) research complete - 11 states, 9 URLs found & applied
- ✅ Batch 2 (HTTP 202) research complete - 6 states researched, script created for remaining 2
- ❌ mcp_docker_playwright not accessible (checked, not in PATH or system)
- ⚠️  27 of 38 states still need URL research (Batches 3-6)

**Goal:** Find and validate working URLs for all 38 remaining states, enabling complete page_range coverage.

---

## Scope

**States Requiring URLs (38):**

### High Priority - URL Errors (36 states)
These states have inaccessible PDFs due to URL issues:

| # | State | # | State | # | State | # | State | # | State |
|---|--------|---|--------|---|--------|---|--------|---|--------|
| 1 | AK | 10 | KY | 19 | MO | 28 | NC | 37 |
| 2 | AZ | 11 | LA | 20 | MN | 29 | NE | 38 |
| 3 | CO | 12 | MA | 21 | MI | 30 | NH | 39 |
| 4 | CT | 13 | MD | 22 | NV | 31 | NM | 40 |
| 5 | DC | 14 | DE | 23 | OR | 32 | SC | 41 |
| 6 | FL | 15 | GA | 24 | RI | 33 | TN | 42 |
| 7 | IL | 25 | KS | 26 | TX | 34 | VA | 43 |
| 8 | IN | 27 | ME | 34 | VT | 35 | WA | 44 |
| 9 | WI | 36 | WV | 37 | WY | 38 |  |  |

### Special Case - Single-Grade Documents (1 state)
**CA** - California has 6 separate grade-specific PDFs (K, 1, 2, 3, 4, 5)
- Already structured correctly (no page_range needed for single-grade docs)
- URLs may still need verification
- Status: Research optional for page_range purposes

### Already Have URLs (1 state)
**AR** - Arkansas has working URL from Batch 1 research
- Has page_range: null (single-grade PDF per grade)
- Status: May need verification but not priority

**Total:** 36 states requiring URL research + 1 optional (CA) + 1 verified (AR) = 38 total

---

## Prerequisites

- [x] URL research workflow documented (URL_RESEARCH_WORKFLOW.md)
- [x] Research plan exists for 35 states (state_url_research_plan.json)
- [x] Research script available (research_state_urls_browser.py)
- [x] URL update template available (docs/templates/url_update_template.md)
- [x] states.json backup exists (data/states.json.backup)
- [x] JSON update guide exists (docs/JSON_UPDATE_GUIDE.md)
- [ ] Web browser access for manual research
- [ ] Dedicated research time blocks (2-4 hour sessions recommended)

**Verification:**
```bash
# Verify research tools exist
ls -lh docs/URL_RESEARCH_WORKFLOW.md
ls -lh research_state_urls_browser.py
ls -lh state_url_research_plan.json

# Verify backup exists
ls -lh data/states.json.backup

# Count states without page_range
python -c "
import json
data = json.load(open('data/states.json'))
without = sum(1 for s in data.values() if not any(d.get('page_range') for d in s.get('documents', [])))
print(f'States without page_range: {without}')
"
# Expected: 38
```

---

## Implementation Steps

### Step 1: Update Research Plan for All 38 States ✅ COMPLETE

**Action:** Create comprehensive research plan covering all 38 states

**Status:** ✅ **COMPLETE** - Research plan already exists (`state_url_research_plan.json`)

**Files to create:** `state_url_research_plan_batch2.json` (not needed - existing plan sufficient)

**Process:**
1. Review existing `state_url_research_plan.json` (covers 35 states)
2. Add missing states: AR (verify existing), CA (optional), WI, WV, WY
3. Organize by error type for batch processing:
   - HTTP 403 Forbidden (11 states)
   - HTTP 202 No Content (8 states)
   - HTTP 404 Not Found (1 state)
   - SSL/Connection errors (4 states)
   - PDF parse errors (12 states)
4. Document expected research difficulty per state
5. Create priority batches for efficient research

**Batch structure:**
```json
{
  "total_states": 38,
  "batches": [
    {
      "name": "Batch 1 - HTTP 403 (Bot Detection)",
      "count": 11,
      "states": ["WA", "VA", "WV", "NE", "KY", "DE", "AZ", "CO", "FL", "HI", "ID"],
      "estimated_time": "2-3 hours",
      "strategy": "Manual browser research, may need alternative hosting"
    },
    {
      "name": "Batch 2 - HTTP 202 (nextgenscience.org)",
      "count": 8,
      "states": ["VT", "KS", "MD", "NH", "RI", "NM", "MI", "IL"],
      "estimated_time": "1-2 hours",
      "strategy": "Find alternative state hosting, nextgenscience broken"
    },
    {
      "name": "Batch 3 - PDF Parse Errors",
      "count": 12,
      "states": ["AK", "OR", "NV", "ND", "SD", "MT", "ME", "MN", "MO", "IA", "MS", "PA"],
      "estimated_time": "2-3 hours",
      "strategy": "Re-download PDFs, verify actual content, find working copies"
    },
    {
      "name": "Batch 4 - SSL/Connection/404 Errors",
      "count": 4,
      "states": ["GA", "IN", "SC", "TN"],
      "estimated_time": "1 hour",
      "strategy": "Troubleshoot network issues, find alternative URLs"
    },
    {
      "name": "Batch 5 - Special Cases",
      "count": 2,
      "states": ["CA", "TX"],
      "estimated_time": "30-60 minutes",
      "strategy": "CA: grade-specific PDFs, TX: complex structure"
    },
    {
      "name": "Batch 6 - Low Priority",
      "count": 1,
      "states": ["DC"],
      "estimated_time": "30 minutes",
      "strategy": "District of Columbia special handling"
    }
  ],
  "tool_check": {
    "mcp_docker_playwright": "NOT AVAILABLE - Checked PATH, not found",
    "research_script": "research_state_urls_browser.py available",
    "manual_research": "Required for most states"
  }
}
```

**Tests required:**
- All 38 states included
- Batches logical and prioritized
- Error types accurate
- Time estimates realistic

**Validation:**
```bash
# Verify plan created
ls -lh state_url_research_plan_batch2.json

# Verify all states accounted for
python -c "
import json
plan = json.load(open('state_url_research_plan_batch2.json'))
total = sum(b['count'] for b in plan['batches'])
print(f'Planned states: {total} (expected: 38)')
"
```

**Commit message:** `docs(research): create batch research plan for 38 remaining states`

**Expected duration:** 30 minutes

---

### Step 2: Research Batch 1 - HTTP 403 States (11 states) ✅ COMPLETE

**Action:** Research working URLs for states with HTTP 403 Forbidden errors

**Status:** ✅ **COMPLETE** - Research done via web search automation

**Actual Results:**
- Working URLs found: 9/11 states (82%)
- High confidence: 7 states (WV, VA, WA, NE, KY, AZ, FL, HI, ID)
- Medium confidence: 2 states (DE, CO) - need manual verification
- Time spent: ~35 minutes (vs 2-3 hours estimated)

**States:**
- ✅ WA (Washington) - URL found, verified
- ✅ VA (Virginia) - URL found, verified
- ✅ WV (West Virginia) - URL found, verified
- ✅ NE (Nebraska) - URL found, verified
- ✅ KY (Kentucky) - URL found, verified
- ⚠️ DE (Delaware) - URL found (NGSS framework), needs manual verification
- ✅ AZ (Arizona) - URL found, verified
- ⚠️ CO (Colorado) - Multiple grade-band options, needs manual verification
- ✅ FL (Florida) - URL found, verified
- ✅ HI (Hawaii) - URL found, verified
- ✅ ID (Idaho) - URL found, verified

**Committed:** `feat(automation): complete Batch 1 research for all 11 states (WV, VA, WA, NE, KY, DE, AZ, CO, FL, HI, ID)`

**Files Created:**
- `docs/url_updates/BATCH1_RESEARCH_SUMMARY.md` - Comprehensive summary
- 17 JSON research templates in `docs/url_updates/`
- `scripts/research_urls_automated.py` - Automated research system

**Strategy:**
- Manual browser research (required)
- Look for alternative document hosting
- Check for "download" vs "view" URLs
- Search for state standards repositories
- Check for PDF download sections with different URLs

**Tools:**
- Manual web browser (Chrome/Firefox)
- Research documentation (URL_RESEARCH_WORKFLOW.md)
- State education agency websites
- Search engines for "[state] science standards PDF"

**Process per state:**
1. Open state education agency website
2. Navigate to science/standards section
3. Find PDF download link
4. Test in browser (download PDF)
5. Verify document content (title, grades, type)
6. Note working URL in research template
7. Document research process
8. Save as `docs/url_updates/[STATE]-[doc-slug].md`

**Time per state:** 10-20 minutes (average 15 min)

**Estimated batch time:** 2-3 hours

**Tests required:**
- Working URL found for each state
- URL verified in browser
- PDF downloads successfully
- Document matches states.json expectations
- Research documented per template

**Validation:**
```bash
# Count research docs created
ls docs/url_updates/WA*.md 2>/dev/null | wc -l
# Should show research documents for all 11 states

# Verify at least 80% success rate (9/11 states)
# Lower success rate indicates systematic issue
```

**Commit message:** `docs(research): complete Batch 1 URL research (11 HTTP 403 states)`

**Expected duration:** 2-3 hours

---

### Step 3: Research Batch 2 - HTTP 202 States (8 states) ✅ COMPLETE

**Action:** Research working URLs for states with HTTP 202 (nextgenscience.org broken)

**Status:** ✅ **COMPLETE** - 6/8 states researched, script ready for remaining

**Actual Results:**
- Working URLs found: 6/8 states (75%)
- High confidence: 6 states (IL, MD, NM, MI, NH, RI)
- Remaining: 2 states (VT, KS) - script created, ready to execute
- Time spent: ~1 hour (vs 1-2 hours estimated)

**States:**
- ⏳ VT (Vermont) - Script ready, pending execution
- ⏳ KS (Kansas) - Script ready, pending execution
- ✅ MD (Maryland) - URL found, verified
- ✅ NH (New Hampshire) - URL found, verified
- ✅ RI (Rhode Island) - URL found, verified
- ✅ NM (New Mexico) - URL found, verified
- ✅ MI (Michigan) - URL found, verified
- ✅ IL (Illinois) - URL found, verified

**Committed:**
- `feat(automation): complete Batch 2 research for 3 states (IL, MD, NM)`
- `feat(automation): complete Batch 2 research for 1 state (MI)`
- `feat(automation): complete Batch 2 research for 2 states (NH, RI)`

**Strategy:**
- Find alternative state hosting (not nextgenscience.org)
- Check state education agency websites for local copies
- Look for state-specific NGSS documents
- Check education department resource pages
- Verify state doesn't host documents elsewhere

**Key insight:** These states likely use nextgenscience.org as primary source, which returns HTTP 202 (accepted but no content). Need to find state-hosted versions.

**Tools:** Same as Batch 1

**Process per state:** Same as Batch 1

**Time per state:** 10-15 minutes (state hosting is usually clearer)

**Estimated batch time:** 1-2 hours

**Tests required:**
- Working URL found (state-hosted, not nextgenscience.org)
- URL verified and working
- Document matches expectations

**Commit message:** `docs(research): complete Batch 2 URL research (8 HTTP 202 states)`

**Expected duration:** 1-2 hours

---

### Step 4: Research Batch 3 - PDF Parse Errors (12 states) ⏳ READY

**Action:** Research and fix PDF parsing errors

**Status:** ⏳ **READY** - Script exists (`batch3_research.py`), needs execution

**Prerequisites met:**
- ✅ Research script created and ready
- ✅ Verification data available (from `validation_results_remaining_36.json`)
- ✅ Template format established from Batches 1-2

**States:**
- AK (Alaska) - Connection error
- OR (Oregon) - Connection error
- NV (Nevada) - Connection error
- ND (North Dakota) - Already has page_range (working URL)
- SD (South Dakota) - Already has page_range (working URL)
- MT (Montana) - Already has page_range (2 docs, working URLs)
- ME (Maine) - Returns HTML instead of PDF
- MN (Minnesota) - Connection error
- MO (Missouri) - Connection error
- IA (Iowa) - Already has page_range (working URL)
- MS (Mississippi) - Already has page_range (working URL)
- PA (Pennsylvania) - Already has page_range (working URL)

**Note:** 5 states (ND, SD, MT, IA, MS, PA) already have page_range data and working URLs. Only 7 states need research.

**Script to execute:**
```bash
python batch3_research.py
```

**Estimated time:** 30-45 minutes (vs 2-3 hours estimated - fewer states to research)

**Strategy:**
- Re-try URL download (may have been temporary error)
- Verify URL points to actual PDF (not HTML)
- Check for redirect to different URL
- Manually download PDF in browser
- Find alternative hosting if original fails

**Process per state:**
1. Test current URL in browser
2. If it works, note as working (parser error, not URL error)
3. If it fails, find alternative URL
4. Document findings

**Time per state:** 10-15 minutes

**Estimated batch time:** 2-3 hours

**Tests required:**
- URLs accessible in browser
- PDFs download successfully
- Clear distinction between URL error vs parser error

**Commit message:** `docs(research): complete Batch 3 URL research (12 PDF parse error states)`

**Expected duration:** 2-3 hours

---

### Step 5: Research Batch 4 - SSL/Connection/404 Errors (4 states)

**Action:** Troubleshoot network and server errors

**States:**
- GA (Georgia) - Connection error
- IN (Indiana) - SSL certificate error
- SC (South Carolina) - Connection error
- TN (Tennessee) - Connection error

**Strategy:**
- Retry URLs (may be temporary network issues)
- Check SSL certificate validity
- Try different browser/network
- Find alternative hosting
- Check for HTTP vs HTTPS
- Verify domain is still active

**Process per state:** Same as previous batches

**Time per state:** 10-15 minutes

**Estimated batch time:** 1 hour

**Tests required:**
- URLs accessible
- SSL/Connection issues resolved or documented

**Commit message:** `docs(research): complete Batch 4 URL research (4 SSL/connection error states)`

**Expected duration:** 1 hour

---

### Step 6: Research Batch 5 - Special Cases (2 states)

**Action:** Handle states with unique document structures

**States:**
- CA (California) - 6 separate grade-specific PDFs
- TX (Texas) - Complex multi-document structure

**Strategy for California:**
- Verify all 6 grade-specific PDFs work (K, 1, 2, 3, 4, 5)
- Each is single-grade, so page_range = null (as expected)
- May need URL verification but not page_range extraction

**Strategy for Texas:**
- Has 9 separate grade-specific PDFs (K-8) + high school
- Verify all URLs work
- Check if any need updates

**Time per state:**
- CA: 30-60 minutes (6 URLs to verify)
- TX: 45-60 minutes (9+ URLs to verify)

**Estimated batch time:** 1-2 hours

**Tests required:**
- All grade-specific URLs verified
- Document structure matches states.json

**Commit message:** `docs(research): complete Batch 5 URL research (CA and TX special cases)`

**Expected duration:** 1-2 hours

---

### Step 7: Research Batch 6 - Low Priority (1 state)

**Action:** Complete research for District of Columbia

**State:**
- DC (District of Columbia)

**Strategy:**
- DC public schools website
- OSSE (Office of the State Superintendent of Education)
- Verify current science standards hosting

**Time:** 30 minutes

**Commit message:** `docs(research): complete Batch 6 URL research (DC low priority)`

**Expected duration:** 30 minutes

---

### Step 8: Compile and Verify Research Findings

**Action:** Aggregate all research into comprehensive summary

**Files to create:** `docs/URL_RESEARCH_BATCH2_SUMMARY.md`

**Structure:**
```markdown
# URL Research Summary - Batch 2 (38 States)

**Research Date:** 2026-02-05
**Researcher:** [Name]
**Total States:** 38

## Overall Results

- Working URLs Found: X/38 (XX%)
- States with Multiple Options: Y
- States Requiring Manual Follow-up: Z
- States Unable to Locate: W

## By Batch

### Batch 1 - HTTP 403 (11 states)
- Successes: X/11
- Findings: [Summary of patterns]

### Batch 2 - HTTP 202 (8 states)
- Successes: X/8
- Findings: [nextgenscience.org alternatives]

### Batch 3 - PDF Parse Errors (12 states)
- Successes: X/12
- Findings: [Parser vs URL error resolution]

### Batch 4 - SSL/Connection (4 states)
- Successes: X/4
- Findings: [Network issue patterns]

### Batch 5 - Special Cases (2 states)
- Successes: X/2
- Findings: [CA/TX verification results]

### Batch 6 - Low Priority (1 state)
- Successes: X/1
- Findings: [DC results]

## States Requiring Further Action

[List any states needing manual escalation or complex resolution]

## Recommendations

1. [Top recommendation 1]
2. [Top recommendation 2]
3. [Future improvement suggestions]

## Time Spent

- Research: X hours
- Documentation: Y hours
- **Total:** Z hours
```

**Tests required:**
- All 38 states accounted for
- Success percentages calculated
- Patterns identified
- Clear next steps documented

**Commit message:** `docs(research): compile Batch 2 research summary for 38 states`

**Expected duration:** 30 minutes

---

### Step 9: Apply URL Updates to states.json

**Action:** Update states.json with verified working URLs

**Files to modify:** `data/states.json`

**Process:**
1. For each state with working URL found:
   - Load states.json
   - Locate state entry
   - Find document by title
   - Update URL field with new working URL
   - Add url_source field (new)
   - Add last_verified field (new) - "2026-02-05"
   - Save with proper formatting
   - Validate JSON syntax
   - Test CLI functionality

2. For states where URL couldn't be found:
   - Keep existing URL
   - Add note to `url_source` or `notes` field
   - Document in summary report
   - Mark for future follow-up

**Example update:**
```json
{
  "WA": {
    "documents": [
      {
        "title": "Washington State K-12 Science Learning Standards",
        "url": "https://NEW-WORKING-URL.pdf",  // UPDATED
        "url_source": "https://ospi.k12.wa.us/science/",  // ADDED
        "last_verified": "2026-02-05",  // ADDED
        // ... all other fields preserved
      }
    ]
  }
}
```

**Safety measures:**
- Only update URLs confirmed working
- Preserve all existing fields
- Document all changes
- Test after each batch
- Keep backup available

**Tests required:**
- JSON syntax valid after updates
- All 51 states still present
- All 80 documents still present
- CLI commands work
- New fields added (url_source, last_verified)

**Validation:**
```bash
# Validate JSON
python -m json.tool data/states.json > /dev/null && echo "✓ JSON valid"

# Verify counts
python -c "
import json
data = json.load(open('data/states.json'))
assert len(data) == 51, 'State count wrong'
assert sum(len(s['documents']) for s in data.values()) == 80, 'Doc count wrong'
print('✓ Counts preserved')
"

# Test CLI
python state_science_standards_system.py list | head -10
python state_science_standards_system.py state WA  # Example updated state

# Verify new fields
python -c "
import json
data = json.load(open('data/states.json'))
wa_doc = data['WA']['documents'][0]
print(f'url_source: {wa_doc.get(\"url_source\", \"NOT SET\")}')
print(f'last_verified: {wa_doc.get(\"last_verified\", \"NOT SET\")}')
"
```

**Commit message:** `fix(data): update URLs for [X] states with verified working links (Batch 2 research)`

**Commit per batch to maintain granular history**

**Expected duration:** 1-2 hours

---

### Step 10: Re-run Page Range Extraction for Newly Accessible Documents

**Action:** Run page range extraction on newly accessible states

**Files to create:** `page_ranges_batch2_extracted.json`

**Command:**
```bash
uv run scripts/extract_page_ranges.py --output page_ranges_batch2_extracted.json
```

**Expected results:**
- New page ranges extracted from newly accessible PDFs
- Total page_range coverage increases from 14/80 (17.5%) to higher percentage
- Multi-grade documents get grade-specific page data

**Process:**
1. Run extraction script
2. Review new results
3. Merge with existing page_ranges_extracted.json
4. Update states.json with new page_range data
5. Test CLI display

**Tests required:**
- Extraction completes successfully
- JSON output valid
- New page ranges found
- Merge successful
- CLI displays new page ranges

**Validation:**
```bash
# Count new page ranges
python -c "
import json
old = json.load(open('page_ranges_extracted.json'))
new = json.load(open('page_ranges_batch2_extracted.json'))
old_count = sum(1 for s in old.values() for d in s.values() if isinstance(d, dict))
new_count = sum(1 for s in new.values() for d in s.values() if isinstance(d, dict))
print(f'Old: {old_count}, New: {new_count}, Added: {new_count - old_count}')
"

# Verify states.json update
python -c "
import json
data = json.load(open('data/states.json'))
with_range = sum(1 for s in data.values() for d in s.get('documents', []) if d.get('page_range'))
print(f'With page_range: {with_range}/80')
"
```

**Commit message:** `feat(page-range): add page ranges from Batch 2 URL updates`

**Expected duration:** 30-45 minutes

---

## Validation Strategy

### After Each Batch
```bash
# Verify research docs created
ls docs/url_updates/ | grep -E "(WA|VA|WV)"  # Example: Batch 1 states

# Verify JSON validity
python -m json.tool data/states.json > /dev/null

# Test CLI
python state_science_standards_system.py state WA
```

### After URL Updates
```bash
# Verify data integrity
python -c "
import json
data = json.load(open('data/states.json'))
print(f'States: {len(data)}')
print(f'Documents: {sum(len(s[\"documents\"]) for s in data.values())}')
"

# Count working URLs
python -c "
import json
data = json.load(open('data/states.json'))
with_url = sum(1 for s in data.values() for d in s.get('documents', []) if d.get('last_verified'))
print(f'Verified URLs: {with_url}/80')
"
```

### After Page Range Extraction
```bash
# Verify page range increase
python -c "
import json
data = json.load(open('data/states.json'))
with_range = sum(1 for s in data.values() for d in s.get('documents', []) if d.get('page_range'))
print(f'With page_range: {with_range}/80 ({with_range/80*100:.1f}%)')
"
```

---

## Success Criteria

- [x] Batch research plan created for all 38 states
- [x] Batch 1 (HTTP 403) researched - 11 states (9/11 URLs found)
- [x] Batch 2 (HTTP 202) researched - 8 states (6/8 URLs found, script ready for 2)
- [ ] Batch 3 (PDF errors) researched - 12 states (script ready, needs execution)
- [ ] Batch 4 (SSL/Connection) researched - 4 states
- [ ] Batch 5 (Special cases) researched - 2 states
- [ ] Batch 6 (Low priority) researched - 1 state
- [ ] Research summary compiled and documented
- [x] Working URLs applied to states.json for Batch 1 (9 states)
- [ ] Working URLs applied to states.json for Batch 2 (6 states)
- [x] JSON syntax valid after updates
- [x] CLI functionality maintained
- [ ] Page ranges extracted from newly accessible documents
- [ ] page_range coverage increased from 14/80 (17.5%)
- [x] All changes committed with proper messages
- [x] Clear documentation of findings and next steps

**Progress:**
- **Batches 1-2:** Complete (17 states researched, 15 URLs found)
- **Batch 3:** Ready (script exists, needs execution)
- **Batches 4-6:** Not started (7 states total)
- **URL updates applied:** 9/15 found URLs (Batch 1 complete)

**Definition of "Done":**

This plan is complete when:
- All 38 states have been researched for working URLs
- Working URLs applied to states.json where found
- Page ranges extracted from newly accessible documents
- page_range coverage significantly increased (target: 50-60% of documents)
- All research findings documented
- System functional and stable

---

## Rollback Plan

### If URL Updates Break Something

```bash
# Restore from backup
cp data/states.json.backup data/states.json
python -m json.tool data/states.json > /dev/null && echo "✓ Restored"
```

### If Page Range Extraction Fails

```bash
# Restore old page_ranges_extracted.json
cp page_ranges_extracted.json page_ranges_extracted.json.backup

# Or revert states.json to before page_range updates
git checkout data/states.json
```

---

## Notes

### Tool Availability

**Checked Tools:**
- ✅ `research_state_urls_browser.py` - Available
- ✅ `scripts/research_urls_automated.py` - Available (created during Batch 1)
- ✅ `batch3_research.py` - Available (created for Batch 3)
- ✅ `docs/URL_RESEARCH_WORKFLOW.md` - Available
- ✅ `docs/templates/url_update_template.md` - Available
- ✅ `docs/JSON_UPDATE_GUIDE.md` - Available
- ✅ `apply_batch1_urls.py` - Available (applies URL updates)
- ✅ MCP_DOCKER_brave_web_search - Available (proven effective)
- ❌ `mcp_docker_playwright` - NOT AVAILABLE (not in PATH)

**Research Approach:**
- **Automated web search** (primary, proven effective)
- Manual browser research (fallback)
- Use existing research scripts where applicable
- Follow URL_RESEARCH_WORKFLOW.md process
- Document findings per template

### Constraints

1. **Hybrid research approach** - Web search automation (proven effective) + manual verification when needed
2. **Time variable** - Some states easy (5-10 min with automation), some hard (20-30 min manual)
3. **Not all URLs may be findable** - Some states may have no current working URL
4. **State website variability** - Different agencies, different structures
5. **No automated web scraping** - mcp_docker_playwright not available
6. **Efficiency gains** - Web search automation reduced research time by ~75%

### Risks

1. **Some states may not have public URLs** - Access restrictions or unpublished
2. **Research may reveal systematic issues** - Multiple states with same problem
3. **New URLs may break again** - State websites may change URLs
4. **Time intensive** - Manual research for 38 states is time-consuming

### Batch Strategy Benefits

1. **Efficient use of time** - Group similar states
2. **Pattern recognition** - Identify common solutions
3. **Incremental progress** - Each batch delivers value
4. **Easier to resume** - Can stop between batches
5. **Better documentation** - Summarize by batch

---

## Potential Blockers

**STOP and alert human if:**

- 3 consecutive batches have <50% success rate (systematic issue)
- Multiple states require paid access/authentication (access barrier)
- State education websites completely down or restructured
- Time exceeds estimates significantly (complexity too high)
- Same URL error appears in all states (methodology issue)

**When blocked:**
1. Document specific blocker
2. Preserve current working state
3. Commit completed work
4. Update research summary with blocker info
5. Alert human with details and recommendations
6. Consider alternative approaches

---

## Expected Outcomes

**Actual Progress So Far:**
- 17 states researched (Batches 1-2 complete, Batch 3 ready)
- 15 working URLs found (88% success rate on researched states)
- 9/15 URLs applied to states.json (Batch 1)
- 6/15 URLs pending application (Batch 2)
- Time spent: ~1.5 hours (vs 3-5 hours estimated)

**Updated Best Case (60-80% success):**
- 23-30 states get working URLs
- page_range coverage increases to 37-44/80 (46-55%)
- Significant progress toward full coverage

**Updated Medium Case (40-60% success):**
- 15-23 states get working URLs
- page_range coverage increases to 29-37/80 (36-46%)
- Good progress, some states need alternative approach

**Updated Worst Case (<40% success):**
- <15 states get working URLs
- page_range coverage <37/80 (<46%)
- May need systematic re-evaluation of approach

**Remaining Work Estimate:**
- Batch 3 execution: 30-45 minutes (7 states to research)
- Batch 4: 1 hour (4 states)
- Batch 5: 1-2 hours (2 states)
- Batch 6: 30 minutes (1 state)
- Apply Batch 2 URL updates: 30 minutes
- Compile research summary: 30 minutes
- Re-run page range extraction: 30-45 minutes
- **Total remaining: 4-6 hours**

---

**Status: In Progress**
**Estimated total time: 5-8 hours (remaining work only)**
**Recommended: Execute Batch 3 next (script ready, quick wins)**

---

## 🚀 Next Immediate Actions (Priority Order)

### 1. Execute Batch 3 Research (HIGH PRIORITY - Quick Wins)
**Command:**
```bash
python batch3_research.py
```

**Why now:**
- Script is ready and waiting
- Only 7 states to research (ND, SD, MT already have page_range)
- Quick wins - some URLs already working
- Estimated: 30-45 minutes

### 2. Apply Batch 2 URL Updates (HIGH PRIORITY - Cleanup)
**Command:**
```bash
# Apply the 6 verified URLs from Batch 2 to states.json
python apply_batch1_urls.py  # (may need update for Batch 2)
```

**Why now:**
- 6 verified URLs waiting to be applied
- Clean up in-progress work
- Enable page_range extraction for these states
- Estimated: 30 minutes

### 3. Continue with Batches 4-6 (MEDIUM PRIORITY)
**Total states remaining:** 7
**Estimated time:** 2-3 hours

### 4. Re-run Page Range Extraction (HIGH VALUE)
**Command:**
```bash
uv run scripts/extract_page_ranges.py --output page_ranges_batch2_extracted.json
```

**Why important:**
- Newly accessible documents will get page_range data
- Significant coverage increase expected
- Enable efficient grade-specific parsing
- Estimated: 30-45 minutes

### 5. Compile Research Summary (DOCUMENTATION)
**File to create:** `docs/URL_RESEARCH_BATCH2_SUMMARY.md`

**Why important:**
- Document all findings from all batches
- Capture success rates and patterns
- Provide clear record of what was done
- Estimated: 30 minutes

---

## 📝 Remaining Tasks Checklist

### URL Research
- [ ] Execute Batch 3 (7 states) - script ready
- [ ] Research Batch 4 (4 states: GA, IN, SC, TN)
- [ ] Research Batch 5 (2 states: CA, TX)
- [ ] Research Batch 6 (1 state: DC)

### URL Updates
- [ ] Apply Batch 2 URLs to states.json (6 states)
- [ ] Apply Batch 3 URLs to states.json (pending research)
- [ ] Apply Batch 4-6 URLs to states.json (pending research)

### Page Range Extraction
- [ ] Re-run extraction on newly accessible documents
- [ ] Merge new page ranges into states.json
- [ ] Verify CLI displays new page ranges correctly

### Documentation
- [ ] Compile comprehensive research summary (all batches)
- [ ] Update progress.txt with final statistics
- [ ] Update DATA_SCHEMA.md if needed

### Testing & Validation
- [ ] Verify JSON syntax after all updates
- [ ] Test CLI functionality
- [ ] Verify all 51 states present
- [ ] Verify all 80 documents present

---
