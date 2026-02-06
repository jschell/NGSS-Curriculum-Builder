# Page Range Extraction Status - All States

**Last Updated:** 2026-02-05
**Total States:** 51
**Parser Run:** Complete

---

## 📊 Summary Statistics

Based on parse_standards.py run on all 51 states:

| Status | Count | Percentage |
|--------|-------|------------|
| **Page Ranges Extracted** | ~20-25 | ~40-50% |
| **Grade-Specific Docs (No Ranges Needed)** | ~6-8 | ~12-16% |
| **Errors/Inaccessible** | ~18-26 | ~35-51% |

---

## ✅ States with Successful Page Range Extraction

These states have single comprehensive PDFs with page ranges successfully extracted:

### High Confidence Extractions
- **Alabama (AL)** - 2023 Alabama Course of Study: Science
- **Arkansas (AR)** - Arkansas K-12 Science Standards
- **Delaware (DE)** - Delaware Science Standards
- **Florida (FL)** - Florida Science Standards
- **Hawaii (HI)** - Hawaii NGSS Standards
- **Illinois (IL)** - K-12 SS Standards
- **Iowa (IA)** - Iowa Science Standards
- **Maryland (MD)** - Maryland Science Standards
- **New Jersey (NJ)** - New Jersey Science Standards
- **New Mexico (NM)** - NM Standards
- **New York (NY)** - NYS Science Learning Standards
- **Nevada (NV)** - Nevada Academic Content Standards
- **Ohio (OH)** - Ohio Science Standards
- **Oregon (OR)** - Oregon Science Standards
- **Rhode Island (RI)** - Rhode Island Science Standards

### Medium Confidence (Needs Review)
- **Minnesota (MN)** - Minnesota Science Standards
- **Mississippi (MS)** - MS Science Standards
- **New Hampshire (NH)** - NH Science Standards
- **Vermont (VT)** - Vermont Science Standards

---

## 📄 States with Grade-Specific Documents

These states have separate documents per grade level - **no page ranges needed** because each grade has its own PDF:

### Documented Multi-Document States

**California (CA)** - 16+ documents
- Elementary: Separate PDF per grade (K, 1, 2, 3, 4, 5)
- Middle School: 6 PDFs (2 models × 3 grades)
- High School: 4 discipline PDFs
- **Status:** Each grade = dedicated document ✅

**Texas (TX)** - 3 comprehensive documents
- Elementary (K-5): ch112a.pdf
- Middle School (6-8): ch112b.pdf
- High School (9-12): ch112c.pdf
- **Status:** Each level = dedicated document ✅

**Indiana (IN)** - Grade-specific only
- Separate PDF for each grade K-8
- Separate PDFs for HS courses (Biology, Chemistry, etc.)
- **Status:** Each grade = dedicated document ✅

**Georgia (GA)** - Grade-specific only
- Separate PDFs by grade band (K-5, 6-8, 9-12)
- **Status:** Each grade = dedicated document ✅

**North Carolina (NC)** - 2023 grade-band specific
- K-2, 3-5, 6-8 grade bands
- HS course-specific documents
- **Status:** Each band = dedicated document ✅

**Louisiana (LA)** - Web-based/grade-specific
- K-12 Louisiana Student Standards for Science (LSSS)
- Organized by grade with crosswalks
- **Status:** Web-based structure ✅

**Missouri (MO)** - Dual documents
- K-5: One PDF
- 6-12: Separate PDF
- **Status:** Two dedicated documents ✅

---

## ❌ States with Errors/Inaccessible Documents

These states encountered errors during parsing - requires manual follow-up:

### 403 Forbidden (Access Denied)
- **Arizona (AZ)** - azed.gov blocks automated access
- **Washington (WA)** - ospi.k12.wa.us returns 403

### 404 Not Found
- **Maine (ME)** - Word doc URL returns 404
- **Michigan (MI)** - PDF URL returns 404

### SSL Certificate Errors
- **Colorado (CO)** - SSL certificate verification failed
- **Kansas (KS)** - community.ksde.org SSL issues

### Connection/Fetch Errors
- **Alaska (AK)** - Failed to fetch
- **Idaho (ID)** - Failed to fetch
- **Kentucky (KY)** - Failed to fetch
- **Montana (MT)** - Failed to fetch
- **Nebraska (NE)** - Failed to fetch
- **North Dakota (ND)** - Failed to fetch
- **Oklahoma (OK)** - Failed to fetch
- **Pennsylvania (PA)** - Failed to fetch
- **South Carolina (SC)** - Failed to fetch
- **South Dakota (SD)** - Failed to fetch
- **Tennessee (TN)** - Failed to fetch
- **Utah (UT)** - Failed to fetch
- **Virginia (VA)** - Failed to fetch (web page, not PDF)
- **West Virginia (WV)** - Failed to fetch (web page, not PDF)
- **Wisconsin (WI)** - Failed to fetch
- **Wyoming (WY)** - Failed to fetch

### Web-Based Standards (Not PDF)
- **Connecticut (CT)** - Uses nextgenscience.org (NGSS direct adoption)
- **District of Columbia (DC)** - May have PDF access issues
- **Massachusetts (MA)** - Large PDF, may have fetch issues

---

## 🔧 Recommended Actions

### High Priority - Fix Accessible Documents

**States that should have working PDFs but encountered errors:**
1. **Tennessee (TN)** - We verified PDF exists, parser should retry
2. **South Carolina (SC)** - We verified PDF exists, parser should retry
3. **Wisconsin (WI)** - We verified PDF exists, parser should retry
4. **Wyoming (WY)** - We verified PDF exists, parser should retry
5. **Massachusetts (MA)** - We verified PDF exists, parser should retry

**Action:** Re-run parser with increased timeout or manual download

### Medium Priority - Manual Verification Needed

**States with access restrictions:**
1. **Arizona (AZ)** - Manually download PDF, then parse locally
2. **Washington (WA)** - Manually download PDF, then parse locally
3. **Michigan (MI)** - Find working URL, update states.json
4. **Maine (ME)** - Find working URL (Word doc issue)

**Action:** Manual download → local parsing

### Low Priority - Web-Based States

**States using NGSS directly (no custom PDFs):**
- Connecticut (CT)
- Vermont (VT) - Though extraction succeeded
- Kansas (KS)

**Action:** Note "Uses NGSS directly - reference nextgenscience.org"

---

## 📋 Implementation Notes

### For States with Page Ranges Extracted
Update states.json documents array with page_range data:
```json
{
  "grade_levels": ["3"],
  "page_range": "38-42"
}
```

### For States with Grade-Specific Documents
Add note to states.json:
```json
{
  "notes": "Grade-specific documents - each grade has dedicated PDF",
  "special_structure": "grade_specific_documents"
}
```

### For States with Errors
Add temporary note:
```json
{
  "notes": "Parser error - requires manual extraction",
  "page_range": null
}
```

---

## 📊 Current Page Range Coverage

**Before URL Research:**
- States with page_range data: 13/51 (25%)

**After URL Research + Parsing:**
- States with page_range data: ~25-30/51 (49-59%)
- States with grade-specific docs: ~6-8/51 (12-16%)
- **Total usable structure:** ~31-38/51 (61-75%)

**Improvement:** +36-50% states now have actionable page/document data

---

## 🎯 Next Steps

1. **Apply Successful Extractions**
   - Update states.json with page ranges for ~20-25 states
   - Add "grade_specific" notes for 6-8 states

2. **Manual Follow-up**
   - Download and parse locally: AZ, WA, TN, SC, WI, WY, MA
   - Find working URLs: MI, ME
   - ~10-15 states need manual attention

3. **Verify and Test**
   - Test page range queries work correctly
   - Verify grade-specific document references
   - Validate data integrity

**Estimated Time:** 2-4 hours for manual follow-up + application

---

*End of Page Range Status Report*
*Generated: 2026-02-05*
