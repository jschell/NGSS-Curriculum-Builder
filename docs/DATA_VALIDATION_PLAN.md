# Data Validation and Update Plan

**Date:** 2026-02-04
**Status:** Planning
**Objective:** Validate and update `data/states.json` URLs for accurate parsing

---

## Current Situation

### Data Overview

**Total Documents:** 80
- PDF: 57 documents (71%)
- HTML: 20 documents (25%)
- Interactive: 2 documents (2%)
- Excel: 1 document (1%)

**Document Types:**
- Complete K-12: 51 documents (64%)
- Grade-specific: 21 documents (26%)
- Grade-band: 8 documents (10%)

### URL Quality Findings

**Parser Testing Results:**
- Washington (WA): 403 Forbidden (server blocking)
- California (CA): 404 Not Found (broken grade-specific links)
- Hawaii (HI): 403 Forbidden (server blocking)
- Oregon (OR): 200 OK (working correctly) ✅
- Texas (TX): 404 Not Found (broken links)
- Nevada (NV): 200 OK (returned HTML instead of PDF)
- Arkansas (AR): Not tested (external hosting)
- Connecticut (CT): Not tested (external hosting)
- Delaware (DE): Not tested (external hosting)
- DC (District of Columbia): Not tested (external hosting)
- Iowa (IA): Not tested (external hosting)
- Kansas (KS): Not tested (external hosting)
- Kentucky (KY): Not tested (external hosting)
- Maine (ME): Not tested (external hosting)
- Maryland (MD): Not tested (external hosting)
- Michigan (MI): Not tested (external hosting)
- Montana (MT): Not tested (external hosting)

**URL Hosting Patterns:**

1. **State Department Direct Hosting**
   - Example: Oregon (`www.oregon.gov`)
   - Status: Working ✅
   - URLs: Direct PDF links

2. **External Hosting (nextgenscience.org)**
   - States: AR, CT, DE, DC, IA, KS, KY, ME, MD, MI, MT, NC, ND, NE, NH, NM, OH, OK, PA, RI, SC, SD, UT, VA, VT, WI, WV, WY
   - Status: Unknown (not tested)
   - Concern: External dependency may cause reliability issues

3. **State Department with Issues**
   - Example: Washington (`ospi.k12.wa.us`)
   - Status: 403 Forbidden
   - Concern: Server blocking automated requests or redirects

4. **Mixed Hosting**
   - Example: California (state site + broken grade-specific)
   - Status: Some working, some broken
   - Concern: Inconsistent data quality

### High-Priority States for Validation

**States with Complete K-12 Documents (48 states):**
- AK, AL, AR, AZ, CA, CO, CT, DE, DC, FL, GA, HI, IA, ID, IL, IN, KS, KY, LA, MA, MD, ME, MI, MN, MO, MS, MT, NC, ND, NE, NH, NM, NV, OH, OK, OR, PA, RI, SC, SD, TN, UT, VA, VT, WA, WI, WV, WY

**Known Working:**
- Oregon (OR) ✅
- California (CA) ✅ (main K-12 document)

**Needs Verification:**
- All other 46 states with complete K-12 documents

---

## Validation Approaches

### Approach 1: Systematic URL Verification (Recommended)

**Objective:** Manually verify each URL in `states.json`

**Process:**
1. Create a validation spreadsheet
2. Check each URL by:
   - Visiting in browser
   - Testing with curl/wget
   - Checking redirect chains
   - Verifying PDF validity
3. Categorize results:
   - Working: Downloads successfully, is valid PDF
   - Redirected: URL works but redirects to different location
   - Broken: Returns 404, 403, or similar error
   - Wrong format: Returns HTML instead of PDF
4. Document findings in spreadsheet

**Time Estimate:** 2-4 hours (manual review of 80 URLs)

**Advantages:**
- High accuracy (manual verification)
- Understands root causes of each failure
- Can find corrected URLs from state websites

**Disadvantages:**
- Time-consuming
- Manual effort required

---

### Approach 2: Source-Based Updates (High Priority)

**Objective:** Visit each state's official science standards page and find current document URLs

**Process:**
1. Start with high-impact states (complete K-12 documents)
2. For each state:
   a. Visit official science standards page
   b. Find "Standards" or "Science" section
   c. Look for K-12 or grade-specific PDF links
   d. Test candidate URLs
   e. Update `states.json` with working URLs
3. Document URL sources for future reference

**Prioritization:**
1. **Tier 1** (Known Working + Easy):
   - Oregon (OR) - Already verified ✅
   - California (CA) - Partially working

2. **Tier 2** (Next Generation States):
   - AR, CT, DE, DC, IA, KS, KY, ME, MD, MI, MT, NC, ND, NE, NH, NM, OH, OK, PA, RI, SC, SD, UT, VA, VT, WI, WV, WY
   - May have URL changes on nextgenscience.org

3. **Tier 3** (Direct Hosting with Issues):
   - Washington (WA) - Needs investigation
   - Hawaii (HI) - Needs investigation
   - Other 403/404 states

**Time Estimate:** 8-12 hours (all 51 states)

**Advantages:**
- Definitive source
- Finds most up-to-date URLs
- Establishes URL verification process

**Disadvantages:**
- Significant time investment
- Requires web research

---

### Approach 3: Crowdsourced Validation (Long-term)

**Objective:** Leverage community to validate and update URLs

**Process:**
1. Document URL validation process in CONTRIBUTING.md
2. Create template for URL update submissions
3. Request validation for:
   - States users are familiar with
   - Educational professionals
   - Curriculum developers
4. Establish review process for submissions
5. Apply verified updates to `states.json`

**Guidelines for Contributors:**
```
When submitting a URL update:
1. Include state abbreviation
2. Include document title
3. Provide working URL
4. Include verification date
5. Include source (state website page URL)
6. Note if URL redirects
```

**Time Estimate:** Ongoing (community-driven)

**Advantages:**
- Distributes validation effort
- Keeps data current over time
- Builds community engagement

**Disadvantages:**
- Requires community setup
- Needs quality control process

---

### Approach 4: Automated Validation Tool (Recommended for Future)

**Objective:** Create utility to automatically validate and categorize URLs

**Features:**
1. Batch HTTP testing with proper user-agents
2. Redirect chain following
3. Content type detection (PDF vs HTML)
4. PDF validation (is valid PDF file?)
5. Categorization of results
6. Generation of validation report

**Process:**
1. Run validation tool on `states.json`
2. Review generated report
3. Categorize by issue type
4. Create fix strategies per category
5. Apply fixes

**Time Estimate:** 1-2 hours (tool development) + 1 hour (run + review)

**Advantages:**
- Systematic coverage of all URLs
- Repeatable process
- Can be run periodically

**Disadvantages:**
- Requires development time
- May need manual follow-up for complex cases

---

## Recommended Action Plan

### Phase 1: Quick Wins (1-2 hours)

**Goal:** Validate known working states + easy fixes

**Actions:**
1. ✅ Oregon (OR) - Mark as verified in `states.json`
2. ✅ California (CA) - Verify K-12 document, mark as verified
3. Find and fix broken California grade-specific links
4. Test 5-10 additional complete K-12 states
5. Document findings

**Success Criteria:**
- [ ] 2+ additional states verified as working
- [ ] Broken California links fixed
- [ ] Verification process documented

**Output:**
- Updated `states.json` with verified URLs
- `docs/URL_VALIDATION_RESULTS.md` documenting findings

---

### Phase 2: Next Generation States (4-6 hours)

**Goal:** Validate 29 states hosted on nextgenscience.org

**Actions:**
1. Visit nextgenscience.org to understand hosting structure
2. Test sample URLs (5-10 states)
3. If working, batch validate remaining states
4. If not working, find alternative sources
5. Update `states.json` with working URLs

**Success Criteria:**
- [ ] All nextgenscience.org URLs tested
- [ ] 20+ states verified as working
- [ ] Alternative sources documented for broken URLs

**Output:**
- Updated `states.json` for 29 states
- `docs/NEXTGEN_VALIDATION.md` with findings

---

### Phase 3: Direct Hosting Issues (2-4 hours)

**Goal:** Resolve 403/404 errors on state department sites

**Actions:**
1. **Washington (WA) Investigation:**
   - Visit OSPI website directly
   - Find science standards section
   - Look for K-12 PDF downloads
   - Test with different user-agents
   - Check for form submissions or JavaScript redirects

2. **Hawaii (HI) Investigation:**
   - Visit Hawaii Public Schools website
   - Find science standards section
   - Look for downloadable documents
   - Check access requirements

3. **Other Error States:**
   - Identify pattern of failures
   - Investigate common causes
   - Document fix strategies

**Success Criteria:**
- [ ] Washington URL resolved or alternative found
- [ ] Hawaii URL resolved or alternative found
- [ ] Root cause of 403/404 errors documented
- [ ] Workaround strategies documented

**Output:**
- Updated `states.json` for investigated states
- `docs/DIRECT_HOSTING_ISSUES.md` with investigation results

---

### Phase 4: Parser Validation with Verified URLs (2-3 hours)

**Goal:** Run parser on verified states to validate grade section detection

**Actions:**
1. Select 5-10 states with verified URLs
2. Run `parse_standards.py` on these states
3. Manually verify detected page ranges
4. Compare detected sections with actual PDF content
5. Document accuracy of detection algorithms
6. Refine patterns if needed

**Success Criteria:**
- [ ] 5+ states parsed successfully
- [ ] Page ranges manually verified for 3+ states
- [ ] Detection accuracy >= 80%
- [ ] False positives < 5% documented
- [ ] False negatives < 5% documented

**Output:**
- Generated `patches/` for verified states
- `docs/PARSER_VALIDATION.md` with accuracy results
- Refined grade detection patterns if needed

---

### Phase 5: Comprehensive Parsing (8-12 hours)

**Goal:** Parse all verified states and apply patches to `states.json`

**Actions:**
1. Run `parse_standards.py parse --all` on updated `states.json`
2. Review generated `reports/grade_sections_analysis.md`
3. Identify states needing manual review
4. Apply patches for high-confidence results
5. Create TODO for medium/low confidence results
6. Document manual review process

**Success Criteria:**
- [ ] All verified states parsed
- [ ] JSON patches generated
- [ ] High-confidence patches applied to `states.json`
- [ ] Medium/low confidence results flagged for review
- [ ] Manual review workflow documented

**Output:**
- Updated `data/states.json` with grade sections
- `reports/COMPREHENSIVE_PARSING_REPORT.md`
- `docs/MANUAL_REVIEW_GUIDE.md`

---

## Success Metrics

### URL Validation Targets

- **Total URLs to Validate:** 80
- **Target Success Rate:** 80% (64 working URLs)
- **Minimum Verified:** 64 URLs
- **Stretch Goal:** 90% (72 working URLs)

### Parser Validation Targets

- **Grade Detection Accuracy:** 80%+
- **Confidence Scoring Accuracy:** 70%+ matches manual verification
- **Section Range Accuracy:** 70%+ within +/- 2 pages
- **False Positive Rate:** < 5%

### Overall Timeline

- **Phase 1 (Quick Wins):** 1-2 hours
- **Phase 2 (NextGen):** 4-6 hours
- **Phase 3 (Direct Hosting):** 2-4 hours
- **Phase 4 (Parser Validation):** 2-3 hours
- **Phase 5 (Comprehensive):** 8-12 hours

- **Total Time Estimate:** 17-27 hours (2-4 days of focused work)

---

## Risk Assessment

### High Risks

1. **NextGenScience.org Unreliable**
   - **Risk:** External hosting may be unstable
   - **Mitigation:** Find alternative state department sources
   - **Contingency:** Document multiple sources per state

2. **Server Blocking Automation**
   - **Risk:** 403 errors prevent parsing
   - **Mitigation:** Vary user-agent, add delays, use manual verification
   - **Contingency:** Document manual download process

3. **URL Redirects Not Handled**
   - **Risk:** Pages redirect but current URLs don't follow
   - **Mitigation:** Use curl with -L flag, test with different tools
   - **Contingency:** Document redirect chains

### Medium Risks

1. **Grade Detection Inaccurate**
   - **Risk:** Parser may misidentify grade boundaries
   - **Mitigation:** Manual verification sample, confidence scoring
   - **Contingency:** Provide manual override capability

2. **Document Organization Changes**
   - **Risk:** States may restructure documents without updating URLs
   - **Mitigation:** Date stamps in data, periodic re-verification
   - **Contingency:** Version control with rollback capability

3. **Large PDFs Cause Timeouts**
   - **Risk:** Parsing may be slow for large documents
   - **Mitigation:** Page-by-page streaming, timeout configuration
   - **Contingency:** Provide progress indicators

---

## Recommendations

### Immediate Actions (Today)

1. **Document Current State**
   - Create validation spreadsheet template
   - Document known working URLs
   - Document known broken URLs

2. **Quick Wins**
   - Verify Oregon (OR) is marked correctly
   - Verify California (CA) K-12 document
   - Fix California grade-specific links
   - Test 5 additional states

3. **Update Project Tracking**
   - Create `docs/URL_VALIDATION_PLAN.md` with this plan
   - Update `IMPLEMENTATION_SUMMARY.md` to note validation work needed

### This Week

1. **Complete Phase 1** (Quick Wins)
2. **Begin Phase 2** (NextGen validation)
3. **Investigate Washington/Hawaii blocking**

### This Month

1. **Complete Phases 1-4**
2. **Begin Phase 5** (Comprehensive parsing)
3. **Establish URL verification process**
4. **Document lessons learned**

---

## Alternative Strategies

### Strategy A: Hybrid Approach (Recommended)

**Combine automation with manual verification:**
1. Run automated validation tool
2. Review results, categorize by confidence
3. Manually verify ambiguous/failed cases
4. Apply fixes in priority order

**Benefits:**
- Balances speed and accuracy
- Handles most cases automatically
- Manual effort focused on edge cases

### Strategy B: Incremental Rollout

**Update states gradually as verified:**
1. Validate 10 states
2. Apply patches to those 10 states
3. Test end-to-end workflow
4. Repeat for remaining states
5. Commit after each batch

**Benefits:**
- Early feedback on process
- Reduces risk of large rollback
- Easier to debug issues
- Provides working system sooner

### Strategy C: Conservative Rollout

**Wait for complete validation before parsing:**
1. Validate all URLs first
2. Batch apply all patches
3. Single large update
4. Comprehensive testing

**Benefits:**
- Consistent final state
- Single validation cycle
- Reduced risk of partial updates

**Drawbacks:**
- Delayed delivery of value
- Risk of late-discovered issues
- Larger rollback if problems found

---

## Decision Guidance

### Use Phase 1 (Quick Wins) When:
- You have 1-2 hours available
- Want to quickly demonstrate progress
- Need to validate parser on working data
- Want to establish baseline

### Use Phase 2 (NextGen) When:
- You have 4-6 hours available
- Need to address external hosting dependency
- Want systematic validation of large state subset
- External hosting appears stable

### Use Phase 3 (Direct Issues) When:
- Washington/Hawaii blocking is critical blocker
- Need to understand 403/404 root causes
- Want to document investigation process
- External blocking patterns need resolution

### Use Phase 4 (Parser Validation) When:
- URLs are mostly validated
- Want to verify detection accuracy
- Ready to test parser with real data
- Need confidence in parsing results

### Use Phase 5 (Comprehensive) When:
- Most URLs are validated
- Want to generate complete data set
- Ready for production deployment
- Have time for full cycle

---

## Success Definition

**Complete When:**
- [ ] 64+ URLs verified as working (80%+)
- [ ] Parser validation completed with documented accuracy
- [ ] Grade sections generated for 40+ states
- [ ] `data/states.json` updated with high-confidence grade_sections
- [ ] Documentation reflects new capabilities
- [ ] Testing end-to-end workflow completes successfully

**Partial Progress When:**
- [ ] Phase 1 completed (quick wins)
- [ ] Phase 2 completed (NextGen validation)
- [ ] Phase 3 completed (direct hosting investigated)
- [ ] Phase 4 completed (parser validated)
- [ ] 25+ URLs verified
- [ ] 20+ states have grade section mappings

**Blocked When:**
- [ ] Critical blocker identified (e.g., all NextGen URLs broken)
- [ ] Parser fundamental issue discovered
- [ ] Data quality issue preventing any progress

---

**Created:** 2026-02-04
**Status:** Planning - Ready for Execution
**Next Step:** Begin Phase 1 (Quick Wins)
