# Quick Start Guide

## Installation

### 1. Install UV (Modern Python Package Manager)

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 2. Verify Installation

```bash
uv --version
```

That's it! Dependencies are managed via UV inline dependencies.

## Basic Usage

### Query State Standards

**List all states:**
```bash
python state_science_standards_system.py list
```

**Search for grade 3 standards:**
```bash
python state_science_standards_system.py search 3
```

**View Washington's standards:**
```bash
python state_science_standards_system.py state WA
```

**View Washington's Grade 3 standards:**
```bash
python state_science_standards_system.py state WA 3
```

### View Grade-Specific Sections

**Show all sections for Washington:**
```bash
python state_science_standards_system.py sections WA
```

**Show Grade 3 sections for Washington:**
```bash
python state_science_standards_system.py sections WA 3
```

Expected output:
```
Washington (WA) - GRADE-SPECIFIC SECTIONS

Grade 3 sections:

Document: Washington State K-12 Science Learning Standards
  URL: https://ospi.k12.wa.us/sites/default/files/...
  Pages: 22-28
  Confidence: High

Document: WSSLS DCI Arrangement
  URL: https://ospi.k12.wa.us/sites/default/files/...
  Pages: 18-24, 52-56, 89-93
  Confidence: Medium
  [!] Needs manual review
```

## Auto-Generate Section Mappings

### Parse Specific States

```bash
uv run parse_standards.py parse --states WA,OR,CA
```

This will:
1. Fetch documents from URLs
2. Parse PDFs to detect grade sections
3. Generate `patches/grade_sections.json` with mappings
4. Create `reports/grade_sections_analysis.md` with human-readable report

### Parse All States

```bash
uv run parse_standards.py parse --all
```

**Note:** This may take several minutes as it downloads and parses ~80 documents.

### Generate Report from Existing Patch

```bash
uv run parse_standards.py report patches/grade_sections.json
```

## Common Workflows

### Workflow 1: Research a State

```bash
# Generate research queries
python state_science_standards_system.py queries WA

# Check K-12 coverage
python state_science_standards_system.py range WA

# Parse documents to find grade sections
uv run parse_standards.py parse --states WA

# View generated report
cat reports/grade_sections_analysis.md
```

### Workflow 2: Compare Grades Across States

```bash
# Compare Grade 5 standards
python state_science_standards_system.py compare 5

# Show specific sections for Grade 5 in California
python state_science_standards_system.py sections CA 5
```

### Workflow 3: Document Standards

```bash
# Get all documents for a grade in a state
python state_science_standards_system.py state TX 5

# See which states have Grade 3
python state_science_standards_system.py search 3
```

## Understanding Output

### Confidence Levels

- **High**: Clear grade heading, sequential organization
- **Medium**: Topic-based organization, multiple sections
- **Low**: Ambiguous patterns, small ranges (<2 pages)

### Manual Review Flag

Documents with `[!]` need manual verification:
- Ambiguous grade headings
- Overlapping page ranges
- Unusual document organization

### Page Numbers

- Page ranges are 1-indexed (e.g., "22-28" means pages 22 through 28)
- Internally 0-indexed for Python list operations

## Troubleshooting

### Parser Returns HTTP 404/403 Errors

**Issue:** Many state department URLs return errors
**Solution:**
1. Manually visit the URL in a browser
2. Update URL in `data/states.json` if broken
3. Re-run parser with corrected URLs

### No Grade Sections Detected

**Issue:** Parser can't find grade headings
**Solutions:**
1. Document may use non-standard headings
2. Check if PDF is OCR'd (images of text)
3. Manually verify PDF structure

### PDF Parsing Fails

**Issue:** "No /Root object! Is this really a PDF?"
**Cause:** Downloaded HTML instead of PDF
**Solution:** Verify URL points to actual PDF file

## Next Steps

1. Explore state standards for your grade level
2. Use `sections` command to find specific pages
3. Parse documents to build comprehensive section mappings
4. Apply patches to update `data/states.json`
5. Share insights with curriculum development team

## Additional Resources

- **README.md** - Complete feature documentation
- **GRADE_FILTERING_EXPLAINED.md** - Technical filtering details
- **PHASE_3_TESTING_REPORT.md** - Testing and validation results
- **Plan** - `.claude/plan/active/` directory contains implementation roadmap

## Support

For issues or questions:
1. Check documentation files
2. Review generated reports in `reports/`
3. Verify URL validity for documents
4. Examine patch files in `patches/`
