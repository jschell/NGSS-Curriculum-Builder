# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "pypdf>=5.0.0",
#     "httpx>=0.26.0",
# ]
# ///

"""
Extract page ranges for remaining states using browser-like HTTP headers.
Targets states with accessible PDFs that failed due to missing User-Agent.
"""

import httpx
import json
import re
import sys
from pathlib import Path
from pypdf import PdfReader
import io

DATA_FILE = Path(__file__).parent.parent.parent / "data" / "states.json"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,application/pdf,*/*;q=0.8",
}

# Grade name patterns for extraction
GRADE_PATTERNS = [
    (r'kindergarten\s+standards?\s*[.\-]+\s*(\d+)', 'K'),
    (r'grade\s+1\s+standards?\s*[.\-]+\s*(\d+)', '1'),
    (r'grade\s+2\s+standards?\s*[.\-]+\s*(\d+)', '2'),
    (r'grade\s+3\s+standards?\s*[.\-]+\s*(\d+)', '3'),
    (r'grade\s+4\s+standards?\s*[.\-]+\s*(\d+)', '4'),
    (r'grade\s+5\s+standards?\s*[.\-]+\s*(\d+)', '5'),
    (r'grade\s+6\s+standards?\s*[.\-]+\s*(\d+)', '6'),
    (r'grade\s+7\s+standards?\s*[.\-]+\s*(\d+)', '7'),
    (r'grade\s+8\s+standards?\s*[.\-]+\s*(\d+)', '8'),
    (r'(?:high\s+school|grades?\s+9[\s\-]+12|9th|hs)\s+.*?[.\-]+\s*(\d+)', '9-12'),
]

# States organized by subject for high school (note special structure)
HS_SUBJECT_PATTERNS = [
    (r'(?:hs\s+)?physical\s+science\s+standards?\s*[.\-]+\s*(\d+)', 'HS-PS'),
    (r'(?:hs\s+)?life\s+science\s+standards?\s*[.\-]+\s*(\d+)', 'HS-LS'),
    (r'(?:hs\s+)?earth\s+(?:and\s+space\s+science|science)\s+standards?\s*[.\-]+\s*(\d+)', 'HS-ESS'),
]


def find_toc_page(pdf: PdfReader) -> tuple[int, str]:
    """Find the table of contents page."""
    for i, page in enumerate(pdf.pages[:10]):
        text = page.extract_text() or ""
        if ("table of contents" in text.lower() or
                ("kindergarten" in text.lower() and re.search(r'\d+\s*$', text, re.MULTILINE))):
            return i, text
    return -1, ""


def extract_from_toc(toc_text: str) -> dict:
    """Extract grade → start page from TOC text."""
    result = {}
    text_lower = toc_text.lower()

    for pattern, grade in GRADE_PATTERNS:
        match = re.search(pattern, text_lower)
        if match:
            result[grade] = int(match.group(1))

    # Try HS subject patterns if no 9-12 found
    if '9-12' not in result:
        for pattern, key in HS_SUBJECT_PATTERNS:
            match = re.search(pattern, text_lower)
            if match:
                result[key] = int(match.group(1))

    return result


def build_page_ranges(start_pages: dict, total_pages: int) -> dict:
    """Convert start pages dict to page range strings."""
    if not start_pages:
        return {}

    # Sort by page number
    sorted_items = sorted(start_pages.items(), key=lambda x: x[1])
    result = {}

    for i, (grade, start) in enumerate(sorted_items):
        if i + 1 < len(sorted_items):
            next_start = sorted_items[i + 1][1]
            end = next_start - 1
        else:
            # Last section — estimate end or use total
            end = min(start + 20, total_pages)

        result[grade] = f"{start}-{end}"

    return result


def parse_pdf_url(state_abbr: str, url: str) -> dict | None:
    """Download and parse a PDF to extract grade page ranges."""
    print(f"  Downloading {url[:70]}...")
    try:
        with httpx.Client(headers=HEADERS, timeout=30, follow_redirects=True) as client:
            response = client.get(url)
            response.raise_for_status()

            if "pdf" not in response.headers.get("content-type", "").lower():
                print(f"  Not a PDF: {response.headers.get('content-type')}")
                return None

            pdf_bytes = response.content
            print(f"  Downloaded {len(pdf_bytes):,} bytes")

        pdf = PdfReader(io.BytesIO(pdf_bytes))
        total_pages = len(pdf.pages)
        print(f"  Total pages: {total_pages}")

        # Find TOC page
        toc_idx, toc_text = find_toc_page(pdf)
        if toc_idx >= 0:
            print(f"  TOC found on page {toc_idx + 1}")
            start_pages = extract_from_toc(toc_text)
        else:
            print(f"  No TOC found, scanning all pages...")
            # Scan all pages for grade markers
            all_text = ""
            for page in pdf.pages[:15]:
                all_text += (page.extract_text() or "") + "\n"
            start_pages = extract_from_toc(all_text)

        if not start_pages:
            print(f"  No grade sections found")
            return None

        print(f"  Found grade starts: {start_pages}")
        page_ranges = build_page_ranges(start_pages, total_pages)
        print(f"  Page ranges: {page_ranges}")
        return page_ranges

    except Exception as e:
        print(f"  ERROR: {e}")
        return None


def apply_page_ranges(state_abbr: str, doc_index: int, page_ranges: dict):
    """Apply extracted page ranges to states.json."""
    data = json.loads(DATA_FILE.read_text(encoding="utf-8"))

    if state_abbr not in data:
        print(f"  State {state_abbr} not found in data")
        return

    docs = data[state_abbr].get("documents", [])
    if doc_index >= len(docs):
        print(f"  Document index {doc_index} out of range")
        return

    docs[doc_index]["page_range"] = page_ranges
    DATA_FILE.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"  Applied page ranges to {state_abbr} document {doc_index}")


def main():
    data = json.loads(DATA_FILE.read_text(encoding="utf-8"))

    # States with confirmed PDF access
    pdf_states = {
        "DC": 0,
        "DE": 0,
        "IN": 0,
        "MD": 0,
        "MN": 0,
        "NE": 0,
    }

    if len(sys.argv) > 1:
        states_arg = sys.argv[1].upper().split(",")
        pdf_states = {s: 0 for s in states_arg if s in pdf_states or s in data}

    results = {}

    for abbr, doc_idx in pdf_states.items():
        if abbr not in data:
            print(f"\n{abbr}: Not in data")
            continue

        state = data[abbr]
        docs = state.get("documents", [])
        if not docs or doc_idx >= len(docs):
            print(f"\n{abbr}: No documents")
            continue

        doc = docs[doc_idx]
        url = doc.get("url", "")
        if not url:
            print(f"\n{abbr}: No URL")
            continue

        print(f"\n{'='*60}")
        print(f"{abbr}: {state.get('state_name', abbr)}")
        print(f"Doc: {doc.get('title', '?')[:60]}")

        page_ranges = parse_pdf_url(abbr, url)
        if page_ranges:
            apply_page_ranges(abbr, doc_idx, page_ranges)
            results[abbr] = "SUCCESS"
        else:
            results[abbr] = "FAILED"

    print(f"\n{'='*60}")
    print("RESULTS:")
    for abbr, status in results.items():
        print(f"  {abbr}: {status}")


if __name__ == "__main__":
    main()
