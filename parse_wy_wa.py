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
import sys

def find_grade_sections(pdf_path, state_abbr):
    """Parse PDF to find grade section boundaries."""

    pdf = pypdf.PdfReader(pdf_path)
    print(f"\n{state_abbr} PDF: {len(pdf.pages)} pages")

    # Search patterns - try multiple variations
    grade_patterns = {
        "K": ["Kindergarten", "Grade K", "K "],
        "1": ["First Grade", "Grade 1", "1st Grade"],
        "2": ["Second Grade", "Grade 2", "2nd Grade"],
        "3": ["Third Grade", "Grade 3", "3rd Grade"],
        "4": ["Fourth Grade", "Grade 4", "4th Grade"],
        "5": ["Fifth Grade", "Grade 5", "5th Grade"],
        "6": ["Sixth Grade", "Grade 6", "6th Grade"],
        "7": ["Seventh Grade", "Grade 7", "7th Grade"],
        "8": ["Eighth Grade", "Grade 8", "8th Grade"],
    }

    # High school subjects
    hs_subjects = ["Chemistry", "Earth Science", "Physics", "Biology", "High School"]

    # Find start pages for each grade
    grade_pages = {}
    hs_pages = {}

    for page_num, page in enumerate(pdf.pages, start=1):
        try:
            text = page.extract_text()
            if not text:
                continue

            # Check for elementary/middle grades
            for grade, patterns in grade_patterns.items():
                if grade in grade_pages:
                    continue

                for pattern in patterns:
                    if pattern in text:
                        # Look for it as a heading
                        lines = text.split('\n')
                        for line in lines:
                            if pattern in line and len(line.strip()) < 100:
                                grade_pages[grade] = page_num
                                print(f"  Found {pattern} on page {page_num}")
                                break
                        if grade in grade_pages:
                            break

            # Check for high school subjects
            for subject in hs_subjects:
                if subject not in hs_pages and subject in text:
                    lines = text.split('\n')
                    for line in lines:
                        if subject in line and len(line.strip()) < 100:
                            hs_pages[subject] = page_num
                            print(f"  Found {subject} on page {page_num}")
                            break

        except Exception as e:
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
            "notes": f"Extracted via text search",
            "needs_review": False
        }

    # Build high school section if found
    if hs_pages:
        sorted_hs = sorted(hs_pages.items(), key=lambda x: x[1])
        hs_ranges = []
        hs_subjects_found = []

        for i, (subject, start_page) in enumerate(sorted_hs):
            if i < len(sorted_hs) - 1:
                end_page = sorted_hs[i + 1][1] - 1
            else:
                end_page = min(start_page + 30, len(pdf.pages))

            hs_ranges.append([start_page, end_page])
            hs_subjects_found.append(subject)

        grade_sections["9-12"] = {
            "page_ranges": hs_ranges,
            "section_ids": hs_subjects_found,
            "confidence": "high" if len(hs_subjects_found) > 0 else "medium",
            "notes": f"High school section: {', '.join(hs_subjects_found)}",
            "needs_review": False
        }

    return grade_sections

def main():
    states_to_parse = [
        ("wy_standards.pdf", "WY", "2023 Wyoming Content and Performance Standards for Science"),
        ("wa_standards.pdf", "WA", "Washington State K-12 Science Learning Standards"),
    ]

    all_patches = {}

    for pdf_file, state_abbr, title in states_to_parse:
        pdf_path = Path(pdf_file)
        if not pdf_path.exists():
            print(f"[!] {pdf_file} not found, skipping {state_abbr}")
            continue

        print(f"\n{'='*60}")
        print(f"Parsing {state_abbr}")
        print('='*60)

        grade_sections = find_grade_sections(pdf_path, state_abbr)

        if grade_sections:
            all_patches[state_abbr] = {
                "documents": [
                    {
                        "title": title,
                        "grade_sections": grade_sections
                    }
                ]
            }
            print(f"\n  [OK] {state_abbr}: Found {len(grade_sections)} grade sections")
        else:
            print(f"\n  [SKIP] {state_abbr}: No grade sections found")

    if all_patches:
        # Save combined patch
        output_path = Path("patches/wy_wa_grades.json")
        with open(output_path, 'w') as f:
            json.dump(all_patches, f, indent=2)

        print(f"\n{'='*60}")
        print(f"Saved to {output_path}")
        print(f"States: {', '.join(all_patches.keys())}")
        print('='*60)

if __name__ == "__main__":
    main()
