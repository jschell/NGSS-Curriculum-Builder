# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "pypdf>=5.0.0",
#     "pikepdf>=8.0.0",
#     "pdfplumber>=0.10.3",
#     "beautifulsoup4>=4.12.2",
#     "lxml>=4.9.3",
#     "httpx>=0.26.0",
#     "aiofiles>=23.2.0",
#     "pydantic>=2.5.0",
#     "orjson>=3.9.0",
# ]
# ///

"""
Standards Document Parser
Extracts grade-level section information from PDF, HTML, and interactive standards documents.
Uses async HTTP for fast concurrent fetching and modern parsing libraries.
"""

import asyncio
import httpx
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from pypdf import PdfReader
import pikepdf
import pdfplumber
from bs4 import BeautifulSoup
import re
import hashlib
import orjson
from dataclasses import dataclass, field
import sys
import os

# Optional content cache (stdlib-only, graceful fallback if unavailable)
try:
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from document_cache import get_cached, write_cache
    _CACHE_AVAILABLE = True
except Exception:  # noqa: BLE001
    _CACHE_AVAILABLE = False

# =============================================================================
# PYDANTIC MODELS
# =============================================================================


@dataclass
class GradeSection:
    """Maps a grade to specific location(s) within a document"""

    page_ranges: List[Tuple[int, int]] = field(default_factory=list)
    section_ids: List[str] = field(default_factory=list)
    confidence: str = "high"
    notes: Optional[str] = None
    needs_review: bool = False


@dataclass
class DocumentParseResult:
    """Result of parsing a single document"""

    document_title: str
    url: str
    format_type: str
    organization: str
    grade_sections: Dict[str, GradeSection]
    parse_errors: List[str] = field(default_factory=list)
    from_cache: bool = False


# =============================================================================
# HTTP CLIENT (Async)
# =============================================================================


async def get_async_client() -> httpx.AsyncClient:
    """Get or create async HTTP client"""
    if not hasattr(get_async_client, "_client"):
        get_async_client._client = httpx.AsyncClient(
            timeout=30.0,
            limits=httpx.Limits(max_connections=10),
            follow_redirects=True,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            },
        )
    return get_async_client._client


async def fetch_document(url: str, output_path: Path) -> bool:
    """Fetch PDF/HTML from URL and save to disk"""
    client = await get_async_client()
    try:
        response = await client.get(url)
        response.raise_for_status()
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_bytes(response.content)
        return True
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return False


# =============================================================================
# GRADE DETECTION PATTERNS
# =============================================================================

GRADE_PATTERNS = {
    "K": [
        re.compile(r"\bKindergarten\b", re.IGNORECASE),
        re.compile(r"\bK\b(?![a-z])", re.IGNORECASE),
    ],
    "1": [
        re.compile(r"\bGrade\s+1\b", re.IGNORECASE),
        re.compile(r"\b1st\s+Grade\b", re.IGNORECASE),
    ],
    "2": [
        re.compile(r"\bGrade\s+2\b", re.IGNORECASE),
        re.compile(r"\b2nd\s+Grade\b", re.IGNORECASE),
    ],
    "3": [
        re.compile(r"\bGrade\s+3\b", re.IGNORECASE),
        re.compile(r"\b3rd\s+Grade\b", re.IGNORECASE),
    ],
    "4": [
        re.compile(r"\bGrade\s+4\b", re.IGNORECASE),
        re.compile(r"\b4th\s+Grade\b", re.IGNORECASE),
    ],
    "5": [
        re.compile(r"\bGrade\s+5\b", re.IGNORECASE),
        re.compile(r"\b5th\s+Grade\b", re.IGNORECASE),
    ],
    "6": [
        re.compile(r"\bGrade\s+6\b", re.IGNORECASE),
        re.compile(r"\b6th\s+Grade\b", re.IGNORECASE),
    ],
    "7": [
        re.compile(r"\bGrade\s+7\b", re.IGNORECASE),
        re.compile(r"\b7th\s+Grade\b", re.IGNORECASE),
    ],
    "8": [
        re.compile(r"\bGrade\s+8\b", re.IGNORECASE),
        re.compile(r"\b8th\s+Grade\b", re.IGNORECASE),
    ],
    "9": [
        re.compile(r"\bGrade\s+9\b", re.IGNORECASE),
        re.compile(r"\b9th\s+Grade\b", re.IGNORECASE),
    ],
    "10": [
        re.compile(r"\bGrade\s+10\b", re.IGNORECASE),
        re.compile(r"\b10th\s+Grade\b", re.IGNORECASE),
    ],
    "11": [
        re.compile(r"\bGrade\s+11\b", re.IGNORECASE),
        re.compile(r"\b11th\s+Grade\b", re.IGNORECASE),
    ],
    "12": [
        re.compile(r"\bGrade\s+12\b", re.IGNORECASE),
        re.compile(r"\b12th\s+Grade\b", re.IGNORECASE),
    ],
}

TOPIC_PATTERNS = [
    re.compile(r"\bPhysical\s+Science\b", re.IGNORECASE),
    re.compile(r"\bLife\s+Science\b", re.IGNORECASE),
    re.compile(r"\bEarth\s+and\s+Space\s+Science\b", re.IGNORECASE),
    re.compile(r"\bEngineering\s+Design\b", re.IGNORECASE),
]


# =============================================================================
# PDF PARSING
# =============================================================================


def extract_text_with_pypdf(pdf_path: Path) -> List[str]:
    """Extract text page-by-page using pypdf"""
    try:
        reader = PdfReader(str(pdf_path))
        pages_text = []
        for page in reader.pages:
            text = page.extract_text() or ""
            pages_text.append(text)
        return pages_text
    except Exception as e:
        print(f"pypdf error: {e}")
        return []


def extract_text_with_plumber(pdf_path: Path) -> List[str]:
    """Extract text page-by-page using pdfplumber (better for complex layouts)"""
    try:
        pages_text = []
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                text = page.extract_text() or ""
                pages_text.append(text)
        return pages_text
    except Exception as e:
        print(f"pdfplumber error: {e}")
        return extract_text_with_pypdf(pdf_path)


def get_pdf_metadata(pdf_path: Path) -> Dict:
    """Get PDF metadata using pikepdf"""
    try:
        with pikepdf.open(pdf_path) as pdf:
            return {
                "pages": len(pdf.pages),
                "is_linearized": pdf.is_linearized,
                "metadata": dict(pdf.docinfo) if pdf.docinfo else {},
            }
    except Exception as e:
        print(f"pikepdf error: {e}")
        return {"pages": 0}


# =============================================================================
# ORGANIZATION DETECTION
# =============================================================================


def detect_organization(pages_text: List[str]) -> str:
    """Detect if PDF is organized by grade or by topic"""

    grade_pattern = re.compile(
        r"\b(Kindergarten|Grade\s+\d+|\d+(st|nd|rd|th)\s+Grade)\b", re.IGNORECASE
    )
    topic_pattern = re.compile(
        r"\b(Physical\s+Science|Life\s+Science|Earth\s+Science|Engineering)\b",
        re.IGNORECASE,
    )

    grade_matches = sum(len(grade_pattern.findall(page)) for page in pages_text)
    topic_matches = sum(len(topic_pattern.findall(page)) for page in pages_text)

    if grade_matches == 0 and topic_matches == 0:
        return "ambiguous"
    elif grade_matches >= topic_matches * 1.5:
        return "by_grade"
    elif topic_matches >= grade_matches * 1.5:
        return "by_topic"
    else:
        return "ambiguous"


# =============================================================================
# GRADE SECTION EXTRACTION
# =============================================================================


def extract_grade_sections_by_grade(pages_text: List[str]) -> Dict[str, GradeSection]:
    """Extract sections when PDF is organized by grade"""

    all_grades = ["K", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12"]
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
                    sections[current_grade] = GradeSection(confidence="high")
                sections[current_grade].page_ranges.append((page_start, i))

            current_grade = detected_grade
            if current_grade not in sections:
                sections[current_grade] = GradeSection(confidence="high")
            page_start = i

    if current_grade:
        sections[current_grade].page_ranges.append((page_start, len(pages_text)))

    return sections


def extract_grade_sections_by_topic(pages_text: List[str]) -> Dict[str, GradeSection]:
    """Extract sections when PDF is organized by topic - more complex"""

    sections = {}

    for i, page_text in enumerate(pages_text):
        for grade in [
            "K",
            "1",
            "2",
            "3",
            "4",
            "5",
            "6",
            "7",
            "8",
            "9",
            "10",
            "11",
            "12",
        ]:
            if grade in GRADE_PATTERNS:
                for pattern in GRADE_PATTERNS[grade]:
                    if pattern.search(page_text):
                        if grade not in sections:
                            sections[grade] = GradeSection(
                                confidence="medium", needs_review=True
                            )

                        if sections[grade].page_ranges:
                            last_start, last_end = sections[grade].page_ranges[-1]
                            if i == last_end:
                                sections[grade].page_ranges[-1] = (last_start, i + 1)
                            else:
                                sections[grade].page_ranges.append((i, i + 1))
                        else:
                            sections[grade].page_ranges.append((i, i + 1))

    return sections


# =============================================================================
# CACHE HELPERS
# =============================================================================


def _grade_sections_to_dict(grade_sections: Dict[str, GradeSection]) -> dict:
    """Serialize GradeSection dataclasses to plain dicts for JSON caching."""
    return {
        grade: {
            "page_ranges": section.page_ranges,
            "section_ids": section.section_ids,
            "confidence": section.confidence,
            "notes": section.notes,
            "needs_review": section.needs_review,
        }
        for grade, section in grade_sections.items()
    }


def _grade_sections_from_dict(raw: dict) -> Dict[str, GradeSection]:
    """Deserialize plain dicts from cache back into GradeSection dataclasses."""
    return {
        grade: GradeSection(
            page_ranges=[tuple(r) for r in data.get("page_ranges", [])],
            section_ids=data.get("section_ids", []),
            confidence=data.get("confidence", "high"),
            notes=data.get("notes"),
            needs_review=data.get("needs_review", False),
        )
        for grade, data in raw.items()
    }


# =============================================================================
# MAIN PARSING FUNCTION
# =============================================================================


async def parse_document(document: Dict, cache_dir: Path) -> DocumentParseResult:
    """Parse a single document and extract grade sections"""

    url = document["url"]
    title = document["title"]
    format_type = document.get("format", "PDF")

    # --- Content cache lookup (skip network fetch entirely on hit) ---
    if _CACHE_AVAILABLE:
        cached = get_cached(url)
        if cached is not None:
            return DocumentParseResult(
                document_title=title,
                url=url,
                format_type=format_type,
                organization="cached",
                grade_sections=_grade_sections_from_dict(cached.get("grade_sections", {})),
                parse_errors=cached.get("parse_errors", []),
                from_cache=True,
            )

    url_hash = hashlib.md5(url.encode()).hexdigest()[:8]
    file_path = cache_dir / f"{url_hash}.{'pdf' if format_type == 'PDF' else 'html'}"

    if not file_path.exists():
        success = await fetch_document(url, file_path)
        if not success:
            return DocumentParseResult(
                document_title=title,
                url=url,
                format_type=format_type,
                organization="error",
                grade_sections={},
                parse_errors=[f"Failed to fetch document"],
            )

    if format_type == "PDF":
        pages_text = extract_text_with_plumber(file_path)
        organization = detect_organization(pages_text)

        if organization == "by_grade":
            grade_sections = extract_grade_sections_by_grade(pages_text)
        elif organization == "by_topic":
            grade_sections = extract_grade_sections_by_topic(pages_text)
        else:
            grade_sections = extract_grade_sections_by_grade(pages_text)
            if not grade_sections:
                grade_sections = extract_grade_sections_by_topic(pages_text)

        if not pages_text:
            organization = "error"
    else:
        organization = "unsupported"
        grade_sections = {}

    result = DocumentParseResult(
        document_title=title,
        url=url,
        format_type=format_type,
        organization=organization,
        grade_sections=grade_sections,
    )

    # --- Write to content cache (only on successful parse with results) ---
    if _CACHE_AVAILABLE and grade_sections and organization not in ("error", "unsupported"):
        try:
            state_abbrev = document.get("state_abbrev", "")
            write_cache(
                url=url,
                result={
                    "grade_sections": _grade_sections_to_dict(grade_sections),
                    "parse_errors": result.parse_errors,
                },
                document_title=title,
                state_abbrev=state_abbrev,
                format_type=format_type,
            )
        except Exception:  # noqa: BLE001
            pass  # Cache write failure is non-fatal

    return result


# =============================================================================
# BATCH PROCESSING
# =============================================================================


async def parse_all_states(
    states_data: Dict,
    cache_dir: Path = Path("./cached"),
    state_filter: Optional[List[str]] = None,
) -> Dict[str, Dict[str, DocumentParseResult]]:
    """Parse documents for multiple states concurrently"""

    results = {}
    cache_dir.mkdir(parents=True, exist_ok=True)

    tasks = []
    state_doc_pairs = []

    for state_abbrev, state_data in states_data.items():
        if state_filter and state_abbrev not in state_filter:
            continue

        for doc in state_data.get("documents", []):
            state_doc_pairs.append((state_abbrev, doc))

    for state_abbrev, doc in state_doc_pairs:
        task = parse_document(doc, cache_dir)
        tasks.append((state_abbrev, task))

    completed_results = await asyncio.gather(
        *[task for _, task in tasks], return_exceptions=True
    )

    for (state_abbrev, _), result in zip(tasks, completed_results):
        if isinstance(result, Exception):
            print(f"Error processing {state_abbrev}: {result}")
            continue

        if state_abbrev not in results:
            results[state_abbrev] = {}
        results[state_abbrev][result.document_title] = result

    return results


# =============================================================================
# OUTPUT GENERATION
# =============================================================================


def generate_json_patch(
    original_data: Dict,
    parsed_sections: Dict[str, Dict[str, DocumentParseResult]],
    output_path: Path,
):
    """Generate JSON patch file"""

    patch = {}

    for state_abbrev, state_sections in parsed_sections.items():
        state_patch = {"documents": []}

        for doc_title, parse_result in state_sections.items():
            doc_patch = {"title": doc_title, "grade_sections": {}}

            for grade, section in parse_result.grade_sections.items():
                doc_patch["grade_sections"][grade] = {
                    "page_ranges": section.page_ranges,
                    "section_ids": section.section_ids,
                    "confidence": section.confidence,
                    "notes": section.notes,
                    "needs_review": section.needs_review,
                }

            state_patch["documents"].append(doc_patch)

        patch[state_abbrev] = state_patch

    output_path.write_bytes(orjson.dumps(patch, option=orjson.OPT_INDENT_2))


def generate_markdown_report(
    parsed_sections: Dict[str, Dict[str, DocumentParseResult]], output_path: Path
):
    """Generate human-readable Markdown report"""

    lines = [
        "# Grade Section Analysis Report\n",
        "Generated by `parse_standards.py` with UV inline dependencies\n",
        "---\n",
    ]

    total_docs = sum(len(s) for s in parsed_sections.values())
    total_sections = sum(
        len(r.grade_sections)
        for state in parsed_sections.values()
        for r in state.values()
    )

    lines.append(f"## Summary\n")
    lines.append(f"- **States Processed:** {len(parsed_sections)}\n")
    lines.append(f"- **Documents Parsed:** {total_docs}\n")
    lines.append(f"- **Grade Sections Found:** {total_sections}\n\n")

    for state_abbrev, state_sections in sorted(parsed_sections.items()):
        lines.append(f"\n## {state_abbrev}\n")

        for doc_title, parse_result in sorted(state_sections.items()):
            lines.append(f"\n### {doc_title}\n")
            lines.append(f"- **Format:** {parse_result.format_type}\n")
            lines.append(f"- **Organization:** {parse_result.organization}\n")
            lines.append(f"- **URL:** {parse_result.url}\n")

            if parse_result.parse_errors:
                lines.append(f"- **Errors:** {', '.join(parse_result.parse_errors)}\n")

            if parse_result.grade_sections:
                lines.append("\n| Grade | Page Ranges | Confidence | Needs Review |\n")
                lines.append("|-------|-------------|------------|--------------|\n")

                for grade, section in sorted(parse_result.grade_sections.items()):
                    page_str = ", ".join(
                        f"{r[0] + 1}-{r[1]}" for r in section.page_ranges
                    )
                    review_str = "[!]" if section.needs_review else "[OK]"
                    lines.append(
                        f"| {grade} | {page_str} | {section.confidence} | {review_str} |\n"
                    )
            else:
                lines.append("*No grade sections detected*\n")

    lines.append("\n---\n*Use `parse_standards.py` to update*\n")
    output_path.write_text("".join(lines))


# =============================================================================
# CLI INTERFACE
# =============================================================================


def print_usage():
    print("""Standards Document Parser - Usage
====================================

Commands:
  parse --states <ST,ST,...>
      Parse specified states' documents
      Example: uv run parse_standards.py parse --states WA,CA,OR

  parse --all
      Parse all states in the database
      Example: uv run parse_standards.py parse --all

  report <patch_file>
      Generate human-readable report from existing patch file
      Example: uv run parse_standards.py report patches/grade_sections.json
""")


async def cmd_parse(
    state_filter: Optional[List[str]],
    output_patch: Path = Path("patches/grade_sections.json"),
    output_report: Path = Path("reports/grade_sections_analysis.md"),
):
    """Parse documents and generate outputs"""

    states_data = orjson.loads(Path("data/states.json").read_bytes())

    print(
        f"Parsing documents for {len(state_filter) if state_filter else 'all'} states..."
    )
    results = await parse_all_states(states_data, state_filter=state_filter)

    print("Generating JSON patch...")
    output_patch.parent.mkdir(parents=True, exist_ok=True)
    generate_json_patch(states_data, results, output_patch)

    print("Generating Markdown report...")
    output_report.parent.mkdir(parents=True, exist_ok=True)
    generate_markdown_report(results, output_report)

    print(f"\n[OK] Complete!")
    print(f"  Patch: {output_patch}")
    print(f"  Report: {output_report}")


def cmd_report(patch_path: Path, output_report: Path = Path("reports/analysis.md")):
    """Generate report from existing patch file"""
    if not patch_path.exists():
        print(f"Error: patch file not found: {patch_path}")
        return

    patch_data = orjson.loads(patch_path.read_bytes())

    lines = ["# Grade Section Analysis Report (From Patch)\n", "---\n\n"]

    for state_abbrev, state_data in sorted(patch_data.items()):
        lines.append(f"\n## {state_abbrev}\n")

        for doc in state_data.get("documents", []):
            lines.append(f"\n### {doc['title']}\n")
            grade_sections = doc.get("grade_sections", {})

            if grade_sections:
                lines.append("\n| Grade | Page Ranges | Confidence | Needs Review |\n")
                lines.append("|-------|-------------|------------|--------------|\n")

                for grade, section in sorted(grade_sections.items()):
                    page_str = ", ".join(
                        f"{r[0] + 1}-{r[1]}" for r in section.get("page_ranges", [])
                    )
                    review_str = "[!]" if section.get("needs_review", False) else "[OK]"
                    lines.append(
                        f"| {grade} | {page_str} | {section['confidence']} | {review_str} |\n"
                    )

                    if section.get("notes"):
                        lines.append(f"| | *{section['notes']}* | | |\n")
            else:
                lines.append("*No grade sections*\n")

    output_report.parent.mkdir(parents=True, exist_ok=True)
    output_report.write_text("".join(lines))

    print(f"[OK] Report generated: {output_report}")


async def main():
    """Main entry point"""
    if len(sys.argv) < 2:
        print_usage()
        return

    command = sys.argv[1].lower()

    if command == "parse":
        if "--all" in sys.argv:
            await cmd_parse(None)
        elif "--states" in sys.argv:
            idx = sys.argv.index("--states")
            if idx + 1 >= len(sys.argv):
                print("Error: --states requires state abbreviations")
                return
            states = [s.strip().upper() for s in sys.argv[idx + 1].split(",")]
            await cmd_parse(states)
        else:
            print("Error: parse requires --all or --states")
            print_usage()
    elif command == "report":
        if len(sys.argv) < 3:
            print("Error: report requires patch file path")
            return
        patch_path = Path(sys.argv[2])
        cmd_report(patch_path)
    else:
        print(f"Unknown command: {command}")
        print_usage()


if __name__ == "__main__":
    asyncio.run(main())
