#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.10"
# dependencies = ["pypdf>=4.0.0"]
# ///

import json
from pathlib import Path

# Wyoming structure from TOC (page 6)
# K-5: Individual grades
# MS (6-8): By subject (Physical, Life, Earth/Space, Engineering)
# HS (9-12): By subject (Physical, Life, Earth/Space, Engineering)

wy_structure = {
    "WY": {
        "documents": [{
            "title": "2021 Wyoming Science Standards",
            "grade_sections": {
                "K": {
                    "page_ranges": [[8, 11]],
                    "section_ids": [],
                    "confidence": "high",
                    "notes": "From TOC page 6",
                    "needs_review": False
                },
                "1": {
                    "page_ranges": [[12, 15]],
                    "section_ids": [],
                    "confidence": "high",
                    "notes": "From TOC page 6",
                    "needs_review": False
                },
                "2": {
                    "page_ranges": [[16, 19]],
                    "section_ids": [],
                    "confidence": "high",
                    "notes": "From TOC page 6",
                    "needs_review": False
                },
                "3": {
                    "page_ranges": [[20, 24]],
                    "section_ids": [],
                    "confidence": "high",
                    "notes": "From TOC page 6",
                    "needs_review": False
                },
                "4": {
                    "page_ranges": [[25, 29]],
                    "section_ids": [],
                    "confidence": "high",
                    "notes": "From TOC page 6",
                    "needs_review": False
                },
                "5": {
                    "page_ranges": [[30, 34]],
                    "section_ids": [],
                    "confidence": "high",
                    "notes": "From TOC page 6",
                    "needs_review": False
                },
                "6-8": {
                    "page_ranges": [[35, 49]],
                    "section_ids": ["Physical Science", "Life Science", "Earth and Space Science", "Engineering"],
                    "confidence": "high",
                    "notes": "Middle School organized by subject domain (pages 35-49)",
                    "needs_review": False
                },
                "9-12": {
                    "page_ranges": [[51, 68]],
                    "section_ids": ["Physical Science", "Life Science", "Earth and Space Science", "Engineering"],
                    "confidence": "high",
                    "notes": "High School organized by subject domain (pages 51-68)",
                    "needs_review": False
                }
            }
        }]
    }
}

# Save patch
output = Path("patches/wy_from_toc.json")
with open(output, 'w') as f:
    json.dump(wy_structure, f, indent=2)

print("Wyoming extraction from TOC:")
print(f"  K-5: Individual grades (pages 8-34)")
print(f"  6-8: Middle School by subject (pages 35-49)")
print(f"  9-12: High School by subject (pages 51-68)")
print(f"\nTotal: 8 grade entries (K-5 + 6-8 + 9-12)")
print(f"Saved to: {output}")
