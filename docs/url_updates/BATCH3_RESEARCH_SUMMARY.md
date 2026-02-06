# Batch 3 URL Research Summary - PDF Parse Error States

**Research Date:** 2026-02-05
**Researcher:** Claude (automated web search via MCP Brave Search + browser navigation)
**Batch:** Batch 3 - PDF Parse Errors
**States Researched:** 6
**Research Method:** Automated web search + browser verification

---

## Overall Results

- **Working URLs Found:** 6/6 states (100%)
- **High Confidence URLs:** 5 states (AK, OR, NV, MN, MO)
- **Medium Confidence URLs:** 1 state (ME - Word format instead of PDF)
- **Special Cases:** 2 states (MO has 2 documents, ME is Word format)
- **Time Spent:** ~45 minutes

---

## Success Rate by State

| State | Status | URL Found | Confidence | Notes |
|-------|--------|-----------|------------|-------|
| AK | ✅ | Yes | High | Direct PDF link |
| OR | ✅ | Yes | High | Complete K-12 with guidance |
| NV | ✅ | Yes | High | NGSS adoption (DCI arrangements) |
| MN | ✅ | Yes | High | 2022 standards from Legislative Reference Library |
| MO | ✅ | Yes (2 docs) | High | Separate K-5 and 6-12 PDFs |
| ME | ⚠️ | Yes (DOCX) | Medium | Word format, not PDF |

---

## Detailed Findings

### Alaska (AK) ✅
**URL:** https://education.alaska.gov/akstandards/science/science-standards-for-alaska.pdf
**Source:** https://education.alaska.gov/akstandards/science
**Document Type:** PDF
**Coverage:** K-12 Science Standards for Alaska
**Confidence:** High
**Notes:** Direct link from Alaska Department of Education. PDF confirmed accessible.

---

### Oregon (OR) ✅
**URL:** https://www.oregon.gov/ode/educator-resources/standards/science/Documents/K-12%20%20Oregon%20Science%20Standards%20with%20Guidance.pdf
**Source:** https://www.oregon.gov/ode/educator-resources/standards/science/
**Document Type:** PDF
**Coverage:** 2022 Oregon K-12 Science Standards (Adopted June 2022)
**Confidence:** High
**Notes:** Complete K-12 document with implementation guidance. 50 pages.

---

### Nevada (NV) ✅
**URL:** https://webapp-strapi-paas-prod-nde-001.azurewebsites.net/uploads/nvacss_dci_arrangements_226290ea15.pdf
**Source:** https://doe.nv.gov/offices/office-of-teaching-and-learning/science
**Document Type:** PDF
**Coverage:** Nevada Academic Content Standards for Science (NVACSS) - DCI Arrangements
**Confidence:** High
**Notes:** Nevada adopted NGSS in February 2014. This PDF organizes standards by Disciplinary Core Ideas. NVACSS is identical to NGSS.

---

### Minnesota (MN) ✅
**URL:** https://www.lrl.mn.gov/docs/2025/mandated/251893.pdf
**Source:** https://education.mn.gov/MDE/dse/stds/sci/
**Document Type:** PDF
**Coverage:** Minnesota Academic Standards in Science—Final 1 May 2022 (edits October 2022)
**Confidence:** High
**Notes:** Complete K-12 standards. Hosted on Minnesota Legislative Reference Library website.

---

### Missouri (MO) ✅ (Special Case)
**URL 1 (K-5):** https://dese.mo.gov/media/pdf/curr-mls-standards-sci-k-5-sboe-2016
**URL 2 (6-12):** https://dese.mo.gov/media/pdf/curr-mls-standards-sci-6-12-sboe-2016
**Source:** https://dese.mo.gov/college-career-readiness/curriculum/science
**Document Type:** PDF (2 documents)
**Coverage:** Missouri Learning Standards for Science (K-5 and 6-12 separately)
**Confidence:** High
**Special Handling Required:** Missouri publishes two separate documents instead of one comprehensive K-12 document. Both documents needed to cover complete K-12 standards.
**Notes:** Both PDFs confirmed on Missouri DESE website. Will need to handle as two separate documents in states.json.

---

### Maine (ME) ⚠️ (Special Case)
**URL:** https://www.maine.gov/doe/sites/maine.gov.doe/files/inline-files/2019%20MLR%20Science%20and%20Engineering.docx
**Source:** https://www.maine.gov/doe/learning/content/science/review
**Document Type:** DOCX (Word Document)
**Coverage:** Maine Learning Results: Science, Technology, and Engineering (2019)
**Confidence:** Medium
**Issue:** Comprehensive document only available in Word format (.docx), not PDF.
**Alternative:** Maine provides separate grade-band documents (K-2, 3-5, 6-8, 9-12) as individual PDF/DOCX files.
**Notes:** Maine adopted NGSS-based standards in 2019. May need to accept Word format or use grade-band documents instead.

---

## Research Methodology

### Tools Used
1. **MCP Brave Web Search** - Primary research tool for finding official DOE pages
2. **MCP Browser Navigation** - Verification and navigation of state DOE websites
3. **MCP Fetch** - PDF verification and content checking

### Search Strategy
1. Search for "[State] science standards K-12 PDF download 2024"
2. Navigate to state Department of Education website
3. Locate science/standards section
4. Find PDF download links
5. Verify PDF accessibility
6. Document findings in JSON format

### Success Factors
- All 6 states have working URLs (100% success rate)
- 5/6 states have direct PDF links (83%)
- 1/6 states has Word format document (17%)
- Average research time: ~7-8 minutes per state
- Automated web search proved highly effective

---

## Issues Encountered

### Missouri (MO)
- **Issue:** Two separate documents (K-5 and 6-12) instead of single K-12 PDF
- **Resolution:** Document both URLs, note special handling required
- **Impact:** Will need to handle as two separate document entries in states.json

### Maine (ME)
- **Issue:** No comprehensive PDF available - only Word (.docx) format
- **Resolution:** Document Word format URL, note alternative grade-band PDFs available
- **Impact:** May need to accept non-PDF format or use alternative grade-band approach

---

## Recommendations

### For Missouri (MO)
**Option 1:** Create two separate document entries in states.json
```json
{
  "MO": {
    "documents": [
      {
        "title": "Missouri Learning Standards for Science K-5",
        "url": "https://dese.mo.gov/media/pdf/curr-mls-standards-sci-k-5-sboe-2016",
        "grades": ["K", "1", "2", "3", "4", "5"]
      },
      {
        "title": "Missouri Learning Standards for Science 6-12",
        "url": "https://dese.mo.gov/media/pdf/curr-mls-standards-sci-6-12-sboe-2016",
        "grades": ["6", "7", "8", "9", "10", "11", "12"]
      }
    ]
  }
}
```

### For Maine (ME)
**Option 1:** Accept Word format (most comprehensive)
- Use the 2019 MLR Science and Engineering DOCX

**Option 2:** Use grade-band PDFs (if PDF required)
- Separate documents for K-2, 3-5, 6-8, 9-12
- Available on Maine DOE website

**Recommendation:** Accept Word format as it provides most comprehensive coverage

---

## Next Steps

1. ✅ **Research Complete** - All 6 states researched
2. ⏳ **Apply URL Updates** - Update states.json with new URLs
3. ⏳ **Handle Special Cases** - Implement Missouri (2 docs) and Maine (Word format) properly
4. ⏳ **Test PDF Accessibility** - Verify all URLs work in production
5. ⏳ **Re-run Page Range Extraction** - Extract page ranges from newly accessible documents

---

## Files Created

Research documentation:
- `docs/url_updates/ak_science_standards.json`
- `docs/url_updates/or_science_standards.json`
- `docs/url_updates/nv_science_standards.json`
- `docs/url_updates/mn_science_standards.json`
- `docs/url_updates/mo_science_standards.json`
- `docs/url_updates/me_science_standards.json`
- `docs/url_updates/BATCH3_RESEARCH_SUMMARY.md` (this file)

---

## Statistics

**Overall Progress:**
- **Batches 1-3 Complete:** 23 states researched
- **URLs Found:** 21/23 (91.3% success rate)
- **High Confidence:** 20 states
- **Medium Confidence:** 1 state (ME - Word format)
- **Total Time:** ~2.5 hours across all batches

**Batch 3 Specific:**
- **States:** 6
- **Success Rate:** 100% (6/6)
- **Time:** ~45 minutes
- **Method:** Automated web search + browser verification

---

**Batch 3 Status:** ✅ **COMPLETE**
**Next Batch:** Batch 4 - SSL/Connection/404 Errors (4 states: GA, IN, SC, TN)
