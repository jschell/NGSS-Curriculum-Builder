# Plan: Data Validation & URL Verification

**STATUS: SUPERSEDED** - This plan was split into 3 incremental Obra-aligned plans on 2026-02-04:
1. `.claude/plan/active/url-validation-execution.md` - Execute validation & generate reports (2-3 hours)
2. `.claude/plan/active/url-update-workflow-documentation.md` - Document update workflows (1 hour)
3. `.claude/plan/active/url-updates-tier1-application.md` - Apply Tier 1 URL updates (2-3 hours)

**Reason for split:** Original plan had 8-12 hour scope with large steps (1-2 hours each). New plans follow Obra standard of 5-30 minute steps with incremental validation gates.

**Original plan preserved below for reference:**

---

## Context

The NGSS Curriculum Builder's parser infrastructure is complete and functional. However, many URLs in `data/states.json` return HTTP 404/403 errors, preventing automatic grade section extraction. This plan creates a validation system to systematically verify, document, and update broken URLs.

**Key Findings:**
- 80 total documents in database
- 57 PDF documents (71%), 20 HTML documents (25%)
- 51 complete K-12 documents (64%)
- Many state URLs return 404/403 errors (Washington, California, Hawaii, Texas)
- Oregon URLs are working and validate correctly
- Parser successfully extracts grade sections when URLs work

**Goal:** Create systematic URL validation workflow without modifying `data/states.json` initially. Only after verification should data be updated.

## Prerequisites

- [x] Python 3.10+ installed
- [x] UV package manager available
- [x] HTTP client utilities (httpx) available via UV
- [x] Existing parser infrastructure (parse_standards.py) functional
- [ ] URL validation utility (to be created)
- [ ] Validation spreadsheet template (to be created)

## Implementation Steps

### Step 1: Create URL Validation Utility

**Action:** Create standalone script to validate URLs systematically

**Files to create:**
- `validate_urls.py` - Main validation script with HTTP testing
- `validation_results.json` - Structured validation output
- `docs/URL_VALIDATION_GUIDE.md` - How to use validation tool

**Features:**
- Test each URL with proper user-agent headers
- Detect HTTP status codes (200, 404, 403, etc.)
- Detect content type (PDF, HTML, text, binary)
- Follow redirects (up to 3 hops)
- Measure response time
- Detect if URL points to actual PDF vs error page
- Validate PDF headers (is it a real PDF?)

**Validation criteria:**
- ✅ Working: HTTP 200, valid PDF headers, content-type: application/pdf
- ⚠️ Redirected: Working but redirects to different location
- ❌ Broken: HTTP 404, 403, 500, connection timeout
- ⚠️ Wrong format: Returns HTML when expecting PDF
- ⚠️ Small file: < 50 KB (likely error page)

**Output format:**
```json
{
  "validation_date": "2026-02-04",
  "validator_version": "1.0",
  "results": {
    "WA": {
      "documents": [
        {
          "title": "Washington State K-12 Science Learning Standards",
          "url": "https://ospi.k12.wa.us/...",
          "status": "broken",
          "http_status": 403,
          "content_type": "text/html",
          "file_size_kb": 0,
          "error": "Server returns HTML error page instead of PDF"
        }
      ]
    }
  }
}
```

**Tests required:**
- Test on known working URLs (Oregon)
- Test on known broken URLs (Washington)
- Verify redirect handling
- Validate JSON output structure

**Commit message:** `feat(validation): add URL validation utility with HTTP testing and content detection`

**Validation:**
- Run `python validate_urls.py OR`
- Verify output JSON is valid: `python -m json.tool validation_results.json`
- Check OR working URL passes validation
- Check WA broken URL fails validation
- Review console output for accuracy

**Estimated time:** 2 hours

---

### Step 2: Execute Validation on All States

**Action:** Run validation utility on all 80 documents in `states.json`

**Files to modify:**
- `validation_results.json` - Generated from Step 1
- `docs/URL_VALIDATION_RESULTS.md` - Human-readable summary

**Process:**
1. Load all states from `data/states.json`
2. Extract all document URLs
3. Test each URL with validation utility
4. Categorize results:
   - Working: Direct PDF downloads work
   - Broken: HTTP 4xx/5xx errors
   - Redirected: Working but not at expected URL
   - Wrong format: HTML instead of PDF
5. Generate summary statistics
6. Create actionable recommendations per state

**Expected output structure:**
```
# Validation Summary

Total URLs tested: 80
Working URLs: XX
Broken URLs: XX
Redirected: XX
Wrong Format: XX

# By State

## Working States
- OR: 100% (7/7 documents working)

## States with Issues

### WA (Washington)
- Status: Critical
- Issues: All 3 documents return 403 Forbidden
- Recommendation: Manual investigation of OSPI website, find alternative sources

### CA (California)
- Status: Partial
- Issues: Complete K-12 document unknown, grade-specific links broken
- Recommendation: Check California Department of Education website

### HI (Hawaii)
- Status: Critical
- Issues: 403 Forbidden
- Recommendation: Manual investigation needed
```

**Tests required:**
- Verify all 80 URLs tested
- Check accuracy of categorization
- Verify file sizes recorded correctly

**Commit message:** `chore(data): validate all 80 document URLs, generate validation results and summary report`

**Validation:**
- Review `validation_results.json` - ensure all 80 documents tested
- Check summary report in `docs/URL_VALIDATION_RESULTS.md`
- Verify state categorization is accurate
- Manual spot-check 5-10 random URLs in browser

**Estimated time:** 1 hour (automated) + 30 minutes (manual review)

---

### Step 3: Create URL Update Templates

**Action:** Create templates for documenting corrected URLs

**Files to create:**
- `templates/url_update_template.md` - Template for documenting URL fixes
- `docs/URL_UPDATE_WORKFLOW.md` - How to apply validated URLs to states.json

**Template structure:**
```markdown
# State: [State Abbreviation] - [State Name]

## Document: [Document Title]

### Current URL
```
https://old-url-that-doesnt-work.pdf
```

**Issue:** [Description of problem]

### Validation Result
- Status: [working/redirected/broken/wrong_format]
- HTTP Status: [200/404/403/etc]
- Content Type: [application/pdf/text/html/etc.]
- File Size: [KB]
- Notes: [Additional observations]

### Corrected URL

```
https://new-working-url.pdf
```

**Source:** [Where new URL was found - state website page, search result, etc.]

**Verification Date:** [YYYY-MM-DD]

### Additional Information
- Redirects: [List redirect chain if applicable]
- Alternative Sources: [Other places to find the document]
- Recommendations: [Any special handling needed]
```

**Tests required:**
- Template renders correctly as Markdown
- All required fields present
- Examples provided for different scenarios

**Commit message:** `docs(validation): create URL update templates and documentation workflow`

**Validation:**
- Verify template completeness by checking all scenarios
- Test with sample data (Oregon working, Washington broken)
- Ensure documentation is clear and actionable

**Estimated time:** 30 minutes

---

### Step 4: Document Findings and Recommendations

**Action:** Create comprehensive analysis report

**Files to modify:**
- `docs/URL_VALIDATION_FINDINGS.md` - Root cause analysis
- `docs/STATE_BY_STATE_RECOMMENDATIONS.md` - Specific guidance per state

**Findings analysis:**

**Hosting patterns:**
1. **State Department Direct Hosting** (Oregon, verified working)
   - Success rate: High
   - Maintenance: Generally reliable
   - Recommendation: Model for other states

2. **External Hosting** (nextgenscience.org, 29 states)
   - Success rate: Unknown
   - Concern: External dependency
   - Recommendation: Find alternatives or validate thoroughly

3. **State Department with Blocking Issues** (Washington, Hawaii)
   - Issue: 403 Forbidden (possible bot detection)
   - Recommendation: Investigate access requirements, manual download, find alternatives

4. **Mixed Hosting** (California)
   - Issue: Inconsistent link quality
   - Recommendation: Systematic state website review

**Root causes:**
- URLs changed without database updates
- External hosting deprecated or unstable
- Server-side bot detection blocking automated requests
- Missing URL validation before initial data entry

**Recommendations:**
1. Add last_verified timestamp to data model
2. Implement periodic URL re-verification
3. Establish URL source documentation
4. Create fallback sources for critical documents
5. Set up monitoring for document availability

**Tests required:**
- Report covers all validation findings
- Root cause analysis is thorough
- Recommendations are actionable
- State-by-state guidance is specific

**Commit message:** `docs(validation): document URL validation findings and root cause analysis with state-specific recommendations`

**Validation:**
- Review findings report for completeness
- Verify recommendations address each root cause
- Check state-specific guidance is actionable
- Confirm no contradictions between recommendations

**Estimated time:** 1 hour

---

### Step 5: Create URL Application Workflow

**Action:** Document process for applying validated URLs to `states.json`

**Files to modify:**
- `docs/URL_UPDATE_WORKFLOW.md` - Detailed step-by-step process
- `docs/JSON_UPDATE_GUIDE.md` - Technical instructions for JSON modifications

**Workflow steps:**

1. **Validation Confirmation**
   - Review validation results
   - Mark URLs as "verified" if passing tests
   - Flag URLs needing manual investigation

2. **Update Preparation**
   - Backup current `states.json`
   - Create update JSON patch
   - Test patch on copy of data file
   - Document update strategy

3. **JSON Update**
   - Apply patch to `data/states.json`
   - Verify JSON validity
   - Test data loading with updated file
   - Ensure backward compatibility

4. **Verification**
   - Run `python state_science_standards_system.py list` - verify no errors
   - Test parser on updated URLs
   - Check specific state queries work

5. **Rollback Plan**
   - Keep backup copy
   - Document rollback procedure
   - Test rollback process if needed

6. **Documentation**
   - Update IMPLEMENTATION_SUMMARY.md
   - Note which URLs were updated
   - Document any changes to data structure

**Update strategy:**
- Update 5-10 states at a time
- Test after each batch
- Monitor for parsing errors
- Document state of each update

**Tests required:**
- Workflow documentation is complete
- JSON update guide is technical and accurate
- Backup strategy is clear
- Rollback procedure is tested

**Commit message:** `docs(workflow): document URL application workflow and JSON update process with batch strategy`

**Validation:**
- Follow workflow with test URLs
- Verify JSON update works correctly
- Test rollback procedure (optional but recommended)
- Ensure backward compatibility maintained

**Estimated time:** 30 minutes

---

### Step 6: Apply Verified URLs to Data

**Action:** Update `data/states.json` with corrected URLs

**Files to modify:**
- `data/states.json` - Main data file

**Priority order:**
1. **Tier 1: Verified Working** (Oregon, 5-10 other states)
   - Update with confidence: high
   - Batch size: 5-10 states

2. **Tier 2: External Hosting** (nextgenscience.org states)
   - Validate all URLs
   - Update with confidence: medium
   - Batch size: 10-15 states

3. **Tier 3: Blocked States** (Washington, Hawaii)
   - Investigate manual download options
   - Update if working URLs found
   - Mark if unresolved with documentation

4. **Tier 4: Mixed Quality** (California, others)
   - Systematic review
   - Update working URLs
   - Document broken URLs for follow-up

**Update approach:**
- Create JSON patches per batch
- Apply patches sequentially
- Test after each batch
- Commit after each successful batch
- Rollback on failure before proceeding

**JSON update format:**
- Only change URL field
- Add/update `last_verified` timestamp
- Add `url_source` field
- Preserve all other data

**Example update:**
```json
{
  "WA": {
    "documents": [
      {
        "title": "Washington State K-12 Science Learning Standards",
        "url": "https://corrected-url.pdf",  // CHANGED
        "url_source": "https://ospi.k12.wa.us/science/",  // NEW
        "last_verified": "2026-02-04"  // NEW
        // ... all other fields unchanged
      }
    ]
  }
}
```

**Tests required:**
- Verify JSON structure after update
- Test data loading: `python state_science_standards_system.py list`
- Query specific state: `python state_science_standards_system.py state OR`
- Verify parser works with new URL
- Check backward compatibility

**Commit message:** `chore(data): update Oregon URLs with verified links, add last_verified timestamps and url_source metadata`

**Validation:**
- All queries work correctly
- Parser fetches and processes updated documents
- JSON is valid: `python -m json.tool data/states.json`
- New metadata fields are accessible to parser
- Rollback capability confirmed

**Estimated time:** 30 minutes per batch

---

## Rollback Plan

### How to Undo Changes

**Backup strategy:**
1. Git commits allow easy rollback to any point
2. Keep original `states.json` as `states.json.backup` before first update
3. Each update batch is a separate commit

**Rollback commands:**
```bash
# Rollback single commit
git revert HEAD

# Rollback to specific commit
git revert <commit-hash>

# Reset to before updates
git reset --hard <commit-hash>
```

**Partial rollback:**
If a batch of updates contains errors:
```bash
# Identify problematic commit
git log --oneline -n 10

# Revert to safe commit
git revert <safe-commit-hash>

# Re-apply good commits individually
git cherry-pick <good-commit-1>
git cherry-pick <good-commit-2>
```

### Rollback triggers

1. **Data corruption detected:** JSON becomes invalid
2. **Critical parser errors:** Parser crashes after update
3. **Breaking changes:** Existing functionality stops working
4. **Manual intervention:** User identifies problem

### Data restoration

From backup:
```bash
# Restore from backup file
cp states.json.backup states.json
git restore states.json
```

From git:
```bash
# Reset to last known good state
git reset --hard HEAD~1
```

---

## Success Criteria

- [ ] URL validation utility created and tested
- [ ] All 80 URLs validated with documented results
- [ ] Validation report generated with state-by-state analysis
- [ ] URL update templates created
- [ ] Application workflow documented
- [ ] 5-10 states updated with verified URLs (Tier 1)
- [ ] Data integrity verified after each batch
- [ ] Backward compatibility maintained
- [ ] Rollback procedure tested and documented
- [ ] Parser works correctly with updated URLs
- [ ] Documentation reflects all changes

**Additional success criteria:**

- [ ] Validation accuracy >= 90% (verified with manual spot-checks)
- [ ] No data corruption incidents
- [ ] Clear audit trail (commits with descriptive messages)
- [ ] All states categorized by update priority
- [ ] External hosting issues documented
- [ ] Blocked states have clear next steps

**Definition of "Done":**

All validation and URL update work is complete when:
- All 80 URLs have been tested
- Validation results are documented
- At least 30 states have verified URLs applied
- All changes are committed and tested
- Documentation is up to date
- Rollback capability exists

---

## Notes

### Constraints

1. **No automatic URL discovery** - This plan only validates existing URLs
2. **Manual verification required** - Some states may need human investigation
3. **External hosting uncertainty** - nextgenscience.org may require community validation
4. **Time estimation** - Based on automation, actual may vary

### Risks

1. **External hosting reliability** - 29 states use nextgenscience.org
2. **Server blocking** - Washington and Hawaii may require manual intervention
3. **Data quality** - Some URLs may be permanently outdated
4. **Parser success** - Depends on validation, not code changes

### Future Enhancements

1. **Periodic re-verification** - Check URLs every 3-6 months
2. **URL health monitoring** - Automated availability checks
3. **Source diversity** - Mirror critical documents
4. **API integration** - Direct access to state education APIs if available
5. **Caching** - Store successful downloads to reduce requests

---

**Created:** 2026-02-04
**Priority:** High - Enables parser validation on real data
**Estimated Total Time:** 8-12 hours (validation + updates)
**Dependencies:** httpx (via UV), Python standard library

## Implementation Order

1. **Execute:** Create URL validation utility (Step 1)
2. **Review:** Validation utility code and tests
3. **Execute:** Validate all 80 URLs (Step 2)
4. **Review:** Validation results and summary report
5. **Execute:** Create URL update templates (Step 3)
6. **Review:** Template completeness and examples
7. **Execute:** Document findings and recommendations (Step 4)
8. **Review:** Findings analysis comprehensiveness
9. **Execute:** Create application workflow (Step 5)
10. **Review:** Workflow documentation and JSON guide
11. **Execute:** Apply Tier 1 updates (5-10 states) (Step 6)
12. **Review:** Updates successful, no data corruption
13. **Execute:** Apply remaining tier updates (Step 6)
14. **Review:** All updates tested and working
15. **Update:** Complete documentation and summaries

**After completion:**
- All validation tools ready for production use
- Systematic URL update workflow established
- `data/states.json` can be safely updated
- `parse_standards.py` can generate accurate grade section mappings
- Rollback capability maintained for safe updates

---

**Ready for human review and execution approval**
