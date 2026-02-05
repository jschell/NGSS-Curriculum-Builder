# Partial States Analysis

## States with Mixed Results

### Oregon (OR) - NGSS Direct Adoption
- **Working:** 1 (Grade 3)
- **Broken:** 6 (K, 1, 2, 4, 5, K-12)
- **Working Ratio:** 14%
- **URL Pattern:** Grade-specific: `.../Grade%20[N]%20Science%20Standards%20with%20Guidance.pdf`
- **Pattern Confidence:** High (consistent structure)
- **Priority:** 1 (NGSS + clear pattern + working example)

## Analysis Notes

### States Without Partial Failures
- All other 50 states either have:
  - 0 working URLs (100% failure)
  - 100% working URLs (no issues needed)
  - No URLs tested (connection errors only)

### Why Oregon is Ideal for Proof-of-Concept

1. **NGSS Direct Adoption:** Likely has consistent URL structure
2. **Clear Working Example:** Grade 3 URL works with 90% confidence
3. **Grade-Specific Documents:** Each grade has separate PDF, predictable naming
4. **URL Pattern Visible:** Grade number is clearly in URL path
5. **Multiple Document Types:** K-12 + grade-specific documents to test matching

### Discovery Strategy for Oregon

**Current Working URL (Seed):**
```
https://www.oregon.gov/ode/educator-resources/standards/science/Documents/Grade%203%20Science%20Standards%20with%20Guidance.pdf
```

**Target Documents (Broken):**
1. K-12 Oregon Science Standards with Guidance
2. Grade K Standards with Guidance
3. Grade 1 Standards with Guidance
4. Grade 2 Standards with Guidance
5. Grade 4 Standards with Guidance
6. Grade 5 Standards with Guidance

**Expected Discovery Approach:**
- Navigate to ODE website
- Find science standards page
- Discover all PDF links
- Match to expected document titles
- Test each discovered URL

## Total Scope

- **States:** 1 (Oregon only)
- **Documents:** 7 total (1 working, 6 broken)
- **Estimated Time:** 1-2 hours for Oregon proof-of-concept
- **Expected Success Rate:** 50-70% (based on clear URL pattern)

## Research Order

1. Oregon (OR) - NGSS direct adoption, 1 working example, clear grade pattern

## Notes for Other States

**Why Other States Not Included:**
- 47 states have 100% failure (Tier 1 critical) - need manual research
- 3 states have 100% working (no fixes needed)
- Only Oregon has partial failures suitable for automated discovery

**For Future Implementation:**
- Apply same discovery process to other partial states if found
- States with 100% failure require different approach (manual research)
