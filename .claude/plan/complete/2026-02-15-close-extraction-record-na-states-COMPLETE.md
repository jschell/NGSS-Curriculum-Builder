# Plan: Close Extraction Plan — Record N/A States in Data

**Status:** Active
**Priority:** High (unblocks migrate-to-grade-sections-format)
**Estimated Time:** 45-60 minutes
**Dependencies:** None

## Overview

16 of the 18 states without `page_range` data don't need page ranges — they have no single K-12 PDF to extract from. This plan formally records that fact in `states.json`, updates `features.txt`, and moves the `extract-remaining-23-states.md` plan to `complete/`.

## Problem Statement

The extraction plan has been open since 2026-02-05 and lists 18 states as missing page ranges. But the plan itself classifies 16 of those as intentionally N/A:

- **Type A (9 states):** NGSS direct adopters that reference `nextgenscience.org` — no state-specific K-12 PDF exists
  - CT, KS, MD, NH, NM, RI, VT, DE, FL
- **Type B (7 states):** Multi-document states — separate PDFs per grade/course, no combined document
  - GA, IN, LA, ME, MO, NC (+ FL is also CPALMS database)

Only **VA** (blocked by Akamai CDN) and **HI/MS** (data regression) are genuine gaps — handled by separate plans.

Leaving the extraction plan open creates confusion about project status and blocks the migration plan.

## Implementation Steps

### Step 1: Add `page_range_status` field to states.json (20 min)

**Goal:** Record why page_range is null for each of the 16 states

**Actions:**
1. For each document in the 16 states, add a `page_range_status` field:
   - `"not_applicable_ngss_reference"` — for Type A states (CT, KS, MD, NH, NM, RI, VT, DE)
   - `"not_applicable_multi_document"` — for Type B states (GA, IN, LA, ME, MO, NC)
   - `"not_applicable_interactive_database"` — for FL (CPALMS)
2. Update the `StandardsDocument` dataclass in `state_science_standards_system.py` to include the new field
3. Verify JSON loads without error

**States and values:**
```
CT  → not_applicable_ngss_reference
DE  → not_applicable_ngss_reference
FL  → not_applicable_interactive_database
GA  → not_applicable_multi_document
IN  → not_applicable_multi_document
KS  → not_applicable_ngss_reference
LA  → not_applicable_multi_document
MD  → not_applicable_ngss_reference
ME  → not_applicable_multi_document
MO  → not_applicable_multi_document
NC  → not_applicable_multi_document
NH  → not_applicable_ngss_reference
NM  → not_applicable_ngss_reference
RI  → not_applicable_ngss_reference
VT  → not_applicable_ngss_reference
```

**Test:**
```bash
python -c "import json; data=json.load(open('data/states.json')); print(sum(1 for s in data.values() for d in s['documents'] if d.get('page_range_status')))"
# Expected: 15+ (one per state, some states have multiple docs)

python state_science_standards_system.py state CT
# Should load without error
```

**Commit:** `feat(data): add page_range_status for 16 states with intentional null page_range`

### Step 2: Update CLI display for N/A states (10 min)

**Goal:** Show meaningful output instead of blank for states without page ranges

**Actions:**
1. In `state_science_standards_system.py`, update the document display logic
2. When `page_range` is null but `page_range_status` exists, display the status:
   - `"Pages: N/A (NGSS reference document)"` for ngss_reference
   - `"Pages: N/A (multi-document state — see individual grade PDFs)"` for multi_document
   - `"Pages: N/A (interactive database — no PDF)"` for interactive_database
3. Test with a few states

**Test:**
```bash
python state_science_standards_system.py state CT
# Should show "Pages: N/A (NGSS reference document)"

python state_science_standards_system.py state GA
# Should show "Pages: N/A (multi-document state — see individual grade PDFs)"
```

**Commit:** `feat(cli): display page_range_status for N/A states`

### Step 3: Update features.txt and close extraction plan (15 min)

**Goal:** Mark extraction work complete and move plan to complete/

**Actions:**
1. Update `features.txt`:
   - Move the extraction line item from "In Progress" to "Done"
   - Add completion note: coverage is 35/51 with page ranges + 16/51 documented N/A = 51/51 accounted for
   - Remove the cleanup line item (already complete per `complete/` dir)
   - Remove the validation suite line item (already complete per `complete/` dir)
2. Move `extract-remaining-23-states.md` to `.claude/plan/complete/` with date prefix and COMPLETE suffix
3. Update the migration plan's dependency status (mark extraction as satisfied)

**Test:**
```bash
ls .claude/plan/active/
# Should NOT contain extract-remaining-23-states.md

ls .claude/plan/complete/ | grep extract
# Should contain dated extraction plan

grep -c "In Progress" features.txt
# Should be fewer items than before
```

**Commit:** `docs(plans): close extraction plan — 51/51 states accounted for`

## Success Criteria

- [ ] 16 states have `page_range_status` field in states.json
- [ ] CLI displays meaningful N/A messages for those states
- [ ] `StandardsDocument` dataclass includes `page_range_status`
- [ ] Extraction plan moved to `complete/`
- [ ] `features.txt` updated
- [ ] Migration plan dependency marked satisfied
- [ ] All CLI test commands pass

## Rollback Plan

1. Remove `page_range_status` field from states.json (additive change, easy to revert)
2. Revert dataclass change
3. Move plan back to `active/` if needed
