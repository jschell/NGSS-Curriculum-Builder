# Grade Filtering Mechanism - Complete Explanation

## Overview

The Python script extracts documents for specific grades using a simple but powerful **membership test** against the `grade_levels` array in each document.

---

## Data Structure in JSON

```json
{
  "WA": {
    "state_name": "Washington",
    "documents": [
      {
        "title": "Washington State K-12 Science Learning Standards",
        "url": "https://ospi.k12.wa.us/sites/default/files/2024-08/...",
        "grade_levels": ["K", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12"],
        "document_type": "complete_k12",
        "format": "PDF"
      }
    ]
  },
  "TX": {
    "state_name": "Texas",
    "documents": [
      {
        "title": "Grade 5 Science TEKS",
        "url": "https://tea.texas.gov/sites/default/files/Grade_5_Science_TEKS.pdf",
        "grade_levels": ["5"],
        "document_type": "grade_specific",
        "format": "PDF"
      }
    ]
  },
  "NY": {
    "state_name": "New York",
    "documents": [
      {
        "title": "Grades 3-5 Science Learning Standards",
        "url": "https://www.nysed.gov/sites/default/files/programs/3-5-science...",
        "grade_levels": ["3", "4", "5"],
        "document_type": "grade_band",
        "format": "PDF"
      }
    ]
  }
}
```

**Key Point:** `grade_levels` is **always** an array of individual grade strings, never ranges like `"K-12"`.

---

## Filtering Algorithm (3 Steps)

### Step 1: Normalize User Input

```python
def normalize_grade(grade: str) -> str:
    """Convert user input to standard format"""
    grade = grade.strip().upper()

    # "kindergarten" → "K"
    if grade in ["KINDERGARTEN", "KINDER", "KG"]:
        return "K"

    # "grade 3" → "3"
    if grade.startswith("GRADE "):
        grade = grade[6:]

    return grade

# Examples:
# "kindergarten" → "K"
# "grade 5" → "5"
# "3" → "3"
```

### Step 2: Expand Grade Ranges (If Needed)

```python
def expand_grade_range(grade_spec: str) -> List[str]:
    """Expand range notation to individual grades"""

    # No range? Return as-is
    if "-" not in grade_spec:
        return [grade_spec]

    # Split range: "K-5" → start="K", end="5"
    start, end = grade_spec.split("-")

    # Special handling for Kindergarten
    if start == "K":
        grades = ["K"]
        start_num = 1
    else:
        grades = []
        start_num = int(start)

    end_num = int(end)

    # Generate range
    for i in range(start_num, end_num + 1):
        grades.append(str(i))

    return grades

# Examples:
# "K" → ["K"]
# "5" → ["5"]
# "K-5" → ["K", "1", "2", "3", "4", "5"]
# "6-8" → ["6", "7", "8"]
# "9-12" → ["9", "10", "11", "12"]
```

**Note:** In the current dataset, ALL documents already use individual grades, so this function returns input unchanged. However, it's implemented to support range notation if states start using it in the future.

### Step 3: Filter Documents

```python
def get_documents_for_grade(state: StateStandards, grade: str) -> List[StandardsDocument]:
    """Find all documents covering a specific grade"""
    matching_docs = []

    for doc in state.documents:
        # Expand any ranges in the document's grade_levels
        all_doc_grades = get_all_grades_from_list(doc.grade_levels)

        # Simple membership test
        if grade in all_doc_grades:
            matching_docs.append(doc)

    return matching_docs

# Example for Washington + Grade 5:
# doc.grade_levels = ["K", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12"]
# all_doc_grades = ["K", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12"]
# "5" in all_doc_grades = True ✓
# Result: Document matches
```

---

## Complete Query Flow

### Example: `python state-science-standards-system.py state WA 5`

```
┌─────────────────────────────────────────────────────────────┐
│ 1. User Input                                               │
│    Command: state WA 5                                      │
│    Parsed: state_abbrev="WA", grade="5"                     │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│ 2. Load Data from JSON                                      │
│    states_dict = json.load(open('data/states.json'))       │
│    state = states_dict["WA"]                                │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│ 3. Get Documents for Grade 5                                │
│    matching_docs = get_documents_for_grade(state, "5")     │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│ 4. Loop Through Each Document                               │
│                                                              │
│    Document 1:                                              │
│    ├─ title: "WA K-12 Science Learning Standards"          │
│    ├─ grade_levels: ["K", "1", ..., "12"]                  │
│    ├─ Check: "5" in ["K", "1", ..., "12"]                  │
│    └─ Result: True ✓ → Add to matching_docs                │
│                                                              │
│    Document 2:                                              │
│    ├─ title: "WSSLS DCI Arrangement"                       │
│    ├─ grade_levels: ["K", "1", ..., "12"]                  │
│    ├─ Check: "5" in ["K", "1", ..., "12"]                  │
│    └─ Result: True ✓ → Add to matching_docs                │
│                                                              │
│    Document 3:                                              │
│    ├─ title: "WSSLS Topic Arrangement"                     │
│    ├─ grade_levels: ["K", "1", ..., "12"]                  │
│    ├─ Check: "5" in ["K", "1", ..., "12"]                  │
│    └─ Result: True ✓ → Add to matching_docs                │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│ 5. Return Results                                           │
│    matching_docs = [doc1, doc2, doc3]                       │
│    Display to user                                          │
└─────────────────────────────────────────────────────────────┘
```

---

## Different Document Types - How They Filter

### Type 1: Complete K-12 Document
```json
{
  "title": "Washington K-12 Standards",
  "grade_levels": ["K", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12"]
}
```
**Filter for grade 5:** `"5" in ["K", "1", ..., "12"]` = `True ✓`
**Result:** Matches **ALL** grades K-12

---

### Type 2: Grade-Specific Document
```json
{
  "title": "Texas Grade 5 TEKS",
  "grade_levels": ["5"]
}
```
**Filter for grade 5:** `"5" in ["5"]` = `True ✓`
**Filter for grade 6:** `"6" in ["5"]` = `False ✗`
**Result:** Matches **ONLY** grade 5

---

### Type 3: Grade-Band Document
```json
{
  "title": "NY Grades 3-5 Standards",
  "grade_levels": ["3", "4", "5"]
}
```
**Filter for grade 5:** `"5" in ["3", "4", "5"]` = `True ✓`
**Filter for grade 6:** `"6" in ["3", "4", "5"]` = `False ✗`
**Result:** Matches grades 3, 4, and 5 only

---

## Why This Design Works

### ✅ Advantages

1. **Simple:** Just a Python `in` operator (O(n) search, but n is small)
2. **Explicit:** No guessing which grades a document covers
3. **Flexible:** Supports any grade organization pattern
4. **Fast:** Direct array lookup, no complex parsing
5. **Maintainable:** Easy to understand and modify

### 🎯 Grade-Agnostic Queries

Because `grade_levels` is stored as data (not code), you can query:
- **Any single grade:** `search 3`, `state WA 5`
- **All states for a grade:** `compare 8`
- **Coverage for all grades:** `range TX`

### 📊 Current Data Reality

**ALL 80 documents use individual grade listings:**
- 0 documents use range notation like `["K-12"]`
- 80 documents use explicit arrays like `["K", "1", "2", ...]`

**This means:**
- The `expand_grade_range()` function currently does nothing (returns input unchanged)
- But it's ready if states start using range notation in future updates
- Filtering is a simple membership test: `grade in doc['grade_levels']`

---

## Performance

For a query like `search 5`:
1. Load JSON: ~10ms (one-time, cached in STATES_DB)
2. Loop through 51 states: ~1ms
3. Check 80 documents: ~1ms (simple array membership)
4. Total: **< 20ms** for complete query

---

## Example Queries in Practice

### Query: "Which states have Grade 3 standards?"
```python
# Pseudocode
for state in all_states:
    for doc in state.documents:
        if "3" in doc.grade_levels:
            print(f"{state.name} has Grade 3 standards")
            break
```

### Query: "Show me Washington's Grade 5 documents"
```python
# Pseudocode
wa_state = STATES_DB["WA"]
for doc in wa_state.documents:
    if "5" in doc.grade_levels:
        print(f"Title: {doc.title}")
        print(f"URL: {doc.url}")
```

### Query: "Does Texas have Grade 11 standards?"
```python
# Pseudocode
tx_state = STATES_DB["TX"]
has_grade_11 = any("11" in doc.grade_levels for doc in tx_state.documents)
print(f"Texas Grade 11: {has_grade_11}")  # False (TX only has K-8)
```

---

## Summary

**The filtering mechanism is:**

1. **Data Structure:** Each document has a `grade_levels` array
2. **Expansion:** Ranges like `"K-12"` expand to `["K", "1", ..., "12"]` (not currently used)
3. **Filtering:** Simple membership test: `if target_grade in doc.grade_levels`
4. **Result:** All documents covering that specific grade

**Key Insight:** The "grade-agnostic" design comes from storing grade coverage as **data** (JSON arrays) rather than **code** (if/else logic). This allows querying any grade without modifying the program.
