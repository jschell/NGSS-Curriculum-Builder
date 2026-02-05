# URL Research Guide - 35 Broken States

**Date:** 2026-02-05
**Status:** Ready for Manual Research
**Estimated Time:** 12-20 hours total (20-30 min per state)

---

## Executive Summary

Out of 36 unverified states (39 documents), validation found:
- **Working:** 1 state (Alabama) - 2.6%
- **Broken:** 35 states (38 documents) - 97.4%

This guide provides a systematic approach to researching and fixing the 35 broken states.

---

## Research Strategy

### Batch Approach (Recommended)

Process states in batches of 5-10 to maintain momentum and allow for patterns/insights to emerge.

**Batch 1: Single-Doc NGSS States (Quick Wins)**
- States that likely adopted NGSS directly
- May be able to use nextgenscience.org URLs
- **States:** AR, CT, MD, NH, RI (5 states)
- **Estimated time:** 1-2 hours

**Batch 2: HTTP 403 States (Bot Detection)**
- Require manual browser access
- **States:** AZ, NE, VA, WV, WY (5 states)
- **Estimated time:** 2-3 hours

**Batch 3: HTML Landing Pages**
- Need to navigate from landing page to PDF
- **States:** GA, LA, ME, NC, NJ (part), SC (6 states)
- **Estimated time:** 2-3 hours

**Batch 4: Connection Errors**
- May have temporary outages or DNS issues
- **States:** CO, NV, TN (3 states)
- **Estimated time:** 1-2 hours

**Batch 5: Remaining States**
- Generic errors, need investigation
- **States:** AK, FL, ID, IN, MA, MN, MO, MS, MT, ND, NJ (part), OH, OK, PA, SD, UT, WI (17 states)
- **Estimated time:** 6-8 hours

---

## Research Process (Per State)

### Step 1: Visit State DOE Website (5 min)

1. Open state Department of Education homepage
2. Look for navigation menu items:
   - "Standards" or "Academic Standards"
   - "Curriculum" or "Instruction"
   - "Science" or "STEM"
3. Common URL patterns:
   - `/standards/`
   - `/curriculum/science/`
   - `/teaching-learning/standards/`

### Step 2: Search for Science Standards (5 min)

Search terms to try:
- "[State] science standards PDF"
- "[State] NGSS"
- "[State] K-12 science standards download"
- "[State] science content standards"

### Step 3: Locate PDF Download (5-10 min)

Look for:
- Direct PDF download links
- "View" or "Download" buttons
- Document libraries or repositories
- Google search: `site:[state-doe-domain] science standards PDF`

### Step 4: Verify PDF Content (2-3 min)

1. Download/open PDF
2. Check first few pages for:
   - State name
   - "Science" or "NGSS"
   - Grade levels covered
   - Publication date
3. Verify file size (typical: 100KB - 10MB)

### Step 5: Document Findings (2-3 min)

Record in research log:
- Working URL(s) found
- URL source (where you found it)
- Confidence level (high/medium/low)
- Notes (any issues, alternatives)

---

## State-by-State Research Plan

### BATCH 1: NGSS Direct Adoption States (Likely Quick Wins)

#### Arkansas (AR)
- **Current URL:** https://www.nextgenscience.org/sites/default/files/Arkansas%20K-12%20S...
- **Issue:** HTTP 202 (Accepted but no content)
- **Likely cause:** nextgenscience.org URL malformed or outdated
- **Research starting point:** Arkansas Dept of Education
- **DOE URL:** https://adeducation.k12.ar.us/
- **Search:** "Arkansas science standards" on DOE site
- **Alternative:** Check if AR has state-specific science page

#### Connecticut (CT)
- **Current URL:** https://www.nextgenscience.org/sites/default/files/Connecticut%20NGSS%...
- **Issue:** HTTP 202
- **DOE URL:** https://portal.ct.gov/SDE
- **Search:** "Connecticut science standards NGSS"

#### Maryland (MD)
- **Current URL:** https://www.nextgenscience.org/standards...
- **Issue:** HTTP 202
- **DOE URL:** https://www.marylandpublicschools.org/
- **Search:** "Maryland NGSS K-12"

#### New Hampshire (NH)
- **Current URL:** https://www.nextgenscience.org/standards...
- **Issue:** HTTP 202
- **DOE URL:** https://www.education.nh.gov/
- **Search:** "New Hampshire NGSS standards"

#### Rhode Island (RI)
- **Current URL:** https://www.nextgenscience.org/standards...
- **Issue:** HTTP 202
- **DOE URL:** https://www.ride.ri.gov/
- **Search:** "Rhode Island NGSS standards"

---

### BATCH 2: HTTP 403 States (Bot Detection - Manual Browser Required)

#### Arizona (AZ)
- **Current URL:** https://www.azed.gov/sites/default/files/2018/10/Full%20Set%20of%20Sta...
- **Issue:** HTTP 403 Forbidden
- **DOE URL:** https://www.azed.gov/
- **Strategy:** Use manual browser, search for "Arizona Science Standards 2018"
- **Likely location:** /standards/ or /science/ section

#### Nebraska (NE)
- **Current URL:** https://cdn.education.ne.gov/wp-content/uploads/2017/10/Nebraska_Scien...
- **Issue:** HTTP 403
- **DOE URL:** https://www.education.ne.gov/
- **Strategy:** Manual browser, look for "Nebraska Science Standards"

#### Virginia (VA)
- **Current URL:** https://www.doe.virginia.gov/teaching-learning-assessment/k-12-standar...
- **Issue:** HTTP 403
- **DOE URL:** https://www.doe.virginia.gov/
- **Strategy:** Navigate to Standards section manually

#### West Virginia (WV)
- **Current URL:** https://wvde.us/middle-secondary-learning/science/standards-and-guidan...
- **Issue:** HTTP 403
- **DOE URL:** https://wvde.us/
- **Strategy:** Science -> Standards section

#### Wyoming (WY)
- **Current URL:** https://edu.wyoming.gov/for-district-leadership/standards/science/...
- **Issue:** HTTP 403
- **DOE URL:** https://edu.wyoming.gov/
- **Strategy:** District Leadership -> Standards -> Science

---

### BATCH 3: HTML Landing Pages (Navigate to PDF)

#### Georgia (GA)
- **Current URL:** https://www.georgiastandards.org/Georgia-Standards/Pages/Science.aspx...
- **Issue:** Returns HTML landing page
- **DOE URL:** https://www.gadoe.org/
- **Strategy:** From landing page, find PDF download link
- **Note:** Redirected to sunset page - may need new standards location

#### Louisiana (LA)
- **Current URL:** https://doe.louisiana.gov/educators/instructional-support/planning-res...
- **Issue:** HTML landing page
- **DOE URL:** https://www.louisianabelieves.com/
- **Strategy:** Navigate from landing page to PDF download

#### Maine (ME)
- **Current URL:** https://www.maine.gov/doe/learning/content/scienceandtech/nextgen...
- **Issue:** HTML page
- **DOE URL:** https://www.maine.gov/doe/
- **Strategy:** Science section -> Download PDF

#### North Carolina (NC)
- **Current URL:** https://www.dpi.nc.gov/districts-schools/classroom-resources/academic-...
- **Issue:** HTML landing page
- **Redirect:** https://www.dpi.nc.gov/districts-schools/classroom-resources/office-teaching-and-learning/standard-course-study/science
- **Strategy:** Follow redirect, find PDF download

#### New Jersey (NJ) - 2 documents
- **Doc 1 URL:** https://www.nj.gov/education/standards/science/Docs/NJSLS-Science_K-5....
- **Doc 2 URL:** https://www.nj.gov/education/standards/science/...
- **Issues:** Doc 1 error, Doc 2 HTML
- **DOE URL:** https://www.nj.gov/education/
- **Strategy:** Standards -> Science -> Find both K-5 and 6-12 PDFs

#### South Carolina (SC)
- **Current URL:** https://ed.sc.gov/instruction/standards/science/standards/...
- **Issue:** HTML landing page
- **DOE URL:** https://ed.sc.gov/
- **Strategy:** Standards -> Science -> Download PDF

---

### BATCH 4: Connection Errors (May Be Temporary)

#### Colorado (CO)
- **Current URL:** https://www.cde.state.co.us/coscience/2020cas-sc...
- **Issue:** Connection error (ConnectError)
- **DOE URL:** https://www.cde.state.co.us/
- **Strategy:** Retry connection, search for "2020 Colorado Academic Standards Science"
- **Note:** URL looks legitimate, may be temporary outage

#### Nevada (NV)
- **Current URL:** https://doe.nv.gov/uploadedFiles/nde.doe.nv.gov/content/Nevada_Academi...
- **Issue:** Connection error
- **DOE URL:** https://doe.nv.gov/
- **Strategy:** Retry, search site for science standards

#### Tennessee (TN)
- **Current URL:** https://www.tn.gov/content/dam/tn/stateboardofeducation/documents/stan...
- **Issue:** Connection error
- **DOE URL:** https://www.tn.gov/education/
- **Strategy:** Retry, look for State Board of Education standards documents

---

### BATCH 5: Remaining States (Generic Errors - Full Investigation)

#### Alaska (AK)
- **Current URL:** https://education.alaska.gov/akstandards/science/science-standards-for...
- **Issue:** Generic error
- **DOE URL:** https://education.alaska.gov/
- **Search:** "Alaska science standards K-12"

#### Florida (FL)
- **Current URL:** https://www.cpalms.org/public/search/Standard...
- **Issue:** HTTP 500 Server Error
- **DOE URL:** https://www.fldoe.org/
- **Alternative:** Try CPALMS.org directly (Florida's standards portal)
- **Search:** "Florida NGSSS science standards"

#### Idaho (ID)
- **Current URL:** https://www.sde.idaho.gov/wp-content/uploads/2025/09/Idaho-K-12-State-...
- **Issue:** Generic error
- **DOE URL:** https://www.sde.idaho.gov/
- **Search:** "Idaho K-12 science standards"

#### Indiana (IN)
- **Current URL:** https://www.in.gov/doe/students/indiana-academic-standards/science-and...
- **Issue:** Generic error
- **DOE URL:** https://www.in.gov/doe/
- **Search:** "Indiana academic standards science"

#### Massachusetts (MA)
- **Current URL:** https://www.doe.mass.edu/frameworks/scitech/2016-04.pdf...
- **Issue:** Generic error
- **DOE URL:** https://www.doe.mass.edu/
- **Search:** "Massachusetts science framework 2016"
- **Note:** URL looks legitimate, may be PDF access issue

#### Minnesota (MN)
- **Current URL:** https://education.mn.gov/MDE/dse/stds/sci/...
- **Issue:** Generic error
- **DOE URL:** https://education.mn.gov/
- **Search:** "Minnesota science standards 2019"

#### Missouri (MO)
- **Current URL:** https://dese.mo.gov/media/file/curr-mls-standards-sci-k-12-sboe-2016...
- **Issue:** Generic error
- **DOE URL:** https://dese.mo.gov/
- **Search:** "Missouri learning standards science K-12"

#### Mississippi (MS)
- **Current URL:** https://www.mdek12.org/sites/default/files/documents/Secondary%20Ed/20...
- **Issue:** Generic error
- **DOE URL:** https://www.mdek12.org/
- **Search:** "Mississippi science standards 2018"

#### Montana (MT) - 2 documents
- **Doc 1:** Montana Science Content Standards 2016
- **Doc 2:** Montana Science Model Curriculum Guide
- **DOE URL:** https://opi.mt.gov/
- **Search:** "Montana science content standards 2016"

#### North Dakota (ND)
- **Current URL:** https://www.nd.gov/dpi/sites/www/files/documents/Academic%20Support/FI...
- **Issue:** Generic error
- **DOE URL:** https://www.nd.gov/dpi/
- **Search:** "North Dakota science content standards"

#### Ohio (OH)
- **Current URL:** https://education.ohio.gov/getattachment/Topics/Learning-in-Ohio/Scien...
- **Issue:** Generic error
- **DOE URL:** https://education.ohio.gov/
- **Search:** "Ohio learning standards science model curriculum"

#### Oklahoma (OK)
- **Current URL:** https://oklahoma.gov/content/dam/ok/en/osde/documents/services/literac...
- **Issue:** Generic error
- **DOE URL:** https://sde.ok.gov/
- **Search:** "Oklahoma academic standards science 2020"

#### Pennsylvania (PA) - 2 documents
- **Doc 1:** K-12 STEELS Standards
- **Doc 2:** Pennsylvania Integrated Standards K-5
- **DOE URL:** https://www.education.pa.gov/
- **Search:** "Pennsylvania STEELS standards science"

#### South Dakota (SD)
- **Current URL:** https://doe.sd.gov/contentstandards/documents/24-SciStandards.pdf...
- **Issue:** Generic error
- **DOE URL:** https://doe.sd.gov/
- **Search:** "South Dakota science standards 2024"

#### Utah (UT)
- **Current URL:** https://schools.utah.gov/curr/science/_science_/UtahSEEdStandards.pdf...
- **Issue:** Generic error
- **DOE URL:** https://www.schools.utah.gov/
- **Search:** "Utah SEEd standards"

#### Wisconsin (WI)
- **Current URL:** https://dpi.wi.gov/sites/default/files/imce/standards/New%20pdfs/Scien...
- **Issue:** Generic error
- **DOE URL:** https://dpi.wi.gov/
- **Search:** "Wisconsin standards for science"

---

## Research Log Template

For each state, document findings in a JSON file:

```json
{
  "state_abbr": "XX",
  "research_date": "2026-02-05",
  "researcher": "Name",
  "findings": {
    "working_url": "https://...",
    "url_source": "Found on [State] DOE Science Standards page",
    "confidence": "high",  // high, medium, low
    "verified_pdf": true,
    "file_size_kb": 1234,
    "notes": "URL found in Standards section, PDF contains K-12 science standards"
  },
  "time_spent_minutes": 25
}
```

---

## Workflow Tools

### Quick Verification Script

After finding a URL, test it:

```bash
# Test URL
curl -I "https://new-url.pdf"

# Or use the test script
python -c "
import httpx
url = 'https://new-url.pdf'
r = httpx.get(url, follow_redirects=True, timeout=10)
print(f'Status: {r.status_code}')
print(f'Content-Type: {r.headers.get(\"content-type\")}')
print(f'Size: {len(r.content) / 1024:.1f} KB')
"
```

### Batch Update Script

After researching 5-10 states, update states.json in batch using update script (to be created).

---

## Success Metrics

### Target Completion Rates

- **Week 1:** Batch 1-2 complete (10 states)
- **Week 2:** Batch 3-4 complete (9 more states = 19 total)
- **Week 3:** Batch 5 first half (8 more states = 27 total)
- **Week 4:** Batch 5 completion (8 remaining = 35 total)

### Quality Checks

- [ ] URL returns HTTP 200
- [ ] Content-Type is application/pdf
- [ ] File size reasonable (>50 KB, <20 MB)
- [ ] PDF contains state name
- [ ] PDF contains "science" or "NGSS"
- [ ] Grade levels match expected
- [ ] URL source documented
- [ ] Last verified date added

---

## Notes

### Common Patterns Discovered

1. **nextgenscience.org URLs broken:** Many states that adopted NGSS directly had URLs pointing to nextgenscience.org that now return HTTP 202. These states likely host their own copies now.

2. **Bot detection:** Several states (AZ, NE, VA, WV, WY) return HTTP 403 for automated requests. Manual browser access required.

3. **Landing pages:** Some states provide HTML landing pages instead of direct PDF links. Need to navigate from landing page.

4. **URL structure changes:** Many state DOE websites have been restructured, breaking old URLs.

### Alternative Sources

If state DOE doesn't have working URL:
1. Check nextgenscience.org state pages
2. Search Google for "[State] science standards PDF"
3. Check state education association websites
4. Contact state DOE directly

---

**Ready to begin research? Start with Batch 1 (NGSS states) for quick wins.**
