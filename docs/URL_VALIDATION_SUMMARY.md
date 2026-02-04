# URL Validation Summary

**Validation Date:** 2026-02-04
**Total URLs Tested:** 80
**Validator Version:** 1.0

---

## Overall Statistics

- Working PDFs (HTTP 200): 2 (2%)
- Broken URLs (HTTP errors): 72 (90%)
- Wrong Format (HTML/Other): 6 (7%)
- Content-Verified URLs (confidence ≥ 0.8): 2 (2%)
- Content-Questionable URLs (confidence 0.5-0.8): 0 (0%)
- Wrong-Document URLs (confidence < 0.5): 0 (0%)

## HTTP Status Distribution

- Connection Errors: 38
- HTTP 200 (OK): 8
- HTTP 202 (Accepted): 3
- HTTP 403: 9
- HTTP 404: 19
- HTTP 500: 1

## Content Type Distribution

- html: 6 (7%)
- pdf: 2 (2%)
- unknown: 70 (87%)

## Confidence Score Distribution

Based on PDF content validation (grade level, state name, science keywords)

- High confidence (0.8-1.0): 2 documents
- Medium confidence (0.5-0.8): 0 documents
- Low confidence (< 0.5): 0 documents
- No content validation (non-PDF or failed): 78 documents

## States Requiring Attention

### Critical (All Documents Broken or Connection Errors)

- **Alaska (AK)** - 1/1 documents broken
- **Arkansas (AR)** - 1/1 documents broken
- **Arizona (AZ)** - 1/1 documents broken
- **California (CA)** - 7/7 documents broken
- **Colorado (CO)** - 1/1 documents broken
- **Connecticut (CT)** - 1/1 documents broken
- **District of Columbia (DC)** - 1/1 documents broken
- **Delaware (DE)** - 1/1 documents broken
- **Florida (FL)** - 1/1 documents broken
- **Georgia (GA)** - 1/1 documents broken
- **Hawaii (HI)** - 1/1 documents broken
- **Iowa (IA)** - 1/1 documents broken
- **Idaho (ID)** - 1/1 documents broken
- **Illinois (IL)** - 1/1 documents broken
- **Indiana (IN)** - 1/1 documents broken
- **Kansas (KS)** - 1/1 documents broken
- **Kentucky (KY)** - 2/2 documents broken
- **Louisiana (LA)** - 1/1 documents broken
- **Massachusetts (MA)** - 1/1 documents broken
- **Maine (ME)** - 1/1 documents broken
- **Michigan (MI)** - 1/1 documents broken
- **Minnesota (MN)** - 1/1 documents broken
- **Missouri (MO)** - 1/1 documents broken
- **Mississippi (MS)** - 1/1 documents broken
- **Montana (MT)** - 2/2 documents broken
- **North Carolina (NC)** - 1/1 documents broken
- **North Dakota (ND)** - 1/1 documents broken
- **Nebraska (NE)** - 1/1 documents broken
- **New Jersey (NJ)** - 2/2 documents broken
- **New Mexico (NM)** - 1/1 documents broken
- **Nevada (NV)** - 1/1 documents broken
- **New York (NY)** - 4/4 documents broken
- **Ohio (OH)** - 1/1 documents broken
- **Oklahoma (OK)** - 1/1 documents broken
- **Pennsylvania (PA)** - 2/2 documents broken
- **Rhode Island (RI)** - 1/1 documents broken
- **South Carolina (SC)** - 1/1 documents broken
- **South Dakota (SD)** - 1/1 documents broken
- **Tennessee (TN)** - 1/1 documents broken
- **Texas (TX)** - 9/9 documents broken
- **Utah (UT)** - 1/1 documents broken
- **Virginia (VA)** - 1/1 documents broken
- **Vermont (VT)** - 1/1 documents broken
- **Washington (WA)** - 3/3 documents broken
- **Wisconsin (WI)** - 1/1 documents broken
- **West Virginia (WV)** - 1/1 documents broken
- **Wyoming (WY)** - 1/1 documents broken

### Partial Issues (Some Documents Broken)

- **Oregon (OR)** - 6/7 documents broken

### All Verified (Working PDFs)

- **Alabama (AL)** - All 1 documents verified

## Content Validation Warnings

*No content validation warnings*

## Next Steps

1. **High Priority:** Investigate connection errors and HTTP 403 forbidden responses (likely bot detection)
2. **High Priority:** Research current state education websites for 404 errors
3. **Medium Priority:** Review HTTP 202 accepted responses (may require manual download)
4. **Low Priority:** Update URLs that redirect but work correctly

### Notes

- Many URLs failed with connection errors (38), suggesting network or server-side issues
- HTTP 403 Forbidden errors (9) likely due to bot detection on state education websites
- Only 2 of 80 URLs were successfully validated as working PDFs with content verification
- Content validation uses PDF text extraction to verify grade level, state name, and science keywords

---

*Report generated on 2026-02-04 13:50:13*