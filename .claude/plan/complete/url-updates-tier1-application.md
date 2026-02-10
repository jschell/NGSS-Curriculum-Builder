# Plan: Apply Verified URL Updates (Tier 1)

**Status:** Not Started
**Created:** 2026-02-04
**Estimated Duration:** 2-3 hours
**Priority:** High
**Depends On:**
- Plan 1 (URL Validation Execution) complete
- Plan 2 (Workflow Documentation) complete

---

## Context

After validating all 80 URLs (Plan 1) and documenting update workflows (Plan 2), this plan applies verified URL updates to `data/states.json` for Tier 1 states. Tier 1 represents states with critical issues (all documents broken) that require URL research and updates.

**Scope:** Update 5-10 Tier 1 states with verified working URLs

**Current State:**
- ✅ URL validation complete (Plan 1)
- ✅ Broken URLs identified with priorities
- ✅ Update workflow documented (Plan 2)
- ❌ No URLs researched yet
- ❌ No states.json updates applied
- ❌ Data model enhancements not added (last_verified, url_source)

**Goal:** Safely update states.json with verified working URLs for Tier 1 states, maintaining data integrity and backward compatibility.

**Out of Scope:** Tier 2, 3, 4 states (separate plan if needed)

---

## Prerequisites

- [x] Plan 1 complete (validation results exist)
- [x] Plan 2 complete (workflow documentation exists)
- [x] URL_UPDATE_PRIORITIES.md identifies Tier 1 states
- [x] JSON_UPDATE_GUIDE.md created
- [x] URL_RESEARCH_WORKFLOW.md created
- [x] url_update_template.md created
- [ ] Tier 1 states researched (URLs found)
- [ ] states.json backup created
- [ ] Data model enhancement plan

**Verification:**
```bash
# Verify Plan 1 & 2 outputs exist
ls -lh validation_results.json docs/URL_UPDATE_PRIORITIES.md docs/JSON_UPDATE_GUIDE.md

# Verify states.json current state
python -c "import json; data=json.load(open('data/states.json')); print(f'States: {len(data)}, Docs: {sum(len(s[\"documents\"]) for s in data.values())}')"
# Expected: States: 51, Docs: 80

# Verify no backup exists yet (will create in Step 1)
ls data/states.json.backup 2>&1 | grep "No such file"
# Expected: Error (no backup yet)
```

---

## Implementation Steps

### Step 1: Create states.json Backup

**Action:** Create safety backup before any modifications

**Files to create:** `data/states.json.backup`

**Command:**
```bash
cp data/states.json data/states.json.backup
```

**Tests required:**
- Backup file created
- Backup matches original (same size)
- Backup is valid JSON

**Validation:**
```bash
# Verify backup created
ls -lh data/states.json.backup

# Verify sizes match
ls -lh data/states.json data/states.json.backup | awk '{print $5}'

# Verify backup is valid JSON
python -m json.tool data/states.json.backup > /dev/null && echo "✓ Backup valid"

# Verify content matches
diff data/states.json data/states.json.backup && echo "✓ Files identical"
```

**Commit message:** `chore(data): create states.json backup before URL updates`

**Expected duration:** 5 minutes

---

### Step 2: Identify Tier 1 States from Validation

**Action:** Extract Tier 1 state list from URL_UPDATE_PRIORITIES.md

**Files to create:** `docs/tier1_update_plan.md`

**Process:**
1. Read URL_UPDATE_PRIORITIES.md
2. Extract all Tier 1 (Critical) states
3. For each state, note:
   - State abbreviation and name
   - Number of broken documents
   - Error types (403, 404, etc.)
4. Create research checklist

**Document structure:**
```markdown
# Tier 1 URL Update Plan

## States Requiring Research

### [State 1: Abbreviation] - [Name]
- **Documents Affected:** X
- **Issue:** [403 Forbidden / 404 Not Found / etc.]
- **Estimated Research Time:** [30-90 min]
- **Status:** Not Started
- **URL Research Doc:** docs/url_updates/[STATE]-*.md
- **Verification:** Pending

### [State 2: Abbreviation] - [Name]
[... repeat ...]

## Total Scope
- **States:** X
- **Documents:** Y
- **Estimated Time:** Z hours

## Research Order

1. [State] - [reason for priority]
2. [State] - [reason for priority]
[... ordered by complexity/priority ...]
```

**Tests required:**
- All Tier 1 states listed
- Document counts accurate
- Priority order logical

**Validation:**
```bash
# Verify tier1_update_plan.md created
ls -lh docs/tier1_update_plan.md

# Count states in plan
grep "^### " docs/tier1_update_plan.md | wc -l
# Should match Tier 1 count from priorities
```

**Commit message:** `docs(planning): create Tier 1 state update plan with research checklist`

**Expected duration:** 15 minutes

---

### Step 3: Research URLs for First Tier 1 State

**Action:** Research and verify working URL for one Tier 1 state

**Files to create:** `docs/url_updates/[STATE]-[doc-slug].md` (using url_update_template.md)

**Process:**
1. Select highest-priority Tier 1 state from tier1_update_plan.md
2. Follow URL_RESEARCH_WORKFLOW.md
3. Visit state education agency website
4. Locate science standards page
5. Find working document URL
6. Verify URL works (browser test)
7. Document findings in url_update template
8. Fill in all template sections

**Tests required:**
- New URL returns HTTP 200
- Content-Type is application/pdf (or HTML if specified)
- Document downloads successfully
- File size is reasonable (> 50 KB, < 50 MB)
- Document content matches grade levels

**Validation:**
```bash
# Verify URL research doc created
ls -lh docs/url_updates/[STATE]-*.md

# Test new URL (example for WA)
NEW_URL="[paste URL here]"
curl -I "$NEW_URL" | grep "HTTP"
# Expected: HTTP/2 200

curl -I "$NEW_URL" | grep -i "content-type"
# Expected: content-type: application/pdf

# Manual verification: Open URL in browser, confirm PDF downloads
```

**Commit message:** `docs(research): research and verify working URL for [STATE] science standards`

**Expected duration:** 30-90 minutes (depends on state complexity)

**STOP CONDITION:** If no working URL found after 90 min research, flag for human intervention

---

### Step 4: Apply First State URL Update to states.json

**Action:** Update states.json with verified URL for researched state

**Files to modify:** `data/states.json`

**Process:**
1. Read current states.json
2. Locate state entry
3. Find document by title
4. Update URL field
5. Add url_source field (new)
6. Add last_verified field (new)
7. Save with proper formatting
8. Validate JSON syntax
9. Test CLI functionality

**JSON changes (example for WA):**
```json
{
  "WA": {
    "documents": [
      {
        "title": "Washington State K-12 Science Learning Standards",
        "url": "https://NEW-VERIFIED-URL.pdf",  // CHANGED
        "url_source": "https://ospi.k12.wa.us/science/",  // ADDED
        "last_verified": "2026-02-04",  // ADDED
        "grade_levels": ["K", "1", "2", ...],  // unchanged
        "document_type": "complete_k12",  // unchanged
        // ... all other fields preserved
      }
    ]
  }
}
```

**Tests required:**
- JSON syntax valid
- State count still 51
- Document count still 80
- No fields removed
- CLI commands work
- New fields accessible

**Validation:**
```bash
# Validate JSON syntax
python -m json.tool data/states.json > /dev/null && echo "✓ JSON valid"

# Verify state count unchanged
python -c "import json; print(len(json.load(open('data/states.json'))))"
# Expected: 51

# Verify document count unchanged
python -c "import json; data=json.load(open('data/states.json')); print(sum(len(s['documents']) for s in data.values()))"
# Expected: 80

# Test CLI functionality
python state_science_standards_system.py list | head -10

# Test specific state updated
python state_science_standards_system.py state [STATE_ABBREV]

# Verify new URL appears in output
python state_science_standards_system.py state [STATE_ABBREV] | grep "url"
```

**Commit message:** `fix(data): update [STATE] science standards URL with verified working link, add url_source and last_verified metadata`

**Expected duration:** 15 minutes

---

### Step 5: Verify Parser Works with Updated URL

**Action:** Test that parse_standards.py can fetch and parse the updated URL

**Files tested:** `parse_standards.py`, `data/states.json`

**Test command:**
```bash
# Test parser on updated state
uv run parse_standards.py [STATE_ABBREV]
```

**Expected behavior:**
- Parser loads states.json
- Fetches document from new URL
- Extracts grade sections
- No errors or crashes

**Tests required:**
- Parser runs without errors
- Document downloads successfully
- Grade sections identified (if applicable)
- No regression in parser functionality

**Validation:**
```bash
# Run parser on updated state
uv run parse_standards.py [STATE_ABBREV] 2>&1 | tee parser_test.log

# Check for errors
grep -i "error\|exception\|failed" parser_test.log
# Expected: No critical errors

# Verify document was fetched
grep -i "fetching\|downloading\|retrieved" parser_test.log

# Test parser still works on unmodified states (regression test)
uv run parse_standards.py OR
```

**Commit message:** `test(parser): verify parser works with updated [STATE] URL`

**Expected duration:** 10 minutes

---

### Step 6: Research and Apply Second Tier 1 State

**Action:** Repeat Steps 3-5 for second Tier 1 state

**Process:**
- Research URLs (Step 3 process)
- Apply update to states.json (Step 4 process)
- Verify parser works (Step 5 process)
- Commit each step

**Tests required:** Same as Steps 3-5

**Validation:** Same validation commands as Steps 3-5

**Commit messages:**
- `docs(research): research and verify working URL for [STATE2] science standards`
- `fix(data): update [STATE2] science standards URL with verified working link`
- `test(parser): verify parser works with updated [STATE2] URL`

**Expected duration:** 60-90 minutes (full cycle for one state)

---

### Step 7: Continue for Remaining Tier 1 States (3-8 more)

**Action:** Repeat Steps 3-5 for each remaining Tier 1 state

**Target:** 5-10 total Tier 1 states updated

**Batching strategy:**
- Update 2-3 states
- Full validation and commit
- Test CLI and parser
- Continue to next batch

**After each batch:**
```bash
# Full validation suite
python -m json.tool data/states.json > /dev/null
python state_science_standards_system.py list
python -c "import json; data=json.load(open('data/states.json')); print(f'States: {len(data)}, Docs: {sum(len(s[\"documents\"]) for s in data.values())}')"

# Commit batch
git add data/states.json docs/url_updates/
git commit -m "fix(data): update Tier 1 batch [N] URLs ([STATE1], [STATE2], [STATE3])"
```

**STOP CONDITION:** If 3 consecutive states have no working URLs found, stop and alert human

**Tests required:**
- All Tier 1 states attempted
- URLs verified for states where found
- states.json maintains integrity
- Parser works with all updates

**Validation:**
```bash
# After all Tier 1 states processed
# Verify all Tier 1 states have url_source and last_verified
python -c "
import json
data = json.load(open('data/states.json'))
tier1_states = ['WA', 'CA', 'HI', ...]  # List from tier1_update_plan.md
for state in tier1_states:
    for doc in data[state]['documents']:
        if 'url_source' in doc and 'last_verified' in doc:
            print(f'✓ {state}: {doc[\"title\"]} - metadata added')
        else:
            print(f'✗ {state}: {doc[\"title\"]} - missing metadata')
"

# Full CLI test suite
python state_science_standards_system.py list
python state_science_standards_system.py search 5
python state_science_standards_system.py compare 3
```

**Commit message:** `fix(data): complete Tier 1 URL updates, X of Y states updated with verified URLs`

**Expected duration:** Variable (30-90 min per state × remaining states)

---

### Step 8: Update Documentation and Summary

**Action:** Update all documentation to reflect completed work

**Files to modify:**
- `progress.txt` - Log Tier 1 completion
- `docs/tier1_update_plan.md` - Mark states as complete
- `docs/URL_VALIDATION_SUMMARY.md` - Update with new statistics
- `features.txt` - Update status

**Progress.txt entry:**
```
2026-02-04 HH:MM - Completed Plan 3: Apply Tier 1 URL Updates
2026-02-04 HH:MM - Updated X Tier 1 states with verified URLs
2026-02-04 HH:MM - Added url_source and last_verified metadata fields
2026-02-04 HH:MM - All updates tested with CLI and parser
2026-02-04 HH:MM - states.json backup maintained at data/states.json.backup
2026-02-04 HH:MM - Tier 1 states with working URLs: X/Y (Z%)
2026-02-04 HH:MM - States requiring further research: [list if any]
```

**Update features.txt:**
```markdown
## In Progress
- [ ] None

## Todo
- [ ] URL updates Tier 2 (partial issues)
- [ ] URL updates Tier 3 (redirects)
[... other features ...]

## Done
✓ Data validation & URL verification (Plan 1)
✓ URL update workflow documentation (Plan 2)
✓ Tier 1 URL updates applied (Plan 3)
[... other completed features ...]
```

**Tests required:**
- All documentation updated accurately
- Statistics match actual updates
- Next steps clear

**Validation:**
```bash
# Verify progress.txt updated
grep "Tier 1" progress.txt

# Verify features.txt updated
grep "Tier 1" features.txt

# Verify tier1_update_plan.md marked complete
grep "Status: Complete" docs/tier1_update_plan.md
```

**Commit message:** `docs(summary): update documentation with Tier 1 URL update completion summary`

**Expected duration:** 15 minutes

---

## Validation Strategy

### After Each State Update
```bash
# JSON validity
python -m json.tool data/states.json > /dev/null

# Data integrity
python -c "import json; data=json.load(open('data/states.json')); print(f'{len(data)} states, {sum(len(s[\"documents\"]) for s in data.values())} docs')"

# CLI functionality
python state_science_standards_system.py state [UPDATED_STATE]

# Parser compatibility
uv run parse_standards.py [UPDATED_STATE]
```

### Before Each Commit
```bash
# Full test suite
python -m json.tool data/states.json > /dev/null && echo "✓ JSON valid"
python state_science_standards_system.py list > /dev/null && echo "✓ CLI works"
python -c "import json; data=json.load(open('data/states.json')); assert len(data) == 51" && echo "✓ State count correct"
python -c "import json; data=json.load(open('data/states.json')); assert sum(len(s['documents']) for s in data.values()) == 80" && echo "✓ Doc count correct"

# Review changes
git diff data/states.json | head -50
```

### Final Validation
```bash
# Comprehensive data integrity check
python -c "
import json
data = json.load(open('data/states.json'))

# Verify counts
assert len(data) == 51, 'State count mismatch'
assert sum(len(s['documents']) for s in data.values()) == 80, 'Document count mismatch'

# Verify no null URLs
null_urls = sum(1 for s in data.values() for d in s['documents'] if not d.get('url'))
assert null_urls == 0, f'{null_urls} documents have null URLs'

# Verify metadata added to Tier 1 states
tier1_states = ['WA', 'CA', ...]  # List from research
updated_count = 0
for state in tier1_states:
    for doc in data[state]['documents']:
        if 'url_source' in doc and 'last_verified' in doc:
            updated_count += 1

print(f'✓ All checks passed')
print(f'✓ States: {len(data)}')
print(f'✓ Documents: {sum(len(s[\"documents\"]) for s in data.values())}')
print(f'✓ Tier 1 docs with metadata: {updated_count}')
"

# CLI full test
python state_science_standards_system.py list
python state_science_standards_system.py search 5
python state_science_standards_system.py state WA
python state_science_standards_system.py range CA

# Parser regression test
uv run parse_standards.py OR  # Test unmodified state
uv run parse_standards.py WA  # Test modified state
```

---

## Success Criteria

- [ ] states.json backup created and verified
- [ ] Tier 1 states identified (5-10 states)
- [ ] URLs researched for all Tier 1 states
- [ ] Working URLs found for at least 70% of Tier 1 states
- [ ] states.json updated with verified URLs
- [ ] url_source and last_verified fields added
- [ ] JSON syntax valid after all updates
- [ ] CLI functionality maintained (all commands work)
- [ ] Parser works with updated URLs
- [ ] Data integrity maintained (51 states, 80 docs)
- [ ] All URL research documented
- [ ] progress.txt and features.txt updated
- [ ] Backup available for rollback if needed

**Definition of "Done":**

This plan is complete when:
- 5-10 Tier 1 states have been researched
- Working URLs applied to states.json where found
- All changes tested and committed
- Documentation updated
- System stable and functional
- Clear status on remaining work

---

## Rollback Plan

### If JSON Becomes Invalid

**Problem:** states.json has syntax errors

**Action:**
```bash
# Restore from backup
cp data/states.json.backup data/states.json

# Verify restoration
python -m json.tool data/states.json > /dev/null && echo "✓ Restored"

# Re-apply updates more carefully
```

### If CLI Breaks

**Problem:** CLI commands fail after updates

**Action:**
```bash
# Test with backup
mv data/states.json data/states.json.broken
cp data/states.json.backup data/states.json

# Test CLI
python state_science_standards_system.py list

# If works, issue is in updates
# Identify problematic state and fix
```

### If Parser Breaks

**Problem:** Parser crashes on updated URLs

**Action:**
```bash
# Identify which state causes issue
uv run parse_standards.py WA
uv run parse_standards.py CA
# ... test each updated state

# Revert problematic state
# Re-research URL or mark as requiring manual intervention
```

### Git Rollback

**If committed changes need reverting:**
```bash
# Revert last commit
git revert HEAD

# Or revert specific commit
git revert <commit-hash>

# Or reset to before updates (DESTRUCTIVE)
git reset --hard <safe-commit-hash>
```

---

## Notes

### Constraints

1. **Manual research required** - Each state needs human URL research
2. **Time variable** - Some states easy (15 min), some hard (90+ min)
3. **Not all URLs may be findable** - Some states may have no current working URL
4. **External dependencies** - Reliant on state education websites

### Risks

1. **URLs break again** - State websites may change URLs in future
2. **Research incomplete** - May not find all URLs in reasonable time
3. **Data model changes** - Adding new fields (low risk, additive only)
4. **Parser compatibility** - New URLs may have unexpected formats

### Scope Decisions

**In Scope:**
- Tier 1 states (critical, all documents broken)
- Add url_source and last_verified fields
- Document all research

**Out of Scope:**
- Tier 2, 3, 4 states (defer to future plans)
- Automated URL discovery
- Document mirroring/caching
- Parser enhancements

### Future Work After This Plan

1. **Tier 2 states** - Partial issues (some docs broken)
2. **Tier 3 states** - Redirects (working but suboptimal)
3. **Periodic re-validation** - Check URLs every 3-6 months
4. **Document caching** - Store copies of critical PDFs

---

## Potential Blockers

**STOP and alert human if:**

- 3 consecutive Tier 1 states have no working URLs found (systematic issue)
- State education websites all use authentication/paywall (access barrier)
- JSON corruption occurs despite validation (data integrity issue)
- CLI breaks in unexpected way after updates (compatibility issue)
- Parser fails on all new URLs (format incompatibility)
- Research time exceeds 3 hours per state (complexity too high)

**When blocked:**
1. Document specific blocker
2. Preserve current working state
3. Commit completed work
4. Update tier1_update_plan.md with blocker info
5. Alert human with details and recommendations
6. Do NOT proceed with more updates until resolved

---

**Ready for execution approval**
**Depends on Plan 1 and Plan 2 completion**
**Estimated total time: 4-8 hours (variable based on research complexity)**
