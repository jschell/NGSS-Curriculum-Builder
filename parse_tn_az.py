#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.10"
# dependencies = ["pypdf>=4.0.0"]
# ///

import json
import pypdf
from pathlib import Path

def find_grade_sections(pdf_path, state_abbr, title):
    """Parse PDF to find grade section boundaries."""

    pdf = pypdf.PdfReader(pdf_path)
    print(f"\n{state_abbr}: {len(pdf.pages)} pages")

    # Multiple search patterns for grades
    grade_patterns = {
        "K": ["Kindergarten", "Grade K", "KINDERGARTEN"],
        "1": ["First Grade", "Grade 1", "1st Grade", "GRADE 1", "FIRST GRADE"],
        "2": ["Second Grade", "Grade 2", "2nd Grade", "GRADE 2", "SECOND GRADE"],
        "3": ["Third Grade", "Grade 3", "3rd Grade", "GRADE 3", "THIRD GRADE"],
        "4": ["Fourth Grade", "Grade 4", "4th Grade", "GRADE 4", "FOURTH GRADE"],
        "5": ["Fifth Grade", "Grade 5", "5th Grade", "GRADE 5", "FIFTH GRADE"],
        "6": ["Sixth Grade", "Grade 6", "6th Grade", "GRADE 6", "SIXTH GRADE"],
        "7": ["Seventh Grade", "Grade 7", "7th Grade", "GRADE 7", "SEVENTH GRADE"],
        "8": ["Eighth Grade", "Grade 8", "8th Grade", "GRADE 8", "EIGHTH GRADE"],
    }

    # High school patterns
    hs_subjects = ["High School", "Biology", "Chemistry", "Earth Science", "Physics",
                   "Grades 9-12", "GRADE 9", "GRADE 10", "GRADE 11", "GRADE 12"]

    # Track found grades
    grade_pages = {}
    hs_pages = {}

    for page_num, page in enumerate(pdf.pages, start=1):
        try:
            text = page.extract_text()
            if not text:
                continue

            # Check each grade
            for grade, patterns in grade_patterns.items():
                if grade in grade_pages:
                    continue

                for pattern in patterns:
                    if pattern in text:
                        # Verify it's a heading (check first 20 lines)
                        lines = text.split('\n')
                        for line in lines[:20]:
                            if pattern in line and len(line.strip()) < 100:
                                grade_pages[grade] = page_num
                                print(f"  {pattern}: page {page_num}")
                                break
                        if grade in grade_pages:
                            break

            # Check high school subjects
            for subject in hs_subjects:
                if subject not in hs_pages and subject in text:
                    lines = text.split('\n')
                    for line in lines[:20]:
                        if subject in line and len(line.strip()) < 100:
                            hs_pages[subject] = page_num
                            print(f"  {subject}: page {page_num}")
                            break

        except Exception:
            continue

    # Build grade sections
    grade_sections = {}

    # Sort K-8 grades
    sorted_grades = sorted(grade_pages.items(), key=lambda x: (x[1], x[0]))

    for i, (grade, start_page) in enumerate(sorted_grades):
        # Calculate end page
        if i < len(sorted_grades) - 1:
            end_page = sorted_grades[i + 1][1] - 1
        else:
            # Last K-8 grade: ends before HS or estimate
            if hs_pages:
                end_page = min(hs_pages.values()) - 1
            else:
                end_page = min(start_page + 10, len(pdf.pages))

        # Validate range
        if end_page >= start_page:
            grade_sections[grade] = {
                "page_ranges": [[start_page, end_page]],
                "section_ids": [],
                "confidence": "high",
                "notes": "Extracted via text search",
                "needs_review": False
            }

    # Build high school section
    if hs_pages:
        sorted_hs = sorted(hs_pages.items(), key=lambda x: x[1])
        hs_ranges = []
        hs_subjects_found = []

        for i, (subject, start_page) in enumerate(sorted_hs):
            if i < len(sorted_hs) - 1:
                end_page = sorted_hs[i + 1][1] - 1
            else:
                end_page = min(start_page + 30, len(pdf.pages))

            if end_page >= start_page:
                hs_ranges.append([start_page, end_page])
                hs_subjects_found.append(subject)

        if hs_ranges:
            grade_sections["9-12"] = {
                "page_ranges": hs_ranges,
                "section_ids": hs_subjects_found,
                "confidence": "high",
                "notes": f"High school: {', '.join(hs_subjects_found)}",
                "needs_review": False
            }

    return grade_sections

def main():
    states = [
        ("tn_standards.pdf", "TN", "Tennessee Academic Standards for Science"),
        ("az_standards.pdf", "AZ", "Arizona Science Standards 2018"),
    ]

    all_patches = {}

    for pdf_file, state_abbrev, title in states:
        if not Path(pdf_file).exists():
            print(f"[SKIP] {pdf_file} not found")
            continue

        print(f"\n{'='*60}")
        print(f"Parsing {state_abbrev}")
        print('='*60)

        grade_sections = find_grade_sections(pdf_file, state_abbrev, title)

        if grade_sections:
            all_patches[state_abbrev] = {
                "documents": [{
                    "title": title,
                    "grade_sections": grade_sections
                }]
            }
            print(f"\n[OK] {state_abbrev}: {len(grade_sections)} grade sections")
        else:
            print(f"\n[SKIP] {state_abbrev}: No sections found")

    # Save patch
    if all_patches:
        output = Path("patches/tn_az_grades.json")
        with open(output, 'w') as f:
            json.dump(all_patches, f, indent=2)
        print(f"\n{'='*60}")
        print(f"Saved: {output}")
        print(f"States: {', '.join(all_patches.keys())}")
        print('='*60)

if __name__ == "__main__":
    main()
