#!/usr/bin/env python3
"""
Quick test of PDF parsing functionality
"""

from pathlib import Path
from pypdf import PdfReader
import pdfplumber
import re

GRADE_PATTERNS = {
    "K": [re.compile(r"\bKindergarten\b", re.IGNORECASE)],
    "1": [re.compile(r"\bGrade\s+1\b", re.IGNORECASE)],
    "2": [re.compile(r"\bGrade\s+2\b", re.IGNORECASE)],
    "3": [re.compile(r"\bGrade\s+3\b", re.IGNORECASE)],
    "4": [re.compile(r"\bGrade\s+4\b", re.IGNORECASE)],
    "5": [re.compile(r"\bGrade\s+5\b", re.IGNORECASE)],
}


def extract_text_with_plumber(pdf_path: Path):
    try:
        pages_text = []
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                text = page.extract_text() or ""
                pages_text.append(text)
        return pages_text
    except Exception as e:
        print(f"pdfplumber error: {e}")
        return []


def detect_organization(pages_text):
    grade_pattern = re.compile(
        r"\b(Kindergarten|Grade\s+\d+|\d+(st|nd|rd|th)\s+Grade)\b", re.IGNORECASE
    )
    topic_pattern = re.compile(
        r"\b(Physical\s+Science|Life\s+Science|Earth\s+Science|Engineering)\b",
        re.IGNORECASE,
    )

    grade_matches = sum(len(grade_pattern.findall(page)) for page in pages_text)
    topic_matches = sum(len(topic_pattern.findall(page)) for page in pages_text)

    if grade_matches >= topic_matches * 1.5:
        return "by_grade"
    elif topic_matches >= grade_matches * 1.5:
        return "by_topic"
    return "ambiguous"


def extract_grade_sections_by_grade(pages_text):
    all_grades = ["K", "1", "2", "3", "4", "5"]
    sections = {}
    current_grade = None
    page_start = 0

    for i, page_text in enumerate(pages_text):
        detected_grade = None
        for grade in all_grades:
            if grade in GRADE_PATTERNS:
                for pattern in GRADE_PATTERNS[grade]:
                    if pattern.search(page_text):
                        detected_grade = grade
                        break
            if detected_grade:
                break

        if detected_grade:
            if current_grade:
                if current_grade not in sections:
                    sections[current_grade] = {"page_ranges": [], "confidence": "high"}
                sections[current_grade]["page_ranges"].append((page_start, i))
            current_grade = detected_grade
            if current_grade not in sections:
                sections[current_grade] = {"page_ranges": [], "confidence": "high"}
            page_start = i

    if current_grade:
        sections[current_grade]["page_ranges"].append((page_start, len(pages_text)))

    return sections


pdf_path = Path("cached/or_k12_test.pdf")
print(f"Parsing: {pdf_path}")
print(f"File size: {pdf_path.stat().st_size / 1024:.1f} KB\n")

pages_text = extract_text_with_plumber(pdf_path)
print(f"Extracted {len(pages_text)} pages")

org = detect_organization(pages_text)
print(f"\nDetected organization: {org}")

if org == "by_grade":
    sections = extract_grade_sections_by_grade(pages_text)
else:
    sections = {}

print(f"\nFound {len(sections)} grades with sections:")
for grade, section in sorted(sections.items()):
    page_ranges = ", ".join(f"{r[0] + 1}-{r[1]}" for r in section["page_ranges"])
    print(f"  Grade {grade}: pages {page_ranges} (confidence: {section['confidence']})")
