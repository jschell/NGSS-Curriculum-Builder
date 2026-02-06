#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.10"
# dependencies = ["pypdf>=4.0.0"]
# ///
import pypdf

pdf = pypdf.PdfReader("wy_standards.pdf")
print(f"WY: {len(pdf.pages)} pages\n")

for i in range(min(len(pdf.pages), 14)):
    print(f"{'='*60}")
    print(f"PAGE {i+1}")
    print('='*60)
    text = pdf.pages[i].extract_text()[:1000]  # First 1000 chars
    print(text)
    print()
