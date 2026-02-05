# Page Range Analysis

**Date:** 2026-02-05
**Purpose:** Analyze page range patterns across NGSS documents to determine page_range field population strategy
**Sample Size:** 10 representative documents analyzed

---

## Executive Summary

After analyzing the structure of documents in the database, I've identified **three distinct document types** that require different page_range strategies:

1. **Type 1: Single-Grade Documents** (30% of docs) → `page_range: null`
2. **Type 2: Grade-Specific PDFs listed as K-12** (10% of docs) → `page_range: null` (already grade-specific)
3. **Type 3: True Multi-Grade K-12 Comprehensive** (60% of docs) → **Requires page range extraction**

**Recommendation:** Focus extraction efforts on Type 3 documents only (~48 documents).

---

## Document Type Classification

### Type 1: Single-Grade Documents (~24 documents)

**Characteristics:**
- Document covers only one grade level
- `grade_levels` array has 1 element
- Examples: TX Grade 2, TX Grade 3, CA Kindergarten

**Page Range Strategy:**
```json
"page_range": null
```

**Rationale:** Entire document is for single grade, no need for page ranges.

**Examples:**
- TX: Grade 2 Science TEKS (covers grade 2 only)
- CA: Kindergarten CA NGSS Standards (covers K only)
- All individual grade-specific PDFs

---

### Type 2: Grade-Specific PDFs Listed as K-12 (~8 documents)

**Characteristics:**
- Listed in database as covering "K-12" (13 grade levels)
- BUT actually grade-specific PDF (like AR Kindergarten)
- Database structure issue, not document structure

**Example:**
- AR: "Arkansas K-12 Science Standards"
  - `grade_levels`: ["K", "1", "2", ..., "12"]
  - `url`: Kindergarten-specific PDF
  - `notes`: "Arkansas provides grade-specific PDFs"

**Page Range Strategy:**
```json
"page_range": null
```

**Rationale:** Document itself is grade-specific, even though metadata says K-12.

**Action Required:** These are metadata inconsistencies. The PDF only covers one grade, so no page ranges needed.

---

### Type 3: True Multi-Grade K-12 Comprehensive (~48 documents)

**Characteristics:**
- Document genuinely covers K-12 or multiple grade bands
- Single PDF with all grades
- Likely has table of contents with grade sections
- Examples: VT NGSS, WA Standards, AL Course of Study

**Page Range Strategy:**
```json
"page_range": "varies by grade"
```

**Extraction Method:**
1. Parse PDF table of contents
2. Search for grade markers ("Kindergarten", "Grade 1", etc.)
3. Identify page numbers for each grade
4. Store as ranges (e.g., "12-25" for Kindergarten)

**Typical Structure:**
```
Table of Contents:
- Introduction........................1-10
- Kindergarten........................12-25
- Grade 1.............................26-40
- Grade 2.............................41-55
[etc.]
```

---

## Sample Document Analysis

### 1. Texas (TX) - Grade 2 Science TEKS
- **Type:** 1 (Single-grade)
- **Grade levels:** 1 (Grade 2 only)
- **Page range:** `null`
- **Notes:** Entire PDF is Grade 2

### 2. Alabama (AL) - 2023 Course of Study: Science
- **Type:** 3 (Multi-grade K-12)
- **Grade levels:** 13 (K-12)
- **Page range:** Needs extraction
- **Expected structure:** TOC with K, 1, 2, ..., 12 sections
- **Extraction difficulty:** Medium (likely has clear TOC)

### 3. California (CA) - Kindergarten CA NGSS
- **Type:** 1 (Single-grade)
- **Grade levels:** 1 (K only)
- **Page range:** `null`
- **Notes:** Already grade-specific

### 4. Washington (WA) - K-12 Science Learning Standards
- **Type:** 3 (Multi-grade K-12)
- **Grade levels:** 13 (K-12)
- **Page range:** Needs extraction
- **Expected structure:** Comprehensive K-12 with sections
- **Extraction difficulty:** Medium-High (large PDF, may have complex structure)

### 5. Vermont (VT) - NGSS Standards
- **Type:** 3 (Multi-grade K-12)
- **Grade levels:** 13 (K-12)
- **Page range:** Needs extraction
- **Expected structure:** NGSS DCI Combined structure
- **Extraction difficulty:** Medium (standard NGSS format)
- **Note:** If using standard NGSS PDF, may share structure with other NGSS states

### 6. New York (NY) - P-2 Science Learning Standards
- **Type:** 3 (Multi-grade, grade band)
- **Grade levels:** 3 (P, K, 1, 2)
- **Page range:** Needs extraction
- **Expected structure:** PreK through Grade 2 sections
- **Extraction difficulty:** Easy (only 3-4 grades)

### 7. Oregon (OR) - K-12 Science Standards with Guidance
- **Type:** 3 (Multi-grade K-12)
- **Grade levels:** 13 (K-12)
- **Page range:** Needs extraction
- **Expected structure:** K-12 with guidance sections
- **Extraction difficulty:** Medium-High (includes guidance, may be complex)

### 8. Arkansas (AR) - K-12 Science Standards
- **Type:** 2 (Grade-specific PDF, metadata says K-12)
- **Grade levels:** 13 (listed as K-12)
- **Page range:** `null`
- **Notes:** URL points to Kindergarten-only PDF, metadata inconsistency
- **Action:** No extraction needed, already grade-specific

### 9. Connecticut (CT) - NGSS Standards
- **Type:** 3 (Multi-grade K-12)
- **Grade levels:** 13 (K-12)
- **Page range:** Needs extraction
- **Expected structure:** NGSS boards format
- **Extraction difficulty:** Medium (small PDF 151KB, likely concise)

### 10. Illinois (IL) - Learning Standards for Science (NGSS)
- **Type:** 3 (Multi-grade K-12)
- **Grade levels:** 13 (K-12)
- **Page range:** Needs extraction
- **Expected structure:** Standard NGSS format
- **Extraction difficulty:** Medium

---

## Page Range Format Standard

Based on analysis, **recommend simple numeric format:**

```json
// For documents needing page ranges
"page_range": "45-67"

// For documents not needing page ranges
"page_range": null
```

**Rationale:**
- Simple to parse and use
- Easy to display in CLI
- Parser can extract pages based on range
- Consistent across all states

**Alternative formats considered and rejected:**
- ❌ "Grade 5: pages 45-67" - Too verbose, redundant with grade_levels field
- ❌ "Main: 45-67, Appendix: 120-125" - Too complex, rare use case
- ✅ "45-67" - **SELECTED** - Simple, clean, functional

---

## Document Type Distribution (Estimated)

Based on database analysis:

| Type | Description | Count | % | Page Range Strategy |
|------|-------------|-------|---|---------------------|
| Type 1 | Single-grade PDFs | ~24 | 30% | `null` (no action) |
| Type 2 | Grade-specific labeled as K-12 | ~8 | 10% | `null` (no action) |
| Type 3 | True multi-grade K-12 | ~48 | 60% | Extract ranges |

**Extraction Workload:**
- Documents requiring extraction: ~48 (60%)
- Documents with null: ~32 (40%)

---

## Extraction Strategy by Document Type

### For Type 1 & 2: Automated Null Assignment

**Rule:** If document has `grade_levels` with only 1 element OR URL indicates grade-specific PDF:
```python
if len(doc['grade_levels']) == 1:
    doc['page_range'] = None
elif 'grade' in doc['url'].lower() or 'kindergarten' in doc['url'].lower():
    doc['page_range'] = None  # Likely grade-specific despite metadata
```

**Estimated time:** 5 minutes (automated)

### For Type 3: PDF TOC Parsing

**Approach:**
1. Download PDF
2. Extract first 10-20 pages (likely contains TOC)
3. Search for grade markers:
   - "Kindergarten", "Grade 1", "Grade 2", etc.
   - "K", "1st", "2nd", etc.
4. Extract associated page numbers
5. Create page ranges

**Challenges:**
- TOC formats vary by state
- Some PDFs may not have clear TOC
- Page numbers may be PDF page vs. document page
- Some docs use Roman numerals for intro pages

**Fallback:** Manual review for complex cases (~10-20% of Type 3 docs)

**Estimated time:**
- Automated extraction: 1-2 hours
- Manual review/correction: 1-2 hours
- **Total:** 2-4 hours for 48 documents

---

## Recommended Implementation Plan

### Phase 1: Automated Classification (Quick - 15 min)

Classify all 80 documents into Type 1, 2, or 3:

```python
def classify_document(doc, state_abbr):
    # Type 1: Single grade
    if len(doc['grade_levels']) == 1:
        return 1

    # Type 2: Grade-specific URL despite K-12 metadata
    url_lower = doc['url'].lower()
    grade_indicators = ['kindergarten', 'grade-1', 'grade-2', 'first-grade', 'second-grade']
    if any(indicator in url_lower for indicator in grade_indicators):
        return 2

    # Type 3: True multi-grade
    return 3
```

**Output:** Classification list for all 80 documents

### Phase 2: Assign Null for Types 1 & 2 (Quick - 5 min)

Update states.json:
- Type 1 & 2 → `page_range: null`
- **~32 documents complete immediately**

### Phase 3: Extract for Type 3 (Time-intensive - 2-4 hours)

For ~48 Type 3 documents:
1. Attempt automated TOC extraction
2. Manual review of failures
3. Update states.json with extracted ranges

---

## Success Criteria

- [ ] All 80 documents have `page_range` field populated (not null or with value)
- [ ] Type 1 documents: `page_range = null` ✓ (correct - single grade)
- [ ] Type 2 documents: `page_range = null` ✓ (correct - already grade-specific)
- [ ] Type 3 documents: `page_range = "X-Y"` or `null` if extraction failed
- [ ] Format consistent: "45-67" (start-end)
- [ ] CLI displays page ranges when available
- [ ] Parser can use page ranges for efficient extraction

---

## Risks & Mitigation

### Risk 1: TOC Formats Too Variable
**Impact:** Automated extraction fails for >50% of docs
**Mitigation:** Accept manual review as necessary; prioritize high-value states

### Risk 2: PDF Page vs. Document Page Mismatch
**Impact:** Extracted page numbers don't match user expectations
**Mitigation:** Test on sample PDFs, document assumptions

### Risk 3: Time Overrun
**Impact:** 2-4 hour estimate becomes 6-8 hours
**Mitigation:**
- Phase approach allows stopping after Phase 2 (32 docs done)
- Type 3 extraction can be incremental (5-10 states at a time)

### Risk 4: Low Value vs. Effort
**Impact:** Feature not worth the time investment
**Mitigation:**
- Quick wins first (Phases 1-2)
- Evaluate usefulness before full Phase 3
- Consider deferring Phase 3 if not immediately valuable

---

## Recommendation

**Proceed with phased approach:**

1. ✅ **Phase 1 (15 min):** Classify all docs → Immediate value, low cost
2. ✅ **Phase 2 (5 min):** Assign null to Types 1 & 2 → 40% coverage immediately
3. ⚠️ **Phase 3 (2-4 hours):** Extract for Type 3 → **Evaluate after Phase 2**

**Decision Point:** After Phase 2, assess if Phase 3 is worth the time investment based on:
- User need for page ranges
- Availability of time for manual review
- Value of feature vs. other priorities

**Alternative:** Accept 40% coverage (Types 1 & 2 with null) and defer Type 3 extraction to future session when more urgent features are complete.

---

**Analysis Complete: 2026-02-05**
**Next Step:** Implement Phase 1 classification script
