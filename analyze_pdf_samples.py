#!/usr/bin/env python3
# /// script
# dependencies = [
#     "httpx>=0.27.0",
#     "pypdf>=3.0.0",
# ]
# ///
"""
Analyze sample PDF documents to understand page range patterns
Downloads and extracts TOC/structure from representative PDFs
"""

import json
import httpx
import pypdf
import io
import re
from pathlib import Path


# Sample documents to analyze
SAMPLES = [
    ('TX', 2, 'Single-grade'),  # Grade 2 TEKS
    ('AL', 0, 'Complete K-12'),  # Alabama K-12
    ('CA', 1, 'Grade-specific'),  # California Kindergarten
    ('WA', 0, 'Complete K-12'),  # Washington K-12
    ('VT', 0, 'Complete K-12'),  # Vermont NGSS
    ('NY', 0, 'Grade band'),  # NY P-2
    ('CT', 0, 'Complete K-12'),  # Connecticut NGSS
]


def analyze_pdf(url, title, state):
    """
    Analyze a PDF to find grade-specific page ranges
    """
    print(f"\nAnalyzing: {state} - {title}")
    print(f"URL: {url}")

    try:
        # Download PDF
        print("  Downloading PDF...")
        response = httpx.get(url, timeout=30, follow_redirects=True)

        if response.status_code != 200:
            print(f"  [X] HTTP {response.status_code}")
            return None

        # Parse PDF
        pdf_file = io.BytesIO(response.content)
        reader = pypdf.PdfReader(pdf_file)

        total_pages = len(reader.pages)
        print(f"  [PDF] Total pages: {total_pages}")

        # Extract text from first 20 pages (likely contains TOC)
        print("  [TOC] Extracting TOC from first 20 pages...")
        toc_text = ""
        pages_to_check = min(20, total_pages)

        for i in range(pages_to_check):
            try:
                page_text = reader.pages[i].extract_text()
                toc_text += f"\n=== PAGE {i+1} ===\n{page_text}\n"
            except Exception as e:
                print(f"  [WARN] Error extracting page {i+1}: {e}")
                continue

        # Look for grade markers
        print("  [SEARCH] Searching for grade markers...")
        grade_markers = find_grade_markers(toc_text)

        if grade_markers:
            print(f"  [OK] Found {len(grade_markers)} grade markers:")
            for grade, page_num in grade_markers.items():
                print(f"    {grade}: page {page_num}")
        else:
            print("  [X] No clear grade markers found")

        # Save TOC excerpt for manual review
        excerpt = toc_text[:2000]  # First 2000 chars
        print(f"  [NOTE] TOC excerpt (first 2000 chars):")
        print("  " + "=" * 60)
        for line in excerpt.split('\n')[:30]:  # First 30 lines
            print(f"  {line}")
        print("  " + "=" * 60)

        return {
            'total_pages': total_pages,
            'grade_markers': grade_markers,
            'toc_excerpt': excerpt,
            'analysis': 'completed'
        }

    except Exception as e:
        print(f"  [X] Error: {type(e).__name__}: {str(e)[:100]}")
        return None


def find_grade_markers(text):
    """
    Search for grade markers in text and extract page numbers
    """
    markers = {}

    # Patterns to search for
    patterns = [
        # "Kindergarten ................. 12"
        (r'Kindergarten\s*[\.\s]+(\d+)', 'K'),
        # "Grade 1 ................. 26"
        (r'Grade\s+1\s*[\.\s]+(\d+)', '1'),
        (r'Grade\s+2\s*[\.\s]+(\d+)', '2'),
        (r'Grade\s+3\s*[\.\s]+(\d+)', '3'),
        (r'Grade\s+4\s*[\.\s]+(\d+)', '4'),
        (r'Grade\s+5\s*[\.\s]+(\d+)', '5'),
        (r'Grade\s+6\s*[\.\s]+(\d+)', '6'),
        (r'Grade\s+7\s*[\.\s]+(\d+)', '7'),
        (r'Grade\s+8\s*[\.\s]+(\d+)', '8'),
        # High school
        (r'Grade\s+9\s*[\.\s]+(\d+)', '9'),
        (r'Grade\s+10\s*[\.\s]+(\d+)', '10'),
        (r'Grade\s+11\s*[\.\s]+(\d+)', '11'),
        (r'Grade\s+12\s*[\.\s]+(\d+)', '12'),
        # Alternative formats
        (r'First\s+Grade\s*[\.\s]+(\d+)', '1'),
        (r'Second\s+Grade\s*[\.\s]+(\d+)', '2'),
    ]

    for pattern, grade in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            page_num = int(match.group(1))
            markers[grade] = page_num

    return markers


def main():
    """Main analysis function"""

    # Load states data
    states_file = Path(__file__).parent / "data" / "states.json"
    with open(states_file) as f:
        states_data = json.load(f)

    print("=" * 80)
    print("PDF SAMPLE ANALYSIS - Page Range Patterns")
    print("=" * 80)

    results = {}

    for state_abbr, doc_idx, category in SAMPLES:
        state_data = states_data[state_abbr]
        doc = state_data['documents'][doc_idx]

        title = doc['title']
        url = doc['url']
        grade_levels = doc['grade_levels']

        print(f"\n{'='*80}")
        print(f"STATE: {state_abbr} ({state_data['state_name']})")
        print(f"Category: {category}")
        print(f"Grade Levels: {len(grade_levels)} grades")
        print(f"{'='*80}")

        result = analyze_pdf(url, title, state_abbr)
        results[state_abbr] = {
            'title': title,
            'category': category,
            'grade_count': len(grade_levels),
            'analysis': result
        }

        # Brief pause to avoid overwhelming servers
        import time
        time.sleep(2)

    # Summary
    print("\n" + "=" * 80)
    print("ANALYSIS SUMMARY")
    print("=" * 80)

    for state, data in results.items():
        print(f"\n{state}: {data['title']}")
        print(f"  Category: {data['category']}")
        print(f"  Grades: {data['grade_count']}")
        if data['analysis']:
            print(f"  Pages: {data['analysis'].get('total_pages', 'N/A')}")
            markers = data['analysis'].get('grade_markers', {})
            if markers:
                print(f"  Grade markers found: {len(markers)}")
            else:
                print("  Grade markers: None found")
        else:
            print("  Status: Analysis failed")

    print("\n" + "=" * 80)
    print("RECOMMENDATIONS")
    print("=" * 80)
    print()
    print("Based on this analysis:")
    print("1. Documents with 1 grade level → page_range: null")
    print("2. Documents with grade markers → page_range: extract from TOC")
    print("3. Documents without clear TOC → page_range: null (manual review)")
    print()


if __name__ == "__main__":
    main()
