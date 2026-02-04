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
    with open("docs/discovered_urls.json") as f:
        discovery = json.load(f)

    # Apply discovered URLs
    state = discovery["state"]
    matched_docs = discovery["matched_docs"]
    updates_made = 0

    # Get expected documents for this state
    expected_docs = [doc["title"] for doc in states[state]["documents"]]

    # Find documents that haven't been updated yet
    # by checking which expected documents are NOT in matched_docs (meaning they need to be fixed)
    documents_to_update = []
    for doc_title in expected_docs:
        if doc_title not in matched_docs:
            documents_to_update.append(doc_title)

    print(f"Documents to update: {len(documents_to_update)}")
    for title in documents_to_update:
        print(f"  - {title}")

    print()

    # Update only documents that haven't been updated yet
    for doc_title in documents_to_update:
        # Find document by title
        for doc in states[state]["documents"]:
            if doc["title"] == doc_title:
                # Check if already updated (has url_source or last_verified)
                already_updated = "url_source" in doc or "last_verified" in doc
                if already_updated:
                    print(f"  Skipping {doc['title'][:50]} (already updated)")
                    continue

                # Check if current URL matches discovered URL
                current_url = doc["url"]
                discovered_url = matched_docs[doc_title]
                if current_url == discovered_url:
                    print(f"  Skipping {doc['title'][:50]} (URL already correct)")
                    continue

                # Update with discovered URL
                doc["url"] = discovered_url
                doc["url_source"] = states[state]["science_page"]
                doc["last_verified"] = datetime.now().strftime("%Y-%m-%d")
                updates_made += 1
                print(f"Updated: {doc['title'][:40]}")
                print(f"  Old: {current_url[:60]}...")
                print(f"  New: {discovered_url[:60]}...")
                print()

    # Save updated states.json
    with open("data/states.json", "w") as f:
        json.dump(states, f, indent=2)

    print(f"Total updates: {updates_made}")
    print(f"Please validate: python -m json.tool data/states.json")


if __name__ == "__main__":
    main()
