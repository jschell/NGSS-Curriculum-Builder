# Plan: Validate Remaining 36 States URLs

**Status:** Not Started
**Created:** 2026-02-04
**Estimated Duration:** 6-8 hours
**Priority:** High

---

## Context

After successfully verifying 15 states (40 documents) with working URLs, 36 states remain unverified (40 documents). This plan validates all remaining state URLs, identifies broken links, and applies fixes where needed to achieve 100% URL coverage.

**Current State:**
- ✅ 15 states verified with metadata (29.4%)
- ✅ 40/80 documents with url_source and last_verified
- ❌ 36 states unverified (70.6%)
- ❌ 40 documents without metadata
- ✅ Validation infrastructure exists (validate_urls.py)
- ✅ Update workflow documented

**Goal:** Validate all 36 remaining states, update broken URLs, add metadata to all 80 documents.

---

## Prerequisites

- [x] validate_urls.py exists and functional (434 lines)
- [x] URL_RESEARCH_WORKFLOW.md documented
- [x] JSON_UPDATE_GUIDE.md safety procedures exist
- [x] data/states.json.backup exists
- [x] 15 states already verified (reference examples)
- [ ] List of 36 unverified states identified
- [ ] Validation ready to run on subset

**Verification:**
```bash
# Verify backup exists
ls -lh data/states.json.backup

# Verify validation script exists
ls -lh validate_urls.py

# Count unverified states
python -c "
import json
data = json.load(open('data/states.json'))
unverified = [abbr for abbr, state in data.items()
              if not any('url_source' in doc for doc in state.get('documents', []))]
print(f'Unverified states: {len(unverified)}')
print(', '.join(sorted(unverified)))
"
# Expected: 36 states
```

---

## Implementation Steps

### Step 1: Create Unverified States List

**Action:** Generate list of 36 unverified states for targeted validation

**Files to create:** `docs/unverified_states_list.md`

**Process:**
1. Read states.json
2. Identify states without url_source metadata
3. Count documents per state
4. Categorize by document count (single vs multi-doc)
5. Create validation checklist

**Document structure:**
```markdown
# Unverified States List

**Total:** 36 states (40 documents)
**Created:** 2026-02-04

## Single Document States (34 states)
- AK (Alaska) - 1 doc
- AL (Alabama) - 1 doc
- AR (Arkansas) - 1 doc
[... list all ...]

## Multiple Document States (2 states)
- MT (Montana) - 2 docs
- NJ (New Jersey) - 2 docs
- PA (Pennsylvania) - 2 docs

## Validation Priority Order
1. Single-doc states (quick wins)
2. Multi-doc states (more complex)
```

**Tests required:**
- Count matches 36 states
- Count matches 40 documents
- No verified states included

**Validation:**
```bash
# Verify list created
ls -lh docs/unverified_states_list.md

# Verify state count
grep "^- [A-Z][A-Z]" docs/unverified_states_list.md | wc -l
# Expected: 36
```

**Commit message:** `docs(validation): create list of 36 unverified states for validation`

**Expected duration:** 10 minutes

---

### Step 2: Run Validation on Unverified States

**Action:** Execute validate_urls.py on 36 unverified states only

**Files to create:** `validation_results_remaining_36.json`

**Modify validate_urls.py temporarily to filter:**
```python
# Add filter for unverified states only
UNVERIFIED_STATES = ['AK', 'AL', 'AR', 'AZ', 'CO', 'CT', 'FL', 'GA',
                     'ID', 'IN', 'LA', 'MA', 'MD', 'ME', 'MN', 'MO',
                     'MS', 'MT', 'NC', 'ND', 'NE', 'NH', 'NJ', 'NV',
                     'OH', 'OK', 'PA', 'RI', 'SC', 'SD', 'TN', 'UT',
                     'VA', 'WI', 'WV', 'WY']

# In main validation loop:
for state_abbr, state_data in states_data.items():
    if state_abbr not in UNVERIFIED_STATES:
        continue  # Skip verified states
    # ... validation code ...
```

**Command:**
```bash
uv run validate_urls.py --output validation_results_remaining_36.json
```

**Tests required:**
- Validation completes without crashes
- 36 states tested
- 40 URLs tested
- JSON output valid
- HTTP status codes recorded
- Content validation performed (confidence scores)

**Validation:**
```bash
# Verify results file created
ls -lh validation_results_remaining_36.json

# Verify JSON valid
python -m json.tool validation_results_remaining_36.json > /dev/null

# Count states validated
python -c "
import json
data = json.load(open('validation_results_remaining_36.json'))
print(f'States validated: {len(data.get(\"results\", {}))}')
"
# Expected: 36

# Count URLs tested
python -c "
import json
data = json.load(open('validation_results_remaining_36.json'))
url_count = sum(len(s['documents']) for s in data['results'].values())
print(f'URLs tested: {url_count}')
"
# Expected: 40
```

**Commit message:** `test(validation): validate URLs for remaining 36 unverified states`

**Expected duration:** 30-45 minutes (network dependent)

---

### Step 3: Generate Validation Report for 36 States

**Action:** Create human-readable summary of validation results

**Files to create:** `docs/VALIDATION_REMAINING_36_SUMMARY.md`

**Report structure:**
```markdown
# Validation Summary - Remaining 36 States

**Date:** 2026-02-04
**States Tested:** 36
**Documents Tested:** 40

## Overall Results

- ✅ Working URLs: X (X%)
- ❌ Broken URLs (404/403): X (X%)
- ⚠️  Wrong Format (HTML): X (X%)
- 🔍 High Confidence (≥0.8): X (X%)
- ⚠️  Low Confidence (<0.5): X (X%)

## States by Status

### All Working (No Action Needed)
[List states with all URLs working, confidence ≥ 0.8]

### Partial Issues (Some Broken)
[List states with some broken URLs]

### Critical (All Broken)
[List states with all URLs broken]

### Wrong Document (Low Confidence)
[List states where URLs return 200 but wrong content]

## Next Actions

1. Fix critical states (all broken)
2. Research partial states
3. Verify low-confidence URLs
4. Add metadata to working URLs
```

**Tests required:**
- All 36 states categorized
- Statistics accurate
- Actionable next steps clear

**Validation:**
```bash
# Verify report created
ls -lh docs/VALIDATION_REMAINING_36_SUMMARY.md

# Manual review: Read summary, verify makes sense
head -50 docs/VALIDATION_REMAINING_36_SUMMARY.md
```

**Commit message:** `docs(validation): generate summary report for 36 remaining states`

**Expected duration:** 20 minutes

---

### Step 4: Fix Working URLs (Add Metadata Only)

**Action:** For states where URLs already work (HTTP 200, confidence ≥ 0.8), add metadata without changing URLs

**Files to modify:** `data/states.json`

**Process:**
1. Identify states with working URLs from validation report
2. For each working URL:
   - Keep existing URL (don't change)
   - Add url_source field (document where URL was found)
   - Add last_verified: "2026-02-04"
3. Update states.json
4. Validate JSON syntax
5. Test CLI

**Example change:**
```json
{
  "AL": {
    "documents": [
      {
        "title": "Alabama Science Standards",
        "url": "https://existing-working-url.pdf",  // UNCHANGED
        "url_source": "Alabama DOE Science Standards page",  // ADDED
        "last_verified": "2026-02-04",  // ADDED
        "grade_levels": ["K", "1", "2", ...],
        // ... other fields unchanged
      }
    ]
  }
}
```

**Tests required:**
- JSON syntax valid
- 51 states still present
- 80 documents still present
- No URLs changed (only metadata added)
- CLI commands work

**Validation:**
```bash
# Validate JSON
python -m json.tool data/states.json > /dev/null && echo "✓ Valid JSON"

# Verify counts unchanged
python -c "
import json
data = json.load(open('data/states.json'))
print(f'States: {len(data)}')
print(f'Docs: {sum(len(s[\"documents\"]) for s in data.values())}')
"
# Expected: 51 states, 80 docs

# Test CLI
python state_science_standards_system.py list | head -10
python state_science_standards_system.py state AL

# Count states with metadata (should increase)
python -c "
import json
data = json.load(open('data/states.json'))
with_metadata = sum(1 for s in data.values()
                    if any('url_source' in d for d in s.get('documents', [])))
print(f'States with metadata: {with_metadata}')
"
# Expected: > 15 (was 15 before)
```

**Commit message:** `chore(data): add url_source and last_verified metadata to working URLs in [X] states`

**Expected duration:** 30 minutes

---

### Step 5: Research and Fix Broken URLs (Batch 1)

**Action:** Research and update URLs for first batch of broken states (5-10 states)

**Files to modify:**
- `data/states.json`
- `docs/url_updates/[STATE]-[doc-slug].md` (create per state)

**Process:**
1. Select 5-10 critical states from validation report (all broken)
2. For each state:
   - Follow URL_RESEARCH_WORKFLOW.md
   - Visit state education website
   - Find working PDF URLs
   - Document in url_updates/ template
   - Update states.json with new URL + metadata
   - Verify URL works (HTTP 200, correct content)
3. Commit after each state or small batch

**Tests required:**
- New URLs return HTTP 200
- Content type is application/pdf
- File size reasonable (> 50 KB)
- CLI works with updated URLs
- Parser can fetch new URLs

**Validation:**
```bash
# After each state update, test the URL
NEW_URL="[paste URL]"
curl -I "$NEW_URL" | grep "HTTP"
# Expected: HTTP/2 200

curl -I "$NEW_URL" | grep -i "content-type"
# Expected: application/pdf

# Test CLI
python state_science_standards_system.py state [STATE]

# Test parser (optional)
uv run parse_standards.py [STATE]
```

**Commit message:** `fix(data): update [STATE] science standards URL with verified working link`

**Expected duration:** 2-4 hours (variable, 20-40 min per state)

**STOP CONDITION:** If 3 consecutive states have no working URLs found, stop and alert human

---

### Step 6: Research and Fix Broken URLs (Batch 2)

**Action:** Continue fixing remaining broken states (next 5-10 states)

**Process:** Same as Step 5, continue with next batch

**Expected duration:** 2-4 hours

---

### Step 7: Handle Edge Cases

**Action:** Address states with special issues (wrong format, low confidence, etc.)

**Files to modify:** `data/states.json`

**Edge cases to handle:**
1. **HTML instead of PDF:** Find PDF version or document HTML URL appropriately
2. **Low confidence URLs:** Manually verify content, update if wrong
3. **Redirects:** Update to final redirect URL
4. **No working URL found:** Document as known issue, add note field

**Example for no working URL:**
```json
{
  "url": "https://last-known-url.pdf",  // Keep last known
  "url_source": "Historical record",
  "last_verified": "2026-02-04",
  "url_status": "broken",  // NEW field
  "notes": "URL returns 404 as of 2026-02-04, requires manual research"  // NEW field
}
```

**Tests required:**
- All 36 states accounted for
- No states left in limbo
- Edge cases documented

**Validation:**
```bash
# Verify all 36 states have metadata
python -c "
import json
data = json.load(open('data/states.json'))
unverified_states = ['AK', 'AL', 'AR', ...]  # Original 36
missing = []
for state in unverified_states:
    docs = data[state]['documents']
    if not any('url_source' in d for d in docs):
        missing.append(state)
print(f'States still missing metadata: {len(missing)}')
if missing:
    print('Missing:', ', '.join(missing))
"
# Expected: 0 missing
```

**Commit message:** `fix(data): handle edge cases for remaining unverified states, document known issues`

**Expected duration:** 1-2 hours

---

### Step 8: Generate Final Validation Report

**Action:** Create comprehensive final report showing 100% coverage

**Files to create:** `docs/URL_VALIDATION_FINAL_2026-02-04.md`

**Report structure:**
```markdown
# Final URL Validation Report

**Date:** 2026-02-04
**Total States:** 51
**Total Documents:** 80

## Validation Coverage

- ✅ States Verified: 51/51 (100%)
- ✅ Documents with Metadata: 80/80 (100%)
- ✅ Working URLs: X/80 (X%)
- ❌ Broken URLs: X/80 (X%)
- ⚠️  Known Issues: X states

## Before This Plan
- States verified: 15 (29.4%)
- Documents with metadata: 40 (50%)

## After This Plan
- States verified: 51 (100%) ✅
- Documents with metadata: 80 (100%) ✅

## States Updated in This Session (36 states)
[List all 36 states with status]

## Known Issues Remaining
[List states with broken URLs that couldn't be fixed]

## Recommendations
1. Periodic re-validation (every 3-6 months)
2. Monitor known broken URLs for updates
3. Consider document caching for critical states
```

**Tests required:**
- Report accurately reflects final state
- All 51 states accounted for
- Statistics match data/states.json

**Validation:**
```bash
# Verify all 51 states have metadata
python -c "
import json
data = json.load(open('data/states.json'))
all_states = list(data.keys())
with_metadata = [s for s in all_states
                 if any('url_source' in d for d in data[s].get('documents', []))]
print(f'States with metadata: {len(with_metadata)}/51')
"
# Expected: 51/51

# Count working vs broken URLs
python -c "
import json
data = json.load(open('data/states.json'))
broken = sum(1 for s in data.values()
            for d in s.get('documents', [])
            if d.get('url_status') == 'broken')
total = sum(len(s['documents']) for s in data.values())
print(f'Broken URLs: {broken}/{total}')
print(f'Working URLs: {total-broken}/{total}')
"
```

**Commit message:** `docs(validation): final validation report - 100% state coverage achieved`

**Expected duration:** 20 minutes

---

### Step 9: Update Project Documentation

**Action:** Update all project docs to reflect 100% validation coverage

**Files to modify:**
- `progress.txt` - Log completion
- `features.txt` - Mark as done
- `docs/PROJECT_STATUS_2026-02-04.md` - Update statistics

**Updates:**

**progress.txt:**
```
2026-02-04 HH:MM - Completed validation of remaining 36 states
2026-02-04 HH:MM - Added metadata to all 40 remaining documents
2026-02-04 HH:MM - Fixed X broken URLs, documented Y known issues
2026-02-04 HH:MM - Achieved 100% state validation coverage (51/51)
2026-02-04 HH:MM - Achieved 100% document metadata coverage (80/80)
```

**features.txt:**
```markdown
## Done
...
✓ Validate remaining 36 states URLs
```

**PROJECT_STATUS:**
- Update "States Verified: 51/51 (100%)"
- Update "Documents with Metadata: 80/80 (100%)"
- Update statistics section

**Tests required:**
- All docs updated accurately
- No conflicting information

**Validation:**
```bash
# Verify progress.txt updated
grep "36 states" progress.txt

# Verify features.txt updated
grep "✓.*36 states" features.txt

# Verify PROJECT_STATUS updated
grep "51/51 (100%)" docs/PROJECT_STATUS_2026-02-04.md
```

**Commit message:** `docs(summary): update project docs with 100% validation coverage`

**Expected duration:** 15 minutes

---

## Validation Strategy

### After Each State Update
```bash
# JSON validity
python -m json.tool data/states.json > /dev/null

# Data integrity
python -c "import json; data=json.load(open('data/states.json'));
           print(f'{len(data)} states, {sum(len(s[\"documents\"]) for s in data.values())} docs')"

# CLI works
python state_science_standards_system.py list | head -5
python state_science_standards_system.py state [UPDATED_STATE]
```

### After Each Batch
```bash
# Full validation suite
python -m json.tool data/states.json > /dev/null && echo "✓ JSON valid"
python state_science_standards_system.py list > /dev/null && echo "✓ CLI works"

# Verify no data loss
python -c "
import json
data = json.load(open('data/states.json'))
assert len(data) == 51, 'State count wrong'
assert sum(len(s['documents']) for s in data.values()) == 80, 'Doc count wrong'
print('✓ Data integrity maintained')
"

# Count progress
python -c "
import json
data = json.load(open('data/states.json'))
with_metadata = sum(1 for s in data.values()
                   if any('url_source' in d for d in s.get('documents', [])))
print(f'Progress: {with_metadata}/51 states verified')
"
```

### Final Validation
```bash
# Comprehensive check
python -c "
import json
data = json.load(open('data/states.json'))

# Counts
assert len(data) == 51
assert sum(len(s['documents']) for s in data.values()) == 80

# Metadata coverage
states_with_metadata = sum(1 for s in data.values()
                          if any('url_source' in d for d in s.get('documents', [])))
docs_with_metadata = sum(1 for s in data.values()
                        for d in s.get('documents', [])
                        if 'url_source' in d and 'last_verified' in d)

print(f'✓ All checks passed')
print(f'✓ States: {len(data)}')
print(f'✓ Documents: {sum(len(s[\"documents\"]) for s in data.values())}')
print(f'✓ States with metadata: {states_with_metadata}/51')
print(f'✓ Docs with metadata: {docs_with_metadata}/80')
"

# Full CLI test suite
python state_science_standards_system.py list
python state_science_standards_system.py search 5
python state_science_standards_system.py compare 3
```

---

## Success Criteria

- [ ] List of 36 unverified states created
- [ ] Validation run on all 36 states (40 documents)
- [ ] Validation report generated
- [ ] Metadata added to all working URLs
- [ ] Broken URLs researched and fixed (best effort)
- [ ] Edge cases handled (HTML, redirects, no URL found)
- [ ] 100% metadata coverage achieved (51/51 states)
- [ ] All 80 documents have url_source and last_verified
- [ ] Final validation report created
- [ ] Project documentation updated
- [ ] JSON valid, CLI functional
- [ ] No data loss or corruption

**Definition of "Done":**

This plan is complete when:
- All 36 states have been validated
- All 80 documents have url_source and last_verified metadata
- 51/51 states verified (100% coverage)
- Broken URLs fixed where possible, documented where not
- Final validation report shows complete status
- All documentation updated

---

## Rollback Plan

### If JSON Corrupted
```bash
# Restore from backup
cp data/states.json.backup data/states.json

# Verify restoration
python -m json.tool data/states.json > /dev/null && echo "✓ Restored"
```

### If CLI Breaks
```bash
# Test with backup
mv data/states.json data/states.json.broken
cp data/states.json.backup data/states.json

# Test CLI
python state_science_standards_system.py list

# If works, issue is in recent changes
# Revert last commit or fix manually
```

### Git Rollback
```bash
# Revert last commit
git revert HEAD

# Or reset to safe state
git reset --hard <safe-commit>

# Restore backup
cp data/states.json.backup data/states.json
```

---

## Notes

### Constraints
1. **Manual research required** - Each broken URL needs human investigation
2. **Time variable** - Some states quick (15 min), some slow (90+ min)
3. **Not all URLs fixable** - Some states may have no working URL available
4. **Network dependent** - Validation requires internet access

### Risks
1. **State websites may be down** - Temporary outages during research
2. **URLs may require authentication** - Some states use login portals
3. **PDF formats vary** - Content validation may fail on some PDFs
4. **Research time uncertainty** - Hard to predict exact duration

### Batching Strategy
- **Batch 1:** States with working URLs (quick, metadata only)
- **Batch 2:** States with broken URLs (research required)
- **Batch 3:** Edge cases (HTML, redirects, etc.)

Commit frequently (after each state or small batch) to preserve progress.

---

## Potential Blockers

**STOP and alert human if:**

- 5+ consecutive states have no working URLs (systematic issue)
- State education websites require authentication (access barrier)
- Validation script crashes repeatedly (tool issue)
- JSON corruption despite validation (data integrity issue)
- Research time exceeds 2 hours per state (complexity too high)
- More than 10 states have unavoidable broken URLs (data quality issue)

**When blocked:**
1. Document specific blocker
2. Preserve current working state
3. Commit completed work
4. Update docs with blocker info
5. Alert human with details
6. Do NOT proceed until resolved

---

**Ready for execution approval**
**Prerequisites verified, waiting for /execute-next or /work command**
**Estimated total time: 6-8 hours (variable based on URL research needs)**
