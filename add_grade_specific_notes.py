#!/usr/bin/env python3
"""
Add grade-specific document notes to states with multiple documents per grade

States with grade-specific documents (no page ranges needed):
- CA: 16+ documents
- TX: 3 documents
- IN: Grade-specific
- GA: Grade-specific
- NC: Grade-band specific
- LA: Web-based/grade-specific
- MO: Dual documents
"""

import json
from pathlib import Path
from datetime import datetime

# Paths
STATES_JSON = Path("data/states.json")

# States with grade-specific structures
GRADE_SPECIFIC_STATES = {
    "CA": {
        "note": "California provides separate grade-specific PDFs. Elementary (K-5): one per grade. Middle School (6-8): two models available (Integrated and Discipline-Specific). High School (9-12): organized by discipline.",
        "special_structure": "grade_specific_documents"
    },
    "TX": {
        "note": "Texas organizes standards in three comprehensive PDFs by school level: Elementary (K-5), Middle School (6-8), and High School (9-12). Each PDF covers all grades within that level.",
        "special_structure": "level_specific_documents"
    },
    "IN": {
        "note": "Indiana provides separate PDFs for each grade K-8 and for each high school course (Biology, Chemistry, Physics, etc.). No comprehensive K-12 document available.",
        "special_structure": "grade_specific_documents"
    },
    "GA": {
        "note": "Georgia provides separate PDFs organized by grade band (K-5, 6-8, 9-12). No comprehensive K-12 document available.",
        "special_structure": "grade_band_documents"
    },
    "NC": {
        "note": "North Carolina 2023 standards organized in grade bands: K-2, 3-5, 6-8, and high school course-specific documents. No comprehensive K-12 PDF.",
        "special_structure": "grade_band_documents"
    },
    "LA": {
        "note": "Louisiana Student Standards for Science (LSSS) organized by grade level with web-based access and implementation guides. LSSS/NGSS crosswalks available for all grades.",
        "special_structure": "web_based_grade_specific"
    },
    "MO": {
        "note": "Missouri provides two separate PDFs: K-5 standards and 6-12 standards. No single comprehensive K-12 document.",
        "special_structure": "dual_documents"
    }
}

def add_grade_specific_notes():
    """Add notes about grade-specific document structures"""

    print("="*80)
    print("Adding Grade-Specific Document Notes")
    print("="*80)
    print()

    # Load states.json
    if not STATES_JSON.exists():
        print(f"[X] states.json not found at {STATES_JSON}")
        return 1

    with open(STATES_JSON, 'r', encoding='utf-8') as f:
        states_data = json.load(f)

    # Track statistics
    states_updated = 0

    # Add notes for each state
    for state_abbr, metadata in GRADE_SPECIFIC_STATES.items():
        if state_abbr not in states_data:
            print(f"[!] State {state_abbr} not found in states.json")
            continue

        state = states_data[state_abbr]
        note = metadata['note']
        special_structure = metadata['special_structure']

        # Add to primary document
        if state.get('documents') and len(state['documents']) > 0:
            doc = state['documents'][0]

            # Add or update notes
            if 'notes' in doc and doc['notes']:
                # Append if note doesn't already mention grade-specific
                if 'grade-specific' not in doc['notes'].lower() and 'separate' not in doc['notes'].lower():
                    doc['notes'] = f"{doc['notes']} | {note}"
                else:
                    # Already has similar note
                    print(f"[OK] {state_abbr}: Already has grade-specific note")
                    continue
            else:
                doc['notes'] = note

            # Add special_structure field if not present
            if 'special_structure' not in doc:
                doc['special_structure'] = special_structure

        # Update state-level metadata
        if 'notes' not in state or not state['notes']:
            state['notes'] = note
        elif 'grade-specific' not in state['notes'].lower():
            state['notes'] = f"{state['notes']} | {note}"

        state['last_updated'] = datetime.now().strftime("%Y-%m-%d")
        states_updated += 1

        print(f"[OK] {state_abbr}: Added grade-specific document note")

    # Save updated states.json
    print(f"\n{'='*80}")
    print("Saving updated states.json...")
    print(f"{'='*80}\n")

    with open(STATES_JSON, 'w', encoding='utf-8') as f:
        json.dump(states_data, f, indent=2, ensure_ascii=False)

    # Print summary
    print(f"\n{'='*80}")
    print("Summary")
    print(f"{'='*80}")
    print(f"[OK] States updated: {states_updated}")
    print(f"\nUpdated states.json saved to: {STATES_JSON}")
    print()

    return 0

if __name__ == "__main__":
    import sys
    sys.exit(add_grade_specific_notes())
