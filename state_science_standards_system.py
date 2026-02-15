# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
#!/usr/bin/env python3
"""
State Science Standards Tracker
A comprehensive, grade-agnostic system for tracking K-12 science learning standards
across all 50 US states + District of Columbia.
Enhanced with grade-specific page/section mapping support.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
import sys
import json
import os

PAGE_RANGE_STATUS_LABELS = {
    "not_applicable_ngss_reference": "N/A (NGSS reference document — no state-specific K-12 PDF)",
    "not_applicable_multi_document": "N/A (multi-document state — see individual grade PDFs)",
    "not_applicable_interactive_database": "N/A (interactive database — no PDF)",
}


@dataclass
class GradeSection:
    """Maps a grade to specific location(s) within a document"""

    page_ranges: List[Tuple[int, int]] = field(default_factory=list)
    section_ids: List[str] = field(default_factory=list)
    confidence: str = "high"
    notes: Optional[str] = None
    needs_review: bool = False


@dataclass
class StandardsDocument:
    """Represents a single standards document"""

    title: str
    url: str
    grade_levels: List[str]  # ["K"], ["3"], ["K-12"], ["3", "4", "5"], etc.
    document_type: str  # "complete_k12", "grade_specific", "grade_band"
    format: str = "PDF"  # "PDF", "HTML", "Interactive"
    page_range: Optional[str] = None  # "18-21" for specific pages
    notes: Optional[str] = None
    grade_sections: Dict[str, GradeSection] = field(
        default_factory=dict
    )  # Grade-specific page/section mappings
    url_source: Optional[str] = None  # Source URL where document was found
    last_verified: Optional[str] = None  # Last verification date (YYYY-MM-DD)
    special_structure: Optional[str] = None  # Special document structure type
    page_range_status: Optional[str] = None  # Why page_range is null: "not_applicable_ngss_reference", "not_applicable_multi_document", "not_applicable_interactive_database"


@dataclass
class Assessment:
    """Represents a state assessment"""

    name: str
    grade_levels: List[str]  # Which grades are tested
    url: Optional[str] = None
    test_type: str = "state"  # "state", "local", "interim"
    notes: Optional[str] = None


@dataclass
class StateStandards:
    """Complete standards information for a state"""

    # Basic Info
    state_name: str
    state_abbrev: str
    agency_name: str
    website: str
    science_page: Optional[str] = None

    # Standards Info
    ngss_status: str = "pending"  # "direct_adoption", "framework_based", "pending"
    standards_name: Optional[str] = None
    adoption_date: Optional[str] = None

    # Documents - CRITICAL FOR GRADE-AGNOSTIC SYSTEM
    documents: List[StandardsDocument] = field(default_factory=list)

    # Assessments
    assessments: List[Assessment] = field(default_factory=list)

    # Organization (defaults to standard K-12 structure)
    elementary_grades: List[str] = field(
        default_factory=lambda: ["K", "1", "2", "3", "4", "5"]
    )
    middle_grades: List[str] = field(default_factory=lambda: ["6", "7", "8"])
    high_school_grades: List[str] = field(
        default_factory=lambda: ["9", "10", "11", "12"]
    )

    # Contacts & Resources
    contacts: Dict[str, str] = field(default_factory=dict)
    resources: Dict[str, str] = field(default_factory=dict)

    # Metadata
    notes: Optional[str] = None
    research_status: str = "PENDING"  # "COMPLETE" or "PENDING"
    last_updated: Optional[str] = None


# ============================================================================
# DATA LOADING
# ============================================================================


def load_states_data(json_path: str = None) -> Dict[str, StateStandards]:
    """
    Load state standards data from JSON file.

    Args:
        json_path: Path to JSON file. If None, uses default location.

    Returns:
        Dictionary mapping state abbreviations to StateStandards objects
    """
    if json_path is None:
        # Default to data/states.json in the same directory as this script
        script_dir = os.path.dirname(os.path.abspath(__file__))
        json_path = os.path.join(script_dir, "data", "states.json")

    if not os.path.exists(json_path):
        raise FileNotFoundError(f"States data file not found: {json_path}")

    with open(json_path, "r", encoding="utf-8") as f:
        states_dict = json.load(f)

    # Convert dictionaries back to dataclasses
    states_db = {}
    for state_abbrev, state_data in states_dict.items():
        # Convert documents
        documents = []
        for doc in state_data.get("documents", []):
            # Parse grade_sections if present
            grade_sections = {}
            for grade, section_data in doc.get("grade_sections", {}).items():
                grade_sections[grade] = GradeSection(**section_data)

            # Create document with grade_sections
            doc_copy = doc.copy()
            doc_copy["grade_sections"] = grade_sections
            documents.append(StandardsDocument(**doc_copy))

        # Convert assessments
        assessments = [
            Assessment(**assess) for assess in state_data.get("assessments", [])
        ]

        # Create StateStandards object
        state_data_copy = state_data.copy()
        state_data_copy["documents"] = documents
        state_data_copy["assessments"] = assessments

        states_db[state_abbrev] = StateStandards(**state_data_copy)

    return states_db


# Load the states database
STATES_DB = load_states_data()


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================


def expand_grade_range(grade_spec: str) -> List[str]:
    """
    Expand grade specifications into individual grades.

    Examples:
        "K" -> ["K"]
        "3" -> ["3"]
        "K-5" -> ["K", "1", "2", "3", "4", "5"]
        "6-8" -> ["6", "7", "8"]
        "9-12" -> ["9", "10", "11", "12"]
    """
    if "-" not in grade_spec:
        return [grade_spec]

    start, end = grade_spec.split("-")

    # Handle K-5 or K-12 cases
    if start == "K":
        grades = ["K"]
        start_num = 1
    else:
        grades = []
        start_num = int(start)

    end_num = int(end)

    for i in range(start_num, end_num + 1):
        grades.append(str(i))

    return grades


def get_all_grades_from_list(grade_list: List[str]) -> List[str]:
    """Expand a list of grade specifications into all individual grades."""
    all_grades = []
    for grade_spec in grade_list:
        all_grades.extend(expand_grade_range(grade_spec))
    return list(dict.fromkeys(all_grades))  # Remove duplicates, preserve order


def get_documents_for_grade(
    state: StateStandards, grade: str
) -> List[StandardsDocument]:
    """Get all documents that cover a specific grade."""
    matching_docs = []

    for doc in state.documents:
        all_doc_grades = get_all_grades_from_list(doc.grade_levels)
        if grade in all_doc_grades:
            matching_docs.append(doc)

    return matching_docs


def normalize_grade(grade: str) -> str:
    """Normalize grade input (e.g., 'kindergarten' -> 'K', 'grade 3' -> '3')."""
    grade = grade.strip().upper()

    if grade in ["KINDERGARTEN", "KINDER", "KG"]:
        return "K"

    # Remove "GRADE" prefix if present
    if grade.startswith("GRADE "):
        grade = grade[6:]

    return grade


def get_coverage_summary(state: StateStandards) -> Dict[str, List[StandardsDocument]]:
    """Get which documents cover each grade for a state."""
    all_grades = ["K", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12"]
    coverage = {}

    for grade in all_grades:
        docs = get_documents_for_grade(state, grade)
        if docs:
            coverage[grade] = docs

    return coverage


# ============================================================================
# CLI COMMANDS
# ============================================================================


def cmd_search(grade: str):
    """Search all states for standards documents covering a specific grade."""
    grade = normalize_grade(grade)

    print(f"\n{'=' * 80}")
    print(f"STATES WITH STANDARDS FOR GRADE {grade}")
    print(f"{'=' * 80}\n")

    found_states = []

    for state_abbrev in sorted(STATES_DB.keys()):
        state = STATES_DB[state_abbrev]
        docs = get_documents_for_grade(state, grade)

        if docs:
            found_states.append((state_abbrev, state, docs))

    if not found_states:
        print(f"No states found with documents for grade {grade}.")
        return

    print(f"Found {len(found_states)} state(s) with grade {grade} standards:\n")

    for state_abbrev, state, docs in found_states:
        print(f"\n{state.state_name} ({state_abbrev})")
        print(f"  Status: {state.ngss_status.replace('_', ' ').title()}")
        print(f"  Standards: {state.standards_name or 'N/A'}")
        print(f"  Documents covering grade {grade}:")

        for doc in docs:
            print(f"    • {doc.title}")
            print(f"      {doc.url}")
            if doc.notes:
                print(f"      Note: {doc.notes}")

        # Show assessments for this grade
        assessed = [a for a in state.assessments if grade in a.grade_levels]
        if assessed:
            print(f"  Assessments at grade {grade}:")
            for assessment in assessed:
                print(f"    • {assessment.name}")


def cmd_state(state_abbrev: str, grade: str = None):
    """Get detailed information about a state's standards, optionally for a specific grade."""
    state_abbrev = state_abbrev.upper()

    if state_abbrev not in STATES_DB:
        print(f"Error: State '{state_abbrev}' not found in database.")
        print(f"Available states: {', '.join(sorted(STATES_DB.keys()))}")
        return

    state = STATES_DB[state_abbrev]

    print(f"\n{'=' * 80}")
    print(f"{state.state_name} ({state_abbrev}) - SCIENCE STANDARDS")
    print(f"{'=' * 80}\n")

    print(f"Agency: {state.agency_name}")
    print(f"Website: {state.website}")
    if state.science_page:
        print(f"Science Page: {state.science_page}")

    print(f"\nStandards Information:")
    print(f"  Name: {state.standards_name or 'N/A'}")
    print(f"  NGSS Status: {state.ngss_status.replace('_', ' ').title()}")
    print(f"  Adoption Date: {state.adoption_date or 'N/A'}")

    if grade:
        grade = normalize_grade(grade)
        print(f"\n{'=' * 80}")
        print(f"GRADE {grade} STANDARDS")
        print(f"{'=' * 80}\n")

        docs = get_documents_for_grade(state, grade)

        if not docs:
            print(f"No documents found for grade {grade}.")
        else:
            print(f"Documents covering grade {grade}:\n")
            for i, doc in enumerate(docs, 1):
                print(f"{i}. {doc.title}")
                print(f"   URL: {doc.url}")
                print(f"   Format: {doc.format}")
                print(f"   Type: {doc.document_type.replace('_', ' ').title()}")
                print(f"   Covers Grades: {', '.join(doc.grade_levels)}")
                if doc.page_range:
                    print(f"   Pages: {doc.page_range}")
                elif doc.page_range_status:
                    print(f"   Pages: {PAGE_RANGE_STATUS_LABELS.get(doc.page_range_status, doc.page_range_status)}")
                if doc.notes:
                    print(f"   Notes: {doc.notes}")
                print()

        # Show assessments for this grade
        assessed = [a for a in state.assessments if grade in a.grade_levels]
        if assessed:
            print(f"Assessments at grade {grade}:")
            for assessment in assessed:
                print(f"  • {assessment.name}")
                if assessment.url:
                    print(f"    URL: {assessment.url}")
                if assessment.notes:
                    print(f"    Notes: {assessment.notes}")
                print()
    else:
        # Show all documents
        if state.documents:
            print(f"\nAll Documents ({len(state.documents)}):")
            for i, doc in enumerate(state.documents, 1):
                print(f"\n{i}. {doc.title}")
                print(f"   URL: {doc.url}")
                print(f"   Covers Grades: {', '.join(doc.grade_levels)}")
                print(f"   Format: {doc.format}")
                if doc.page_range:
                    print(f"   Pages: {doc.page_range}")
                elif doc.page_range_status:
                    print(f"   Pages: {PAGE_RANGE_STATUS_LABELS.get(doc.page_range_status, doc.page_range_status)}")
                if doc.notes:
                    print(f"   Notes: {doc.notes}")

        # Show all assessments
        if state.assessments:
            print(f"\nAssessments ({len(state.assessments)}):")
            for assessment in state.assessments:
                print(f"\n  • {assessment.name}")
                print(f"    Grades: {', '.join(assessment.grade_levels)}")
                print(f"    Type: {assessment.test_type.title()}")
                if assessment.url:
                    print(f"    URL: {assessment.url}")
                if assessment.notes:
                    print(f"    Notes: {assessment.notes}")

    # Contacts
    if state.contacts:
        print(f"\nContacts:")
        for key, value in state.contacts.items():
            print(f"  {key.title()}: {value}")

    # Resources
    if state.resources:
        print(f"\nAdditional Resources:")
        for key, value in state.resources.items():
            print(f"  {key.replace('_', ' ').title()}: {value}")

    # Notes and metadata
    if state.notes:
        print(f"\nNotes: {state.notes}")

    print(f"\nResearch Status: {state.research_status}")
    if state.last_updated:
        print(f"Last Updated: {state.last_updated}")


def cmd_range(state_abbrev: str):
    """Show complete K-12 coverage for a state."""
    state_abbrev = state_abbrev.upper()

    if state_abbrev not in STATES_DB:
        print(f"Error: State '{state_abbrev}' not found in database.")
        return

    state = STATES_DB[state_abbrev]
    coverage = get_coverage_summary(state)

    print(f"\n{'=' * 80}")
    print(f"{state.state_name} ({state_abbrev}) - K-12 COVERAGE")
    print(f"{'=' * 80}\n")

    all_grades = ["K", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12"]

    covered_grades = set(coverage.keys())
    missing_grades = [g for g in all_grades if g not in covered_grades]

    print(f"Coverage: {len(covered_grades)}/13 grades")
    print(f"Status: {state.research_status}")

    if missing_grades:
        print(f"\n⚠️  Missing grades: {', '.join(missing_grades)}")
    else:
        print(f"\n✓ Complete K-12 coverage")

    print(f"\nGrade-by-Grade Breakdown:\n")

    for grade in all_grades:
        if grade in coverage:
            docs = coverage[grade]
            print(f"  Grade {grade:>2}: ✓ ({len(docs)} document(s))")
            for doc in docs:
                print(f"             • {doc.title}")
        else:
            print(f"  Grade {grade:>2}: ✗ (no documents)")

    print(f"\n{'=' * 80}")


def cmd_compare(grade: str):
    """Compare all states for a specific grade."""
    grade = normalize_grade(grade)

    print(f"\n{'=' * 80}")
    print(f"GRADE {grade} STANDARDS - STATE COMPARISON")
    print(f"{'=' * 80}\n")

    ngss_states = []
    framework_states = []
    no_data_states = []

    for state_abbrev in sorted(STATES_DB.keys()):
        state = STATES_DB[state_abbrev]
        docs = get_documents_for_grade(state, grade)

        if docs:
            if state.ngss_status == "direct_adoption":
                ngss_states.append((state_abbrev, state, docs))
            else:
                framework_states.append((state_abbrev, state, docs))
        else:
            no_data_states.append(state_abbrev)

    print(f"States with NGSS Direct Adoption ({len(ngss_states)}):")
    for state_abbrev, state, docs in ngss_states:
        print(f"  {state_abbrev}: {state.state_name} - {len(docs)} document(s)")

    print(f"\nStates with Framework-Based Standards ({len(framework_states)}):")
    for state_abbrev, state, docs in framework_states:
        print(
            f"  {state_abbrev}: {state.state_name} ({state.standards_name}) - {len(docs)} document(s)"
        )

    if no_data_states:
        print(f"\nStates without grade {grade} data ({len(no_data_states)}):")
        print(f"  {', '.join(no_data_states)}")


def cmd_queries(state_abbrev: str, grade: str = None):
    """Generate search queries for researching a state."""
    state_abbrev = state_abbrev.upper()

    if state_abbrev not in STATES_DB:
        print(f"Error: State '{state_abbrev}' not found.")
        return

    state = STATES_DB[state_abbrev]
    state_name = state.state_name

    print(f"\n{'=' * 80}")
    print(f"RESEARCH QUERIES FOR {state_name} ({state_abbrev})")
    print(f"{'=' * 80}\n")

    queries = [
        f'"{state_name} department of education" science standards',
        f"site:{state.website.replace('https://', '').replace('http://', '')} science standards K-12",
        f'"{state_name} science standards" PDF',
        f'"{state_name} NGSS adoption"',
        f'"{state_name} science assessment"',
    ]

    if grade:
        grade = normalize_grade(grade)
        queries.extend(
            [
                f'"{state_name} grade {grade} science standards"',
                f'"{state_name} science standards" "grade {grade}"',
                f'"{state_name} science assessment" grade {grade}',
            ]
        )

    print("Suggested search queries:\n")
    for i, query in enumerate(queries, 1):
        print(f"{i}. {query}")

    print(f"\nDirect URLs to check:\n")
    print(f"1. {state.website}")
    if state.science_page:
        print(f"2. {state.science_page}")


def cmd_list():
    """List all states in the database with their status."""
    print(f"\n{'=' * 80}")
    print(f"STATE SCIENCE STANDARDS DATABASE")
    print(f"{'=' * 80}\n")

    complete_states = []
    pending_states = []

    for state_abbrev in sorted(STATES_DB.keys()):
        state = STATES_DB[state_abbrev]
        if state.research_status == "COMPLETE":
            complete_states.append((state_abbrev, state))
        else:
            pending_states.append((state_abbrev, state))

    print(f"COMPLETE ({len(complete_states)}):\n")
    for state_abbrev, state in complete_states:
        coverage = get_coverage_summary(state)
        print(f"  {state_abbrev}: {state.state_name}")
        print(f"       Status: {state.ngss_status.replace('_', ' ').title()}")
        print(f"       Coverage: {len(coverage)}/13 grades")
        print(f"       Documents: {len(state.documents)}")
        print()

    if pending_states:
        print(f"PENDING ({len(pending_states)}):\n")
        for state_abbrev, state in pending_states:
            print(f"  {state_abbrev}: {state.state_name}")

    print(f"{'=' * 80}")
    print(f"Total: {len(STATES_DB)} states")
    print(f"Complete: {len(complete_states)}")
    print(f"Pending: {len(pending_states)}")
    print(f"{'=' * 80}\n")


def cmd_sections(state_abbrev: str, grade: str = None):
    """Show grade-specific page/section information for a state."""
    state_abbrev = state_abbrev.upper()

    if state_abbrev not in STATES_DB:
        print(f"Error: State '{state_abbrev}' not found in database.")
        print(f"Available states: {', '.join(sorted(STATES_DB.keys()))}")
        return

    state = STATES_DB[state_abbrev]

    print(f"\n{'=' * 80}")
    print(f"{state.state_name} ({state_abbrev}) - GRADE-SPECIFIC SECTIONS")
    print(f"{'=' * 80}\n")

    if grade:
        grade = normalize_grade(grade)
        show_grade_sections(state, grade)
    else:
        show_all_grade_sections(state)


def show_grade_sections(state: StateStandards, grade: str):
    """Display sections for a specific grade."""
    docs = get_documents_for_grade(state, grade)

    if not docs:
        print(f"No documents found for grade {grade}")
        return

    print(f"Grade {grade} sections:\n")

    for doc in docs:
        section = doc.grade_sections.get(grade)

        print(f"Document: {doc.title}")
        print(f"  URL: {doc.url}")

        if section:
            if section.page_ranges:
                pages = ", ".join(f"{r[0] + 1}-{r[1]}" for r in section.page_ranges)
                print(f"  Pages: {pages}")

            if section.section_ids:
                print(f"  Section IDs: {', '.join(section.section_ids)}")

            print(f"  Confidence: {section.confidence}")

            if section.needs_review:
                print(f"  [!] This section needs manual review")

            if section.notes:
                print(f"  Notes: {section.notes}")
        else:
            print(f"  [!] No specific section mapping found")

        print()


def show_all_grade_sections(state: StateStandards):
    """Display sections for all grades in a state."""
    all_grades = ["K", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12"]

    for grade in all_grades:
        docs = get_documents_for_grade(state, grade)

        if not docs:
            continue

        print(f"\nGrade {grade} sections:")

        for doc in docs:
            section = doc.grade_sections.get(grade)
            if section:
                if section.page_ranges:
                    pages = ", ".join(f"{r[0] + 1}-{r[1]}" for r in section.page_ranges)
                    print(f"  • {doc.title}: {pages}")
                else:
                    print(f"  • {doc.title}")
            else:
                print(f"  • {doc.title}: (no section mapping)")

    print()


# ============================================================================
# MAIN CLI
# ============================================================================


def print_usage():
    """Print usage information."""
    print("""
State Science Standards Tracker - Usage
========================================

Commands:

  list
      List all states in the database with status

  search <grade>
      Search all states for standards covering a specific grade
      Example: python state_science_standards_system.py search 3

  state <ST> [grade]
      Get detailed information about a state's standards
      Optionally specify a grade to see grade-specific info
      Example: python state_science_standards_system.py state WA 5

  range <ST>
      Show complete K-12 coverage for a state
      Example: python state_science_standards_system.py range CA

  compare <grade>
      Compare all states for a specific grade
      Example: python state_science_standards_system.py compare 5

  queries <ST> [grade]
      Generate search queries for researching a state
      Example: python state_science_standards_system.py queries IL 4

  sections <ST> [grade]
      Show grade-specific page/section information for a state
      Optionally specify a grade to see grade-specific sections
      Example: python state_science_standards_system.py sections WA 3

  Grades: Use K for Kindergarten, or numbers 1-12
  State abbreviations: Use two-letter codes (WA, CA, TX, etc.)
""")


def main():
    """Main entry point for CLI."""
    if len(sys.argv) < 2:
        print_usage()
        return

    command = sys.argv[1].lower()

    if command == "list":
        cmd_list()
    elif command == "search":
        if len(sys.argv) < 3:
            print("Error: search command requires a grade")
            print("Usage: python state_science_standards_system.py search <grade>")
            return
        cmd_search(sys.argv[2])
    elif command == "state":
        if len(sys.argv) < 3:
            print("Error: state command requires a state abbreviation")
            print("Usage: python state_science_standards_system.py state <ST> [grade]")
            return
        grade = sys.argv[3] if len(sys.argv) > 3 else None
        cmd_state(sys.argv[2], grade)
    elif command == "range":
        if len(sys.argv) < 3:
            print("Error: range command requires a state abbreviation")
            print("Usage: python state_science_standards_system.py range <ST>")
            return
        cmd_range(sys.argv[2])
    elif command == "compare":
        if len(sys.argv) < 3:
            print("Error: compare command requires a grade")
            print("Usage: python state_science_standards_system.py compare <grade>")
            return
        cmd_compare(sys.argv[2])
    elif command == "queries":
        if len(sys.argv) < 3:
            print("Error: queries command requires a state abbreviation")
            print(
                "Usage: python state_science_standards_system.py queries <ST> [grade]"
            )
            return
        grade = sys.argv[3] if len(sys.argv) > 3 else None
        cmd_queries(sys.argv[2], grade)
    elif command == "sections":
        if len(sys.argv) < 3:
            print("Error: sections command requires a state abbreviation")
            print(
                "Usage: python state_science_standards_system.py sections <ST> [grade]"
            )
            return
        grade = sys.argv[3] if len(sys.argv) > 3 else None
        cmd_sections(sys.argv[2], grade)
    else:
        print(f"Error: Unknown command '{command}'")
        print_usage()


if __name__ == "__main__":
    main()
