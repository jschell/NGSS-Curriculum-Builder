# Plan: Document URL Update Workflow

**Status:** Not Started
**Created:** 2026-02-04
**Estimated Duration:** 1 hour
**Priority:** High
**Depends On:** Plan 1 (URL Validation Execution) must be complete

---

## Context

After validating all 80 URLs (Plan 1), we need clear documentation for how to apply URL updates to `data/states.json` safely. This plan creates templates, workflows, and guides to ensure URL updates maintain data integrity and follow project standards.

**Current State:**
- ✅ URL validation complete (Plan 1)
- ✅ Broken URLs identified with priorities
- ❌ No documented workflow for applying updates
- ❌ No templates for documenting URL fixes
- ❌ No JSON update guide

**Goal:** Create comprehensive documentation so URL updates can be applied safely and systematically.

---

## Prerequisites

- [x] Plan 1 (URL Validation Execution) complete
- [x] validation_results.json exists
- [x] URL_UPDATE_PRIORITIES.md exists
- [x] Identified which states need URL updates
- [ ] Update workflow documented
- [ ] Update templates created
- [ ] JSON modification guide created

**Verification:**
```bash
# Verify Plan 1 outputs exist
ls -lh validation_results.json docs/URL_UPDATE_PRIORITIES.md docs/URL_VALIDATION_SUMMARY.md

# Verify validation identified broken URLs
python -c "import json; data=json.load(open('validation_results.json')); broken = sum(1 for s in data['results'].values() for d in s['documents'] if d.get('http_status', 0) >= 400); print(f'Broken URLs: {broken}')"
# Should show > 0
```

---

## Implementation Steps

### Step 1: Create URL Update Documentation Template

**Action:** Create template for documenting each URL fix

**Files to create:** `docs/templates/url_update_template.md`

**Template content:**
```markdown
# URL Update: [State Abbreviation] - [State Name]

## Document: [Document Title]

### Current URL (Broken)
```
[Current broken URL from states.json]
```

**Validation Result:**
- HTTP Status: [404/403/500/etc]
- Content Type: [what was returned]
- File Size: [size or "not retrieved"]
- Error: [description of issue]

---

### Research Process

**Date Researched:** YYYY-MM-DD
**Researcher:** [Name or "Claude Code"]

**Steps Taken:**
1. Visited [state education agency website]
2. Navigated to [science/standards section]
3. Found [current standards page]
4. Located [document download link]

**Official Source Page:** [URL of page containing the document link]

---

### Proposed URL (Working)
```
[New working URL]
```

**Verification:**
- HTTP Status: 200 OK
- Content Type: application/pdf
- File Size: [size in KB/MB]
- Verification Date: YYYY-MM-DD
- Verified By: [Manual browser test / validation script]

---

### Changes to states.json

**JSON Patch:**
```json
{
  "state": "[STATE_ABBREV]",
  "document_index": [0-based index],
  "changes": {
    "url": "[new URL]",
    "url_source": "[official source page]",
    "last_verified": "YYYY-MM-DD"
  }
}
```

---

### Additional Notes

- **Redirects:** [List redirect chain if any]
- **Alternative Sources:** [Other places document can be found]
- **Future Monitoring:** [Any concerns about URL stability]
- **Special Requirements:** [Access restrictions, file size, etc.]

---

### Approval Checklist

- [ ] New URL tested manually in browser
- [ ] PDF downloads and opens correctly
- [ ] Content matches expected grade levels
- [ ] URL is from official state education source
- [ ] No authentication or paywall required
- [ ] File size reasonable (< 50 MB)
- [ ] states.json backup created before update
```

**Tests required:**
- Template renders correctly as markdown
- All placeholders clearly marked
- Format is consistent and complete

**Validation:**
```bash
# Verify template created
ls -lh docs/templates/url_update_template.md

# Check template is valid markdown (opens without errors)
head -50 docs/templates/url_update_template.md
```

**Commit message:** `docs(templates): create URL update documentation template for tracking fixes`

**Expected duration:** 15 minutes

---

### Step 2: Create JSON Update Safety Guide

**Action:** Document safe practices for modifying states.json

**Files to create:** `docs/JSON_UPDATE_GUIDE.md`

**Guide structure:**
```markdown
# JSON Update Safety Guide

## ⚠️ Critical Rules

1. **ALWAYS backup before editing:** `cp data/states.json data/states.json.backup`
2. **NEVER edit JSON manually:** Use scripts or careful text editor
3. **ALWAYS validate after changes:** `python -m json.tool data/states.json`
4. **ALWAYS test after updates:** `python state_science_standards_system.py list`
5. **ALWAYS commit working state:** Don't leave JSON broken

## Pre-Update Checklist

- [ ] Create backup: `cp data/states.json data/states.json.backup`
- [ ] Document planned changes in url_update_template.md
- [ ] Verify new URLs work (manual browser test)
- [ ] Read current JSON structure for state
- [ ] Plan exact changes needed

## Update Methods

### Method 1: Direct Edit (Small Changes)

**When to use:** 1-2 URLs, simple updates

**Steps:**
1. Open states.json in text editor
2. Search for state abbreviation
3. Find document by title
4. Update URL field only
5. Add/update last_verified and url_source
6. Save file
7. Validate JSON
8. Test CLI

**Example:**
```json
{
  "WA": {
    "documents": [
      {
        "title": "Washington State K-12 Science Learning Standards",
        "url": "https://NEW-WORKING-URL.pdf",  // CHANGED
        "url_source": "https://ospi.k12.wa.us/science/",  // ADDED
        "last_verified": "2026-02-04",  // ADDED
        "grade_levels": ["K", "1", ...],
        // ... all other fields unchanged
      }
    ]
  }
}
```

### Method 2: Python Script (Batch Updates)

**When to use:** 5+ URLs, systematic updates

**Script template:**
```python
#!/usr/bin/env python3
import json
from pathlib import Path

# Load data
with open('data/states.json', 'r') as f:
    states = json.load(f)

# Define updates
updates = [
    {
        'state': 'WA',
        'doc_title': 'Washington State K-12 Science Learning Standards',
        'new_url': 'https://NEW-URL.pdf',
        'url_source': 'https://ospi.k12.wa.us/science/',
    },
    # ... more updates
]

# Apply updates
for update in updates:
    state_data = states[update['state']]
    for doc in state_data['documents']:
        if doc['title'] == update['doc_title']:
            doc['url'] = update['new_url']
            doc['url_source'] = update['url_source']
            doc['last_verified'] = '2026-02-04'
            print(f"Updated: {update['state']} - {doc['title']}")

# Save
with open('data/states.json', 'w') as f:
    json.dump(states, f, indent=2)
print("Updates complete. Run validation.")
```

## Validation Commands

### JSON Syntax Check
```bash
python -m json.tool data/states.json > /dev/null && echo "✓ JSON valid"
```

### CLI Functionality Test
```bash
# List all states
python state_science_standards_system.py list

# Test specific updated state
python state_science_standards_system.py state WA

# Test grade query
python state_science_standards_system.py search 5
```

### Data Integrity Checks
```bash
# Verify state count still 51
python -c "import json; print(len(json.load(open('data/states.json'))))"
# Expected: 51

# Verify document count unchanged (or note expected changes)
python -c "import json; data=json.load(open('data/states.json')); print(sum(len(s['documents']) for s in data.values()))"
# Expected: 80 (or document expected total)

# Verify no null URLs introduced
python -c "import json; data=json.load(open('data/states.json')); nulls = sum(1 for s in data.values() for d in s['documents'] if not d.get('url')); print(f'Documents with null URLs: {nulls}')"
# Expected: 0
```

## Rollback Procedures

### If JSON Becomes Invalid

**Error:** `json.tool` fails or CLI crashes

**Action:**
```bash
# Restore from backup
cp data/states.json.backup data/states.json

# Verify restoration worked
python -m json.tool data/states.json > /dev/null && echo "Restored"

# Re-attempt update more carefully
```

### If Git Commit Needed

**Error:** Changes committed but broken

**Action:**
```bash
# Revert last commit
git revert HEAD

# Or reset to previous commit
git reset --hard HEAD~1

# Restore states.json
git restore data/states.json
```

## Batch Update Strategy

**Recommended approach:** Update in small batches

### Batch Sizes
- **Tier 1 (Critical):** 1-2 states at a time (high complexity)
- **Tier 2 (Partial):** 3-5 states at a time
- **Tier 3 (Warnings):** 5-10 states at a time
- **Tier 4 (Working):** No updates needed

### Between Batches
1. Validate JSON
2. Test CLI
3. Commit changes
4. Update progress.txt
5. Review for issues before next batch

## Common Pitfalls

❌ **Don't:** Edit JSON in basic editor that can't handle large files
❌ **Don't:** Update 20+ URLs at once without testing
❌ **Don't:** Skip validation after changes
❌ **Don't:** Forget to update last_verified timestamp
❌ **Don't:** Remove fields (preserve all existing data)

✅ **Do:** Use VSCode, Sublime, or similar JSON-aware editor
✅ **Do:** Update small batches with validation between
✅ **Do:** Run full test suite after updates
✅ **Do:** Add url_source for auditability
✅ **Do:** Keep backups until changes fully tested
```

**Tests required:**
- Guide covers all safety scenarios
- Rollback procedures are clear
- Examples are accurate
- Commands tested

**Validation:**
```bash
# Verify guide created
ls -lh docs/JSON_UPDATE_GUIDE.md

# Verify markdown renders
head -100 docs/JSON_UPDATE_GUIDE.md

# Test validation commands in guide work
python -m json.tool data/states.json > /dev/null && echo "Commands work"
```

**Commit message:** `docs(workflow): create JSON update safety guide with validation and rollback procedures`

**Expected duration:** 25 minutes

---

### Step 3: Document URL Research Workflow

**Action:** Create step-by-step guide for researching replacement URLs

**Files to create:** `docs/URL_RESEARCH_WORKFLOW.md`

**Workflow content:**
```markdown
# URL Research Workflow

## Purpose

When validation identifies broken URLs, this workflow guides the research process to find working replacements from official state sources.

## Research Process

### Step 1: Identify Target State and Document

**Input:** URL_UPDATE_PRIORITIES.md (from Plan 1)

**Select state from priority list:**
- Start with Tier 1 (critical) states
- Work down to Tier 2, Tier 3 as needed

**Example:**
```
State: Washington (WA)
Document: Washington State K-12 Science Learning Standards
Current URL: https://ospi.k12.wa.us/... (403 Forbidden)
Priority: Tier 1 (Critical)
```

---

### Step 2: Visit State Education Agency Website

**Find the official state education website:**

**Common patterns:**
- `[state]education.gov` or `education.[state].gov`
- `k12.[state].us` or `[state].k12.us`
- `doe.[state].gov` (Department of Education)
- `dpi.[state].gov` (Department of Public Instruction)

**For Washington example:**
- Agency: Office of Superintendent of Public Instruction (OSPI)
- Website: https://ospi.k12.wa.us

**Navigation tips:**
- Look for "Standards" or "Curriculum" section
- Find "Science" or "Science Standards"
- Check "Educator Resources" or "Instructional Materials"

---

### Step 3: Locate Science Standards Page

**Common page structures:**
- `/student-success/learning-standards-instructional-materials/science/`
- `/academics/standards/science/`
- `/curriculum/science-standards/`

**What to look for:**
- "Next Generation Science Standards" (NGSS states)
- "[State] Science Standards" (framework states)
- "K-12 Science Learning Standards"
- Download links for PDF documents

**Document characteristics:**
- Grade levels should match states.json entry
- Official publication from state education agency
- Recent adoption date (match data if possible)

---

### Step 4: Verify Document Match

**Before selecting replacement URL, verify:**

- [ ] Title matches or is equivalent to states.json entry
- [ ] Grade levels match (e.g., K-12, 6-8, etc.)
- [ ] Document type matches (complete K-12 vs grade-specific)
- [ ] File format is PDF (or HTML if specified)
- [ ] Published by official state education agency

**Test the URL:**
```bash
# Test HTTP status
curl -I "[URL]" | grep "HTTP"
# Should show: HTTP/2 200

# Check content type
curl -I "[URL]" | grep -i "content-type"
# Should show: content-type: application/pdf

# Check file size (optional)
curl -I "[URL]" | grep -i "content-length"
```

---

### Step 5: Document Findings

**Use url_update_template.md** (from Step 1)

**Fill in:**
- Current broken URL and validation results
- Research process (which pages visited)
- Official source page URL
- Proposed new working URL
- Verification results
- JSON patch details

**Save as:** `docs/url_updates/[STATE_ABBREV]-[doc-slug].md`

**Example:** `docs/url_updates/WA-k12-science-standards.md`

---

### Step 6: Manual Browser Verification

**Always verify URLs manually:**

1. Open new URL in browser
2. Confirm PDF downloads
3. Open PDF and verify:
   - Document title matches
   - Grade levels are correct
   - Content is science standards (not other subject)
   - Document is complete (not truncated)
4. Note file size and page count

**If PDF won't download:**
- Check for authentication requirements
- Try different browser (some states block certain browsers)
- Check for JavaScript requirements
- Look for alternative download links

---

### Step 7: Research Alternative Sources (If Needed)

**If official state URL broken/unavailable:**

1. **Check nextgenscience.org** (for NGSS states)
   - Many states reference NGSS documents here
   - Look under "NGSS by State"

2. **Check state archives**
   - Look for "archived" or "previous versions"
   - Wayback Machine (archive.org) for old URLs

3. **Check education org repositories**
   - NSTA (National Science Teaching Association)
   - State science teacher associations

4. **Contact state education agency**
   - Email or phone contact
   - Request current standards document link
   - Ask about official hosting

**Document all sources checked:**
- Note which alternatives tried
- Why each was/wasn't suitable
- Final recommendation

---

## Research Documentation Template

For each URL research session, document:

```markdown
## Research Session: [Date]

**State:** [State abbreviation and name]
**Document:** [Title]
**Priority:** Tier [1/2/3/4]
**Researcher:** [Name]

### URLs Checked
1. [State education homepage]
2. [Science standards page]
3. [Alternative source 1]
4. [Alternative source 2]

### Findings
- **Working URL found:** [Yes/No]
- **URL:** [If found]
- **Source:** [Official/Alternative]
- **Confidence:** [High/Medium/Low]

### Issues Encountered
- [List any problems during research]

### Recommendations
- [Next steps or concerns]

### Time Spent
- Research: [X minutes]
- Verification: [Y minutes]
- Documentation: [Z minutes]
- **Total:** [T minutes]
```

---

## Special Cases

### Case 1: State Uses nextgenscience.org Exclusively

**Example:** State has no state-hosted documents

**Action:**
- Verify nextgenscience.org URLs work
- Document external dependency
- Note in states.json with url_source
- Consider mirroring critical documents

### Case 2: State Website Blocks Automated Access

**Example:** 403 Forbidden, but works in browser

**Action:**
- Document access requirements
- Manually download PDF
- Look for alternative official hosting
- Note special handling needed

### Case 3: Standards Recently Updated

**Example:** Current URL is old version, new version exists

**Action:**
- Verify which version is in states.json (check adoption_date)
- If states.json references old version, update to new version
- Note version change in url_update documentation
- Update adoption_date if appropriate

### Case 4: No Working URL Found

**Example:** All sources exhausted, no valid URL

**Action:**
- Document thorough research attempt
- Mark document status as "URL unavailable"
- Flag for human escalation
- Consider manual document procurement
- Do NOT remove from states.json

---

## Batch Research Strategy

**For multiple states:**

1. Group states by education agency pattern
2. Research states with similar structures together
3. Document common patterns for efficiency
4. Take breaks between complex states

**Time estimates:**
- Simple state (working URL, easy to find): 10-15 min
- Medium state (some research needed): 20-30 min
- Complex state (multiple documents, issues): 45-60 min
- Blocked state (access issues, alternatives): 60-90 min

---

## Quality Checklist

Before considering research complete:

- [ ] Official state education source identified
- [ ] Working URL found and tested
- [ ] Document match confirmed
- [ ] URL stability assessed (is it likely to break again?)
- [ ] Research documented in url_update template
- [ ] Alternative sources noted if found
- [ ] Ready for JSON update (Plan 3)
```

**Tests required:**
- Workflow is comprehensive
- Examples are clear
- Special cases covered
- Research template useful

**Validation:**
```bash
# Verify workflow created
ls -lh docs/URL_RESEARCH_WORKFLOW.md

# Create url_updates directory for documentation
mkdir -p docs/url_updates

# Verify directory structure
ls -lh docs/url_updates
```

**Commit message:** `docs(workflow): create comprehensive URL research workflow with special case handling`

**Expected duration:** 20 minutes

---

## Validation Strategy

### After Each Step
- Verify documentation files created
- Check markdown renders correctly
- Ensure examples are accurate
- Test any commands provided

### Final Validation
```bash
# Verify all documentation created
ls -lh docs/templates/url_update_template.md
ls -lh docs/JSON_UPDATE_GUIDE.md
ls -lh docs/URL_RESEARCH_WORKFLOW.md

# Verify directory structure
ls -lh docs/url_updates/

# Verify markdown quality
for file in docs/templates/url_update_template.md docs/JSON_UPDATE_GUIDE.md docs/URL_RESEARCH_WORKFLOW.md; do
  echo "Checking $file..."
  head -20 "$file"
done

# Verify progress.txt updated
grep "URL update workflow" progress.txt
```

---

## Success Criteria

- [ ] URL update template created
- [ ] JSON update safety guide created
- [ ] URL research workflow documented
- [ ] docs/url_updates/ directory created
- [ ] All markdown renders correctly
- [ ] Examples are accurate and tested
- [ ] Commands in guides work correctly
- [ ] progress.txt updated
- [ ] All committed with proper messages
- [ ] Ready for Plan 3 (applying updates)

**Definition of "Done":**

This plan is complete when:
- All 3 documentation files created
- Documentation is comprehensive and clear
- Examples tested and accurate
- Directory structure established
- Committed and ready for URL update execution

---

## Rollback Plan

**If documentation has errors:**
- Git revert commits
- Fix documentation
- Recommit corrected versions

**No data risk:** This plan only creates documentation, no states.json changes

---

## Notes

### Dependencies for Plan 3

Plan 3 (Apply URL Updates) depends on:
- ✅ Plan 1 complete (validation results)
- ✅ Plan 2 complete (this plan - workflow documentation)
- Pending: Research completed for states being updated

### Future Use

This documentation will be used for:
- Initial URL fixes (Plan 3)
- Periodic re-validation
- Adding new states
- Maintaining URL quality over time

---

**Ready for execution approval**
**This plan has no prerequisites beyond Plan 1 completion**
