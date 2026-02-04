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
- [ ] UV dependencies added to validate_urls.py
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
```

---

## Implementation Steps

### Step 1: Add UV Inline Dependencies to validate_urls.py

**Action:** Add UV dependency markers for httpx and orjson at top of validate_urls.py

**Files to modify:** `validate_urls.py`

**Changes needed:**
Add after the shebang line (line 1-2):
```python
#!/usr/bin/env python3
# /// script
# dependencies = [
#     "httpx>=0.27.0",
#     "orjson>=3.9.0",
# ]
# ///
# -*- coding: utf-8 -*-
```

**Tests required:** None (syntax-only change)

**Validation:**
```bash
# Verify UV can parse dependencies
uv run validate_urls.py --help 2>&1 | head -5
# Should not show "ModuleNotFoundError: No module named 'httpx'"

# Verify script loads without errors
uv run python -c "import sys; sys.path.insert(0, '.'); exec(open('validate_urls.py').read().split('if __name__')[0])"
```

**Commit message:** `fix(validation): add UV inline dependencies for httpx and orjson`

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

## By Status Code

- HTTP 200 (OK): XX
- HTTP 403 (Forbidden): XX
- HTTP 404 (Not Found): XX
- HTTP 301/302 (Redirect): XX
- Other errors: XX

## States Requiring Attention

### Critical (All Documents Broken)
- [List states]

### Partial Issues (Some Documents Broken)
- [List states]

### All Working
- [List states]

## Next Steps
1. Investigate critical states first
2. Research current state education websites
3. Find replacement URLs
4. Document findings
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
- ✅ Working: 3
- ❌ Broken: 0

#### Document: [Title]
- **URL:** [URL]
- **Status:** ✅ Working
- **HTTP Status:** 200
- **Content Type:** application/pdf
- **File Size:** XXX KB

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

## Tier 1: Critical - All Documents Broken (Highest Priority)

### Washington (WA)
- **Documents Affected:** 3/3 (100%)
- **Issue:** HTTP 403 Forbidden
- **Root Cause:** Possible bot detection on OSPI website
- **Recommended Action:** Manual investigation, download documents, find alternative hosting
- **Estimated Effort:** 2-3 hours

[... repeat for other Tier 1 states ...]

## Tier 2: Partial - Some Documents Broken

### California (CA)
- **Documents Affected:** 2/5 (40%)
- **Issue:** Mixed - some 404, some working
- **Root Cause:** URLs changed on CDE website
- **Recommended Action:** Check current CDE science standards page
- **Estimated Effort:** 1 hour

[... repeat for other Tier 2 states ...]

## Tier 3: Working with Warnings

### States with Redirects (Still Working)
- [List states where URLs redirect but work]
- **Recommended Action:** Update to final redirect URL
- **Estimated Effort:** 15 min per state

## Tier 4: All Working - No Action Needed

- [List states with 100% working URLs]
- Total: XX states

## Summary

- **Tier 1 (Critical):** X states, Y documents - Immediate attention
- **Tier 2 (Partial):** X states, Y documents - Medium priority
- **Tier 3 (Warnings):** X states, Y documents - Low priority
- **Tier 4 (Working):** X states - No action needed

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

# Verify progress.txt updated
grep "URL validation" progress.txt

# All reports referenced in features.txt
grep -i "validation" features.txt
```

---

## Success Criteria

- [x] UV dependencies added to validate_urls.py
- [ ] All 80 URLs validated successfully
- [ ] validation_results.json created and valid
- [ ] Summary report generated (URL_VALIDATION_SUMMARY.md)
- [ ] State-by-state report generated (URL_VALIDATION_BY_STATE.md)
- [ ] Priority list created (URL_UPDATE_PRIORITIES.md)
- [ ] Manual verification completed (90%+ accuracy)
- [ ] progress.txt updated with completion log
- [ ] All changes committed with proper messages
- [ ] No data corruption or validation errors
- [ ] Clear next steps documented

**Definition of "Done":**

This plan is complete when:
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

### Risks

1. **State websites may block** - Bot detection could prevent validation
2. **URLs may change during validation** - Remote possibility
3. **Large file downloads** - PDFs may be large, increasing validation time
4. **Timeout issues** - Slow servers may cause timeouts

### Dependencies for Next Plans

**Plan 2 (Workflow Documentation) depends on:**
- validation_results.json exists
- Priority list identifies which states need updates
- Validation accuracy confirmed

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

**When blocked:**
1. Document specific failure condition
2. Log to progress.txt
3. Preserve validation_results.json if partial
4. Alert human with details
5. Wait for intervention

---

**Ready for execution approval**
**Prerequisites verified, waiting for /execute-next command**
