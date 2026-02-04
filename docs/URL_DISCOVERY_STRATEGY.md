# URL Discovery Strategy Guide

## Purpose

This guide documents the URL discovery process for fixing states with partial URL failures. The strategy uses state website navigation to systematically find working document URLs.

## When to Use Website Discovery

**Good candidates:**
- States with partial URL failures (some working, some broken)
- NGSS-aligned states (consistent URL structures expected)
- States with documented `website` and `science_page` fields
- States with grade-specific or range-based documents

**Poor candidates:**
- States with 100% failure (homepage may be broken too)
- States with 100% working (no fixes needed)
- States without website field in states.json
- States using external hosting exclusively (nextgenscience.org, etc.)

## Discovery Process

### Navigation Strategy: Step-by-Step

**Process Overview:**
1. **Test State Website** - Verify state.website is accessible
2. **Navigate to Science Page** - Access state.science_page
3. **Discover Document Links** - Find all PDF URLs on science page
4. **Test Discovered URLs** - Validate each URL returns working PDF
5. **Match to Expected Documents** - Link working URLs to states.json entries

### Step 1: Test State Website

**Goal:** Verify state education agency website is accessible

**What to test:**
- HTTP status (should be 200)
- Content loads correctly
- No major errors in HTML

**Example (Oregon):**
```
Homepage: https://www.oregon.gov/ode
Test: GET request
Expected: HTTP 200, HTML loads
```

**If homepage fails:**
- Check for alternate URLs
- Look for website restructure
- Mark state for manual investigation

### Step 2: Navigate to Science Page

**Goal:** Access the science standards/resources page

**What to expect:**
- HTTP 200 OK
- Links to science standards documents
- May have grade-level or document organization

**Example (Oregon):**
```
Science Page: https://www.oregon.gov/ode/educator-resources/standards/science/pages/sciencestandards.aspx
Expected: Links to Oregon Science Standards documents
```

**If science page fails:**
- Look for alternate navigation paths
- Check for moved content
- Document in discovery results

### Step 3: Discover Document Links

**Goal:** Find all PDF links on the science page

**Discovery methods:**

**Method A: Parse HTML for PDF Links**
- Search for all `href` attributes
- Filter for `.pdf` extension
- Filter for same domain only
- Extract absolute URLs

**Method B: Follow Section Links**
- Many pages organize by grade range (K-5, 6-8, 9-12)
- Navigate each section
- Discover documents within sections

**Method C: Look for Download Directories**
- Some sites have `/downloads/` or `/documents/` folders
- Try accessing directory listing
- List all PDF files

**What to capture:**
- Full URL for each PDF
- Document title (from link text or filename)
- File size (if available)

### Step 4: Test Discovered URLs

**Goal:** Validate each discovered URL returns a working PDF

**Testing approach:**
1. HTTP HEAD request (fast)
2. Verify status code 200
3. Verify Content-Type: application/pdf
4. Optionally: Download small portion to verify

**Expected success criteria:**
- HTTP 200 OK
- Content-Type: application/pdf
- No authentication required
- File size reasonable (> 10 KB, < 50 MB)

**Common failures:**
- 404 Not Found: Document moved or renamed
- 403 Forbidden: Bot detection or access restrictions
- 500 Server Error: Temporary server issue

### Step 5: Match to Expected Documents

**Goal:** Link discovered working URLs to states.json entries

**Matching strategies:**

**Strategy A: Exact Title Match**
- Compare discovered link text to document titles
- Look for exact or near-exact matches
- Best for documents with clear names

**Strategy B: Grade Level Match**
- Extract grade number from URL path/filename
- Match to document's `grade_levels` field
- Works for grade-specific documents

**Strategy C: Range Match**
- Match "K-12" URLs to complete documents
- Match "K-5", "6-8" URLs to range documents
- Works for documents with multiple grades

**Strategy D: Keyword Match**
- Look for "science", "standards", "ngss" in URL
- Match to state name if present
- Works for documents with generic names

**Matching priority:**
1. Exact title match (highest confidence)
2. Grade level match
3. Range match
4. Keyword match (lowest confidence)

## Applying Discovered URLs

### Safety First

Before applying any discovered URLs:
1. **Create backup:** `cp data/states.json data/states.json.backup`
2. **Validate backup:** `python -m json.tool data/states.json.backup`
3. **Document findings:** Use docs/templates/url_update_template.md
4. **Review matches:** Verify manually before applying
5. **Low confidence matches:** Require human review

### Application Process

Use `scripts/apply_discovered_urls.py`:
```bash
python scripts/apply_discovered_urls.py
```

**What the script does:**
1. Loads discovery results
2. Extracts matched documents
3. Updates states.json with new URLs
4. Adds `url_source` field (science page URL)
5. Adds `last_verified` field (current date)

### Validation After Updates

Always run:
```bash
# Validate JSON
python -m json.tool data/states.json

# Test CLI
python state_science_standards_system.py state [STATE]

# Re-validate URLs
uv run validate_urls.py --states [STATE]
```

## Success Criteria

A discovery attempt is successful when:
- [ ] State website homepage accessible
- [ ] Science standards page accessible
- [ ] PDF links discovered (at least 1)
- [ ] Discovered URLs tested and validated
- [ ] At least 1 URL matched to expected document
- [ ] Matched URLs return working PDFs
- [ ] Content matches expected grade level
- [ ] states.json updated successfully

## Failure Analysis

### If Discovery Fails at Homepage

**Document findings:**
1. HTTP status code and error message
2. Any alternate URLs found
3. Check if URL structure changed

**Next steps:**
1. Check Wayback Machine for old working homepage
2. Google search state education agency
3. Look for news about website migration
4. Mark for manual investigation

### If Discovery Fails at Science Page

**Document findings:**
1. Science page URL error
2. Navigation paths tried
3. Any alternate science pages found

**Next steps:**
1. Look for science content in different section
2. Check for recent website restructure
3. Try site search for "science standards"
4. Mark for manual research

### If No Matches Found

**Document findings:**
1. URLs discovered and tested
2. Expected documents vs available documents
3. Matching strategy gaps

**Next steps:**
1. Try different matching strategies
2. Look for alternate naming conventions
3. Check if documents exist under different organization
4. Mark for manual review

## State-by-State Strategy

Based on partial states analysis:

### Oregon (OR) - Proven Success

- **NGSS Status:** Direct adoption
- **Website:** https://www.oregon.gov/ode
- **Science Page:** https://www.oregon.gov/ode/educator-resources/standards/science/pages/sciencestandards.aspx
- **Expected documents:** 7 (K-12 + Grades K-5)
- **Discovery strategy:** Parse science page for PDF links
- **Discovery results:** 
  - 23 PDF links discovered
  - 22/23 URLs working (95.7% success rate)
  - 6/7 documents matched (85.7% match rate)
- **Applied updates:** 6/7 documents (85.7%) successfully updated
- **Overall success rate:** 85.7%

**Lessons Learned:**
1. Oregon ODE website is accessible and well-structured
2. Grade-specific URLs follow clear pattern: `.../Documents/[N]...`
3. K-12 document also accessible with different naming
4. Title-based matching works well for Oregon
5. High success rate indicates approach is effective

**For Other Partial States:**
- Apply same 5-step discovery process
- Expect similar or better success rates for other NGSS states
- Non-NGSS states may have different structures
- Success rate will inform strategy effectiveness

## Automation Potential

Future enhancements:
1. **Multi-state discovery:** Apply to all partial states in sequence
2. **Intelligent matching:** Use title similarity algorithms
3. **Success rate tracking:** Track which strategies work best
4. **Auto-apply:** Automatically apply high-confidence matches (> 0.9)
5. **Human review queue:** Flag low-confidence matches for review

## Scripts Created

### scripts/discover_urls_from_website.py

**Purpose:** Automate the 5-step website navigation discovery process

**Features:**
- Tests state website accessibility
- Navigates to science page
- Discovers all PDF links
- Tests each discovered URL
- Matches URLs to expected documents
- Generates detailed discovery report

**Usage:**
```bash
uv run --with httpx python scripts/discover_urls_from_website.py
```

**Output:** `docs/discovered_urls.json`

### scripts/apply_discovered_urls.py

**Purpose:** Apply discovered working URLs to states.json

**Features:**
- Loads discovery results
- Updates document URLs
- Adds `url_source` field
- Adds `last_verified` field
- Validates JSON after updates

**Usage:**
```bash
python scripts/apply_discovered_urls.py
```

## Recommended Workflow for Other States

1. Run discovery script on target state
2. Review discovery results (homepage accessible? science page accessible? match rate?)
3. If success rate > 70%:
   - Apply discovered URLs automatically
   - Re-validate with validation script
   - Commit changes
4. If success rate < 70%:
   - Manual review of discovery results
   - Research alternative matching strategies
   - Consider different discovery methods
5. Document findings using url_update_template.md
6. Move to next state

## Notes

This guide was created based on successful proof-of-concept with Oregon (OR):
- Website navigation approach validated
- Discovery process works for NGSS states
- High success rate achieved (85.7%)
- Process is repeatable for other states
- All scripts are functional and tested
