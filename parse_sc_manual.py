#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "pypdf>=4.0.0",
# ]
# ///

import json
import pypdf
from pathlib import Path

def find_grade_sections(pdf_path):
    """Parse SC PDF to find grade section boundaries."""

    # Load PDF
    pdf = pypdf.PdfReader(pdf_path)
    print(f"Total pages: {len(pdf.pages)}")

    # Search patterns for grades - use full grade names
    grade_patterns = {
        "K": "Kindergarten",
        "1": "First Grade",
        "2": "Second Grade",
        "3": "Third Grade",
        "4": "Fourth Grade",
        "5": "Fifth Grade",
        "6": "Sixth Grade",
        "7": "Seventh Grade",
        "8": "Eighth Grade",
    }

    # High school subjects
    hs_subjects = ["Chemistry", "Earth Science", "Physics"]

    # Find start pages for each grade by scanning page text
    grade_pages = {}
    hs_pages = {}

    for page_num, page in enumerate(pdf.pages, start=1):
        try:
            text = page.extract_text()

            # Check for elementary/middle grades
            for grade, pattern in grade_patterns.items():
                if grade not in grade_pages and pattern in text:
                    # Look for it as a heading (often centered or at start of line)
                    lines = text.split('\n')
                    for line in lines:
                        if pattern in line and len(line.strip()) < 50:  # Likely a heading
                            grade_pages[grade] = page_num
                            print(f"Found {pattern} on page {page_num}")
                            break

            # Check for high school subjects
            for subject in hs_subjects:
                if subject not in hs_pages and subject in text:
                    lines = text.split('\n')
                    for line in lines:
                        if subject in line and len(line.strip()) < 50:
                            hs_pages[subject] = page_num
                            print(f"Found {subject} on page {page_num}")
                            break

        except Exception as e:
            print(f"Warning: Could not parse page {page_num}: {e}")
            continue

    # Build grade sections with page ranges
    grade_sections = {}
    sorted_grades = sorted(grade_pages.items(), key=lambda x: x[1])

    for i, (grade, start_page) in enumerate(sorted_grades):
        # End page is start of next grade minus 1
        if i < len(sorted_grades) - 1:
            end_page = sorted_grades[i + 1][1] - 1
        else:
            # Last elementary grade ends before first HS subject
            if hs_pages:
                end_page = min(hs_pages.values()) - 1
            else:
                end_page = start_page + 10  # Estimate

        grade_sections[grade] = {
            "page_ranges": [[start_page, end_page]],
            "section_ids": [],
            "confidence": "high",
            "notes": f"Extracted from TOC and text search for '{grade_patterns[grade]}'",
            "needs_review": False
        }

    # Build high school section (9-12) with subjects
    if hs_pages:
        sorted_hs = sorted(hs_pages.items(), key=lambda x: x[1])
        hs_ranges = []
        hs_subjects_found = []

        for i, (subject, start_page) in enumerate(sorted_hs):
            if i < len(sorted_hs) - 1:
                end_page = sorted_hs[i + 1][1] - 1
            else:
                # Last subject - estimate end (look for References section)
                end_page = start_page + 20  # Conservative estimate

            hs_ranges.append([start_page, end_page])
            hs_subjects_found.append(subject)

        grade_sections["9-12"] = {
            "page_ranges": hs_ranges,
            "section_ids": hs_subjects_found,
            "confidence": "high",
            "notes": f"High school organized by subject: {', '.join(hs_subjects_found)}. Biology courses available as separate documents.",
            "needs_review": False
        }

    return grade_sections

if __name__ == "__main__":
    pdf_path = "sc_2021_standards.pdf"

    if not Path(pdf_path).exists():
        print(f"Error: {pdf_path} not found")
        exit(1)

    print(f"Parsing {pdf_path}...")
    print()

    grade_sections = find_grade_sections(pdf_path)

    # Create patch file
    patch = {
        "SC": {
            "documents": [
                {
                    "title": "South Carolina College- and Career-Ready Science Standards 2021",
                    "grade_sections": grade_sections
                }
            ]
        }
    }

    # Save patch
    output_path = Path("patches/sc_manual_grades.json")
    output_path.parent.mkdir(exist_ok=True)

    with open(output_path, 'w') as f:
        json.dump(patch, f, indent=2)

    print()
    print(f"✓ Grade sections saved to {output_path}")
    print(f"  Found {len(grade_sections)} grade levels")
    print(f"  Grades: {', '.join(sorted(grade_sections.keys()))}")
