import sys
import json
from pathlib import Path

VERIFIED_URLS = {
    "WV": {
        "url": "https://apps.sos.wv.gov/adlaw/csr/readfile.aspx?DocId=54673&Format=PDF",
        "url_source": "https://apps.sos.wv.gov/",
        "notes": "West Virginia Secretary of State website. Direct PDF link to WV College and Career-Readiness Standards for Science.",
    },
    "VA": {
        "url": "https://www.doe.virginia.gov/teaching-learning-assessment/k-12-standards-instruction/science/standards-of-learning",
        "url_source": "https://www.doe.virginia.gov/teaching-learning-assessment/k-12-standards-instruction/",
        "notes": "Virginia DOE website - 2018 Science Standards of Learning K-Physics. Found via web search, same as existing entry.",
    },
    "WA": {
        "url": "https://ospi.k12.wa.us/student-success/resources-subject-area/science/science-k-12-learning-standards",
        "url_source": "https://ospi.k12.wa.us/student-success/learning-standards-instructional-materials/",
        "notes": "OSPI Washington State K-12 Science Learning Standards. Found via web search.",
    },
    "NE": {
        "url": "https://cdn.education.ne.gov/wp-content/uploads/2017/10/Nebraska_Science_Standards_Final_10_23.pdf",
        "url_source": "https://www.education.ne.gov/wp-content/uploads/",
        "notes": "Nebraska College and Career Ready Standards for Science. Note: This is Nebraska's CCR Science Standards, but URL is from Nebraska DOE domain. Used for Nebraska entry.",
    },
    "KY": {
        "url": "https://education.ky.gov/curriculum/standards/kyacadstand/Documents/Kentucky_Academic_Standards_for_Science_2022.pdf",
        "url_source": "https://education.ky.gov/curriculum/standards/kyacadstand/Documents/",
        "notes": "Kentucky Academic Standards for Science 2022. Same URL as existing states.json entry - confirms document is correct.",
    },
    "AZ": {
        "url": "https://www.azed.gov/sites/default/files/2018/10/Full%20Set%20of%20Standards%20K_12_%20Updated_10_19_19.pdf",
        "url_source": "https://www.azed.gov/sites/default/files/",
        "notes": "Arizona Science Standards 2018 - Complete K-12. Same URL as existing states.json entry - confirms document is correct.",
    },
    "FL": {
        "url": "https://info.fldoe.org/docushare/dsweb/Get/Document/6516/dps-2012-140b.pdf",
        "url_source": "https://info.fldoe.org/",
        "notes": "Florida NGSSS: 9-12 Science Standards Body of Knowledge. FLDoe.org hosting.",
    },
    "HI": {
        "url": "https://manoa.hawaii.edu/sealearning/sites/default/files/NGSSReduced.pdf",
        "url_source": "https://manoa.hawaii.edu/sealearning/",
        "notes": "Hawaii NGSS Standards K-12. University of Hawaii hosting.",
    },
    "ID": {
        "url": "https://www.sde.idaho.gov/wp-content/uploads/2025/09/Idaho-K-12-State-Standards-for-Science.pdf",
        "url_source": "https://www.sde.idaho.gov/wp-content/uploads/",
        "notes": "Idaho K-12 State Standards for Science. Idaho SDE hosting.",
    },
}


def load_states_data():
    """Load states.json"""
    # Use Path.resolve() to get absolute path from current working directory
    current_dir = Path.cwd().resolve()
    script_dir = Path(__file__).resolve().parent

    # Navigate from script dir to project root if needed
    while script_dir.name != "scripts":
        script_dir = script_dir.parent

    states_file = script_dir / "data" / "states.json"

    if not states_file.exists():
        print(f"ERROR: states.json not found at {states_file}")
        return None

    with open(states_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
        return data


def save_states_data(states_data):
    """Save states.json"""
    states_file = script_dir / "data" / "states.json"

    with open(states_file, 'w', encoding='utf-8') as f:
        json.dump(states_data, f, indent=2)

    print(f"Saved {states_file}")


def apply_url_update(state_abbr: str, states_data: dict, verified_url: str, url_source: str):
    """Apply URL update to state's first science document"""
    if state_abbr not in states_data:
        print(f"  [SKIP] State {state_abbr} not found")
        return False

    state_data = states_data[state_abbr]

    # Find first document
    documents = state_data.get("documents", [])
    if not documents:
        print(f"  [SKIP] No documents found for {state_abbr}")
        return False

    doc = documents[0]  # Assume first document
    doc_title = doc.get("title", "Unknown")

    # Check if document exists in verified list
    if state_abbr in VERIFIED_URLS:
        if verified_url == VERIFIED_URLS[state_abbr]["url"]:
            # URL matches - update fields
            doc["url"] = verified_url
            doc["url_source"] = url_source
            doc["last_verified"] = "2026-02-05"
            print(f"  {state_abbr}: {doc_title[:40]} - URL updated")
            return True
        else:
            # URL doesn't match - add as new field
            print(f"  {state_abbr}: {doc_title[:40]} - Skipped (URL not in verified list)")
            return False

    print(f"  {state_abbr}: {doc_title[:40]} - Skipped (URL not in verified list)")
    return False


def main():
    """Main function"""
    print("=" * 80)
    print("APPLYING URL UPDATES")
    print("=" * 80)
    print()

    # Load states data
    print("Loading states.json...")
    states_data = load_states_data()

    if not states_data:
        print("ERROR: Failed to load states.json")
        sys.exit(1)

    print(f"Loaded {len(states_data)} states")
    print()

    # Get state abbreviations from command line
    if len(sys.argv) < 2:
        print("Usage: python simple_url_updates.py [STATE_ABBREV] [STATE_ABBREV2] ...")
        print()
        print("Available states with verified URLs:")
        for state in VERIFIED_URLS.keys():
            print(f"  - {state}")
        print()
        sys.exit(1)

    state_abbrevs = [arg.upper() for arg in sys.argv[1:]]
    print(f"\nApplying updates for {len(state_abbrevs)} state(s): {', '.join(state_abbrevs)}")
    print()

    # Apply updates
    updated = 0
    skipped = 0
    for state_abbr in state_abbrevs:
        if state_abbr in VERIFIED_URLS:
            if apply_url_update(state_abbr, states_data, VERIFIED_URLS[state_abbr]["url"], VERIFIED_URLS[state_abbr]["url_source"]):
                updated += 1
        else:
            skipped += 1
    else:
        skipped += 1

    # Save updated data
    save_states_data(states_data)

    print()
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"  States Updated: {updated}")
    print(f"  States Skipped: {skipped}")
    print(f"  Total Processed: {updated + skipped}")
    print()
