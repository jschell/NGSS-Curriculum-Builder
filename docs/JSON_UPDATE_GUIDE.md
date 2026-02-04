# JSON Update Safety Guide

## Critical Rules

1. **ALWAYS backup before editing:** `cp data/states.json data/states.json.backup`
2. **NEVER edit JSON manually:** Use scripts or careful text editor
3. **ALWAYS validate after changes:** `python -m json.tool data/states.json`
4. **ALWAYS test after updates:** `python state_science_standards_system.py list`
5. **ALWAYS commit working state:** Don't leave JSON broken

## Pre-Update Checklist

- [ ] Create backup: `cp data/states.json data/states.json.backup`
- [ ] Document planned changes in url_update_template.md
- [ ] Verify new URLs work (manual browser test)
- [ ] Read current JSON structure for state
- [ ] Plan exact changes needed

## Update Methods

### Method 1: Direct Edit (Small Changes)

**When to use:** 1-2 URLs, simple updates

**Steps:**
1. Open states.json in text editor
2. Search for state abbreviation
3. Find document by title
4. Update URL field only
5. Add/update last_verified and url_source
6. Save file
7. Validate JSON
8. Test CLI

**Example:**
```json
{
  "WA": {
    "documents": [
      {
        "title": "Washington State K-12 Science Learning Standards",
        "url": "https://NEW-WORKING-URL.pdf",  // CHANGED
        "url_source": "https://ospi.k12.wa.us/science/",  // ADDED
        "last_verified": "2026-02-04",  // ADDED
        "grade_levels": ["K", "1", ...],
        // ... all other fields unchanged
      }
    ]
  }
}
```

### Method 2: Python Script (Batch Updates)

**When to use:** 5+ URLs, systematic updates

**Script template:**
```python
#!/usr/bin/env python3
import json
from pathlib import Path

# Load data
with open('data/states.json', 'r') as f:
    states = json.load(f)

# Define updates
updates = [
    {
        'state': 'WA',
        'doc_title': 'Washington State K-12 Science Learning Standards',
        'new_url': 'https://NEW-URL.pdf',
        'url_source': 'https://ospi.k12.wa.us/science/',
    },
    # ... more updates
]

# Apply updates
for update in updates:
    state_data = states[update['state']]
    for doc in state_data['documents']:
        if doc['title'] == update['doc_title']:
            doc['url'] = update['new_url']
            doc['url_source'] = update['url_source']
            doc['last_verified'] = '2026-02-04'
            print(f"Updated: {update['state']} - {doc['title']}")

# Save
with open('data/states.json', 'w') as f:
    json.dump(states, f, indent=2)
print("Updates complete. Run validation.")
```

## Validation Commands

### JSON Syntax Check
```bash
python -m json.tool data/states.json > /dev/null && echo "JSON valid"
```

### CLI Functionality Test
```bash
# List all states
python state_science_standards_system.py list

# Test specific updated state
python state_science_standards_system.py state WA

# Test grade query
python state_science_standards_system.py search 5
```

### Data Integrity Checks
```bash
# Verify state count still 51
python -c "import json; print(len(json.load(open('data/states.json'))))"
# Expected: 51

# Verify document count unchanged (or note expected changes)
python -c "import json; data=json.load(open('data/states.json')); print(sum(len(s['documents']) for s in data.values()))"
# Expected: 80 (or document expected total)

# Verify no null URLs introduced
python -c "import json; data=json.load(open('data/states.json')); nulls = sum(1 for s in data.values() for d in s['documents'] if not d.get('url')); print(f'Documents with null URLs: {nulls}')"
# Expected: 0
```

## Rollback Procedures

### If JSON Becomes Invalid

**Error:** `json.tool` fails or CLI crashes

**Action:**
```bash
# Restore from backup
cp data/states.json.backup data/states.json

# Verify restoration worked
python -m json.tool data/states.json > /dev/null && echo "Restored"

# Re-attempt update more carefully
```

### If Git Commit Needed

**Error:** Changes committed but broken

**Action:**
```bash
# Revert last commit
git revert HEAD

# Or reset to previous commit
git reset --hard HEAD~1

# Restore states.json
git restore data/states.json
```

## Batch Update Strategy

**Recommended approach:** Update in small batches

### Batch Sizes
- **Tier 1 (Critical):** 1-2 states at a time (high complexity)
- **Tier 2 (Partial):** 3-5 states at a time
- **Tier 3 (Warnings):** 5-10 states at a time
- **Tier 4 (Working):** No updates needed

### Between Batches
1. Validate JSON
2. Test CLI
3. Commit changes
4. Update progress.txt
5. Review for issues before next batch

## Common Pitfalls

- **Don't:** Edit JSON in basic editor that can't handle large files
- **Don't:** Update 20+ URLs at once without testing
- **Don't:** Skip validation after changes
- **Don't:** Forget to update last_verified timestamp
- **Don't:** Remove fields (preserve all existing data)
- **Do:** Use VSCode, Sublime, or similar JSON-aware editor
- **Do:** Update small batches with validation between
- **Do:** Run full test suite after updates
- **Do:** Add url_source for auditability
- **Do:** Keep backups until changes fully tested
