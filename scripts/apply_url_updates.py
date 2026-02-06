#!/usr/bin/env python3
# /// script
# dependencies = []
# ///

"""
Apply URL Updates to states.json

Applies verified working URLs from research templates to states.json.
Updates url, url_source, and last_verified fields.
"""

import sys
import json
from pathlib import Path


# Confirmed working URLs from Batch 1 research
VERIFIED_URLS = {
    "WV": {
        "url": "https://apps.sos.wv.gov/adlaw/csr/readfile.aspx?DocId=54673&Format=PDF",
        "url_source": "https://apps.sos.wv.gov/",
        "confidence": "High",
        "notes": "West Virginia Secretary of State website. Direct PDF link to WV College and Career-Readiness Standards for Science.",
    },
    "VA": {
        "url": "https://www.doe.virginia.gov/teaching-learning-assessment/k-12-standards-instruction/science/standards-of-learning",
        "url_source": "https://www.doe.virginia.gov/teaching-learning-assessment/k-12-standards-instruction/",
        "confidence": "High",
        "notes": "Virginia DOE website - 2018 Science Standards of Learning K-Physics. Found via web search, same as existing entry.",
    },
    "WA": {
        "url": "https://ospi.k12.wa.us/student-success/resources-subject-area/science/science-k-12-learning-standards",
        "url_source": "https://ospi.k12.wa.us/student-success/",
        "confidence": "High",
        "notes": "OSPI Washington State K-12 Science Learning Standards. Found via web search.",
    },
    "NE": {
        "url": "https://cdn.education.ne.gov/wp-content/uploads/2017/10/Nebraska_Science_Standards_Final_10_23.pdf",
        "url_source": "https://www.education.ne.gov/",
        "confidence": "High",
        "notes": "Nebraska College and Career Ready Standards for Science. Note: This is Nebraska's CCR Science Standards, but URL is from Nebraska DOE domain. Used for Nebraska entry.",
    },
    "KY": {
        "url": "https://education.ky.gov/curriculum/standards/kyacadstand/Documents/Kentucky_Academic_Standards_for_Science_2022.pdf",
        "url_source": "https://education.ky.gov/curriculum/standards/kyacadstand/Documents/",
        "confidence": "High",
        " notes": "Kentucky Academic Standards for Science 2022. Same URL as existing states.json entry - confirms document is correct.",
    },
    "AZ": {
        "url": "https://www.azed.gov/sites/default/files/2018/10/Full%20Set%20of%20Standards%20K_12_%20Updated_10_19_19.pdf",
        "url_source": "https://www.azed.gov/sites/default/files/",
        "confidence": "High",
        "notes": "Arizona Science Standards 2018 - Complete K-12. Same URL as existing states.json entry - confirms document is correct.",
    },
    "FL": {
        "url": "https://info.fldoe.org/docushare/dsweb/Get/Document/6516/dps-2012/140b.pdf",
        "url_source": "https://info.fldoe.org/",
        "confidence": "High",
        " notes": "Florida NGSSS: 9-12 Science Standards Body of Knowledge. FLDoe.org hosting.",
    },
    "HI": {
        "url": "https://manoa.hawaii.edu/sealearning/sites/default/files/NGSSReduced.pdf",
        "url_source": "https://manoa.hawaii.edu/sealearning/",
        "confidence": "High",
        " notes": "Hawaii NGSS Standards K-12. University of Hawaii hosting.",
    },
    "ID": {
        "url": "https://www.sde.idaho.gov/wp-content/uploads/2025/09/Idaho-K-12-State-Standards-for-Science.pdf",
        "url_source": "https://www.sde.idaho.gov/wp-content/uploads/",
        "confidence": "High",
        "notes": "Idaho K-12 State Standards for Science. Idaho SDE hosting.",
    },
}


def load_states_data():
    """Load states.json"""

    states_file = Path(__file__).parent / "data" / "states.json"

    if not states_file.exists():
        print(f"ERROR: states.json not found at {states_file}")
        return None

    with open(states_file, "r", encoding="utf-8") as f:
        data = json.load(f)
        return data


def save_states_data(states_data):
    """Save states.json"""

    states_file = Path(__file__).parent / "data" / "states.json"

    with open(states_file, "w") as f:
        json.dump(states_data, f, indent=2)

    print(f"Saved: {states_file}")


def apply_url_update(state_abbr: str, states_data: dict, verified_info: dict) -> bool:
    """
    Apply URL update to a state's first science document
    """

    if state_abbr not in states_data:
        print(f"  [SKIP] State {state_abbr} not found in states.json")
        return False

    state_data = states_data[state_abbr]

    # Find first document (science standards)
    documents = state_data.get("documents", [])
    if not documents:
        print(f"  [SKIP] No documents found for {state_abbr}")
        return False

    # Look for science standards document
    science_doc = None
    for doc in documents:
        doc_title_lower = doc.get("title", "").lower()
        # Check if this is the science standards document
        if "science" in doc_title_lower and "standard" in doc_title_lower:
            science_doc = doc
            break

    if not science_doc:
        print(f"  [WARNING] No science standards document found for {state_abbr}")
        return False

    # Apply update
    print(f"  Updating {state_abbr}: {science_doc.get('title')}")

    # Update URL
    science_doc["url"] = verified_info["url"]

    # Add url_source
    science_doc["url_source"] = verified_info["url_source"]

    # Add last_verified
    science_doc["last_verified"] = "2026-02-05"

    # Add notes if provided
    if verified_info.get("notes"):
        existing_notes = science_doc.get("notes", "")
        science_doc["notes"] = f"{existing_notes} {verified_info['notes']}".strip()

    print(f"  - URL: {verified_info['url']}")
    print(f"  - Source: {verified_info['url_source']}")
    print(f"  - Last Verified: 2026-02-05")

    return True


def main():
    """Main function"""

    if len([arg for arg in sys.argv if arg.startswith("-")]) < 1:
        print("Usage: python apply_url_updates.py [STATE_ABBREV] [STATE_ABBREV2] ...")
        print("\nApply verified URLs from Batch 1 research")
        print("\nStates with verified URLs:")
        for state in VERIFIED_URLS.keys():
            print(f"  - {state}: {VERIFIED_URLS[state]['url']}")
        print()
        print("Or apply to all 7 confirmed states at once:")
        print("  python apply_url_updates.py WV VA WA NE KY AZ FL HI ID")
        sys.exit(1)

    # Load states data
    print("Loading states.json...")
    states_data = load_states_data()
    if not states_data:
        print("ERROR: Failed to load states.json")
        sys.exit(1)

    print(f"Loaded {len(states_data)} states")

    # Get state abbreviations
    state_abbrevs = [arg.upper() for arg in sys.argv if not arg.startswith("-")]

    # Apply updates
    print(f"\n{'=' * 80}")
    print("APPLYING URL UPDATES")
    print(f"{'=' * 80}")

    updates_applied = 0
    updates_skipped = 0

    for state_abbr in state_abbrevs:
        if state_abbr not in VERIFIED_URLS:
            print(f"\n[SKIP] {state_abbr}: Not in verified URLs list")
            updates_skipped += 1
            continue

        print(f"\n{state_abbr}: {VERIFIED_URLS[state_abbr]['state_name']}")
        if apply_url_update(state_abbr, states_data, VERIFIED_URLS[state_abbr]):
            updates_applied += 1
        else:
            print(f"  [FAILED] Could not update")
            updates_skipped += 1

    # Save updated data
    save_states_data(states_data)

    print(f"\n{'=' * 80}")
    print("SUMMARY")
    print(f"{'=' * 80}")
    print(f"  Updates Applied: {updates_applied}")
    print(f"  Updates Skipped: {updates_skipped}")
    print(f"  Total Processed: {updates_applied + updates_skipped}")


if __name__ == "__main__":
    main()
