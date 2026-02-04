# Plan: Execute URL Validation & Generate Reports

**Status:** Not Started
**Created:** 2026-02-04
**Estimated Duration:** 2-3 hours
**Priority:** High

---

## Context

The URL validation utility (`validate_urls.py`, 434 lines) already exists but hasn't been executed on the full dataset. This plan focuses on running comprehensive validation on all 80 documents in `data/states.json`, generating structured reports, and identifying broken URLs that need fixing.

**Current State:**
- ✅ `validate_urls.py` exists (434 lines, 16KB)
- ❌ Missing UV inline dependencies (httpx, orjson)
- ❌ No validation results generated yet
- ❌ Unknown how many URLs are broken

**Goal:** Execute validation, generate comprehensive reports, identify states requiring URL updates.

---

## Prerequisites

- [x] Python 3.10+ installed
- [x] UV package manager available
- [x] `validate_urls.py` exists (434 lines)
- [x] `data/states.json` exists with 80 documents
- [x] `pypdf` dependency available (used in parse_standards.py)
- [ ] UV dependencies added to validate_urls.py (httpx, orjson, pypdf)
- [ ] Validation has not been run yet

**Verification:**
```bash
# Verify UV available
uv --version

# Verify states.json exists with 80 documents
python -c "import json; data=json.load(open('data/states.json')); print(f'{sum(len(s[\"documents\"]) for s in data.values())} documents')"
# Expected: 80 documents

# Verify validate_urls.py exists
wc -l validate_urls.py
# Expected: 434 lines

# Verify pypdf is available (used for content validation)
python -c "import pypdf; print('pypdf available')"
# Expected: No error

# Or check parse_standards.py for pypdf usage
grep -i "pypdf\|PdfReader" parse_standards.py
# Expected: Matches found
```

---

## Implementation Steps

### Step 1: Add UV Inline Dependencies to validate_urls.py

**Action:** Add UV dependency markers for httpx, orjson, and pypdf at top of validate_urls.py

**Files to modify:** `validate_urls.py`

**Changes needed:**
Add after the shebang line (line 1-2):
```python
#!/usr/bin/env python3
# /// script
# dependencies = [
#     "httpx>=0.27.0",
#     "orjson>=3.9.0",
#     "pypdf>=3.0.0",
# ]
# ///
# -*- coding: utf-8 -*-
```

**Note:** pypdf is already used in `parse_standards.py` for PDF parsing, so adding it here for content validation is consistent.

**Tests required:** None (syntax-only change)

**Validation:**
```bash
# Verify UV can parse dependencies
uv run validate_urls.py --help 2>&1 | head -5
# Should not show "ModuleNotFoundError: No module named 'httpx'" or 'pypdf'

# Verify pypdf is available
uv run python -c "import pypdf; print('pypdf:', pypdf.__version__)"
# Expected: pypdf version number

# Verify script loads without errors
uv run python -c "import sys; sys.path.insert(0, '.'); exec(open('validate_urls.py').read().split('if __name__')[0])"
```

**Commit message:** `fix(validation): add UV inline dependencies for httpx, orjson, and pypdf for content validation`

**Expected duration:** 10 minutes

---

### Step 2: Run Validation on All 80 URLs (Automated)

**Action:** Execute validate_urls.py on entire states.json dataset

**Files to create:**
- `validation_results.json` - Structured validation output (generated)

**Command to run:**
```bash
uv run validate_urls.py
```

**Expected output:**
- Console progress showing each state being tested
- JSON file with validation results
- Summary statistics at end

**Tests required:**
- Validation completes without crashes
- All 80 URLs tested
- JSON output is valid
- Results categorized (working/broken/redirected)

**Validation:**
```bash
# Verify validation_results.json was created
ls -lh validation_results.json

# Verify JSON is valid
python -m json.tool validation_results.json > /dev/null && echo "Valid JSON"

# Count URLs tested
python -c "import json; data=json.load(open('validation_results.json')); print(f'URLs tested: {sum(len(state[\"documents\"]) for state in data[\"results\"].values())}')"
# Expected: 80

# Check for any validation errors
python -c "import json; data=json.load(open('validation_results.json')); errors = sum(1 for s in data['results'].values() for d in s['documents'] if d.get('error')); print(f'Documents with errors: {errors}')"
```

**Commit message:** `test(validation): execute URL validation on all 80 documents, generate results JSON`

**Expected duration:** 30 minutes (mostly automated, URL fetching time)

---

### Step 2b: Enhanced Content Validation (NEW)

**Action:** Add content verification to detect wrong-document URLs that return HTTP 200 but contain incorrect content

**Rationale:** URLs like `https://www.cde.ca.gov/pd/ca/sc/documents/grade1.pdf` return HTTP 200 OK with valid PDF content, but are wrong documents. HTTP status validation alone cannot catch this.

**Files to modify:** `validate_urls.py`

**Validation checks to add:**

1. **PDF Text Extraction** (using existing `pypdf` dependency from parse_standards.py)
   - Extract first 5 pages of text for efficiency
   - Search for grade level indicators matching `grade_levels` field
   - Search for state name matching `state_name` field
   - Search for science-related keywords ("Science", "NGSS", "Standards", "Performance Expectations")

2. **PDF Metadata Validation**
   - Extract PDF title/author metadata
   - Compare to document title in states.json
   - Check if author is state education agency

3. **URL Pattern Analysis**
   - Flag URLs with suspicious path patterns
   - Check for domain subdirectory mismatches (e.g., `/pd/ca/sc/` vs `/ci/pl/` for CA)
   - Identify potential redirect landing pages (too short)

4. **Confidence Score Calculation**
   - Calculate 0.0-1.0 score based on content matches
   - Grade level found: +0.4
   - State name found: +0.3
   - Science keyword found: +0.2
   - Metadata title match: +0.1

**Enhanced validation_results.json structure:**
```json
{
  "state": "CA",
  "documents": [
    {
      "title": "Grade 1 CA NGSS Standards",
      "url": "https://www.cde.ca.gov/pd/ca/sc/documents/grade1.pdf",
      "http_status": 200,
      "content_type": "application/pdf",
      "content_validation": {
        "grade_level_found": false,
        "state_name_found": false,
        "science_keyword_found": true,
        "metadata_title_match": "none",
        "confidence_score": 0.2,
        "warnings": [
          "grade level '1' not found in PDF",
          "state name 'California' not found in PDF",
          "low confidence score suggests wrong document"
        ]
      },
      "validation_status": "wrong_document"
    }
  ]
}
```

**Implementation details:**

```python
# Add to validate_urls.py after HTTP validation
def validate_pdf_content(url, expected_grade, expected_state, expected_title):
    """
    Validate PDF contains expected content.
    
    Returns:
        dict: Content validation results with confidence score
    """
    try:
        # Download PDF
        response = httpx.get(url, timeout=30)
        pdf_file = io.BytesIO(response.content)
        
        # Extract text from first 5 pages
        reader = pypdf.PdfReader(pdf_file)
        text = ""
        for page in reader.pages[:5]:
            text += page.extract_text() + "\n"
        
        # Extract metadata
        metadata = reader.metadata or {}
        pdf_title = metadata.get("/Title", "")
        
        # Check for expected content
        grade_found = str(expected_grade) in text or f"Grade {expected_grade}" in text
        state_found = expected_state in text or expected_state.split()[-1] in text  # Handle "New York" -> "NY"
        science_found = any(keyword in text.lower() for keyword in ["science", "ngss", "standards", "performance expectations"])
        title_match = expected_title in pdf_title if pdf_title else False
        
        # Calculate confidence
        confidence = 0.0
        if grade_found:
            confidence += 0.4
        if state_found:
            confidence += 0.3
        if science_found:
            confidence += 0.2
        if title_match:
            confidence += 0.1
        
        # Generate warnings
        warnings = []
        if not grade_found:
            warnings.append(f"grade level '{expected_grade}' not found in PDF")
        if not state_found:
            warnings.append(f"state name '{expected_state}' not found in PDF")
        if not science_found:
            warnings.append("science keyword not found in PDF")
        if confidence < 0.5:
            warnings.append(f"low confidence score ({confidence:.2f}) suggests wrong document")
        
        # Determine validation status
        if confidence >= 0.8:
            status = "content_verified"
        elif confidence >= 0.5:
            status = "content_questionable"
        else:
            status = "wrong_document"
        
        return {
            "grade_level_found": grade_found,
            "state_name_found": state_found,
            "science_keyword_found": science_found,
            "metadata_title_match": "exact" if title_match else "none",
            "confidence_score": confidence,
            "warnings": warnings,
            "validation_status": status
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "grade_level_found": false,
            "state_name_found": false,
            "science_keyword_found": false,
            "metadata_title_match": "error",
            "confidence_score": 0.0,
            "warnings": [f"content validation failed: {e}"],
            "validation_status": "validation_error"
        }
```

**Tests required:**
- Correct CA Grade 1 URL (`cangssgr1-dci.pdf`): confidence > 0.8, status = "content_verified"
- Wrong URL (`grade1.pdf` from example): confidence < 0.3, status = "wrong_document"
- Redirect to standards page: confidence < 0.2, status = "wrong_document"
- PDF with different grade: grade_found = false, confidence < 0.5
- Non-PDF URL (HTML): validation_status = "wrong_document"

**Validation:**
```bash
# After running enhanced validation, check for wrong-document URLs
python -c "
import json
data = json.load(open('validation_results.json'))
wrong_docs = []
for state, state_data in data['results'].items():
    for doc in state_data['documents']:
        if doc.get('content_validation', {}).get('validation_status') == 'wrong_document':
            wrong_docs.append(f\"{state}: {doc['title']}\")
print(f'Wrong-document URLs found: {len(wrong_docs)}')
for doc in wrong_docs[:10]:  # Show first 10
    print(f'  - {doc}')
"
# Expected: Several wrong-document URLs detected

# Verify confidence scores are calculated
python -c "
import json
data = json.load(open('validation_results.json'))
for state, state_data in data['results'].items():
    for doc in state_data['documents']:
        cv = doc.get('content_validation', {})
        if 'confidence_score' in cv:
            print(f\"{state}: {doc['title']} - Confidence: {cv['confidence_score']:.2f}\")
" | head -20
```

**Commit message:** `feat(validation): add PDF content validation to detect wrong-document URLs with confidence scoring`

**Expected duration:** 45 minutes

**STOP CONDITION:** If content validation fails on >20% of documents, investigate and adjust confidence thresholds

---

### Step 3: Generate Human-Readable Summary Report

**Action:** Create markdown summary of validation results with statistics

**Files to create:** `docs/URL_VALIDATION_SUMMARY.md`

**Report structure:**
```markdown
# URL Validation Summary

**Validation Date:** YYYY-MM-DD
**Total URLs Tested:** 80
**Validator Version:** 1.0

## Overall Statistics

- ✅ Working URLs: XX (XX%)
- ⚠️ Redirected URLs: XX (XX%)
- ❌ Broken URLs: XX (XX%)
- ⚠️ Wrong Format: XX (XX%)
- 🔍 Content-Verified URLs: XX (XX%)
- ⚠️ Wrong-Document URLs: XX (XX%)
- ❓ Content-Questionable URLs: XX (XX%)

## By Status Code

- HTTP 200 (OK): XX
  - Content verified (confidence ≥ 0.8): XX
  - Content questionable (confidence 0.5-0.8): XX
  - Wrong document (confidence < 0.5): XX
- HTTP 403 (Forbidden): XX
- HTTP 404 (Not Found): XX
- HTTP 301/302 (Redirect): XX
- Other errors: XX

## Content Validation Results

### Confidence Score Distribution

- High confidence (0.8-1.0): XX documents
- Medium confidence (0.5-0.8): XX documents
- Low confidence (0.2-0.5): XX documents
- Very low confidence (0.0-0.2): XX documents

### Common Content Validation Warnings

- Grade level not found: XX documents
- State name not found: XX documents
- Science keyword not found: XX documents
- Low confidence score: XX documents

## States Requiring Attention

### Critical (All Documents Broken or Wrong)
- [List states with all documents 404/403 or confidence < 0.3]

### Partial Issues (Some Documents Broken or Wrong)
- [List states with some broken or wrong-document URLs]

### Content Verification Needed
- [List states with confidence scores 0.3-0.8 requiring manual review]

### All Verified
- [List states with all URLs confidence ≥ 0.8]

## Next Steps
1. **High Priority:** Investigate wrong-document URLs (confidence < 0.5)
2. Research current state education websites for affected documents
3. Find replacement URLs from official sources
4. Document findings with URL update templates
5. **Medium Priority:** Review questionable URLs (confidence 0.5-0.8)
```

**Data source:** Parse `validation_results.json` to generate statistics

**Tests required:**
- Summary matches validation_results.json
- All 51 states categorized
- Statistics add up to 80 total

**Validation:**
```bash
# Verify summary file created
ls -lh docs/URL_VALIDATION_SUMMARY.md

# Verify markdown renders correctly
head -50 docs/URL_VALIDATION_SUMMARY.md

# Manual verification: spot-check 3-5 states against JSON
```

**Commit message:** `docs(validation): generate human-readable summary report of URL validation results`

**Expected duration:** 30 minutes

---

### Step 4: Generate State-by-State Detailed Report

**Action:** Create comprehensive per-state analysis report

**Files to create:** `docs/URL_VALIDATION_BY_STATE.md`

**Report structure:**
```markdown
# URL Validation Results by State

## Alabama (AL)

### Documents: 3 total
- ✅ Verified (confidence ≥ 0.8): 2
- ⚠️ Questionable (confidence 0.5-0.8): 0
- ❌ Wrong Document (confidence < 0.5): 0
- ❌ Broken (404/403): 1

#### Document: [Title]
- **URL:** [URL]
- **Status:** ✅ Content Verified
- **HTTP Status:** 200
- **Content Type:** application/pdf
- **File Size:** XXX KB
- **Content Validation:**
  - Grade level found: ✓
  - State name found: ✓
  - Science keyword found: ✓
  - Confidence score: 0.9
  - Warnings: None

#### Document: [Title] (Example of wrong document)
- **URL:** [URL]
- **Status:** ❌ Wrong Document
- **HTTP Status:** 200
- **Content Type:** application/pdf
- **File Size:** XXX KB
- **Content Validation:**
  - Grade level found: ✗
  - State name found: ✗
  - Science keyword found: ✓
  - Confidence score: 0.2
  - Warnings:
    - "grade level '1' not found in PDF"
    - "state name 'Alabama' not found in PDF"
    - "low confidence score suggests wrong document"

[... repeat for each document ...]

---

## Alaska (AK)
[... same format ...]

---

[... repeat for all 51 states ...]
```

**Data source:** Parse `validation_results.json` for detailed per-document status

**Tests required:**
- All 51 states included
- All 80 documents listed
- Status icons consistent (✅/⚠️/❌)
- File sizes and HTTP codes accurate

**Validation:**
```bash
# Verify report file created
ls -lh docs/URL_VALIDATION_BY_STATE.md

# Count states in report
grep -c "^## " docs/URL_VALIDATION_BY_STATE.md
# Expected: 51

# Verify structure is consistent
grep "^### Documents:" docs/URL_VALIDATION_BY_STATE.md | wc -l
# Expected: 51

# Manual spot-check: Compare 3 states against validation_results.json
```

**Commit message:** `docs(validation): generate detailed state-by-state URL validation report`

**Expected duration:** 30 minutes

---

### Step 5: Identify High-Priority States for URL Updates

**Action:** Create prioritized action list for URL fixing

**Files to create:** `docs/URL_UPDATE_PRIORITIES.md`

**Report structure:**
```markdown
# URL Update Priorities

## Tier 1: Critical - All Documents Broken or Wrong Document (Highest Priority)

### Washington (WA)
- **Documents Affected:** 3/3 (100%)
- **Issue:** HTTP 403 Forbidden
- **Root Cause:** Possible bot detection on OSPI website
- **Recommended Action:** Manual investigation, download documents, find alternative hosting
- **Estimated Effort:** 2-3 hours

### California (CA) - Wrong Documents Example
- **Documents Affected:** 2/6 (33%)
- **Issue:** Wrong Document URLs (HTTP 200 but incorrect content)
- **Root Cause:** Old URLs pointing to outdated/incorrect PDFs
- **Examples:**
  - `https://www.cde.ca.gov/pd/ca/sc/documents/grade1.pdf` (wrong, confidence: 0.2)
  - Correct URL: `https://www.cde.ca.gov/ci/pl/documents/cangssgr1-dci.pdf`
- **Recommended Action:** Cross-reference with CA NGSS standards page, find correct PDF URLs
- **Estimated Effort:** 1-2 hours

[... repeat for other Tier 1 states ...]

## Tier 2: Partial - Some Documents Broken or Questionable

### [State Name]
- **Documents Affected:** X/Y (XX%)
- **Issue:** Mixed - some 404, some wrong documents, some questionable (confidence 0.5-0.8)
- **Root Cause:** [URL change, content mismatch, etc.]
- **Recommended Action:** [Check current state standards page, verify document content]
- **Estimated Effort:** 1 hour

[... repeat for other Tier 2 states ...]

## Tier 3: Verified with Minor Warnings

### States with Redirects or Low Confidence Scores
- [List states where URLs redirect but work, or have confidence 0.6-0.8]
- **Recommended Action:**
  - For redirects: Update to final redirect URL
  - For low confidence: Manual review of document content
- **Estimated Effort:** 15 min per state

## Tier 4: All Verified - No Action Needed

- [List states with 100% URLs confidence ≥ 0.8]
- Total: XX states

## Summary

- **Tier 1 (Critical):** X states, Y documents - Immediate attention
- **Tier 2 (Partial):** X states, Y documents - Medium priority
- **Tier 3 (Warnings):** X states, Y documents - Low priority
- **Tier 4 (Verified):** X states - No action needed

## Content Validation Summary

- **High confidence (≥ 0.8):** X documents - Verified correct
- **Medium confidence (0.5-0.8):** X documents - Needs manual review
- **Low confidence (< 0.5):** X documents - Likely wrong document
- **No confidence (validation error):** X documents - Failed to validate

## Estimated Total Effort

- Tier 1: X-Y hours
- Tier 2: X-Y hours
- Tier 3: X-Y hours
- **Total:** X-Y hours of URL research and updates
```

**Data source:** Analyze `validation_results.json` and categorize by urgency

**Tests required:**
- All broken/redirected URLs categorized
- States sorted by priority
- Effort estimates realistic
- Action items clear and specific

**Validation:**
```bash
# Verify priorities file created
ls -lh docs/URL_UPDATE_PRIORITIES.md

# Verify all tiers present
grep "^## Tier" docs/URL_UPDATE_PRIORITIES.md
# Expected: 4 tiers

# Verify state counts add up to 51
# (manual check: sum of all tier state counts = 51)

# Manual review: Do priorities make sense?
```

**Commit message:** `docs(validation): create prioritized action list for URL updates by urgency`

**Expected duration:** 30 minutes

---

### Step 6: Manual Spot-Check Verification

**Action:** Manually verify validation accuracy on sample of URLs

**Files to modify:**
- `docs/URL_VALIDATION_SUMMARY.md` - Add verification section

**Process:**
1. Select 10 random URLs from validation results
2. Manually test each URL in browser
3. Compare browser results to validation_results.json
4. Calculate accuracy percentage
5. Document any discrepancies

**Sample selection:**
- 3 URLs marked "working"
- 3 URLs marked "broken"
- 2 URLs marked "redirected"
- 2 URLs marked "wrong format"

**Tests required:**
- Validation accuracy >= 90%
- Any discrepancies documented
- Root cause of mismatches identified

**Validation:**
```bash
# Add verification section to summary
tail -20 docs/URL_VALIDATION_SUMMARY.md
# Should show "Manual Verification" section with results
```

**Add to summary:**
```markdown
## Manual Verification

**Sample Size:** 10 URLs
**Accuracy:** 9/10 (90%)

**Verified Working:** 3/3 matched
**Verified Broken:** 3/3 matched
**Verified Redirected:** 2/2 matched
**Verified Wrong Format:** 1/2 matched (1 discrepancy)

**Discrepancies:**
- [Document title]: Validator reported [X], manual test showed [Y]
  - Root cause: [Explanation]
  - Action: [How to fix validator if needed]

**Conclusion:** Validation is sufficiently accurate for planning URL updates.
```

**Commit message:** `docs(validation): add manual verification section confirming 90%+ validation accuracy`

**Expected duration:** 30 minutes

---

### Step 7: Final Summary and Recommendations

**Action:** Update progress.txt and create executive summary

**Files to modify:**
- `progress.txt` - Log completion of validation phase
- `docs/URL_VALIDATION_SUMMARY.md` - Add recommendations section

**Progress.txt entry:**
```
2026-02-04 HH:MM - Completed URL validation execution plan
2026-02-04 HH:MM - Validated all 80 documents in states.json
2026-02-04 HH:MM - Generated 3 reports: summary, state-by-state, priorities
2026-02-04 HH:MM - Manual verification: 90%+ accuracy confirmed
2026-02-04 HH:MM - Identified X critical states, Y partial issues
2026-02-04 HH:MM - Ready for URL update workflow documentation (Plan 2)
```

**Recommendations section for summary:**
```markdown
## Recommendations

### Immediate Actions
1. Execute Plan 2: Document URL Update Workflow
2. Begin Tier 1 state research (critical broken URLs)
3. Review nextgenscience.org states (if many use external hosting)

### Data Model Enhancements
- Add `last_verified` timestamp field
- Add `url_source` documentation field
- Add `validation_status` field

### Future Improvements
- Periodic re-validation (every 3-6 months)
- Automated health monitoring
- Document mirroring for critical states
```

**Tests required:**
- progress.txt updated correctly
- Recommendations are actionable
- Summary is complete

**Validation:**
```bash
# Verify progress.txt updated
tail -10 progress.txt | grep "URL validation"

# Verify summary has recommendations
grep "## Recommendations" docs/URL_VALIDATION_SUMMARY.md

# All commits made
git log --oneline -n 7
```

**Commit message:** `docs(validation): add final summary, recommendations, and next steps for URL update workflow`

**Expected duration:** 15 minutes

---

## Validation Strategy

### After Each Step
- Verify files created/modified as expected
- Check JSON validity if applicable
- Run specified validation commands
- Ensure no data corruption

### Before Commit
- Review changes with `git diff`
- Verify commit message follows convention
- Ensure no sensitive data in output

### Final Validation
```bash
# Verify all reports created
ls -lh docs/URL_VALIDATION*.md docs/URL_UPDATE_PRIORITIES.md validation_results.json

# Verify JSON validity
python -m json.tool validation_results.json > /dev/null

# Verify 80 URLs tested
python -c "import json; data=json.load(open('validation_results.json')); print(sum(len(s['documents']) for s in data['results'].values()))"
# Expected: 80

# Verify content validation fields present
python -c "
import json
data = json.load(open('validation_results.json'))
with_cv = sum(1 for s in data['results'].values() for d in s['documents'] if 'content_validation' in d)
print(f'Documents with content_validation: {with_cv}/80')
"
# Expected: 80/80

# Verify wrong-document URLs identified
python -c "
import json
data = json.load(open('validation_results.json'))
wrong_docs = sum(1 for s in data['results'].values() for d in s['documents'] 
                    if d.get('content_validation', {}).get('validation_status') == 'wrong_document')
print(f'Wrong-document URLs identified: {wrong_docs}')
"
# Expected: > 0 (some wrong documents should be found)

# Verify confidence scores calculated
python -c "
import json
data = json.load(open('validation_results.json'))
scores = [d.get('content_validation', {}).get('confidence_score', 0) 
            for s in data['results'].values() for d in s['documents']]
print(f'Confidence scores calculated: {len(scores)}/80')
print(f'  High (≥0.8): {sum(1 for s in scores if s >= 0.8)}')
print(f'  Medium (0.5-0.8): {sum(1 for s in scores if 0.5 <= s < 0.8)}')
print(f'  Low (<0.5): {sum(1 for s in scores if s < 0.5)}')
"

# Verify progress.txt updated
grep "URL validation" progress.txt

# All reports referenced in features.txt
grep -i "validation" features.txt
```

---

## Success Criteria

- [x] UV dependencies added to validate_urls.py (httpx, orjson, pypdf)
- [ ] All 80 URLs validated successfully
- [ ] Content validation implemented (PDF text extraction, confidence scoring)
- [ ] validation_results.json created and valid with content_validation fields
- [ ] Summary report generated (URL_VALIDATION_SUMMARY.md) with content statistics
- [ ] State-by-state report generated (URL_VALIDATION_BY_STATE.md) with confidence scores
- [ ] Priority list created (URL_UPDATE_PRIORITIES.md) including wrong-document URLs
- [ ] Wrong-document URLs identified (confidence < 0.5)
- [ ] Manual verification completed (90%+ accuracy including content checks)
- [ ] progress.txt updated with completion log
- [ ] All changes committed with proper messages
- [ ] No data corruption or validation errors
- [ ] Clear next steps documented

**Definition of "Done":**

This plan is complete when:
- All 80 URLs have HTTP validation results
- All 80 URLs have content validation results (confidence scores)
- Wrong-document URLs identified and prioritized
- 3 comprehensive reports generated and committed (including content validation stats)
- Manual verification confirms HTTP and content accuracy (90%+)
- Clear priorities identified for URL updates (including wrong-document detection)
- Ready to proceed with Plan 2 (workflow documentation)
- All 80 URLs have validation results
- 3 comprehensive reports generated and committed
- Manual verification confirms accuracy
- Clear priorities identified for URL updates
- Ready to proceed with Plan 2 (workflow documentation)

---

## Rollback Plan

### If Validation Fails

**Problem:** validate_urls.py crashes or hangs

**Action:**
1. Check error messages for specific failures
2. Debug individual URL if needed
3. Skip problematic URLs temporarily
4. Document failures for manual review

**Commands:**
```bash
# If validation crashes, check logs
uv run validate_urls.py 2>&1 | tee validation.log

# Manually test single state if needed
python -c "from validate_urls import validate_state; validate_state('OR')"
```

### If Reports Are Incorrect

**Problem:** Generated reports don't match validation_results.json

**Action:**
1. Re-run report generation
2. Fix any parsing logic errors
3. Regenerate from validation_results.json
4. Verify manually

**Commands:**
```bash
# Rollback commits if needed
git revert HEAD~N

# Regenerate reports from valid JSON
# (would need report generation script)
```

### Data Restoration

**If validation_results.json corrupted:**
```bash
# Re-run validation
uv run validate_urls.py

# Restore from git if committed
git restore validation_results.json
```

---

## Notes

### Constraints

1. **Network dependent** - Validation requires internet access to test URLs
2. **Time variable** - URL testing time depends on server response
3. **Rate limiting** - Some servers may rate-limit requests
4. **Manual verification required** - Automated validation not 100% accurate
5. **PDF text extraction** - Content validation requires parsing PDFs, which may fail on encrypted or image-based PDFs
6. **Confidence thresholds** - Thresholds (0.8, 0.5, 0.3) may need adjustment based on results

### Risks

1. **State websites may block** - Bot detection could prevent validation
2. **URLs may change during validation** - Remote possibility
3. **Large file downloads** - PDFs may be large, increasing validation time
4. **Timeout issues** - Slow servers may cause timeouts
5. **Content validation false positives** - Some valid PDFs may not contain grade/state names in first 5 pages
6. **Content validation false negatives** - Some wrong documents may coincidentally contain expected keywords
7. **PDF parsing errors** - Encrypted, scanned, or corrupted PDFs may fail text extraction

### Dependencies for Next Plans

**Plan 2 (Workflow Documentation) depends on:**
- validation_results.json exists
- Priority list identifies which states need updates (including wrong-document URLs)
- Validation accuracy confirmed (both HTTP and content)
- Wrong-document URLs identified for special handling in URL research workflow

**Plan 3 (Apply Updates) depends on:**
- Plan 1 complete (this plan)
- Plan 2 complete (workflow documentation)
- Research complete for Tier 1 states

---

## Potential Blockers

**STOP and alert human if:**

- Validation crashes on >10% of URLs (systematic failure)
- All nextgenscience.org URLs fail (external hosting issue)
- Manual verification accuracy <80% (validation logic issues)
- Critical infrastructure states all broken (>5 states with 100% failure)
- Rate limiting encountered from multiple state servers
- Network connectivity issues prevent testing
- **Content validation fails on >20% of documents** (PDF extraction or logic issues)
- **Confidence scores all <0.5 for known-good URLs** (thresholds too strict)
- **Confidence scores all >0.8 for known-bad URLs** (thresholds too lenient)

**When blocked:**
1. Document specific failure condition
2. Log to progress.txt
3. Preserve validation_results.json if partial
4. Alert human with details including content validation error logs
5. Wait for intervention

---

**Ready for execution approval**
**Prerequisites verified, waiting for /execute-next command**
