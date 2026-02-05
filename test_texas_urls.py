#!/usr/bin/env python3
# /// script
# dependencies = [
#     "httpx>=0.27.0",
# ]
# ///
"""
Quick test to verify Texas (TX) URLs in states.json
Checks HTTP status and content type for all TX documents
"""

import json
import httpx
from pathlib import Path


def test_texas_urls():
    """Test all Texas document URLs"""

    # Load states.json
    states_file = Path(__file__).parent / "data" / "states.json"
    with open(states_file, 'r', encoding='utf-8') as f:
        states_data = json.load(f)

    tx_data = states_data.get("TX")
    if not tx_data:
        print("❌ Texas (TX) not found in states.json")
        return

    print("=" * 80)
    print("TEXAS (TX) URL VALIDATION TEST")
    print("=" * 80)
    print()

    documents = tx_data.get("documents", [])
    print(f"Total TX documents in states.json: {len(documents)}")
    print()

    working = 0
    broken = 0

    for idx, doc in enumerate(documents, 1):
        title = doc.get("title", "Untitled")
        url = doc.get("url", "")
        grade_levels = doc.get("grade_levels", [])
        url_source = doc.get("url_source", "Not specified")
        last_verified = doc.get("last_verified", "Not specified")

        print(f"\n{idx}. {title}")
        print(f"   Grades: {', '.join(map(str, grade_levels))}")
        print(f"   URL: {url}")
        print(f"   Source: {url_source}")
        print(f"   Last Verified: {last_verified}")

        # Test URL
        if not url:
            print(f"   [X] Status: No URL specified")
            broken += 1
            continue

        try:
            # Try to fetch the URL
            response = httpx.get(url, timeout=10.0, follow_redirects=True)
            status = response.status_code
            content_type = response.headers.get("content-type", "unknown")
            content_length = len(response.content)

            if status == 200:
                print(f"   [OK] Status: HTTP {status} OK")
                print(f"   Content-Type: {content_type}")
                print(f"   Size: {content_length:,} bytes ({content_length / 1024:.1f} KB)")

                # Check if it's actually a PDF
                if "pdf" in content_type.lower():
                    print(f"   [CHECK] Confirmed PDF format")
                    working += 1
                elif "html" in content_type.lower():
                    print(f"   [WARN] WARNING: Returns HTML, not PDF!")
                    broken += 1
                else:
                    print(f"   [WARN] WARNING: Unexpected content type")
                    broken += 1
            else:
                print(f"   [X] Status: HTTP {status}")
                broken += 1

        except httpx.TimeoutException:
            print(f"   [X] Status: Timeout (>10s)")
            broken += 1
        except httpx.ConnectError:
            print(f"   [X] Status: Connection Error")
            broken += 1
        except Exception as e:
            print(f"   [X] Status: Error - {type(e).__name__}: {str(e)[:100]}")
            broken += 1

    # Summary
    print()
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Total documents: {len(documents)}")
    print(f"[OK] Working PDFs: {working} ({working/len(documents)*100:.1f}%)")
    print(f"[X] Broken/Wrong: {broken} ({broken/len(documents)*100:.1f}%)")
    print()

    if working == len(documents):
        print("SUCCESS: ALL TEXAS URLs ARE WORKING!")
    elif working > 0:
        print(f"PARTIAL: {working}/{len(documents)} URLs working")
    else:
        print("FAIL: ALL TEXAS URLs ARE BROKEN - Need research")

    print()


if __name__ == "__main__":
    test_texas_urls()
