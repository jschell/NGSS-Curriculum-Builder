#!/usr/bin/env python3
# /// script
# dependencies = [
#     "httpx>=0.27.0",
#     "pypdf>=3.0.0",
# ]
# ///

"""
Parse specific grades from PDF documents using page_range data

This module provides functions for efficient grade-specific parsing by leveraging
page_range data from states.json. Instead of parsing entire PDFs, only the
relevant pages for a specific grade are extracted and analyzed.

Usage:
    uv run parse_by_page_range.py AL K

This demonstrates how page_range data can be used for efficient parsing.
"""

import json
import httpx
import pypdf
import io
import re
import sys
from pathlib import Path
from typing import Optional, Dict, List, Tuple


def parse_page_range_string(page_range_str: str) -> Dict[str, Tuple[int, int]]:
    """
    Parse page_range string from states.json into structured format

    Args:
        page_range_str: String like "K:16-18, 1:19-20, 2:21-26"

    Returns:
        Dict mapping grades to (start_page, end_page) tuples
        Example: {"K": (16, 18), "1": (19, 20), "2": (21, 26)}
    """
    if not page_range_str:
        return {}

    result = {}

    # Split by comma to get grade:range pairs
    pairs = page_range_str.split(",")

    for pair in pairs:
        pair = pair.strip()
        if not pair:
            continue

        # Split by colon to get grade and range
        parts = pair.split(":")
        if len(parts) != 2:
            continue

        grade = parts[0].strip()
        range_str = parts[1].strip()

        # Parse range like "16-18"
        range_parts = range_str.split("-")
        if len(range_parts) != 2:
            continue

        try:
            start_page = int(range_parts[0].strip())
            end_page = int(range_parts[1].strip())
            result[grade] = (start_page, end_page)
        except ValueError:
            continue

    return result


def get_page_range_for_grade(
    page_range_str: str, grade: str
) -> Optional[Tuple[int, int]]:
    """
    Get page range for a specific grade

    Args:
        page_range_str: String like "K:16-18, 1:19-20, 2:21-26"
        grade: Grade to look up (e.g., "K", "1", "2")

    Returns:
        Tuple of (start_page, end_page) or None if not found
    """
    page_ranges = parse_page_range_string(page_range_str)
    return page_ranges.get(grade)


def parse_pdf_for_grade(
    url: str, grade: str, page_range_str: Optional[str] = None
) -> str:
    """
    Parse PDF, optionally limiting to specific page range

    Args:
        url: PDF URL
        grade: Grade to parse
        page_range_str: Optional page_range string from states.json

    Returns:
        Extracted text from specified pages
    """
    try:
        # Download PDF
        response = httpx.get(url, timeout=30, follow_redirects=True)
        if response.status_code != 200:
            return f"Error: HTTP {response.status_code}"

        # Parse PDF
        pdf_file = io.BytesIO(response.content)
        reader = pypdf.PdfReader(pdf_file)

        total_pages = len(reader.pages)

        # Determine pages to parse
        if page_range_str:
            grade_range = get_page_range_for_grade(page_range_str, grade)
            if grade_range:
                start_page, end_page = grade_range
                # Adjust for 0-indexing (page 1 = index 0)
                start_idx = max(0, start_page - 1)
                end_idx = min(total_pages, end_page)

                print(
                    f"  Using page_range: {start_page}-{end_page} (pages {start_idx + 1} to {end_idx} in PDF)"
                )
                pages_to_parse = reader.pages[start_idx:end_idx]
            else:
                print(f"  No page_range found for grade {grade}, parsing entire PDF")
                pages_to_parse = reader.pages
        else:
            print(f"  No page_range available, parsing entire PDF")
            pages_to_parse = reader.pages

        # Extract text from pages
        text = ""
        for i, page in enumerate(pages_to_parse, start=1):
            try:
                page_text = page.extract_text()
                if page_text:
                    text += f"\n--- PAGE {i} ---\n{page_text}\n"
            except Exception as e:
                text += f"\n--- PAGE {i} ---\nError extracting text: {e}\n"

        return text

    except Exception as e:
        return f"Error: {type(e).__name__}: {str(e)}"


def main():
    """Parse a specific grade for a state"""

    if len(sys.argv) < 3:
        print("Usage: parse_by_page_range.py <STATE_ABBREV> <GRADE>")
        print("Example: parse_by_page_range.py AL K")
        print()
        print(
            "This demonstrates efficient grade-specific parsing using page_range data."
        )
        sys.exit(1)

    state_abbr = sys.argv[1].upper()
    grade = sys.argv[2]

    # Load states data
    script_dir = Path(__file__).parent
    states_file = script_dir / "data" / "states.json"

    with open(states_file) as f:
        states_data = json.load(f)

    if state_abbr not in states_data:
        print(f"Error: State '{state_abbr}' not found")
        sys.exit(1)

    state = states_data[state_abbr]

    print(f"\n{'=' * 80}")
    print(f"PARSING {state['state_name']} - GRADE {grade}")
    print(f"{'=' * 80}\n")

    # Find documents covering this grade
    for doc in state["documents"]:
        if grade in doc.get("grade_levels", []):
            print(f"Document: {doc['title']}")
            print(f"URL: {doc['url']}")
            print(f"page_range: {doc.get('page_range', 'N/A')}")

            # Parse using page_range
            text = parse_pdf_for_grade(doc["url"], grade, doc.get("page_range"))

            # Show first 500 characters
            print(f"\nExtracted text (first 500 chars):")
            print("-" * 40)
            print(text[:500])
            print("-" * 40)

            # Show statistics
            char_count = len(text)
            line_count = len(text.split("\n"))
            print(f"\nTotal extracted: {char_count} chars, {line_count} lines")

            break
    else:
        print(f"No documents found for grade {grade}")


if __name__ == "__main__":
    main()
