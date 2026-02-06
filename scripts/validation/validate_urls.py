#!/usr/bin/env python3
# /// script
# dependencies = [
#     "httpx>=0.27.0",
#     "orjson>=3.9.0",
#     "pypdf>=3.0.0",
# ]
# ///
# -*- coding: utf-8 -*-
"""
URL Validation Utility
Validates URLs in states.json and generates update patches
"""

import json
import sys
import os
from pathlib import Path
import httpx
import hashlib
from typing import Dict, List, Optional, Tuple
import orjson
import pypdf
import io
import dataclasses

# =============================================================================
# DATA MODELS
# =============================================================================


@dataclasses.dataclass
class ValidationResult:
    """Result of validating a single URL"""

    url: str
    title: str
    state_abbrev: str
    http_status: int
    content_type: str  # "pdf", "html", "text", "error_page", "unknown"
    file_size_kb: Optional[int]
    error: Optional[str]
    redirect_chain: List[str]
    confidence: str  # "high", "medium", "low"
    notes: str
    content_validation: Optional[Dict] = None  # PDF content validation results

    def to_dict(self):
        return {
            "url": self.url,
            "title": self.title,
            "state_abbrev": self.state_abbrev,
            "http_status": self.http_status,
            "content_type": self.content_type,
            "file_size_kb": self.file_size_kb,
            "error": self.error,
            "redirect_chain": self.redirect_chain,
            "confidence": self.confidence,
            "notes": self.notes,
            "content_validation": self.content_validation,
        }


@dataclasses.dataclass
class ValidationReport:
    """Summary of validation results"""

    validation_date: str
    validator_version: str
    total_urls: int
    results: Dict[str, ValidationResult]
    summary: Dict[str, int]

    def to_dict(self):
        return {
            "validation_date": self.validation_date,
            "validator_version": self.validator_version,
            "total_urls": self.total_urls,
            "results": {
                abbr: result.to_dict() for abbr, result in self.results.items()
            },
            "summary": self.summary,
        }


# =============================================================================
# VALIDATION
# =============================================================================


def validate_pdf_content(
    url: str, expected_grades: List[str], expected_state: str, expected_title: str
) -> Dict:
    """
    Validate PDF contains expected content.

    Returns:
        dict: Content validation results with confidence score
    """
    try:
        response = httpx.get(url, timeout=30, follow_redirects=True)
        if response.status_code != 200:
            return {
                "error": f"HTTP {response.status_code}",
                "grade_level_found": False,
                "state_name_found": False,
                "science_keyword_found": False,
                "metadata_title_match": "error",
                "confidence_score": 0.0,
                "warnings": [f"HTTP {response.status_code} when downloading PDF"],
                "validation_status": "http_error",
            }

        pdf_file = io.BytesIO(response.content)
        reader = pypdf.PdfReader(pdf_file)

        # Extract text from first 5 pages
        text = ""
        for page in reader.pages[:5]:
            try:
                text += page.extract_text() + "\n"
            except:
                pass

        # Extract metadata
        metadata = reader.metadata or {}
        pdf_title = metadata.get("/Title", "") if metadata else ""

        # Check for expected content
        grade_found = False
        for grade in expected_grades:
            if (
                str(grade) in text
                or f"Grade {grade}" in text
                or f"grade {grade}" in text
            ):
                grade_found = True
                break

        state_found = expected_state in text or expected_state.split()[-1] in text
        science_found = any(
            keyword in text.lower()
            for keyword in ["science", "ngss", "standards", "performance expectations"]
        )
        title_match = expected_title in pdf_title if pdf_title else False

        # Calculate confidence
        confidence = 0.0
        if grade_found:
            confidence += 0.4
        if state_found:
            confidence += 0.3
        if science_found:
            confidence += 0.2
        if title_match:
            confidence += 0.1

        # Generate warnings
        warnings = []
        if not grade_found:
            warnings.append(f"grade levels {expected_grades} not found in PDF")
        if not state_found:
            warnings.append(f"state name '{expected_state}' not found in PDF")
        if not science_found:
            warnings.append("science keyword not found in PDF")

        # Determine validation status
        if confidence >= 0.8:
            status = "content_verified"
        elif confidence >= 0.5:
            status = "content_questionable"
        elif confidence >= 0.3:
            status = "content_questionable"
        else:
            status = "wrong_document"

        if confidence < 0.5:
            warnings.append(
                f"low confidence score ({confidence:.2f}) suggests wrong document"
            )

        return {
            "grade_level_found": grade_found,
            "state_name_found": state_found,
            "science_keyword_found": science_found,
            "metadata_title_match": "exact" if title_match else "none",
            "confidence_score": confidence,
            "warnings": warnings,
            "validation_status": status,
        }

    except Exception as e:
        return {
            "error": str(e),
            "grade_level_found": False,
            "state_name_found": False,
            "science_keyword_found": False,
            "metadata_title_match": "error",
            "confidence_score": 0.0,
            "warnings": [f"content validation failed: {e}"],
            "validation_status": "validation_error",
        }


class URLValidator:
    """Validates document URLs"""

    def __init__(self, timeout: int = 30, max_redirects: int = 3):
        self.timeout = timeout
        self.max_redirects = max_redirects
        self.client = None

    async def get_client(self) -> httpx.AsyncClient:
        if self.client is None:
            self.client = httpx.AsyncClient(
                timeout=self.timeout,
                limits=httpx.Limits(max_connections=10),
                follow_redirects=True,
                headers={
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                    "Accept": "application/pdf,application/xhtml+xml,application/xml,text/html,*/*",
                },
            )
        return self.client

    async def validate_url(
        self,
        url: str,
        title: str,
        state_abbrev: str,
        grade_levels: Optional[List[str]] = None,
        state_name: str = "",
    ) -> ValidationResult:
        """Validate a single URL"""
        if grade_levels is None:
            grade_levels = []
        client = await self.get_client()
        result = ValidationResult(
            url=url,
            title=title,
            state_abbrev=state_abbrev,
            http_status=0,
            content_type="unknown",
            file_size_kb=None,
            error=None,
            redirect_chain=[],
            confidence="medium",
            notes="",
            content_validation=None,
        )

        try:
            # Follow redirects
            final_url = url
            redirect_chain = []
            for _ in range(self.max_redirects):
                try:
                    response = await client.head(url, follow_redirects=True)
                    if response.status_code == 200:
                        final_url = str(response.url)
                        if final_url != url:
                            redirect_chain.append(final_url)
                            url = final_url
                        break
                    elif response.status_code in (301, 302, 303, 307, 308):
                        redirect_chain.append(str(response.url))
                        url = str(response.url)
                    else:
                        result.http_status = response.status_code
                        result.error = f"HTTP {response.status_code}"
                        result.confidence = "low"
                        return result

                except httpx.TimeoutException:
                    result.http_status = 408
                    result.error = "Timeout"
                    result.confidence = "low"
                    return result
                except Exception as e:
                    result.http_status = 0
                    result.error = f"Connection error: {type(e).__name__}"
                    result.confidence = "low"
                    return result

            # Download small portion to check content type
            try:
                response = await client.get(
                    url, follow_redirects=True, headers={"Range": "bytes=0-1024"}
                )

                if response.status_code == 200:
                    result.http_status = 200
                    content_type_bytes = response.content[:100]

                    # Detect content type from header
                    content_type_header = response.headers.get("content-type", "")

                    if "application/pdf" in content_type_header.lower():
                        result.content_type = "pdf"
                        result.confidence = "high"
                    elif (
                        "text/html" in content_type_header.lower()
                        or "text/plain" in content_type_header.lower()
                    ):
                        result.content_type = "html"
                        result.confidence = "low"
                        result.error = "Returns HTML instead of PDF"
                    elif "text/plain" in content_type_header.lower():
                        result.content_type = "text"
                        result.confidence = "low"
                        result.error = "Returns plain text"
                    elif "error" in response.headers.get("content-type", "").lower():
                        result.content_type = "error_page"
                        result.error = "Server returned error page"
                    else:
                        result.content_type = "unknown"
                        result.confidence = "low"

                    # Check file size if available
                    if "content-length" in response.headers:
                        try:
                            size = int(response.headers["content-length"])
                            result.file_size_kb = size // 1024
                        except:
                            pass

                    if redirect_chain:
                        result.notes = f"Redirected: {' -> '.join(redirect_chain)}"
                    else:
                        result.notes = "No redirects"

            except httpx.TimeoutException:
                result.http_status = 408
                result.error = "Timeout during content check"
                result.confidence = "low"
                return result
            except Exception as e:
                result.http_status = 0
                result.error = f"Content check error: {type(e).__name__}"
                result.confidence = "low"
                return result

        except Exception as e:
            result.http_status = 0
            result.error = f"Validation error: {type(e).__name__}"
            result.confidence = "low"
            return result

        # Run content validation if we have a valid PDF
        if result.http_status == 200 and result.content_type == "pdf":
            result.content_validation = validate_pdf_content(
                url, grade_levels, state_name, title
            )
            # Update confidence based on content validation
            if result.content_validation.get("confidence_score", 0) < 0.5:
                result.confidence = "low"
                result.error = result.content_validation.get("warnings", ["Unknown"])[0]

        return result

    async def validate_urls_batch(
        self, items: List[Tuple[str, str, str, Optional[List[str]], str]]
    ) -> List[ValidationResult]:
        """Validate multiple URLs in batches"""
        results = []

        for state_abbrev, title, url, grade_levels, state_name in items:
            result = await self.validate_url(
                url, title, state_abbrev, grade_levels, state_name
            )
            results.append(result)

            print(f"  {state_abbrev}: {title[:40]}...")
            if result.http_status == 200 and result.content_type == "pdf":
                if result.content_validation:
                    confidence = result.content_validation.get("confidence_score", 0)
                    status = result.content_validation.get(
                        "validation_status", "unknown"
                    )
                    print(
                        f"    Status: PDF {result.file_size_kb}KB - Confidence: {confidence:.2f} ({status})"
                    )
                else:
                    print(f"    Status: Working PDF {result.file_size_kb}KB")
            elif result.http_status == 200:
                print(
                    f"    Status: {result.content_type.upper()} - {result.error or 'OK'}"
                )
            else:
                print(
                    f"    Status: HTTP {result.http_status} - {result.error or 'Error'}"
                )

        return results


# =============================================================================
# OUTPUT GENERATION
# =============================================================================


def generate_validation_report(results: List[ValidationResult], output_path: Path):
    """Generate human-readable validation report"""
    from datetime import datetime

    validation_date = datetime.now().strftime("%Y-%m-%d")
    validator_version = "1.0"

    report_lines = [
        "# URL Validation Report\n",
        f"**Validation Date:** {validation_date}\n",
        f"**Validator Version:** {validator_version}\n",
        "---\n\n",
    ]

    # Summary statistics
    working = sum(
        1 for r in results if r.http_status == 200 and r.content_type == "pdf"
    )
    broken = sum(1 for r in results if r.http_status != 200)
    other_issues = sum(
        1 for r in results if r.http_status == 200 and r.content_type != "pdf"
    )

    report_lines.append("## Summary\n")
    report_lines.append(f"- **Total URLs Validated:** {len(results)}\n")
    report_lines.append(f"- **Working PDFs:** {working}\n")
    report_lines.append(f"- **Broken URLs (HTTP errors):** {broken}\n")
    report_lines.append(f"- **Wrong Format (HTML/Error):** {other_issues}\n")
    report_lines.append(
        f"- **Overall Success Rate:** {working * 100 // len(results)}%\n"
    )
    report_lines.append("\n")

    # By state
    state_results = {}
    for r in results:
        if r.state_abbrev not in state_results:
            state_results[r.state_abbrev] = []
        state_results[r.state_abbrev].append(r)

    report_lines.append("## By State\n\n")
    for state_abbrev in sorted(state_results.keys()):
        state_urls = state_results[state_abbrev]
        working = sum(
            1 for r in state_urls if r.http_status == 200 and r.content_type == "pdf"
        )
        total = len(state_urls)
        report_lines.append(f"\n### {state_abbrev} ({total} URLs)\n")

        if working > 0:
            report_lines.append(f"**Working URLs:** {working}/{total}\n")
        elif total > 0:
            report_lines.append(f"**Broken URLs:** {total - working}/{total}\n")
        else:
            report_lines.append(f"**Status:** All broken\n")

        for r in state_urls:
            if r.http_status == 200:
                status_icon = "✅" if r.content_type == "pdf" else "⚠️ "
                status_text = f"{status_icon} {r.content_type.upper()}"
                if r.file_size_kb:
                    status_text += f" ({r.file_size_kb}KB)"
            elif r.http_status != 0:
                status_text = f"❌ HTTP {r.http_status}"
            else:
                status_text = "❌ Error"

            report_lines.append(f"- {r.title[:60]}: {status_text}")
            if r.error:
                report_lines.append(f"  Error: {r.error}")
            if r.notes and "Redirected" in r.notes:
                report_lines.append(f"  Notes: {r.notes}")

    report_lines.append("\n---\n")

    # Issues list
    issue_urls = [r for r in results if r.http_status != 200 or r.content_type != "pdf"]
    if issue_urls:
        report_lines.append("## URLs Needing Attention\n\n")
        for r in issue_urls:
            issue_type = "HTTP Error" if r.http_status != 200 else "Wrong Format"
            report_lines.append(f"- **{r.state_abbrev}**: {r.title[:50]}")
            report_lines.append(f"  - Issue: {issue_type}")
            if r.http_status != 200:
                report_lines.append(f"  - Details: HTTP {r.http_status} - {r.error}")
            else:
                report_lines.append(f"  - Details: {r.content_type} - {r.error}")
            report_lines.append(f"  - URL: {r.url[:70]}...")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("".join(report_lines), encoding="utf-8")


def generate_validation_json(results: List[ValidationResult], output_path: Path):
    """Generate structured JSON output"""
    from datetime import datetime

    validation_date = datetime.now().strftime("%Y-%m-%d")
    validator_version = "1.0"

    report_data = {
        "validation_date": validation_date,
        "validator_version": validator_version,
        "total_urls": len(results),
        "results": {r.url: r.to_dict() for r in results},
        "summary": {
            "working_pdf": sum(
                1 for r in results if r.http_status == 200 and r.content_type == "pdf"
            ),
            "broken": sum(1 for r in results if r.http_status != 200),
            "other_issues": sum(
                1 for r in results if r.http_status == 200 and r.content_type != "pdf"
            ),
            "content_verified": sum(
                1
                for r in results
                if r.content_validation
                and r.content_validation.get("confidence_score", 0) >= 0.8
            ),
            "content_questionable": sum(
                1
                for r in results
                if r.content_validation
                and 0.5 <= r.content_validation.get("confidence_score", 0) < 0.8
            ),
            "wrong_document": sum(
                1
                for r in results
                if r.content_validation
                and r.content_validation.get("confidence_score", 0) < 0.5
            ),
        },
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_bytes(orjson.dumps(report_data, option=orjson.OPT_INDENT_2))


# =============================================================================
# MAIN CLI
# =============================================================================


async def validate_states(
    states_data: Dict,
    state_filter: Optional[List[str]] = None,
    output_json: Path = Path("validation_results.json"),
    output_report: Path = Path("reports/url_validation_report.md"),
):
    """Validate all document URLs in states.json"""

    # Collect all URLs to validate
    items = []
    for state_abbrev, state_data in states_data.items():
        if state_filter and state_abbrev not in state_filter:
            continue

        state_name = state_data.get("state_name", "")
        for doc in state_data.get("documents", []):
            grade_levels = doc.get("grade_levels", [])
            items.append(
                (state_abbrev, doc["title"], doc["url"], grade_levels, state_name)
            )

    print(f"\nValidating {len(items)} document URLs...\n")

    # Validate in batches
    validator = URLValidator()
    results = await validator.validate_urls_batch(items)

    # Generate outputs
    print(f"\nGenerating validation report...")
    generate_validation_report(results, output_report)

    print(f"Generating validation JSON...")
    generate_validation_json(results, output_json)

    print(f"\nDone!")
    print(f"  Report: {output_report}")
    print(f"  JSON: {output_json}")
    print(
        f"\nWorking PDFs: {sum(1 for r in results if r.http_status == 200 and r.content_type == 'pdf')}"
    )

    return results


async def main():
    if len(sys.argv) < 2:
        print("Usage: python validate_urls.py validate")
        print("       python validate_urls.py validate --states WA,OR,CA")
        print("\nOptions:")
        print("  validate        Validate all states")
        print("  --states ST,ST   Validate specific states")
        return

    command = sys.argv[1].lower()

    if command == "validate":
        state_filter = None
        if "--states" in sys.argv:
            idx = sys.argv.index("--states")
            if idx + 1 >= len(sys.argv):
                print("Error: --states requires state abbreviations")
                return
            state_filter = sys.argv[idx + 1].split(",")

        script_dir = Path(__file__).parent
        states_file = script_dir / "data" / "states.json"

        if not states_file.exists():
            print(f"Error: states.json not found at {states_file}")
            return

        import json

        with open(states_file) as f:
            states_data = json.load(f)

        output_json = script_dir / "validation_results.json"
        output_report = script_dir / "reports" / "url_validation_report.md"

        await validate_states(states_data, state_filter, output_json, output_report)


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
