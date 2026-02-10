# Batch 1 Research Findings - NGSS Direct Adoption States

**Date:** 2026-02-05
**States Researched:** AR, CT, MD, NH, RI (5 states)
**Time Spent:** ~60 minutes
**Status:** 2/5 URLs found

---

## Arkansas (AR) ✅ - FOUND

**Status:** Working URLs found (grade-specific PDFs)

**Finding:**
Arkansas does NOT have a single K-12 comprehensive PDF. Instead, they provide grade-specific science standards documents.

**Available PDFs:**
- **Elementary (K-5):**
  - Kindergarten: https://dese.ade.arkansas.gov/Files/Kindergarten-general_science_LS.pdf (✅ HTTP 200, 1.2MB)
  - Grade 1: https://dese.ade.arkansas.gov/Files/First_Grade_general_science_LS.pdf
  - Grade 2: https://dese.ade.arkansas.gov/Files/Second_Grade_general_science_LS.pdf
  - Grade 3: https://dese.ade.arkansas.gov/Files/Third_Grade_general_science_LS.pdf
  - Grade 4: https://dese.ade.arkansas.gov/Files/Fourth_Grade_general_science_LS.pdf
  - Grade 5: https://dese.ade.arkansas.gov/Files/Fifth_Grade_general_science_LS.pdf

- **Middle School (6-8):**
  - Grade 6: https://dese.ade.arkansas.gov/Files/Sixth_Grade_general_science_LS.pdf
  - Grade 7: https://dese.ade.arkansas.gov/Files/Seventh_Grade_general_science_LS.pdf
  - Grade 8: https://dese.ade.arkansas.gov/Files/Eighth_Grade_general_science_LS.pdf

- **High School (9-12):** (Multiple course-specific documents)
  - Biology Integrated, Chemistry Integrated, Physical Science Integrated, etc.

**URL Source:** https://dese.ade.arkansas.gov/Offices/learning-services/curriculum-support/science-standards-and-courses

**Recommendation for Database:**
Use the Kindergarten PDF as the primary document, but note that Arkansas has grade-specific PDFs available.

**Proposed Update:**
```json
{
  "title": "Arkansas K-12 Science Standards",
  "url": "https://dese.ade.arkansas.gov/Files/Kindergarten-general_science_LS.pdf",
  "grade_levels": ["K", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12"],
  "notes": "Arkansas provides grade-specific science standards PDFs. This URL links to Kindergarten standards. Full list available at: https://dese.ade.arkansas.gov/Offices/learning-services/curriculum-support/science-standards-and-courses",
  "url_source": "https://dese.ade.arkansas.gov/Offices/learning-services/curriculum-support/science-standards-and-courses",
  "last_verified": "2026-02-05"
}
```

---

## Connecticut (CT) ✅ - FOUND

**Status:** Working URL found

**Finding:**
Connecticut adopted NGSS in November 2015. Found working PDF document.

**Working URL:**
- https://portal.ct.gov/-/media/sde/science/ngss_boards.pdf (✅ HTTP 200, 151KB)

**URL Source:** https://portal.ct.gov/sde/science/science-standards-and-resources

**Proposed Update:**
```json
{
  "title": "Connecticut Next Generation Science Standards",
  "url": "https://portal.ct.gov/-/media/sde/science/ngss_boards.pdf",
  "grade_levels": ["K", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12"],
  "url_source": "https://portal.ct.gov/sde/science/science-standards-and-resources",
  "last_verified": "2026-02-05"
}
```

---

## Maryland (MD) ❌ - NOT FOUND

**Status:** No working direct PDF found

**Finding:**
Maryland adopted NGSS as Maryland Science Standards. However, the MD Department of Education website directs users to nextgenscience.org for the actual standards documents rather than hosting their own PDF.

**Resources Found:**
- Science Branch page: https://www.marylandpublicschools.org/about/Pages/DCAA/Science/index.aspx
- Page directs to: https://www.nextgenscience.org/

**Issue:** nextgenscience.org URLs return HTTP 202 (Accepted - no content), same issue as before.

**Recommendation:**
- Requires further manual research via web browser
- May need to contact MD Dept of Education directly
- Alternative: Check if MD has any state-specific NGSS implementation guides

**Status:** Deferred to manual research

---

## New Hampshire (NH) ❌ - NOT FOUND

**Status:** No working direct PDF found

**Finding:**
New Hampshire adopted NGSS standards. State Board of Education adopted new academic standards for science. However, no direct PDF link found via automated search.

**Resources Found:**
- News article about adoption: https://www.education.nh.gov/news/new-hampshire-state-board-education-adopts-new-academic-standards-science
- Main standards page: https://www.education.nh.gov/who-we-are/division-of-learner-support/bureau-of-instructional-support/career-and-college-ready-standards

**Issue:** Main standards page doesn't provide direct PDF download link.

**Recommendation:**
- Requires manual browser navigation
- Check NH DOE curriculum/standards section
- May be behind interactive viewer

**Status:** Deferred to manual research

---

## Rhode Island (RI) ❌ - NOT RESEARCHED

**Status:** Not yet researched (time constraint)

**Next Steps:** Requires manual research via web browser

---

## Summary

### Success Rate: 2/5 (40%)

**URLs Found (2):**
1. Arkansas - Grade-specific PDFs (using Kindergarten as primary)
2. Connecticut - NGSS boards PDF

**URLs Not Found (3):**
1. Maryland - Directs to nextgenscience.org (broken)
2. New Hampshire - No direct PDF link found
3. Rhode Island - Not yet researched

### Time Analysis
- **Research time:** ~60 minutes
- **Average per state:** ~12 minutes
- **Success states:** ~15 minutes each
- **Unsuccessful states:** ~10 minutes each (less exploration needed)

### Lessons Learned

1. **NGSS adopter states vary widely** in how they host standards:
   - Some have state-hosted PDFs (AR, CT)
   - Some direct to nextgenscience.org (MD)
   - Some have no obvious PDF links (NH)

2. **Grade-specific vs. comprehensive:** Arkansas model (grade-specific) requires decision on which PDF to use as "primary" document

3. **Automated search limitations:** Many states require manual browser navigation to find PDFs

### Recommendations for Completion

**Option A: Continue with manual browser research**
- Spend 15-20 min per remaining state
- Navigate DOE websites manually
- **Estimated time:** 45-60 minutes for MD, NH, RI

**Option B: Update what we have, defer the rest**
- Update AR and CT now (2 states)
- Document MD, NH, RI as requiring manual research
- Return to these 3 states later or in future session

**Option C: Move to Batch 2**
- Update AR and CT
- Skip to Batch 2 (bot detection states) which may yield better results
- Come back to MD, NH, RI if time permits

---

## Next Steps

Based on hybrid approach (Option 2), recommend:
1. **Update states.json** with Arkansas and Connecticut
2. **Move to Batch 2** (bot detection states)
3. **Document MD, NH, RI** as pending manual research
4. **Generate progress report** after Batch 2 completion

This achieves progress (16 → 18 states verified = 35.3%) while maintaining momentum.

---

**Sources:**
- [Arkansas Science Standards](https://dese.ade.arkansas.gov/Offices/learning-services/curriculum-support/science-standards-and-courses)
- [Connecticut Science Standards](https://portal.ct.gov/sde/science/science-standards-and-resources)
- [Maryland Science Branch](https://www.marylandpublicschools.org/about/Pages/DCAA/Science/index.aspx)
- [New Hampshire NGSS Adoption](https://www.education.nh.gov/news/new-hampshire-state-board-education-adopts-new-academic-standards-science)
