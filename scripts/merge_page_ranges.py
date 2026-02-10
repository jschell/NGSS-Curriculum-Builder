#!/usr/bin/env python3
"""
Merge page range data into states.json

Merges extracted page ranges with manual corrections and updates
the page_range field in states.json for all documents.
"""

import json
from pathlib import Path


def page_ranges_to_string(ranges_dict):
    """
    Convert page ranges dict to human-readable string format

    Args:
        ranges_dict: Dict like {"K": "16-18", "1": "19-20", ...}

    Returns:
        String like "K:16-18, 1:19-20, 2:21-26"
    """
    if not ranges_dict or not isinstance(ranges_dict, dict):
        return None

    # Sort by grade (K, 1, 2, 3, ...)
    def grade_sort_key(grade):
        if grade == "K":
            return (0, "K")
        try:
            return (1, int(grade))
        except ValueError:
            return (2, grade)

    sorted_grades = sorted(ranges_dict.keys(), key=grade_sort_key)

    # Create comma-separated string
    parts = [f"{grade}:{ranges_dict[grade]}" for grade in sorted_grades]
    return ", ".join(parts)


def main():
    """Merge page ranges into states.json"""

    script_dir = Path(__file__).parent

    # Load files
    states_file = script_dir / ".." / "data" / "states.json"
    extracted_file = script_dir / ".." / "page_ranges_extracted.json"
    corrections_file = script_dir / ".." / "page_ranges_manual_corrections.json"

    print("Loading files...")
    with open(states_file) as f:
        states_data = json.load(f)

    with open(extracted_file) as f:
        extracted_data = json.load(f)

    with open(corrections_file) as f:
        corrections_data = json.load(f)

    # Merge page ranges
    print("\nMerging page ranges...")

    stats = {
        "total": 0,
        "from_corrections": 0,
        "from_extracted": 0,
        "kept_null": 0,
        "url_errors": 0,
    }

    for state_abbr, state_data in states_data.items():
        for doc in state_data["documents"]:
            title = doc["title"]
            stats["total"] += 1

            # Check manual corrections first (highest priority)
            if state_abbr in corrections_data.get("corrections", {}):
                state_corrections = corrections_data["corrections"][state_abbr]
                if title in state_corrections:
                    correction = state_corrections[title]["correction"]
                    if correction is not None:
                        # Apply manual correction
                        doc["page_range"] = correction
                        stats["from_corrections"] += 1
                        continue

            # Check extracted data (second priority)
            if state_abbr in extracted_data:
                if title in extracted_data[state_abbr]:
                    extracted = extracted_data[state_abbr][title]

                    # Skip URL errors
                    if isinstance(extracted, str) and extracted.startswith("ERROR"):
                        stats["url_errors"] += 1
                        continue

                    # Convert dict to string format
                    if isinstance(extracted, dict) and len(extracted) > 0:
                        page_range_str = page_ranges_to_string(extracted)
                        doc["page_range"] = page_range_str
                        stats["from_extracted"] += 1
                    else:
                        # Single-grade or no TOC found - keep as null
                        doc["page_range"] = None
                        stats["kept_null"] += 1
                    continue

            # No data available - keep as null
            doc["page_range"] = None
            stats["kept_null"] += 1

    # Save updated states.json
    output_file = states_file
    with open(output_file, "w") as f:
        json.dump(states_data, f, indent=2)

    print(f"\nMerge complete!")
    print(f"Output: {output_file}")
    print(f"\nStatistics:")
    print(f"  Total documents: {stats['total']}")
    print(f"  From manual corrections: {stats['from_corrections']}")
    print(f"  From extracted data: {stats['from_extracted']}")
    print(f"  Kept null (single-grade/no TOC): {stats['kept_null']}")
    print(f"  URL errors (skipped): {stats['url_errors']}")

    # Validate
    print("\nValidating...")
    with open(output_file) as f:
        validation_data = json.load(f)

    total_states = len(validation_data)
    total_docs = sum(len(s["documents"]) for s in validation_data.values())
    with_page_range = sum(
        1
        for s in validation_data.values()
        for d in s["documents"]
        if d.get("page_range") is not None
    )

    print(f"  States: {total_states} (expected: 51)")
    print(f"  Documents: {total_docs} (expected: 80)")
    print(f"  With page_range: {with_page_range}")

    if total_states == 51 and total_docs == 80:
        print("\n✓ Merge successful!")
    else:
        print("\n✗ Data integrity issue detected!")


if __name__ == "__main__":
    main()
