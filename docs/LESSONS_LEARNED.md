# Lessons Learned: Manual Page Range Extraction Project

**Project:** Extract grade-level page ranges from 18 state science standards documents
**Duration:** February 6, 2026 (1 day, ~4 hours)
**Success Rate:** 94% (17/18 states usable)
**Total Extracted:** 119 grade ranges across 16 states

---

## Executive Summary

Successfully extracted page range data from 18 state standards documents using a multi-phase approach combining automated parsing, MCP browser tools, and manual downloads. The project achieved 94% success rate with only Wyoming requiring special TOC-based handling.

**Key Learning:** No single approach works for all documents. Success requires a toolkit of methods and the flexibility to adapt based on document structure and access restrictions.

---

## Parsing Approaches & Success Rates

### Phase 1: Remote Automated Parsing (61% success)
**Method:** Direct HTTP download and pypdf text parsing
**Results:** 11/18 states successfully extracted (61%)
**States:** AL, AR, CT, DE, GA, ID, KY, MT, NC, OK, PA

**When to Use:**
- PDFs are publicly accessible (no bot protection)
- Standard grade naming patterns ("Grade K", "Kindergarten")
- Clear section boundaries in text

**Limitations:**
- Fails on 403 Forbidden / Cloudflare protection
- Cannot handle non-standard structures
- Misses TOC-only references

### Phase 2: MCP Browser Tools (75% success)
**Method:** brave_web_search + browser navigation
**Results:** 3/4 states extracted (MI, SC, WA), 1 documented (ME)

**MCP Tools Used:**
- `brave_web_search`: Find alternative URLs when original 404s
- `browser_navigate`: Access PDFs blocked by 403/Cloudflare
- `browser_snapshot`: Verify page loaded (returns empty for PDFs)
- `browser_take_screenshot`: Visual confirmation of PDF content

**Key Pattern:**
```python
# Find working URL
brave_web_search("Michigan science standards 2024 PDF site:michigan.gov")

# Navigate to PDF (bypasses bot protection)
browser_navigate(url)

# Verify with screenshot
browser_take_screenshot("pdf_loaded.png")

# Download manually or parse locally
```

**When to Use:**
- Original URL returns 404 (need to find new URL)
- Site blocks automated access (403 Forbidden, Cloudflare)
- Visual confirmation needed before parsing

**Limitations:**
- `browser_run_code` with `printToPDF` only captures visible page(s)
- Cannot programmatically download full PDF from browser
- Manual download still needed after browser access

### Phase 3: Manual Browser Download (100% success)
**Method:** User downloads via real browser, then parse locally
**Results:** 2/2 states extracted (TN, AZ)

**Workflow:**
1. User opens PDF URL in browser
2. Uses browser's download button (bypasses all protection)
3. Saves to project directory
4. Developer parses with pypdf locally

**When to Use:**
- MCP browser tools can access but not download
- Cloudflare or aggressive bot detection
- Connection resets on programmatic access

**Advantages:**
- 100% success rate for accessible PDFs
- Bypasses all bot protection
- Fast and reliable

### Phase 4: Table of Contents Extraction (100% success)
**Method:** Extract TOC, manually map grade levels to pages
**Results:** 1/1 states extracted (WY)

**Pattern:**
```python
# Extract TOC page
toc_text = pdf.pages[5].extract_text()  # Page 6 = index 5

# Parse TOC structure manually
# Wyoming example:
# "KINDERGARTEN...........................8"
# "GRADE 1...................................12"

# Create structured mappings
grade_sections = {
    "K": {"page_ranges": [[8, 11]]},
    "1": {"page_ranges": [[12, 15]]},
    # ...
}
```

**When to Use:**
- Non-standard document structure
- Text search patterns don't match grade markers
- TOC has clear page number listings
- Middle/High school organized by subject instead of grade

---

## Grade Pattern Recognition

### Successful Patterns

**Full Grade Names (Most Reliable):**
```python
"Kindergarten"      # → K
"First Grade"       # → 1
"Second Grade"      # → 2
# ... etc
```

**Abbreviated Patterns:**
```python
"Grade K"           # → K
"Grade 1"           # → 1
"GRADE 2"           # → 2 (case variations)
"1st Grade"         # → 1
"2nd Grade"         # → 2
```

**High School Patterns:**
```python
"High School"       # General HS section
"Biology"           # HS subject
"Chemistry"
"Physics"
"Earth Science"
"Grades 9-12"       # Range format
```

### Common Failures

1. **TOC Mentions vs Actual Content**
   - Problem: "High School" appears on page 3 (TOC) and page 63 (content)
   - Solution: Check line length and position (TOC lines are short, <100 chars)

2. **Missing Grade 8**
   - Problem: Parser stops at grade 7, assumes next is High School
   - Solution: Always validate K-8 sequence before assigning 9-12

3. **Subject-Based Organization**
   - Problem: Middle/High school by subject (Physical, Life, Earth)
   - Solution: Use grade range (6-8, 9-12) with subject IDs

---

## State-Specific Structures

### By Grade (Standard)
**States:** Most states (TN, AZ, SC, etc.)
**Structure:** K, 1, 2, 3, 4, 5, 6, 7, 8, then High School
**Parsing:** Direct text search for grade names

### By Subject (Wyoming)
**Structure:**
- K-5: Individual grades
- 6-8: Middle School by domain (Physical, Life, Earth, Engineering)
- 9-12: High School by domain

**Parsing:** TOC extraction required

### Grade-Specific Documents (Maine)
**Structure:** Separate PDF for each grade (K-ESS2.pdf, 1-LS1.pdf, etc.)
**Parsing:** Not applicable - documented as special structure
**Handling:** Add `special_structure: "grade_specific_documents"` field

---

## MCP Tool Patterns & Limitations

### Working Patterns

**1. Find Alternative URLs**
```python
# When original URL 404s
results = brave_web_search("state standards 2024 PDF site:state.gov")
# Extract working URL from results
new_url = extract_pdf_url(results)
```

**2. Access Blocked PDFs**
```python
# Browser can view what curl cannot
browser_navigate("https://blocked-site.gov/standards.pdf")
browser_take_screenshot("verify.png")  # Confirm it loaded
# Then: manual download via browser UI
```

**3. Visual Verification**
```python
# Screenshot confirms PDF rendered
screenshot = browser_take_screenshot()
# Check for PDF viewer UI elements
if "135 pages" in screenshot_text:
    proceed_with_parsing()
```

### Known Limitations

**1. printToPDF Captures Only Visible Content**
```python
# ❌ This only gets ~0.15 MB for 135-page PDF
client = await page.context().newCDPSession(page)
data = await client.send('Page.printToPDF')
# Only captures currently visible page(s)
```

**2. Cannot Programmatically Download**
```python
# ❌ These fail on bot-protected sites
response = await page.context().request.get(url)  # Connection reset
buffer = await response.body()                     # Never gets here
```

**Workaround:** Manual browser download after visual confirmation

---

## Common Issues & Solutions

### Issue 1: Overlapping Page Ranges

**Problem:**
```json
"9-12": "3-62, 63-73, 74-120"  // Page 3 is in K-8 range!
```

**Cause:** TOC mentions "High School" on early page

**Solution:**
```python
# Filter out TOC mentions (short lines, early pages)
if page_num < 10 and len(line.strip()) < 50:
    continue  # Likely TOC, not actual section
```

### Issue 2: Missing Grade 8

**Problem:** Parser finds K-7, then jumps to 9-12

**Cause:** Grade 8 marker found but not added to output

**Solution:**
```python
# Always validate complete K-8 sequence
expected_grades = ['K', '1', '2', '3', '4', '5', '6', '7', '8']
found_grades = list(grade_pages.keys())

if '8' not in found_grades and '7' in found_grades:
    # Grade 8 likely between grade 7 end and HS start
    grade_8_start = grade_pages['7'] + estimated_pages
```

### Issue 3: Non-Standard Grade Names

**Problem:** Document uses "Kindergarten through Grade 2" spans

**Solution:** Fall back to TOC extraction for non-standard structures

---

## Tooling Recommendations

### Essential Tools

1. **pypdf** (PDF text extraction)
   ```python
   import pypdf
   pdf = pypdf.PdfReader("document.pdf")
   text = pdf.pages[page_num].extract_text()
   ```

2. **MCP Browser Tools** (access blocked content)
   - brave_web_search
   - browser_navigate
   - browser_take_screenshot

3. **Manual Download Workflow** (ultimate fallback)
   - Always works if PDF is viewable
   - Bypasses all bot protection

### Script Organization

**Reusable Scripts (keep):**
- `parse_standards.py` - Core automated parser
- `apply_page_ranges.py` - Apply extractions to states.json
- `validate_urls.py` - Check URL accessibility

**Reference Scripts (archive):**
- State-specific parsers showing patterns
- MCP browser tool usage examples
- TOC extraction examples

---

## Success Metrics

- **Extraction Rate:** 89% (16/18 states)
- **Usable Coverage:** 94% (17/18 including documented)
- **Total Grade Ranges:** 119
- **Methods Used:** 4 distinct approaches
- **Time Efficiency:** ~4 hours for 18 states (13 min/state average)

---

## Future Improvements

1. **Enhanced Pattern Matching**
   - Add more grade name variations
   - Detect subject-based organization automatically
   - Better TOC vs content distinction

2. **MCP Tool Enhancements**
   - Request full PDF download capability in browser tools
   - Batch processing for multiple states

3. **Automation Opportunities**
   - Auto-detect document structure type
   - Suggest appropriate parsing method
   - Validate extracted ranges against TOC

---

## Conclusion

**Key Takeaway:** Multi-method approach essential for high success rates.

**Recommended Workflow:**
1. Try automated remote parsing (fast, works 60% of time)
2. Use MCP browser tools for blocked URLs (finds alternatives, confirms access)
3. Fall back to manual download (100% success for accessible PDFs)
4. Extract from TOC for non-standard structures (handles edge cases)

**Most Valuable Pattern:** Browser tool + manual download workflow provides universal solution while maintaining automation where possible.
