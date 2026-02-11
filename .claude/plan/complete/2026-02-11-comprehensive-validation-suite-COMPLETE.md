# Plan: Create Comprehensive Validation Suite

**Status:** COMPLETE
**Priority:** High
**Estimated Time:** 2-3 hours
**Completed:** 2026-02-11
**Dependencies:** None (supports all other plans)

## Overview

Create a comprehensive validation suite that checks data integrity, page range quality, URL accessibility, and overall system health. This provides automated quality assurance for current data and future updates.

## Problem Statement

Current validation is minimal:
- `validate_urls.py` only checks URL accessibility
- No automated page range quality checks
- No grade coverage validation
- No detection of data inconsistencies
- Manual review required for quality issues

Need comprehensive, automated validation across all data dimensions.

## Prerequisites

- [x] states.json exists with current data
- [x] Python 3.10+ environment
- [x] UV for dependency management
- [ ] Validation suite implemented

## Implementation Steps

### Step 1: Create Validation Framework (45 min)

**Goal:** Reusable validation infrastructure

**Actions:**
1. Create `scripts/validation/validation_framework.py`
2. Implement base validator class:
   ```python
   class Validator:
       def validate(self, data):
           """Run validation and return issues list."""
           pass

       def report(self, issues):
           """Generate human-readable report."""
           pass
   ```
3. Implement validation runner:
   - Runs all validators
   - Collects issues
   - Generates comprehensive report
   - Supports selective validation (by state, by type)
4. Add severity levels: ERROR, WARNING, INFO

**Test:**
```python
from validation_framework import ValidationRunner
runner = ValidationRunner()
runner.add_validator(URLValidator())
issues = runner.run(states_data)
```

**Commit:** `feat(validation): create validation framework`

### Step 2: URL Validation Enhancements (30 min)

**Goal:** Improve existing URL validation

**Actions:**
1. Refactor existing `validate_urls.py` to use new framework
2. Add validations:
   - Check for HTTP vs HTTPS consistency
   - Detect redirect chains
   - Validate SSL certificates
   - Check for common typos (e.g., "htpp://")
   - Flag URLs to deprecated domains
3. Add caching to avoid repeated requests
4. Implement parallel checking for speed

**Test:**
```bash
cd scripts/validation
uv run validate_urls.py --verbose
# Should complete in <2 minutes for all 80+ URLs
```

**Commit:** `feat(validation): enhance URL validation with comprehensive checks`

### Step 3: Page Range Quality Validation (60 min)

**Goal:** Automated detection of page range issues

**Actions:**
1. Create `PageRangeValidator` class
2. Implement checks:

   **Completeness checks:**
   - Detect incomplete K-12 coverage
   - Flag missing grade 8 (common issue)
   - Identify gaps in grade sequence
   - Check K-5 vs K-8 vs K-12 coverage patterns

   **Quality checks:**
   - Detect overlapping page ranges
   - Flag unreasonably long range strings (parser artifacts)
   - Check for negative or zero-length ranges
   - Validate page numbers are sequential within grades

   **Format checks:**
   - Parse all page_range strings successfully
   - Validate format consistency (e.g., "4-7" vs "4 - 7")
   - Check for invalid characters
   - Ensure ranges are well-formed

3. Generate detailed issue reports with fix suggestions
4. Add auto-fix capability for simple issues

**Example issues detected:**
```
ERROR: WA - Missing grades 6-8 in complete_k12 document
WARNING: AK - Only grades K, 5 extracted (incomplete)
WARNING: NV - Overlapping ranges: grade 5 (11-12) overlaps with grade 6 (11-13)
INFO: MT - Only Kindergarten extracted (likely incomplete)
```

**Test:**
```bash
cd scripts/validation
uv run validate_page_ranges.py --state WA
uv run validate_page_ranges.py --all
uv run validate_page_ranges.py --auto-fix --dry-run
```

**Commit:** `feat(validation): add comprehensive page range quality checks`

### Step 4: Data Integrity Validation (45 min)

**Goal:** Check overall data structure and consistency

**Actions:**
1. Create `DataIntegrityValidator` class
2. Implement checks:

   **Structure validation:**
   - All required fields present
   - Field types match schema
   - No null/undefined values where required
   - Array fields contain expected items

   **Consistency validation:**
   - grade_levels matches page_range keys
   - document_type aligns with grade structure
   - NGSS status is valid value
   - Adoption dates are realistic (not in future)

   **Cross-reference validation:**
   - State abbreviations are standard
   - URLs match expected domain patterns
   - Document count matches expected range (1-3 per state typically)

   **Statistical validation:**
   - Flag outliers (e.g., state with 10 documents)
   - Check for duplicate URLs across states
   - Validate reasonable page counts per grade

3. Generate summary statistics report

**Test:**
```bash
cd scripts/validation
uv run validate_data_integrity.py
# Should report 51 states, 80 documents, expected patterns
```

**Commit:** `feat(validation): add data integrity and consistency checks`

### Step 5: Special Structure Validation (30 min)

**Goal:** Validate states with non-standard organization

**Actions:**
1. Create `SpecialStructureValidator` class
2. Implement checks for special structures:
   - grade_specific_documents (like ME, TX)
   - level_specific_documents (elementary, middle, high)
   - subject_based_organization (like WY 6-8, 9-12)
3. Validate special_structure field matches actual document structure
4. Ensure notes field explains organization
5. Flag states that might have special structure but aren't marked

**Example checks:**
```
INFO: ME - Confirmed grade_specific_documents (separate PDFs per grade)
WARNING: TX - Marked as level_specific but only K extracted
ERROR: WY - Has subject-based 6-8 but special_structure not set
```

**Test:**
```bash
cd scripts/validation
uv run validate_special_structures.py
```

**Commit:** `feat(validation): add special structure validation`

### Step 6: Create Master Validation Script (30 min)

**Goal:** Single command to run all validations

**Actions:**
1. Create `scripts/validation/validate_all.py`
2. Runs all validators in sequence:
   - URL validation
   - Page range quality
   - Data integrity
   - Special structures
3. Generate comprehensive HTML report
4. Add CLI options:
   - `--quick`: Fast checks only
   - `--state <CODE>`: Validate single state
   - `--severity <LEVEL>`: Filter by severity
   - `--fix`: Auto-fix simple issues
   - `--report <FILE>`: Save report to file

**Output format:**
```
================================================================================
NGSS Curriculum Builder - Validation Report
Generated: 2026-02-06 14:30:00
================================================================================

SUMMARY
------------------------------------------------------------------------
Total States: 51
Total Documents: 80
Total Issues: 23 (5 errors, 12 warnings, 6 info)

ERRORS (5)
------------------------------------------------------------------------
[E001] WA - Missing grades 6-8 in complete_k12 document
[E002] MI - Missing grade 8 in complete_k12 document
...

WARNINGS (12)
------------------------------------------------------------------------
[W001] AK - Incomplete grade coverage (only K, 5)
[W002] AL - Incomplete grade coverage (missing 9-12)
...

INFO (6)
------------------------------------------------------------------------
[I001] ME - Special structure: grade_specific_documents
[I002] WY - Subject-based organization for grades 6-8, 9-12
...

STATISTICS
------------------------------------------------------------------------
States with complete K-12: 28 (54.9%)
States with page ranges: 28 (54.9%)
States with special structures: 7 (13.7%)
Average documents per state: 1.57

URL HEALTH
------------------------------------------------------------------------
Accessible URLs: 76 (95%)
404 Errors: 2 (CA, HI)
403 Forbidden: 2 (WA, AZ)
```

**Test:**
```bash
cd scripts/validation
uv run validate_all.py
uv run validate_all.py --quick
uv run validate_all.py --state WA
uv run validate_all.py --report validation_report.html
```

**Commit:** `feat(validation): create master validation script with HTML reports`

### Step 7: Integration & Documentation (20 min)

**Goal:** Make validation part of standard workflow

**Actions:**
1. Add validation to README.md usage section
2. Create `scripts/validation/README.md` with:
   - Overview of each validator
   - Common issues and fixes
   - How to interpret reports
3. Add validation to git pre-commit hook (optional)
4. Update features.txt with completion
5. Add example reports to docs/

**Pre-commit hook example:**
```bash
#!/bin/bash
# Run quick validation before allowing commit to states.json
if git diff --cached --name-only | grep -q "data/states.json"; then
    cd scripts/validation
    uv run validate_all.py --quick --severity ERROR
    if [ $? -ne 0 ]; then
        echo "Validation failed! Fix errors before committing."
        exit 1
    fi
fi
```

**Commit:** `docs(validation): add comprehensive validation documentation`

## Success Criteria

- [ ] All validators implemented and tested
- [ ] Master validation script runs successfully
- [ ] HTML report generation working
- [ ] Detects all known issues in current data
- [ ] Documentation complete
- [ ] Validation takes <3 minutes for full suite
- [ ] Auto-fix capability for simple issues

## Validation Coverage

**URL Validation:**
- Accessibility checks
- SSL validation
- Redirect detection
- Domain consistency

**Page Range Validation:**
- Completeness (K-12 coverage)
- Quality (no overlaps, artifacts)
- Format consistency
- Sequential ordering

**Data Integrity:**
- Schema compliance
- Field consistency
- Cross-reference checks
- Statistical outliers

**Special Structures:**
- Proper marking
- Documentation completeness
- Structure validation

## Notes

- Validation should be fast (<3 min for full suite)
- Reports should be actionable (suggest fixes)
- Auto-fix only for unambiguous issues
- Severity levels help prioritize fixes
- HTML reports make sharing results easy

## Related Work

- Existing: validate_urls.py (basic URL checking)
- New: Comprehensive multi-validator framework
- Supports: All data quality improvement plans
- Enables: Continuous data quality monitoring

## Future Enhancements

- CI/CD integration (run on every PR)
- Automated issue tracking
- Trend analysis (quality over time)
- Performance benchmarks
- Regression detection
