#!/usr/bin/env python3
# /// script
# dependencies = [
#     "httpx>=0.27.0",
#     "orjson>=3.9.0",
#     "pypdf>=3.0.0",
# ]
# ///
"""
Validate URLs for the 36 remaining unverified states
"""

import json
import sys
import asyncio
from pathlib import Path

# Import validation functions from validate_urls.py
sys.path.insert(0, str(Path(__file__).parent))

# Import after path is set
from validate_urls import validate_states


# List of 36 unverified states
UNVERIFIED_STATES = [
    'AK', 'AL', 'AR', 'AZ', 'CO', 'CT', 'FL', 'GA',
    'ID', 'IN', 'LA', 'MA', 'MD', 'ME', 'MN', 'MO',
    'MS', 'MT', 'NC', 'ND', 'NE', 'NH', 'NJ', 'NV',
    'OH', 'OK', 'PA', 'RI', 'SC', 'SD', 'TN', 'UT',
    'VA', 'WI', 'WV', 'WY'
]


async def main():
    """Validate only the 36 unverified states"""

    script_dir = Path(__file__).parent
    states_file = script_dir / "data" / "states.json"

    if not states_file.exists():
        print(f"Error: states.json not found at {states_file}")
        return

    print(f"Loading states data from {states_file}")
    with open(states_file) as f:
        states_data = json.load(f)

    # Filter to only unverified states
    filtered_data = {k: v for k, v in states_data.items() if k in UNVERIFIED_STATES}

    print(f"\nFiltered to {len(filtered_data)} unverified states")
    print(f"States: {', '.join(sorted(filtered_data.keys()))}")

    # Count documents
    doc_count = sum(len(s.get('documents', [])) for s in filtered_data.values())
    print(f"Total documents to validate: {doc_count}")

    # Output files
    output_json = script_dir / "validation_results_remaining_36.json"
    output_report = script_dir / "docs" / "VALIDATION_REMAINING_36_SUMMARY.md"

    print(f"\nStarting validation...")
    print(f"Output JSON: {output_json}")
    print(f"Output report: {output_report}")
    print()

    # Run validation with state filter
    await validate_states(
        states_data,  # Pass full data but use filter
        state_filter=UNVERIFIED_STATES,
        output_json=output_json,
        output_report=output_report
    )

    print(f"\n✓ Validation complete!")
    print(f"  Results: {output_json}")
    print(f"  Report: {output_report}")


if __name__ == "__main__":
    asyncio.run(main())
