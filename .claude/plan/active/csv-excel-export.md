# Plan: Add CSV/Excel Export Functionality

**Status:** Active
**Priority:** Medium
**Estimated Time:** 1.5-2 hours
**Dependencies:** None (can run independently)

## Overview

Add export commands to the CLI that output standards data in CSV and Excel formats. This enables teachers, curriculum coordinators, and researchers to use the data in spreadsheets for comparison, filtering, and reporting.

## Problem Statement

All data is currently accessible only via CLI text output or raw JSON. Users who want to:
- Compare standards across multiple states in a spreadsheet
- Filter/sort by grade level across all jurisdictions
- Share data with colleagues who don't use CLI tools
- Import into curriculum planning tools

...must manually copy/paste or write their own JSON parser. Export functionality removes this barrier.

## Prerequisites

- [x] states.json with 51 states of data
- [x] CLI with working query commands
- [x] UV for inline script dependencies (openpyxl for Excel)

## Implementation Steps

### Step 1: Design export data schema (15 min)

**Goal:** Define what columns/fields each export format includes

**Actions:**
1. Design two export templates:

**Template A: State Overview (one row per state)**
```
state_abbr, state_name, ngss_status, num_documents, num_assessments, has_page_ranges, grades_covered, primary_doc_url
```

**Template B: Document Detail (one row per document)**
```
state_abbr, state_name, doc_title, doc_url, doc_format, grades, page_range, special_structure, page_range_status, notes
```

**Template C: Grade Coverage Matrix (states as rows, grades as columns)**
```
state_abbr, state_name, K, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12
```
Each cell = "yes"/"no" or document title

2. All templates should be useful standalone — no need to cross-reference

### Step 2: Implement CSV export (30 min)

**Goal:** Add `export` command to CLI with CSV output

**Actions:**
1. Add `export` subcommand to `state_science_standards_system.py`
2. Use stdlib `csv` module (no new dependencies)
3. Implement three export types:
   ```bash
   python state_science_standards_system.py export states --format csv > states_overview.csv
   python state_science_standards_system.py export documents --format csv > documents.csv
   python state_science_standards_system.py export coverage --format csv > coverage_matrix.csv
   ```
4. Support optional filters:
   - `--grade 5` — only include data for grade 5
   - `--state TX,CA,NY` — only include specific states
   - `--ngss-only` — only NGSS direct adoption states
5. Write to stdout by default (pipe to file), or `--output filename.csv`

**Implementation pattern:**
```python
import csv
import sys

def export_states_csv(states_data, output=sys.stdout, grade_filter=None, state_filter=None):
    writer = csv.writer(output)
    writer.writerow(['state_abbr', 'state_name', 'ngss_status', 'num_documents',
                     'num_assessments', 'has_page_ranges', 'grades_covered', 'primary_doc_url'])
    for abbr, state in sorted(states_data.items()):
        if state_filter and abbr not in state_filter:
            continue
        # ... build row
        writer.writerow(row)
```

**Test:**
```bash
python state_science_standards_system.py export states --format csv | head -5
# Should show CSV header + first 4 states

python state_science_standards_system.py export documents --format csv | wc -l
# Should be ~94 (header + 93 documents)

python state_science_standards_system.py export coverage --format csv --grade 5 | head -5
# Should show grade 5 coverage for first states
```

**Commit:** `feat(cli): add CSV export for states, documents, and coverage matrix`

### Step 3: Implement Excel export (30 min)

**Goal:** Add Excel (.xlsx) export with formatting

**Actions:**
1. Use `openpyxl` via UV inline dependency
2. Create a standalone export script (keeps main CLI dependency-free):
   ```bash
   uv run scripts/export_excel.py --output standards_export.xlsx
   ```
3. Create a multi-sheet workbook:
   - Sheet 1: "State Overview" (Template A)
   - Sheet 2: "All Documents" (Template B)
   - Sheet 3: "Grade Coverage" (Template C with conditional formatting)
4. Add formatting:
   - Header row bold + frozen
   - Auto-column widths
   - Grade coverage: green = covered, red = not covered
   - Hyperlinked URLs

**Script structure:**
```python
#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.10"
# dependencies = ["openpyxl>=3.1.0"]
# ///

import json
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils import get_column_letter

def create_export(data, output_path):
    wb = Workbook()
    # Sheet 1: State Overview
    ws1 = wb.active
    ws1.title = "State Overview"
    # ... populate

    # Sheet 2: All Documents
    ws2 = wb.create_sheet("All Documents")
    # ... populate

    # Sheet 3: Grade Coverage Matrix
    ws3 = wb.create_sheet("Grade Coverage")
    # ... populate with conditional formatting

    wb.save(output_path)
```

**Test:**
```bash
uv run scripts/export_excel.py --output test_export.xlsx
python -c "
from openpyxl import load_workbook
wb = load_workbook('test_export.xlsx')
print(f'Sheets: {wb.sheetnames}')
for name in wb.sheetnames:
    ws = wb[name]
    print(f'  {name}: {ws.max_row} rows x {ws.max_column} cols')
"
rm test_export.xlsx
```

**Commit:** `feat(export): add Excel export with multi-sheet workbook and formatting`

### Step 4: Add CLI integration for Excel (10 min)

**Goal:** Make Excel export accessible from main CLI

**Actions:**
1. Add `--format xlsx` option to the `export` command
2. When xlsx is requested, shell out to the export script (keeps main CLI dependency-free):
   ```python
   if args.format == 'xlsx':
       import subprocess
       subprocess.run(['uv', 'run', 'scripts/export_excel.py',
                       '--output', args.output or 'standards_export.xlsx'])
   ```
3. Or alternatively, detect openpyxl availability and use it directly if installed

**Test:**
```bash
python state_science_standards_system.py export states --format xlsx --output test.xlsx
ls -la test.xlsx
rm test.xlsx
```

**Commit:** `feat(cli): integrate Excel export into main CLI`

### Step 5: Test and document (15 min)

**Goal:** Verify all export paths work and add usage docs

**Actions:**
1. Run full export test suite:
   ```bash
   # CSV exports
   python state_science_standards_system.py export states --format csv > /tmp/test_states.csv
   python state_science_standards_system.py export documents --format csv > /tmp/test_docs.csv
   python state_science_standards_system.py export coverage --format csv > /tmp/test_coverage.csv

   # Filtered exports
   python state_science_standards_system.py export states --format csv --ngss-only > /tmp/test_ngss.csv
   python state_science_standards_system.py export documents --format csv --state TX,CA > /tmp/test_txca.csv

   # Excel export
   uv run scripts/export_excel.py --output /tmp/test_full.xlsx

   # Verify row counts
   wc -l /tmp/test_states.csv    # ~52 (header + 51)
   wc -l /tmp/test_docs.csv      # ~94 (header + 93)
   wc -l /tmp/test_coverage.csv  # ~52 (header + 51)
   wc -l /tmp/test_ngss.csv      # ~22 (header + 21)
   ```
2. Add export usage to CLI help text
3. Update CLAUDE.md "Core Functionality" section to mention export
4. Update features.txt: move CSV/Excel export to Done

**Commit:** `docs: add export functionality documentation`

## Success Criteria

- [ ] `export states --format csv` outputs valid CSV with all 51 states
- [ ] `export documents --format csv` outputs valid CSV with all 93 documents
- [ ] `export coverage --format csv` outputs grade coverage matrix
- [ ] Excel export creates valid .xlsx with 3 formatted sheets
- [ ] Filters work: `--grade`, `--state`, `--ngss-only`
- [ ] Main CLI remains dependency-free (CSV via stdlib, Excel via separate script)
- [ ] CLI help text updated

## Rollback Plan

- New `export` command is additive — no existing commands affected
- Excel script is standalone — can be removed independently
- No data changes — read-only feature

## Design Decisions

- **CSV via stdlib:** No new dependencies for the main CLI
- **Excel via UV script:** Keeps openpyxl isolated, consistent with project pattern
- **stdout default for CSV:** Unix-friendly, allows piping
- **Multi-sheet Excel:** More useful than separate files for end users
- **Grade coverage matrix:** The most-requested view for curriculum coordinators
