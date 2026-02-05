#!/usr/bin/env python3
"""
Apply discovered URLs to states.json.
Updates states.json with working URLs found through website discovery.
"""

import json
from datetime import datetime


def main():
    # Load data
    with open("data/states.json", "r") as f:
        states = json.load(f)

    # Load discovery results
    with open("docs/discovered_urls.json", "r") as f:
        discovery = json.load(f)

    # Apply discovered URLs
    state = discovery["state"]
    matched_docs = discovery["matched_docs"]
    updates_made = 0

    for doc_title, new_url in matched_docs.items():
        # Find document by title
        for doc in states[state]["documents"]:
            if doc["title"] == doc_title:
                old_url = doc["url"]
                doc["url"] = new_url
                doc["url_source"] = states[state]["science_page"]
                doc["last_verified"] = datetime.now().strftime("%Y-%m-%d")
                updates_made += 1
                print(f"Updated: {doc['title'][:40]}")
                print(f"  Old: {old_url[:60]}...")
                print(f"  New: {new_url[:60]}...")
                print()

    # Save updated states.json
    with open("data/states.json", "w") as f:
        json.dump(states, f, indent=2)

    print(f"Total updates: {updates_made}")
    print(f"Please validate: python -m json.tool data/states.json")


if __name__ == "__main__":
    main()
