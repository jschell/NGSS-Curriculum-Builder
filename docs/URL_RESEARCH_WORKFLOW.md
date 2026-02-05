# URL Research Workflow

## Purpose

When validation identifies broken URLs, this workflow guides research process to find working replacements from official state sources.

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

**Find official state education website:**

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

**Test URL:**
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
