#!/usr/bin/env python3
"""
Apply extracted page ranges from patches/grade_sections.json to data/states.json

This script reads the page range extraction results and updates the states.json
documents with page_range data for each grade level.
"""

import json
from pathlib import Path
from datetime import datetime

# Paths
STATES_JSON = Path("data/states.json")
PATCH_FILE = Path("patches/grade_sections.json")

def format_page_ranges(ranges: list) -> str:
    """Convert page range tuples to string format"""
    if not ranges:
        return None

    # Flatten overlapping ranges and format
    range_strs = []
    for start, end in ranges:
        if start == end:
            range_strs.append(str(start))
        else:
            range_strs.append(f"{start}-{end}")

    return ", ".join(range_strs)

def apply_page_ranges():
    """Apply page ranges from patch file to states.json"""

    print("="*80)
    print("Applying Page Ranges to states.json")
    print("="*80)
    print()

    # Load states.json
    if not STATES_JSON.exists():
        print(f"[X] states.json not found at {STATES_JSON}")
        return 1

    with open(STATES_JSON, 'r', encoding='utf-8') as f:
        states_data = json.load(f)

    # Load patch file
    if not PATCH_FILE.exists():
        print(f"[X] Patch file not found at {PATCH_FILE}")
        return 1

    with open(PATCH_FILE, 'r', encoding='utf-8') as f:
        patch_data = json.load(f)

    # Track statistics
    states_updated = 0
    documents_updated = 0
    grades_updated = 0

    # Apply patches
    for state_abbr, patch_info in patch_data.items():
        if state_abbr not in states_data:
            print(f"[!] State {state_abbr} in patch but not in states.json")
            continue

        state = states_data[state_abbr]

        if 'documents' not in patch_info:
            continue

        state_had_updates = False

        # Process each document
        for doc_idx, patch_doc in enumerate(patch_info['documents']):
            if doc_idx >= len(state.get('documents', [])):
                continue

            target_doc = state['documents'][doc_idx]
            grade_sections = patch_doc.get('grade_sections', {})

            if not grade_sections:
                continue

            # Update document with page range data
            for grade, section_info in grade_sections.items():
                page_ranges = section_info.get('page_ranges', [])

                if not page_ranges:
                    continue

                # Find matching grade_level in document
                grade_str = grade
                if 'grade_levels' in target_doc:
                    if grade_str in target_doc['grade_levels']:
                        # This is a multi-grade document, add page_range
                        formatted_range = format_page_ranges(page_ranges)
                        if formatted_range:
                            # Handle different page_range formats
                            if 'page_range' not in target_doc or target_doc['page_range'] is None:
                                target_doc['page_range'] = {}
                            elif isinstance(target_doc['page_range'], str):
                                # Convert string to dict for multi-grade documents
                                old_range = target_doc['page_range']
                                target_doc['page_range'] = {'_all': old_range}

                            target_doc['page_range'][grade_str] = formatted_range
                            grades_updated += 1
                            state_had_updates = True

        if state_had_updates:
            states_updated += 1
            documents_updated += 1
            state['last_updated'] = datetime.now().strftime("%Y-%m-%d")
            print(f"[OK] {state_abbr}: Updated page ranges")

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
    print(f"[OK] Documents updated: {documents_updated}")
    print(f"[OK] Grade ranges added: {grades_updated}")
    print(f"\nUpdated states.json saved to: {STATES_JSON}")
    print()

    return 0

if __name__ == "__main__":
    import sys
    sys.exit(apply_page_ranges())
