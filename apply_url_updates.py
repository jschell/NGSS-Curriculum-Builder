#!/usr/bin/env python3
"""
Apply verified URL updates from research files to states.json

This script reads all research JSON files from docs/url_updates/ and applies
the verified URLs to the corresponding states in data/states.json.

Batches to apply:
- Batch 2: IL, MD, NM, MI, NH, RI (6 states)
- Batch 3: AK, OR, NV, MN, MO, ME (6 states)
- Batch 4: GA, IN, SC, TN (4 states)
- Batch 5: CA, TX (2 states)
- Batch 6: DC (1 state)

Total: 19 states
"""

import json
import sys
from pathlib import Path
from datetime import datetime

# Paths
STATES_JSON = Path("data/states.json")
RESEARCH_DIR = Path("docs/url_updates")

# States to update (Batches 2-6)
BATCH_2 = ["IL", "MD", "NM", "MI", "NH", "RI"]
BATCH_3 = ["AK", "OR", "NV", "MN", "MO", "ME"]
BATCH_4 = ["GA", "IN", "SC", "TN"]
BATCH_5 = ["CA", "TX"]
BATCH_6 = ["DC"]

STATES_TO_UPDATE = BATCH_2 + BATCH_3 + BATCH_4 + BATCH_5 + BATCH_6

def load_research_file(state_abbr: str) -> dict:
    """Load research JSON file for a state"""
    research_file = RESEARCH_DIR / f"{state_abbr.lower()}_science_standards.json"
    if not research_file.exists():
        print(f"[X] Research file not found: {research_file}")
        return None

    with open(research_file, 'r', encoding='utf-8') as f:
        return json.load(f)

def apply_url_update(states_data: dict, state_abbr: str, research_data: dict) -> bool:
    """Apply URL update from research data to states.json"""

    if state_abbr not in states_data:
        print(f"[X] State {state_abbr} not found in states.json")
        return False

    state = states_data[state_abbr]

    # Extract info from research
    working_url = research_data.get("working_url")
    confidence = research_data.get("confidence")
    special_structure = research_data.get("special_structure")
    notes = research_data.get("notes")

    if not working_url:
        print(f"[!] {state_abbr}: No working URL in research file")
        return False

    # Find the primary document to update
    if not state.get("documents"):
        print(f"[X] {state_abbr}: No documents array in state")
        return False

    # Update the first document (primary standards document)
    doc = state["documents"][0]
    old_url = doc.get("url")

    # Update URL
    doc["url"] = working_url

    # Add research metadata
    if special_structure:
        if "notes" in doc:
            doc["notes"] = f"{doc['notes']} | Special structure: {special_structure}"
        else:
            doc["notes"] = f"Special structure: {special_structure}"

    # Add research notes if significant
    if notes and len(notes) < 200:
        if "notes" in doc and doc["notes"]:
            doc["notes"] = f"{doc['notes']} | {notes}"
        else:
            doc["notes"] = notes

    # Update last_updated
    state["last_updated"] = datetime.now().strftime("%Y-%m-%d")

    print(f"[OK] {state_abbr}: Updated URL (confidence: {confidence})")
    if old_url != working_url:
        print(f"     Old: {old_url[:80]}...")
        print(f"     New: {working_url[:80]}...")

    return True

def main():
    """Main function to apply all URL updates"""

    print("=" * 80)
    print("Applying URL Updates from Batches 2-6")
    print("=" * 80)
    print()

    # Load states.json
    if not STATES_JSON.exists():
        print(f"[X] states.json not found at {STATES_JSON}")
        return 1

    with open(STATES_JSON, 'r', encoding='utf-8') as f:
        states_data = json.load(f)

    # Track statistics
    updated = 0
    failed = 0
    skipped = 0

    # Apply updates by batch
    for batch_num, batch_states in enumerate([BATCH_2, BATCH_3, BATCH_4, BATCH_5, BATCH_6], start=2):
        print(f"\n{'='*80}")
        print(f"Batch {batch_num}: {len(batch_states)} states")
        print(f"{'='*80}\n")

        for state_abbr in batch_states:
            # Load research file
            research_data = load_research_file(state_abbr)
            if not research_data:
                failed += 1
                continue

            # Apply update
            if apply_url_update(states_data, state_abbr, research_data):
                updated += 1
            else:
                failed += 1

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
    print(f"[OK] Updated: {updated}/{len(STATES_TO_UPDATE)} states")
    print(f"[X]  Failed:  {failed}/{len(STATES_TO_UPDATE)} states")
    print(f"\nUpdated states.json saved to: {STATES_JSON}")
    print()

    return 0 if failed == 0 else 1

if __name__ == "__main__":
    sys.exit(main())
