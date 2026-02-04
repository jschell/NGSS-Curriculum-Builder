#!/usr/bin/env python3
"""
State Science Standards Tracker
A comprehensive, grade-agnostic system for tracking K-12 science learning standards
across all 50 US states + District of Columbia.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional
import sys


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
    elementary_grades: List[str] = field(default_factory=lambda: ["K", "1", "2", "3", "4", "5"])
    middle_grades: List[str] = field(default_factory=lambda: ["6", "7", "8"])
    high_school_grades: List[str] = field(default_factory=lambda: ["9", "10", "11", "12"])

    # Contacts & Resources
    contacts: Dict[str, str] = field(default_factory=dict)
    resources: Dict[str, str] = field(default_factory=dict)

    # Metadata
    notes: Optional[str] = None
    research_status: str = "PENDING"  # "COMPLETE" or "PENDING"
    last_updated: Optional[str] = None


# ============================================================================
# STATES DATABASE
# ============================================================================

STATES_DB = {
    "WA": StateStandards(
        state_name="Washington",
        state_abbrev="WA",
        agency_name="Office of Superintendent of Public Instruction (OSPI)",
        website="https://ospi.k12.wa.us",
        science_page="https://ospi.k12.wa.us/student-success/resources-subject-area/science",
        ngss_status="direct_adoption",
        standards_name="Washington State K-12 Science Learning Standards (WSSLS)",
        adoption_date="October 2013 (Updated 2024)",

        documents=[
            StandardsDocument(
                title="Washington State K-12 Science Learning Standards",
                url="https://ospi.k12.wa.us/sites/default/files/2024-08/washington_state_k-12_science_learning_standards_version_2.0.pdf",
                grade_levels=["K", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12"],
                document_type="complete_k12",
                format="PDF",
                notes="Single comprehensive K-12 document, identical to NGSS"
            ),
            StandardsDocument(
                title="WSSLS DCI Arrangement",
                url="https://ospi.k12.wa.us/sites/default/files/2024-08/washington_state_k-12_science_learning_standards_dci_arrangement_version_2.0.pdf",
                grade_levels=["K", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12"],
                document_type="complete_k12",
                format="PDF",
                notes="Organized by Disciplinary Core Ideas"
            ),
            StandardsDocument(
                title="WSSLS Topic Arrangement",
                url="https://ospi.k12.wa.us/sites/default/files/2024-08/washington_state_k-12_science_learning_standards_topic_arrangement_version_2.0.pdf",
                grade_levels=["K", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12"],
                document_type="complete_k12",
                format="PDF",
                notes="Organized by topics for easier curriculum planning"
            ),
        ],

        assessments=[
            Assessment(
                name="Washington Comprehensive Assessment of Science (WCAS)",
                grade_levels=["5", "8", "11"],
                url="https://ospi.k12.wa.us/assessment/state-assessments/wcas",
                test_type="state",
                notes="Computer-based assessment aligned to NGSS"
            ),
        ],

        contacts={
            "email": "johanna.brown@k12.wa.us",
            "name": "Johanna Brown, Science Assessment and Standards Coordinator"
        },

        resources={
            "curriculum": "https://ospi.k12.wa.us/student-success/resources-subject-area/science/science-curriculum",
            "assessment": "https://ospi.k12.wa.us/assessment/state-assessments/wcas"
        },

        notes="Washington adopted NGSS in October 2013, updated to version 2.0 in 2024. Standards are identical to NGSS.",
        research_status="COMPLETE",
        last_updated="2026-02-03"
    ),

    "OR": StateStandards(
        state_name="Oregon",
        state_abbrev="OR",
        agency_name="Oregon Department of Education",
        website="https://www.oregon.gov/ode",
        science_page="https://www.oregon.gov/ode/educator-resources/standards/science/pages/science-standards.aspx",
        ngss_status="direct_adoption",
        standards_name="Oregon K-12 Science Standards",
        adoption_date="March 2014 (Updated June 2022)",

        documents=[
            StandardsDocument(
                title="K-12 Oregon Science Standards with Guidance",
                url="https://www.oregon.gov/ode/educator-resources/standards/science/Documents/K-12%20%20Oregon%20Science%20Standards%20with%20Guidance.pdf",
                grade_levels=["K", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12"],
                document_type="complete_k12",
                format="PDF",
                notes="Complete K-12 standards in one document"
            ),
            StandardsDocument(
                title="Grade K Standards with Guidance",
                url="https://www.oregon.gov/ode/educator-resources/standards/science/Documents/Grade%20K%20Science%20Standards%20with%20Guidance.pdf",
                grade_levels=["K"],
                document_type="grade_specific",
                format="PDF"
            ),
            StandardsDocument(
                title="Grade 1 Standards with Guidance",
                url="https://www.oregon.gov/ode/educator-resources/standards/science/Documents/Grade%201%20Science%20Standards%20with%20Guidance.pdf",
                grade_levels=["1"],
                document_type="grade_specific",
                format="PDF"
            ),
            StandardsDocument(
                title="Grade 2 Standards with Guidance",
                url="https://www.oregon.gov/ode/educator-resources/standards/science/Documents/Grade%202%20Science%20Standards%20with%20Guidance.pdf",
                grade_levels=["2"],
                document_type="grade_specific",
                format="PDF"
            ),
            StandardsDocument(
                title="Grade 3 Standards with Guidance",
                url="https://www.oregon.gov/ode/educator-resources/standards/science/Documents/Grade%203%20Science%20Standards%20with%20Guidance.pdf",
                grade_levels=["3"],
                document_type="grade_specific",
                format="PDF"
            ),
            StandardsDocument(
                title="Grade 4 Standards with Guidance",
                url="https://www.oregon.gov/ode/educator-resources/standards/science/Documents/Grade%204%20Science%20Standards%20with%20Guidance.pdf",
                grade_levels=["4"],
                document_type="grade_specific",
                format="PDF"
            ),
            StandardsDocument(
                title="Grade 5 Standards with Guidance",
                url="https://www.oregon.gov/ode/educator-resources/standards/science/Documents/Grade%205%20Science%20Standards%20with%20Guidance.pdf",
                grade_levels=["5"],
                document_type="grade_specific",
                format="PDF"
            ),
        ],

        assessments=[
            Assessment(
                name="Oregon Statewide Assessment System (OSAS) Science",
                grade_levels=["5", "8", "11"],
                url="https://www.oregon.gov/ode/educator-resources/assessment/pages/science.aspx",
                test_type="state",
                notes="Computer-adaptive test"
            ),
            Assessment(
                name="Interim Assessments",
                grade_levels=["3", "4", "5", "6", "7", "8", "9", "10", "11", "12"],
                test_type="interim",
                notes="Optional formative assessments"
            ),
            Assessment(
                name="Local Performance Assessments",
                grade_levels=["3", "4", "5", "6", "7", "8"],
                test_type="local",
                notes="Required by OAR 581-022-0615"
            ),
        ],

        contacts={
            "email": "mariela.salamanuesbao@ode.oregon.gov",
            "name": "Mariela Salamanues-Bao, Science Specialist"
        },

        notes="Oregon adopted NGSS in March 2014. 2022 update added climate change connections (^) and clarification statements for K-5.",
        research_status="COMPLETE",
        last_updated="2026-02-03"
    ),

    "CA": StateStandards(
        state_name="California",
        state_abbrev="CA",
        agency_name="California Department of Education",
        website="https://www.cde.ca.gov",
        science_page="https://www.cde.ca.gov/pd/ca/sc/ngssstandards.asp",
        ngss_status="direct_adoption",
        standards_name="California Next Generation Science Standards (CA NGSS)",
        adoption_date="September 4, 2013",

        documents=[
            StandardsDocument(
                title="California NGSS Searchable Standards Database",
                url="https://www2.cde.ca.gov/cacs/science",
                grade_levels=["K", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12"],
                document_type="complete_k12",
                format="Interactive",
                notes="Interactive, searchable database"
            ),
            StandardsDocument(
                title="Kindergarten CA NGSS Standards",
                url="https://www.cde.ca.gov/pd/ca/sc/documents/kindergarten.pdf",
                grade_levels=["K"],
                document_type="grade_specific",
                format="PDF"
            ),
            StandardsDocument(
                title="Grade 1 CA NGSS Standards",
                url="https://www.cde.ca.gov/pd/ca/sc/documents/grade1.pdf",
                grade_levels=["1"],
                document_type="grade_specific",
                format="PDF"
            ),
            StandardsDocument(
                title="Grade 2 CA NGSS Standards",
                url="https://www.cde.ca.gov/pd/ca/sc/documents/grade2.pdf",
                grade_levels=["2"],
                document_type="grade_specific",
                format="PDF"
            ),
            StandardsDocument(
                title="Grade 3 CA NGSS Standards",
                url="https://www.cde.ca.gov/pd/ca/sc/documents/grade3.pdf",
                grade_levels=["3"],
                document_type="grade_specific",
                format="PDF"
            ),
            StandardsDocument(
                title="Grade 4 CA NGSS Standards",
                url="https://www.cde.ca.gov/pd/ca/sc/documents/grade4.pdf",
                grade_levels=["4"],
                document_type="grade_specific",
                format="PDF"
            ),
            StandardsDocument(
                title="Grade 5 CA NGSS Standards",
                url="https://www.cde.ca.gov/pd/ca/sc/documents/grade5.pdf",
                grade_levels=["5"],
                document_type="grade_specific",
                format="PDF"
            ),
        ],

        assessments=[
            Assessment(
                name="California Science Test (CAST)",
                grade_levels=["5", "8"],
                url="https://www.cde.ca.gov/ta/tg/ca/",
                test_type="state",
                notes="Computer-based test aligned to CA NGSS"
            ),
            Assessment(
                name="California Science Test (CAST) - High School",
                grade_levels=["10", "11", "12"],
                url="https://www.cde.ca.gov/ta/tg/ca/",
                test_type="state",
                notes="Administered once in high school (grade 10, 11, or 12)"
            ),
        ],

        contacts={
            "email": "science@cde.ca.gov"
        },

        resources={
            "framework": "https://www.cde.ca.gov/ci/sc/cf/",
            "ep_and_c": "https://www.cde.ca.gov/pd/ca/sc/ngssepcs.asp"
        },

        notes="California adopted NGSS in September 2013 with modifications to include California Environmental Principles & Concepts (EP&Cs).",
        research_status="COMPLETE",
        last_updated="2026-02-03"
    ),

    "TX": StateStandards(
        state_name="Texas",
        state_abbrev="TX",
        agency_name="Texas Education Agency",
        website="https://tea.texas.gov",
        science_page="https://tea.texas.gov/academics/curriculum-standards/teks/science",
        ngss_status="framework_based",
        standards_name="Texas Essential Knowledge and Skills (TEKS) for Science",
        adoption_date="December 2021 (K-8), November 2020 (HS)",

        documents=[
            StandardsDocument(
                title="Kindergarten Science TEKS",
                url="https://tea.texas.gov/sites/default/files/K_Science_TEKS.pdf",
                grade_levels=["K"],
                document_type="grade_specific",
                format="PDF"
            ),
            StandardsDocument(
                title="Grade 1 Science TEKS",
                url="https://tea.texas.gov/sites/default/files/Grade_1_Science_TEKS.pdf",
                grade_levels=["1"],
                document_type="grade_specific",
                format="PDF"
            ),
            StandardsDocument(
                title="Grade 2 Science TEKS",
                url="https://tea.texas.gov/sites/default/files/Grade_2_Science_TEKS.pdf",
                grade_levels=["2"],
                document_type="grade_specific",
                format="PDF"
            ),
            StandardsDocument(
                title="Grade 3 Science TEKS",
                url="https://tea.texas.gov/sites/default/files/Grade_3_Science_TEKS.pdf",
                grade_levels=["3"],
                document_type="grade_specific",
                format="PDF"
            ),
            StandardsDocument(
                title="Grade 4 Science TEKS",
                url="https://tea.texas.gov/sites/default/files/Grade_4_Science_TEKS.pdf",
                grade_levels=["4"],
                document_type="grade_specific",
                format="PDF"
            ),
            StandardsDocument(
                title="Grade 5 Science TEKS",
                url="https://tea.texas.gov/sites/default/files/Grade_5_Science_TEKS.pdf",
                grade_levels=["5"],
                document_type="grade_specific",
                format="PDF"
            ),
            StandardsDocument(
                title="Grade 6 Science TEKS",
                url="https://tea.texas.gov/sites/default/files/Grade_6_Science_TEKS.pdf",
                grade_levels=["6"],
                document_type="grade_specific",
                format="PDF"
            ),
            StandardsDocument(
                title="Grade 7 Science TEKS",
                url="https://tea.texas.gov/sites/default/files/Grade_7_Science_TEKS.pdf",
                grade_levels=["7"],
                document_type="grade_specific",
                format="PDF"
            ),
            StandardsDocument(
                title="Grade 8 Science TEKS",
                url="https://tea.texas.gov/sites/default/files/Grade_8_Science_TEKS.pdf",
                grade_levels=["8"],
                document_type="grade_specific",
                format="PDF"
            ),
        ],

        assessments=[
            Assessment(
                name="STAAR Science",
                grade_levels=["5", "8"],
                url="https://tea.texas.gov/student-assessment/testing/staar",
                test_type="state",
                notes="State of Texas Assessments of Academic Readiness"
            ),
        ],

        contacts={
            "email": "curriculum@tea.texas.gov"
        },

        resources={
            "teks_guide": "https://teksguide.org/",
            "resource_system": "https://www.teksresourcesystem.net/"
        },

        notes="Texas uses TEKS framework, NOT NGSS. K-8 TEKS revised December 2021, HS TEKS revised November 2020. Comprehensive TEKS Guide available at teksguide.org.",
        research_status="COMPLETE",
        last_updated="2026-02-03"
    ),

    "NY": StateStandards(
        state_name="New York",
        state_abbrev="NY",
        agency_name="New York State Education Department",
        website="https://www.nysed.gov",
        science_page="https://www.nysed.gov/curriculum-instruction/science-learning-standards",
        ngss_status="framework_based",
        standards_name="New York State P-12 Science Learning Standards (NYSP12SLS)",
        adoption_date="2016",

        documents=[
            StandardsDocument(
                title="P-2 Science Learning Standards",
                url="https://www.nysed.gov/sites/default/files/programs/curriculum-instruction/p-2-science-learning-standards.pdf",
                grade_levels=["K", "1", "2"],
                document_type="grade_band",
                format="PDF",
                notes="Pre-K through Grade 2"
            ),
            StandardsDocument(
                title="Grades 3-5 Science Learning Standards",
                url="https://www.nysed.gov/sites/default/files/programs/curriculum-instruction/3-5-science-learning-standards.pdf",
                grade_levels=["3", "4", "5"],
                document_type="grade_band",
                format="PDF"
            ),
            StandardsDocument(
                title="Grades 6-8 Science Learning Standards",
                url="https://www.nysed.gov/sites/default/files/programs/curriculum-instruction/6-8-science-learning-standards.pdf",
                grade_levels=["6", "7", "8"],
                document_type="grade_band",
                format="PDF",
                notes="Middle School"
            ),
            StandardsDocument(
                title="High School Science Learning Standards",
                url="https://www.nysed.gov/sites/default/files/programs/curriculum-instruction/hs-science-learning-standards.pdf",
                grade_levels=["9", "10", "11", "12"],
                document_type="grade_band",
                format="PDF",
                notes="Grades 9-12"
            ),
        ],

        assessments=[
            Assessment(
                name="New York State Science Test",
                grade_levels=["4", "8"],
                url="https://www.nysed.gov/state-assessment/science",
                test_type="state",
                notes="Grade 4 and 8 state tests"
            ),
            Assessment(
                name="Regents Examinations in Science",
                grade_levels=["9", "10", "11", "12"],
                url="https://www.nysed.gov/state-assessment/regents-examinations",
                test_type="state",
                notes="Living Environment, Earth Science, Chemistry, Physics. Requires 1,200 minutes of lab for each Regents course."
            ),
        ],

        contacts={
            "email": "ScienceStandards@nysed.gov"
        },

        resources={
            "curriculum_modules": "https://www.nysed.gov/curriculum-instruction/new-york-state-science-learning-standards-curriculum-modules"
        },

        notes="New York adopted P-12 Science Learning Standards in 2016, adapted from NGSS with modifications. High school Regents courses require 1,200 minutes of laboratory experience.",
        research_status="COMPLETE",
        last_updated="2026-02-03"
    ),
}


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


def get_documents_for_grade(state: StateStandards, grade: str) -> List[StandardsDocument]:
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

    print(f"\n{'='*80}")
    print(f"STATES WITH STANDARDS FOR GRADE {grade}")
    print(f"{'='*80}\n")

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

    print(f"\n{'='*80}")
    print(f"{state.state_name} ({state_abbrev}) - SCIENCE STANDARDS")
    print(f"{'='*80}\n")

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
        print(f"\n{'='*80}")
        print(f"GRADE {grade} STANDARDS")
        print(f"{'='*80}\n")

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

    print(f"\n{'='*80}")
    print(f"{state.state_name} ({state_abbrev}) - K-12 COVERAGE")
    print(f"{'='*80}\n")

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

    print(f"\n{'='*80}")


def cmd_compare(grade: str):
    """Compare all states for a specific grade."""
    grade = normalize_grade(grade)

    print(f"\n{'='*80}")
    print(f"GRADE {grade} STANDARDS - STATE COMPARISON")
    print(f"{'='*80}\n")

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
        print(f"  {state_abbrev}: {state.state_name} ({state.standards_name}) - {len(docs)} document(s)")

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

    print(f"\n{'='*80}")
    print(f"RESEARCH QUERIES FOR {state_name} ({state_abbrev})")
    print(f"{'='*80}\n")

    queries = [
        f'"{state_name} department of education" science standards',
        f'site:{state.website.replace("https://", "").replace("http://", "")} science standards K-12',
        f'"{state_name} science standards" PDF',
        f'"{state_name} NGSS adoption"',
        f'"{state_name} science assessment"',
    ]

    if grade:
        grade = normalize_grade(grade)
        queries.extend([
            f'"{state_name} grade {grade} science standards"',
            f'"{state_name} science standards" "grade {grade}"',
            f'"{state_name} science assessment" grade {grade}',
        ])

    print("Suggested search queries:\n")
    for i, query in enumerate(queries, 1):
        print(f"{i}. {query}")

    print(f"\nDirect URLs to check:\n")
    print(f"1. {state.website}")
    if state.science_page:
        print(f"2. {state.science_page}")


def cmd_list():
    """List all states in the database with their status."""
    print(f"\n{'='*80}")
    print(f"STATE SCIENCE STANDARDS DATABASE")
    print(f"{'='*80}\n")

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

    print(f"{'='*80}")
    print(f"Total: {len(STATES_DB)} states")
    print(f"Complete: {len(complete_states)}")
    print(f"Pending: {len(pending_states)}")
    print(f"{'='*80}\n")


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
      Example: python state-science-standards-system.py search 3

  state <ST> [grade]
      Get detailed information about a state's standards
      Optionally specify a grade to see grade-specific info
      Example: python state-science-standards-system.py state WA 5

  range <ST>
      Show complete K-12 coverage for a state
      Example: python state-science-standards-system.py range CA

  compare <grade>
      Compare all states for a specific grade
      Example: python state-science-standards-system.py compare 5

  queries <ST> [grade]
      Generate search queries for researching a state
      Example: python state-science-standards-system.py queries IL 4

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
            print("Usage: python state-science-standards-system.py search <grade>")
            return
        cmd_search(sys.argv[2])
    elif command == "state":
        if len(sys.argv) < 3:
            print("Error: state command requires a state abbreviation")
            print("Usage: python state-science-standards-system.py state <ST> [grade]")
            return
        grade = sys.argv[3] if len(sys.argv) > 3 else None
        cmd_state(sys.argv[2], grade)
    elif command == "range":
        if len(sys.argv) < 3:
            print("Error: range command requires a state abbreviation")
            print("Usage: python state-science-standards-system.py range <ST>")
            return
        cmd_range(sys.argv[2])
    elif command == "compare":
        if len(sys.argv) < 3:
            print("Error: compare command requires a grade")
            print("Usage: python state-science-standards-system.py compare <grade>")
            return
        cmd_compare(sys.argv[2])
    elif command == "queries":
        if len(sys.argv) < 3:
            print("Error: queries command requires a state abbreviation")
            print("Usage: python state-science-standards-system.py queries <ST> [grade]")
            return
        grade = sys.argv[3] if len(sys.argv) > 3 else None
        cmd_queries(sys.argv[2], grade)
    else:
        print(f"Error: Unknown command '{command}'")
        print_usage()


if __name__ == "__main__":
    main()
