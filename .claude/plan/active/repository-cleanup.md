# Plan: Repository Cleanup and Documentation Consolidation

**Status:** Ready for Review
**Created:** 2026-02-06
**Priority:** High (prepare for next phase)
**Estimated Duration:** 1-2 hours

---

## Context

After completing the manual page range extraction project (18 states, 119 grade ranges), the repository contains numerous temporary files, one-off scripts, log files, and downloaded PDFs that were used during development but are no longer needed for production use.

**Current State:**
- 41 temporary files in root (*.py scripts, *.log files, *.pdf downloads)
- 6 patch files in patches/ directory
- Completed plan in .claude/plan/complete/
- Multiple parsing scripts with overlapping functionality

**Goal:** Clean and organize the repository to be presentable, maintainable, and ready for the next development phase while preserving:
- Lessons learned from parsing approaches
- Reusable parsing scripts and methods
- Documentation of MCP tool usage patterns

---

## Objectives

1. **Remove temporary files** - Clean up one-off scripts, logs, and downloaded PDFs
2. **Consolidate parsing scripts** - Keep only reusable, documented scripts
3. **Document lessons learned** - Capture parsing patterns and MCP tool techniques
4. **Organize artifacts** - Move completed work to appropriate directories
5. **Update documentation** - Ensure README and docs reflect current state

---

## Prerequisites

- [x] Manual page range extraction complete (18/18 states)
- [x] All work committed to git (current branch: interesting-rubin)
- [x] states.json contains all extracted page ranges
- [ ] Review which scripts are reusable vs one-off
- [ ] Identify lessons learned to document

---

## Implementation Steps

### Step 1: Audit and Categorize Files

**Action:** Identify which files to keep, archive, or delete

**Categories:**
1. **Keep (Production):**
   - state_science_standards_system.py (main CLI)
   - parse_standards.py (core parser)
   - apply_page_ranges.py (apply patches to states.json)
   - validate_urls.py (URL validation)
   - data/states.json (primary data)
   - README files and documentation

2. **Archive (Reference):**
   - Completed plans from .claude/plan/complete/
   - Final patch files that were successfully applied
   - Research scripts that document methodology

3. **Delete (Temporary):**
   - One-off parsing scripts (parse_sc_manual.py, parse_tn_az.py, etc.)
   - Log files (*.log)
   - Downloaded PDFs (*.pdf - can be re-downloaded if needed)
   - Intermediate patch files
   - Test/debugging scripts

**Test:**
```bash
# Verify files to delete don't break core functionality
python state_science_standards_system.py list
uv run parse_standards.py --help
```

**Success Criteria:**
- Clear categorization of all 41+ temporary files
- List of files to keep/archive/delete documented

---

### Step 2: Document Lessons Learned

**Action:** Create docs/LESSONS_LEARNED.md capturing parsing patterns

**Content to Include:**
1. **Parsing Approaches:**
   - Remote parsing (61% success rate)
   - MCP browser tools (access PDFs blocked by 403/Cloudflare)
   - Manual browser download (bypass bot protection)
   - TOC extraction (handle non-standard structures)

2. **Grade Pattern Recognition:**
   - Full grade names ("Kindergarten", "First Grade")
   - Abbreviated patterns ("Grade K", "GRADE 1")
   - Subject-based organization (Wyoming MS/HS by domain)

3. **MCP Tool Patterns:**
   - brave_web_search: Find alternative URLs
   - browser_navigate + browser_snapshot: Access blocked PDFs
   - browser_run_code: CDP printToPDF (limitations noted)
   - Manual download workflow when automation fails

4. **Common Issues & Solutions:**
   - Overlapping high school ranges (TOC mentions vs actual content)
   - Missing grade 8 in automated extractions
   - State-specific structures (grade-specific PDFs, subject domains)

**Files to Create:**
- docs/LESSONS_LEARNED.md
- docs/PARSING_PATTERNS.md (optional if detailed)

**Success Criteria:**
- Future developers can understand parsing approaches
- MCP tool usage patterns documented
- Common pitfalls and solutions captured

---

### Step 3: Consolidate Parsing Scripts

**Action:** Create scripts/ directory and organize reusable tools

**Structure:**
```
scripts/
├── parsing/
│   └── parse_standards.py (moved from root)
├── validation/
│   ├── validate_urls.py (moved from root)
│   └── apply_page_ranges.py (moved from root)
├── research/
│   ├── batch3_research.py (example research script)
│   └── research_state_urls_browser.py (MCP browser example)
└── README.md (explains each script category)
```

**Actions:**
- Move core scripts to scripts/ subdirectories
- Update import paths if needed
- Create scripts/README.md documenting each script's purpose
- Delete one-off parsing scripts

**Test:**
```bash
# Verify moved scripts still work
python scripts/parsing/parse_standards.py --help
python scripts/validation/validate_urls.py
```

**Success Criteria:**
- Core scripts organized in scripts/ directory
- One-off scripts removed
- scripts/README.md documents each tool

---

### Step 4: Clean Temporary Files

**Action:** Remove logs, PDFs, and intermediate files

**Files to Delete:**
- *.log files (parse_*.log, apply_*.log, extraction.log)
- *.pdf files (sc_2021_standards.pdf, az_standards.pdf, tn_standards.pdf, wa_standards.pdf, wy_standards_2021.pdf)
- One-off parsing scripts:
  - parse_sc_manual.py
  - parse_tn_az.py
  - parse_wy_from_toc.py
  - parse_final_states.py
  - parse_wy_wa.py
  - check_wy_toc.py
  - inspect_wy.py
  - analyze_pdf_samples.py
  - parse_by_page_range.py
- Intermediate patch files (keep only final applied patches for reference)

**Files to Keep in Root:**
- state_science_standards_system.py (main CLI - stays in root)
- features.txt
- progress.txt
- data/states.json

**Archive to docs/archive/ (optional):**
- Final successful patch files (patches/tn_az_grades.json, etc.)
- Completed plan (manual-page-range-extraction.md - already in .claude/plan/complete/)

**Commands:**
```bash
# Remove log files
rm *.log

# Remove PDFs
rm *.pdf

# Remove one-off scripts (list to be confirmed)
rm parse_sc_manual.py parse_tn_az.py parse_wy_from_toc.py # ... etc
```

**Success Criteria:**
- Root directory contains only essential files
- All temporary files removed
- Core functionality still works

---

### Step 5: Update Documentation

**Action:** Update README.md and create/update relevant docs

**README.md Updates:**
1. Add "Recent Accomplishments" section:
   - 30/51 states (59%) now have page range data
   - 119 grade ranges extracted across 18 states
   - Automated + manual parsing approaches documented

2. Update "Project Status" section:
   - Current coverage statistics
   - Link to LESSONS_LEARNED.md

3. Add "Scripts" section:
   - Brief description of scripts/ directory
   - Link to scripts/README.md

**New Documentation:**
- docs/LESSONS_LEARNED.md (from Step 2)
- scripts/README.md (from Step 3)
- docs/PARSING_GUIDE.md (optional - detailed parsing instructions)

**Update Existing Docs:**
- Update any outdated information in existing docs/
- Ensure CLAUDE.md reflects current state

**Success Criteria:**
- README.md is current and accurate
- New documentation captures project knowledge
- Links between documents work correctly

---

### Step 6: Final Verification

**Action:** Test all core functionality after cleanup

**Tests:**
```bash
# CLI tests
python state_science_standards_system.py list
python state_science_standards_system.py state WY
python state_science_standards_system.py search 5

# Parser tests
cd scripts/parsing
uv run parse_standards.py --help

# Validation tests
cd scripts/validation
uv run validate_urls.py

# Data integrity
python -c "import json; data=json.load(open('data/states.json')); print(f'States: {len(data)}, Page ranges: {sum(1 for s in data.values() for d in s[\"documents\"] if d.get(\"page_range\"))}')"
```

**Git Status:**
```bash
git status  # Should show deleted files, moved files, new docs
git diff data/states.json  # Should show no changes (data preserved)
```

**Success Criteria:**
- All CLI commands work
- Core scripts functional in new locations
- data/states.json unchanged
- Git shows clean organization

---

## Rollback Plan

If cleanup causes issues:

1. **Git Reset:** `git reset --hard HEAD` (if not committed)
2. **Restore from Commit:** Repository state before cleanup is committed
3. **Selective Restore:** `git checkout HEAD -- <file>` for individual files

**Prevention:**
- Test each step before proceeding to next
- Commit after each major step
- Keep one commit for "delete temporary files" (easy to revert)

---

## Success Metrics

- ✅ Root directory contains <15 files (currently 41+ temp files)
- ✅ All temporary files removed or organized
- ✅ Lessons learned documented in docs/LESSONS_LEARNED.md
- ✅ Core scripts organized in scripts/ directory
- ✅ README.md updated with current status
- ✅ All CLI tests pass
- ✅ data/states.json unchanged
- ✅ Repository ready for next development phase

---

## Files to Create/Modify

**New Files:**
- docs/LESSONS_LEARNED.md
- scripts/README.md
- scripts/parsing/parse_standards.py (moved)
- scripts/validation/validate_urls.py (moved)
- scripts/validation/apply_page_ranges.py (moved)
- scripts/research/batch3_research.py (moved, example)

**Modified Files:**
- README.md (updated status, new sections)
- .claude/CLAUDE.md (updated if needed)

**Deleted Files:**
- ~30-35 temporary *.py, *.log, *.pdf files
- Intermediate patch files

---

## Notes

- **Keep progress.txt:** Historical record of session work
- **Keep features.txt:** Feature backlog still relevant
- **Archive patches:** Move applied patches to docs/archive/patches/ for reference
- **Git history:** Full history preserved even after file deletion
- **MCP patterns:** Document browser tool limitations (printToPDF only captures visible page)

---

## Next Steps After Completion

1. Review repository structure
2. Verify all documentation is current
3. Consider creating a "Getting Started" guide
4. Plan next feature from features.txt
5. Merge branch to main if ready
