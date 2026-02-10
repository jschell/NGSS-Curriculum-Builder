#!/usr/bin/env python3
# /// script
# dependencies = [
#     "httpx>=0.27.0",
#     "pypdf>=3.0.0",
# ]
# ///

"""
Extract grade-specific page ranges from multi-grade PDFs

Processes all 80 documents in states.json to identify grade-specific
page numbers for multi-grade documents. Single-grade documents are
marked as null (not applicable).
"""

import json
import httpx
import pypdf
import io
import re
import time
from pathlib import Path


def extract_grade_page_ranges(url, grade_levels):
    """
    Extract grade-specific page ranges from PDF table of contents

    Returns:
        dict: Page range mapping {"K": "12-25", "1": "26-40", ...}
        or None if single-grade document
        or str "ERROR: message" if extraction failed
    """
    # Skip single-grade documents
    if len(grade_levels) == 1:
        return None

    try:
        # Download PDF
        response = httpx.get(url, timeout=30, follow_redirects=True)

        if response.status_code != 200:
            return f"ERROR: HTTP {response.status_code}"

        # Parse PDF
        pdf_file = io.BytesIO(response.content)
        reader = pypdf.PdfReader(pdf_file)

        total_pages = len(reader.pages)

        # Extract text from first 30 pages (TOC typically in first 20-30 pages)
        toc_text = ""
        pages_to_check = min(30, total_pages)

        for i in range(pages_to_check):
            try:
                page_text = reader.pages[i].extract_text()
                if page_text:
                    toc_text += f"\n{page_text}"
            except Exception:
                continue

        # Find grade markers
        grade_markers = find_grade_markers(toc_text)

        if not grade_markers:
            # No clear TOC found
            return None

        # Calculate page ranges
        page_ranges = calculate_page_ranges(grade_markers, total_pages)

        return page_ranges

    except httpx.TimeoutException:
        return "ERROR: Timeout downloading PDF"
    except Exception as e:
        return f"ERROR: {type(e).__name__}: {str(e)[:100]}"


def find_grade_markers(text):
    """
    Search for grade markers in text and extract page numbers

    Returns:
        dict: Grade to page number mapping {"K": 12, "1": 26, ...}
    """
    markers = {}

    # Patterns to search for
    patterns = [
        (r"Kindergarten\s*[\.\s]+(\d+)", "K"),
        (r"Grade\s+1\s*[\.\s]+(\d+)", "1"),
        (r"Grade\s+2\s*[\.\s]+(\d+)", "2"),
        (r"Grade\s+3\s*[\.\s]+(\d+)", "3"),
        (r"Grade\s+4\s*[\.\s]+(\d+)", "4"),
        (r"Grade\s+5\s*[\.\s]+(\d+)", "5"),
        (r"Grade\s+6\s*[\.\s]+(\d+)", "6"),
        (r"Grade\s+7\s*[\.\s]+(\d+)", "7"),
        (r"Grade\s+8\s*[\.\s]+(\d+)", "8"),
        (r"Grade\s+9\s*[\.\s]+(\d+)", "9"),
        (r"Grade\s+10\s*[\.\s]+(\d+)", "10"),
        (r"Grade\s+11\s*[\.\s]+(\d+)", "11"),
        (r"Grade\s+12\s*[\.\s]+(\d+)", "12"),
    ]

    for pattern, grade in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            page_num = int(match.group(1))
            markers[grade] = page_num

    return markers


def calculate_page_ranges(grade_markers, total_pages):
    """
    Calculate page ranges from grade markers

    Args:
        grade_markers: dict of grade -> page number
        total_pages: total pages in PDF

    Returns:
        dict: grade -> "start-end" page range string
    """
    # Sort grades by page number
    sorted_grades = sorted(grade_markers.items(), key=lambda x: x[1])

    page_ranges = {}

    for i, (grade, page_num) in enumerate(sorted_grades):
        # Calculate end page (next grade's page - 1, or total_pages if last)
        if i < len(sorted_grades) - 1:
            end_page = sorted_grades[i + 1][1] - 1
        else:
            end_page = total_pages

        # Create range string
        page_ranges[grade] = f"{page_num}-{end_page}"

    return page_ranges


def extract_page_ranges_for_state(state_abbr, state_data):
    """
    Process all documents for a state

    Returns:
        dict: Document title -> page_range mapping
    """
    results = {}

    for doc in state_data.get("documents", []):
        title = doc["title"]
        url = doc["url"]
        grade_levels = doc["grade_levels"]

        print(f"  {title}")

        try:
            page_ranges = extract_grade_page_ranges(url, grade_levels)
            results[title] = page_ranges

            if page_ranges is None:
                print(f"    -> No page range (single-grade or no TOC)")
            elif isinstance(page_ranges, str) and page_ranges.startswith("ERROR"):
                print(f"    -> {page_ranges}")
            else:
                print(f"    -> {len(page_ranges)} grade ranges extracted")

        except Exception as e:
            error_msg = f"ERROR: {str(e)[:100]}"
            results[title] = error_msg
            print(f"    -> {error_msg}")

        # Brief pause to avoid overwhelming servers
        time.sleep(1)

    return results


def main():
    """Main extraction function"""

    # Load states data
    script_dir = Path(__file__).parent
    states_file = script_dir / ".." / "data" / "states.json"

    with open(states_file) as f:
        states_data = json.load(f)

    print("=" * 80)
    print("EXTRACTING PAGE RANGES FROM ALL 80 DOCUMENTS")
    print("=" * 80)
    print()

    results = {}

    # Process each state
    for state_abbr, state_data in sorted(states_data.items()):
        print(f"\n{state_abbr}: {state_data['state_name']}")
        state_results = extract_page_ranges_for_state(state_abbr, state_data)
        results[state_abbr] = state_results

    # Save results
    output_file = script_dir / ".." / "page_ranges_extracted.json"

    with open(output_file, "w") as f:
        json.dump(results, f, indent=2)

    print()
    print("=" * 80)
    print("EXTRACTION COMPLETE")
    print("=" * 80)
    print(f"\nResults saved to: {output_file}")

    # Summary statistics
    total_docs = sum(len(docs) for docs in results.values())
    with_ranges = sum(
        1
        for state_docs in results.values()
        for doc_ranges in state_docs.values()
        if isinstance(doc_ranges, dict) and len(doc_ranges) > 0
    )
    single_grade = sum(
        1
        for state_docs in results.values()
        for doc_ranges in state_docs.values()
        if doc_ranges is None
    )
    errors = sum(
        1
        for state_docs in results.values()
        for doc_ranges in state_docs.values()
        if isinstance(doc_ranges, str) and doc_ranges.startswith("ERROR")
    )

    print(f"\nSummary:")
    print(f"  Total documents: {total_docs}")
    print(f"  With page ranges: {with_ranges}")
    print(f"  Single-grade (null): {single_grade}")
    print(f"  Errors: {errors}")
    print(
        f"  Success rate: {with_ranges}/{total_docs} ({with_ranges / total_docs * 100:.1f}%)"
    )


if __name__ == "__main__":
    main()
