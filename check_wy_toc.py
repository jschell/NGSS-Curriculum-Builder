#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.10"
# dependencies = ["pypdf>=4.0.0"]
# ///

import pypdf

pdf = pypdf.PdfReader("wy_standards_2021.pdf")
print(f"Total pages: {len(pdf.pages)}\n")
print("="*60)
print("PAGE 6 - Table of Contents")
print("="*60)
print(pdf.pages[5].extract_text())  # Page 6 is index 5
