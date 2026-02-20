# Plan: Data Quality Fixes — TX K-8, needs_review Items, Stale Docs

**Created:** 2026-02-19
**Status:** Active
**Estimated Time:** 30-40 min
**Branch:** `claude/data-quality-fixes`

---

## Context

All 101 documents now have `page_range_status` (0 pending). However a data quality
audit identified three categories of fixable issues in the current `main` branch:

1. **TX K-8 parser artifacts** — 9 documents (indices 0-8) have fragmented multi-range
   grade_sections from an old toc_extraction run. Each TX K-8 doc is a single-grade PDF;
   the entire PDF = that grade. Correct approach: whole-doc range `[[1, N]]`, confidence
   high — same pattern used successfully for CA grades 2-5 this session.

2. **`needs_review` grade_sections** — 3 entries flagged in data:
   - NJ K-5 doc, grade 5: `[[82, 82]]` (1-page, medium confidence)
   - WV doc, grade 1: `[[12, 12]]` (1-page, medium confidence)
   - WV doc, grade 4: `[[18, 18]]` (1-page, medium confidence)
   Each needs to be verified against the actual PDF and corrected.

3. **Stale CLAUDE.md** — Several line references are outdated (assessment count 67→70,
   some sections still say 80 documents or reflect pre-session state).

4. **Stale IMPLEMENTATION_ROADMAP.md** — This file in `.claude/plan/` describes Plans
   1-4 from 2026-02-06 as "Ready for Execution" but all 4 are long since complete. It
   references `active/` plan files that no longer exist. Should be archived.

---

## Step 1: Fix TX K-8 grade_sections (parser artifacts)

**Problem:** TX[0]–TX[8] are individual single-grade PDFs from tea.texas.gov. The
grade_sections were extracted by an automated TOC parser which picked up fragmented
page numbers from a combined reference document. Each PDF is a standalone grade doc;
the correct grade_sections is simply `[[1, page_count]]` for the grade that doc covers.

**TX K-8 documents (confirmed accessible with browser User-Agent):**
| Index | Grade | URL |
|-------|-------|-----|
| 0 | K | https://ritter.tea.state.tx.us/rules/tac/chapter112/ch112a.pdf |
| 1 | 1 | (similar pattern) |
| 2 | 2 | |
| 3 | 3 | |
| 4 | 4 | |
| 5 | 5 | |
| 6 | 6 | (ch112b.pdf) |
| 7 | 7 | |
| 8 | 8 | |

**Approach:**
1. Load states.json, get URLs for TX[0]-TX[8]
2. Download each PDF with browser User-Agent
3. Count pages with pypdf
4. Replace grade_sections with `{grade_key: {"page_ranges": [[1, N]], "section_ids": [],
   "confidence": "high", "notes": "Single-grade document — entire PDF covers Grade X TEKS",
   "needs_review": false}}`
5. Update page_range to `{grade_key: "1-N"}`

**Commit:** `fix(data): correct TX K-8 grade_sections — replace parser artifacts with full-doc ranges`

---

## Step 2: Fix needs_review items (NJ grade 5, WV grades 1 and 4)

**Problem:** Three grade_sections have `needs_review: true` and suspicious single-page
ranges, indicating the automated extractor only found an index/TOC entry, not the actual
grade content.

**NJ K-5 doc — grade 5:**
- Current: `[[82, 82]]`, medium, needs_review
- The NJ K-5 PDF is 82 pages total. Grade 5 at page 82 alone is suspicious (likely
  just a final page or index entry).
- Fix: Download PDF, find where Grade 5 content actually starts/ends via TOC or headers.

**WV doc — grades 1 and 4:**
- WV[0] is a 56-page image-based PDF. Grade 1 = `[[12, 12]]` (1 page) and grade 4 =
  `[[18, 18]]` (1 page). Given the surrounding grades (K=10-11, 2=13-14, 3=15-17,
  5=19-20), single pages for grades 1 and 4 are plausible if those grades have thin
  content — but need to verify via screenshot/visual.

**Approach:**
1. Download NJ K-5 PDF, scan pages around 82 for grade 5 content; find actual start
2. Download WV PDF (image-based), screenshot pages 10-25 to visually confirm grade
   boundary pages; correct ranges if needed
3. Set confidence to "high" once verified; set needs_review: false

**Commit:** `fix(data): resolve needs_review grade_sections — NJ grade 5, WV grades 1 and 4`

---

## Step 3: Update CLAUDE.md

**Stale references to fix:**
- Assessment count: 67 → 70 (in "Core Functionality" section)
- Known Issues section: remove "Texas missing high school grades (9-12)" (fixed 2026-02-15)
- Known Issues section: remove "Page ranges: Not populated" (wrong — 71 docs are complete)
- Data Counts quick reference: update Documents (80→101), Assessments (67→70)
- Project status (Current State): update to reflect 0 pending, all docs resolved

**Commit:** `docs(claude): update CLAUDE.md — correct doc/assessment counts, remove stale issues`

---

## Step 4: Archive IMPLEMENTATION_ROADMAP.md

Move `.claude/plan/IMPLEMENTATION_ROADMAP.md` to `.claude/plan/complete/` and rename
to `2026-02-06-implementation-roadmap-COMPLETE.md`. Add a header note that all 4 plans
described are complete as of 2026-02-19.

**Commit:** `docs: archive stale IMPLEMENTATION_ROADMAP.md — all plans complete`

---

## Verification

```bash
# Zero needs_review remaining
python -c "
import json, sys; sys.stdout.reconfigure(encoding='utf-8')
d = json.load(open('data/states.json', encoding='utf-8'))
nr = [(s, doc['title'], k) for s, v in d.items() for doc in v['documents']
      for k, gs in doc.get('grade_sections',{}).items() if gs.get('needs_review')]
print(f'needs_review: {len(nr)}')  # Expected: 0
for x in nr: print(' ', x)
"

# TX K-8 all high confidence
python -c "
import json, sys; sys.stdout.reconfigure(encoding='utf-8')
d = json.load(open('data/states.json', encoding='utf-8'))
for i, doc in enumerate(d['TX']['documents'][:9]):
    for k, gs in doc.get('grade_sections',{}).items():
        print(f'TX[{i}] {k}: conf={gs[\"confidence\"]} ranges={gs[\"page_ranges\"]}')
"

# CLI still works
python state_science_standards_system.py state TX K
python state_science_standards_system.py state NJ 5
python state_science_standards_system.py state WV 4

# JSON valid
python -c "import json; d=json.load(open('data/states.json',encoding='utf-8')); print(f'OK: {sum(len(v[chr(100)+chr(111)+chr(99)+chr(117)+chr(109)+chr(101)+chr(110)+chr(116)+chr(115)]) for v in d.values())} docs')"
```

---

## Files Modified

| File | Change |
|------|--------|
| `data/states.json` | TX[0-8] grade_sections; NJ[0] grade 5; WV[0] grades 1, 4 |
| `.claude/CLAUDE.md` | Doc/assessment counts, remove stale known issues |
| `.claude/plan/IMPLEMENTATION_ROADMAP.md` | Move to complete/ |

---

## Success Criteria

- `needs_review` count: 0 (down from 3)
- TX K-8 grade_sections: all high confidence, single contiguous range per grade
- CLAUDE.md: accurate doc count (101), assessment count (70), no stale known issues
- CLI: all test commands pass without errors
- JSON: valid and loads cleanly
