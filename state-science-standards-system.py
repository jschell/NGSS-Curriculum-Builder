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

    "AR": StateStandards(
        state_name="Arkansas",
        state_abbrev="AR",
        agency_name="Arkansas Division of Elementary and Secondary Education",
        website="https://dese.ade.arkansas.gov",
        science_page="https://dese.ade.arkansas.gov/Offices/learning-services/curriculum-support/science-standards-and-courses",
        ngss_status="direct_adoption",
        standards_name="Arkansas K-12 Science Standards",
        adoption_date="2013",

        documents=[
            StandardsDocument(
                title="Arkansas K-12 Science Standards",
                url="https://www.nextgenscience.org/sites/default/files/Arkansas%20K-12%20Science%20Standards.pdf",
                grade_levels=["K", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12"],
                document_type="complete_k12",
                format="PDF",
                notes="Based on A Framework for K-12 Science Education"
            ),
        ],

        assessments=[
            Assessment(
                name="Arkansas Science Assessment",
                grade_levels=["5", "7"],
                test_type="state",
                notes="State science assessment"
            ),
        ],

        contacts={
            "email": "science@ade.arkansas.gov"
        },

        notes="Arkansas was a Lead State Partner in developing NGSS. Standards based on A Framework for K-12 Science Education.",
        research_status="COMPLETE",
        last_updated="2026-02-04"
    ),

    "CT": StateStandards(
        state_name="Connecticut",
        state_abbrev="CT",
        agency_name="Connecticut State Department of Education",
        website="https://portal.ct.gov/SDE",
        science_page="https://portal.ct.gov/sde/science/science-standards-and-resources",
        ngss_status="direct_adoption",
        standards_name="Connecticut Next Generation Science Standards (CT NGSS)",
        adoption_date="November 4, 2015",

        documents=[
            StandardsDocument(
                title="Connecticut Next Generation Science Standards",
                url="https://www.nextgenscience.org/sites/default/files/Connecticut%20NGSS%20K-12.pdf",
                grade_levels=["K", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12"],
                document_type="complete_k12",
                format="PDF",
                notes="Adopted by unanimous vote of State Board of Education"
            ),
        ],

        assessments=[
            Assessment(
                name="Connecticut Next Generation Science Assessment (NGSA)",
                grade_levels=["5", "8", "11"],
                url="https://ct.portal.cambiumast.com/ngss.html",
                test_type="state",
                notes="Aligned to NGSS across corresponding grade bands"
            ),
            Assessment(
                name="NGSS Interim Assessments",
                grade_levels=["K", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12"],
                test_type="interim",
                notes="Available August through May"
            ),
        ],

        contacts={
            "email": "sde.ngss@ct.gov"
        },

        notes="Connecticut adopted NGSS by unanimous vote in November 2015.",
        research_status="COMPLETE",
        last_updated="2026-02-04"
    ),

    "DE": StateStandards(
        state_name="Delaware",
        state_abbrev="DE",
        agency_name="Delaware Department of Education",
        website="https://education.delaware.gov",
        science_page="https://education.delaware.gov/educators/academic-support/standards-and-assessments/science/",
        ngss_status="direct_adoption",
        standards_name="Delaware Science Standards (NGSS)",
        adoption_date="September 19, 2013",

        documents=[
            StandardsDocument(
                title="Delaware Science Standards K-12",
                url="https://education.delaware.gov/educators/academic-support/standards-and-assessments/science/de-science-standards/",
                grade_levels=["K", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12"],
                document_type="complete_k12",
                format="HTML",
                notes="Organized into grade band content standards (K-3, 4-5, 6-8, 9-12)"
            ),
        ],

        assessments=[
            Assessment(
                name="DeSSA (Delaware State Science Assessment)",
                grade_levels=["5", "8", "11"],
                test_type="state",
                notes="NGSS-aligned state science assessment"
            ),
        ],

        contacts={
            "email": "dedoe_science@doe.k12.de.us"
        },

        notes="Delaware was the seventh state to adopt NGSS with a unanimous 6-0 vote in September 2013. Delaware was a Lead State Partner in NGSS development.",
        research_status="COMPLETE",
        last_updated="2026-02-04"
    ),

    "DC": StateStandards(
        state_name="District of Columbia",
        state_abbrev="DC",
        agency_name="Office of the State Superintendent of Education (OSSE)",
        website="https://osse.dc.gov",
        science_page="https://osse.dc.gov/service/next-generation-science-standards-ngss-page",
        ngss_status="direct_adoption",
        standards_name="Next Generation Science Standards (NGSS)",
        adoption_date="December 18, 2013",

        documents=[
            StandardsDocument(
                title="DC Next Generation Science Standards",
                url="https://osse.dc.gov/service/next-generation-science-standards-ngss-page",
                grade_levels=["K", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12"],
                document_type="complete_k12",
                format="HTML",
                notes="Based on National Research Council's Framework for K-12 Science Education"
            ),
        ],

        assessments=[
            Assessment(
                name="DC Science Assessment",
                grade_levels=["5", "8"],
                test_type="state",
                notes="NGSS-aligned assessment"
            ),
        ],

        contacts={
            "email": "osse@dc.gov"
        },

        notes="DC State Board of Education adopted NGSS in December 2013 with an 8-1 vote, becoming the ninth jurisdiction to adopt these standards. Implementation began in 2016-17 school year.",
        research_status="COMPLETE",
        last_updated="2026-02-04"
    ),

    "HI": StateStandards(
        state_name="Hawaii",
        state_abbrev="HI",
        agency_name="Hawaii Department of Education",
        website="https://hawaiipublicschools.org",
        science_page="https://www.hawaiipublicschools.org/TeachingAndLearning/StudentLearning/ngss/Pages/default.aspx",
        ngss_status="direct_adoption",
        standards_name="Hawaii Next Generation Science Standards",
        adoption_date="February 2016",

        documents=[
            StandardsDocument(
                title="Hawaii NGSS Standards K-12",
                url="https://www.hawaiipublicschools.org/TeachingAndLearning/StudentLearning/ngss/Pages/default.aspx",
                grade_levels=["K", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12"],
                document_type="complete_k12",
                format="HTML",
                notes="Three-dimensional approach integrating practices, concepts, and core ideas"
            ),
        ],

        assessments=[
            Assessment(
                name="Hawaii State Science Assessment (HSSA)",
                grade_levels=["4", "8"],
                test_type="state",
                notes="NGSS-aligned state assessment"
            ),
        ],

        contacts={
            "email": "science@hidoe.k12.hi.us"
        },

        resources={
            "learning_design": "https://learningdesign.hawaiipublicschools.org/standards-based-content/science"
        },

        notes="Hawaii Board of Education adopted NGSS in February 2016. Full implementation completed by 2019-20 school year.",
        research_status="COMPLETE",
        last_updated="2026-02-04"
    ),

    "IL": StateStandards(
        state_name="Illinois",
        state_abbrev="IL",
        agency_name="Illinois State Board of Education",
        website="https://www.isbe.net",
        science_page="https://www.isbe.net/Pages/Science-Standards.aspx",
        ngss_status="direct_adoption",
        standards_name="Illinois Learning Standards for Science",
        adoption_date="2014",

        documents=[
            StandardsDocument(
                title="Illinois Learning Standards for Science (NGSS)",
                url="https://www.isbe.net/Documents/Next-Gen-Science-Std.pdf",
                grade_levels=["K", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12"],
                document_type="complete_k12",
                format="PDF",
                notes="Based on NGSS, adopted 2014"
            ),
        ],

        assessments=[
            Assessment(
                name="Illinois Science Assessment (ISA)",
                grade_levels=["5", "8", "11"],
                url="https://www.isbe.net/assessment/science",
                test_type="state",
                notes="Aligned to Illinois Learning Standards for Science incorporating NGSS"
            ),
        ],

        contacts={
            "email": "science@isbe.net"
        },

        notes="Illinois became one of 26 state partners in 2011 to guide NGSS development. Climate change education requirement takes effect in 2026-27 school year.",
        research_status="COMPLETE",
        last_updated="2026-02-04"
    ),

    "IA": StateStandards(
        state_name="Iowa",
        state_abbrev="IA",
        agency_name="Iowa Department of Education",
        website="https://educate.iowa.gov",
        science_page="https://educate.iowa.gov/pk-12/standards/academics/science",
        ngss_status="direct_adoption",
        standards_name="Iowa Academic Standards for Science",
        adoption_date="August 6, 2015 (Revised May 8, 2025)",

        documents=[
            StandardsDocument(
                title="Iowa Academic Standards for Science",
                url="https://educate.iowa.gov/media/8211/download",
                grade_levels=["K", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12"],
                document_type="complete_k12",
                format="PDF",
                notes="Based on NGSS Performance Expectations, revised 2025"
            ),
        ],

        assessments=[
            Assessment(
                name="Iowa Statewide Assessment of Student Progress (ISASP) Science",
                grade_levels=["5", "8", "10"],
                url="https://educate.iowa.gov/pk-12/standards/instruction/science/science-assessment",
                test_type="state",
                notes="Spring testing window (March-May). First administered spring 2019."
            ),
        ],

        contacts={
            "email": "chris.like@iowa.gov",
            "name": "Christopher Like, Science Program Consultant"
        },

        notes="Iowa was a Lead State Partner in NGSS development. Standards adopted August 2015, with revised version adopted May 2025.",
        research_status="COMPLETE",
        last_updated="2026-02-04"
    ),

    "KS": StateStandards(
        state_name="Kansas",
        state_abbrev="KS",
        agency_name="Kansas State Department of Education",
        website="https://www.ksde.org",
        science_page="https://community.ksde.org/Default.aspx?tabid=5785",
        ngss_status="direct_adoption",
        standards_name="Kansas College and Career Ready Standards for Science",
        adoption_date="June 2013",

        documents=[
            StandardsDocument(
                title="Kansas Science Standards",
                url="https://www.ksde.org/Portals/0/TLA/Accreditation/Science_Standards.pdf",
                grade_levels=["K", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12"],
                document_type="complete_k12",
                format="PDF",
                notes="Standards set in grade bands K-2, 3-4, 5-7, and 8-12"
            ),
        ],

        assessments=[
            Assessment(
                name="Kansas Science Assessment",
                grade_levels=["4", "7"],
                test_type="state",
                notes="Online assessment"
            ),
            Assessment(
                name="Kansas Science Assessment - High School",
                grade_levels=["9", "10", "11", "12"],
                test_type="state",
                notes="Assessed once in high school"
            ),
        ],

        contacts={
            "email": "science@ksde.org"
        },

        notes="Kansas State Board of Education adopted NGSS in June 2013 with an 8-2 vote. Three-dimensional standards integrating practices, core ideas, and crosscutting concepts.",
        research_status="COMPLETE",
        last_updated="2026-02-04"
    ),

    "KY": StateStandards(
        state_name="Kentucky",
        state_abbrev="KY",
        agency_name="Kentucky Department of Education",
        website="https://www.education.ky.gov",
        science_page="https://www.education.ky.gov/curriculum/conpro/science/Pages/default.aspx",
        ngss_status="direct_adoption",
        standards_name="Kentucky Academic Standards for Science",
        adoption_date="2013 (Revised 2022)",

        documents=[
            StandardsDocument(
                title="Kentucky Academic Standards for Science 2022",
                url="https://www.education.ky.gov/curriculum/standards/kyacadstand/Documents/Kentucky_Academic_Standards_for_Science_2022.pdf",
                grade_levels=["K", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12"],
                document_type="complete_k12",
                format="PDF",
                notes="Based on Framework for K-12 Science Education"
            ),
            StandardsDocument(
                title="High School Science Course Standards",
                url="https://www.education.ky.gov/curriculum/standards/kyacadstand/Documents/High_School_Science_Course_Standards_Documents.pdf",
                grade_levels=["9", "10", "11", "12"],
                document_type="grade_band",
                format="PDF",
                notes="High school course-specific standards"
            ),
        ],

        assessments=[
            Assessment(
                name="Kentucky Science Assessment",
                grade_levels=["4", "8", "11"],
                test_type="state",
                notes="Part of Kentucky assessment system"
            ),
        ],

        contacts={
            "email": "science@education.ky.gov"
        },

        resources={
            "kystandards": "https://kystandards.org"
        },

        notes="Kentucky was a Lead State Partner in NGSS development. Standards implemented beginning 2023-24 school year.",
        research_status="COMPLETE",
        last_updated="2026-02-04"
    ),

    "ME": StateStandards(
        state_name="Maine",
        state_abbrev="ME",
        agency_name="Maine Department of Education",
        website="https://www.maine.gov/doe",
        science_page="https://www.maine.gov/doe/learning/content/scienceandtech/nextgen",
        ngss_status="direct_adoption",
        standards_name="Maine Science and Engineering Standards",
        adoption_date="April 19, 2019",

        documents=[
            StandardsDocument(
                title="Maine Science and Engineering Standards",
                url="https://www.maine.gov/doe/learning/content/scienceandtech/nextgen",
                grade_levels=["K", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12"],
                document_type="complete_k12",
                format="HTML",
                notes="Heavily adapted from NGSS. Arranged in grade bands K-2, 3-5, 6-8, 9-12"
            ),
        ],

        assessments=[
            Assessment(
                name="Maine Science Assessment",
                grade_levels=["5", "8", "11"],
                url="https://www11.maine.gov/doe/Testing_Accountability/MECAS/Generalscience",
                test_type="state",
                notes="Aligned to NGSS"
            ),
        ],

        contacts={
            "email": "science@maine.gov"
        },

        notes="Maine was a Lead State Partner in NGSS development. Current standards signed into law April 19, 2019.",
        research_status="COMPLETE",
        last_updated="2026-02-04"
    ),

    "MD": StateStandards(
        state_name="Maryland",
        state_abbrev="MD",
        agency_name="Maryland State Department of Education",
        website="https://www.marylandpublicschools.org",
        science_page="https://www.marylandpublicschools.org/about/Pages/DCAA/Science/index.aspx",
        ngss_status="direct_adoption",
        standards_name="Maryland Next Generation Science Standards (NGSS)",
        adoption_date="June 25, 2013",

        documents=[
            StandardsDocument(
                title="Maryland NGSS K-12",
                url="https://www.nextgenscience.org/standards",
                grade_levels=["K", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12"],
                document_type="complete_k12",
                format="HTML",
                notes="Maryland is a Lead State for NGSS"
            ),
        ],

        assessments=[
            Assessment(
                name="Maryland Integrated Science Assessment (MISA)",
                grade_levels=["5", "8"],
                url="https://www.marylandpublicschools.org/about/Pages/DAAIT/Assessment/MISA/index.aspx",
                test_type="state",
                notes="Grades 5 and 8 assess elementary and middle school NGSS standards"
            ),
            Assessment(
                name="MCAP Life Science MISA",
                grade_levels=["9", "10", "11", "12"],
                test_type="state",
                notes="End-of-course exam for high school Biology/Life Science"
            ),
        ],

        contacts={
            "email": "[email protected]",
            "name": "Dr. Elise Brown, Assistant State Superintendent"
        },

        notes="Maryland was a Lead State for NGSS adoption on June 25, 2013. Full implementation by 2017-18 school year.",
        research_status="COMPLETE",
        last_updated="2026-02-04"
    ),

    "MI": StateStandards(
        state_name="Michigan",
        state_abbrev="MI",
        agency_name="Michigan Department of Education",
        website="https://www.michigan.gov/mde",
        science_page="https://www.michigan.gov/mde/services/academic-standards/science",
        ngss_status="direct_adoption",
        standards_name="Michigan K-12 Science Standards",
        adoption_date="November 10, 2015",

        documents=[
            StandardsDocument(
                title="Michigan K-12 Science Standards",
                url="https://www.michigan.gov/documents/mde/K-12_Science_Performance_Expectations_v5_496901_7.pdf",
                grade_levels=["K", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12"],
                document_type="complete_k12",
                format="PDF",
                notes="Derived from NGSS with Michigan-specific contexts"
            ),
        ],

        assessments=[
            Assessment(
                name="M-STEP Science",
                grade_levels=["5", "8", "11"],
                test_type="state",
                notes="Michigan Student Test of Educational Progress"
            ),
        ],

        contacts={
            "email": "mde-science@michigan.gov"
        },

        notes="Michigan was a lead partner in NGSS development. Adopted November 10, 2015, becoming the 17th state to adopt NGSS. Standards include Michigan-specific contexts for Great Lakes Basin and state-specific flora/fauna.",
        research_status="COMPLETE",
        last_updated="2026-02-04"
    ),

    "NV": StateStandards(
        state_name="Nevada",
        state_abbrev="NV",
        agency_name="Nevada Department of Education",
        website="https://doe.nv.gov",
        science_page="https://doe.nv.gov/offices/office-of-teaching-and-learning/science",
        ngss_status="direct_adoption",
        standards_name="Nevada Academic Content Standards for Science (NVACSS)",
        adoption_date="February 2014",

        documents=[
            StandardsDocument(
                title="Nevada Academic Content Standards for Science",
                url="https://doe.nv.gov/uploadedFiles/nde.doe.nv.gov/content/Nevada_Academic_Standards/Science/NSACCSScienceTopics.pdf",
                grade_levels=["K", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12"],
                document_type="complete_k12",
                format="PDF",
                notes="Based on NGSS, adopted February 2014"
            ),
        ],

        assessments=[
            Assessment(
                name="Nevada Science Assessment",
                grade_levels=["5", "8", "10"],
                test_type="state",
                notes="NGSS-aligned state assessment"
            ),
        ],

        contacts={
            "email": "science@doe.nv.gov"
        },

        notes="Nevada State Board of Education unanimously adopted NGSS in February 2014, becoming the tenth NGSS adopter.",
        research_status="COMPLETE",
        last_updated="2026-02-04"
    ),

    "NH": StateStandards(
        state_name="New Hampshire",
        state_abbrev="NH",
        agency_name="New Hampshire Department of Education",
        website="https://www.education.nh.gov",
        science_page="https://www.education.nh.gov/who-we-are/division-of-learner-support/bureau-of-instructional-support/career-and-college-ready-standards",
        ngss_status="direct_adoption",
        standards_name="New Hampshire College and Career Ready Science Standards (NGSS)",
        adoption_date="2016",

        documents=[
            StandardsDocument(
                title="New Hampshire NGSS Standards",
                url="https://www.nextgenscience.org/standards",
                grade_levels=["K", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12"],
                document_type="complete_k12",
                format="HTML",
                notes="K-5 grade-by-grade, middle school and high school standards"
            ),
        ],

        assessments=[
            Assessment(
                name="New Hampshire Science Assessment",
                grade_levels=["5", "8", "11"],
                test_type="state",
                notes="NGSS-aligned assessment"
            ),
        ],

        contacts={
            "email": "science@doe.nh.gov"
        },

        notes="Over 90% of New Hampshire local communities were already implementing NGSS before state adoption. Standards incorporate 3-dimensional learning strategy.",
        research_status="COMPLETE",
        last_updated="2026-02-04"
    ),

    "NJ": StateStandards(
        state_name="New Jersey",
        state_abbrev="NJ",
        agency_name="New Jersey Department of Education",
        website="https://www.nj.gov/education",
        science_page="https://www.nj.gov/education/standards/science/curriculum.shtml",
        ngss_status="direct_adoption",
        standards_name="New Jersey Student Learning Standards for Science (NJSLS-S)",
        adoption_date="July 9, 2014 (Updated 2020)",

        documents=[
            StandardsDocument(
                title="NJ Student Learning Standards Science K-5",
                url="https://www.nj.gov/education/standards/science/Docs/NJSLS-Science_K-5.pdf",
                grade_levels=["K", "1", "2", "3", "4", "5"],
                document_type="grade_band",
                format="PDF",
                notes="Elementary K-5 standards"
            ),
            StandardsDocument(
                title="NJ Student Learning Standards Science 6-12",
                url="https://www.nj.gov/education/standards/science/",
                grade_levels=["6", "7", "8", "9", "10", "11", "12"],
                document_type="grade_band",
                format="HTML",
                notes="Middle and high school standards"
            ),
        ],

        assessments=[
            Assessment(
                name="New Jersey Science Assessment",
                grade_levels=["5", "8", "11"],
                test_type="state",
                notes="NGSS-aligned state assessment"
            ),
        ],

        contacts={
            "email": "science@doe.nj.gov"
        },

        notes="New Jersey was a Lead State Partner in NGSS development. State Board adopted NGSS July 9, 2014. Standards updated in 2020.",
        research_status="COMPLETE",
        last_updated="2026-02-04"
    ),

    "NM": StateStandards(
        state_name="New Mexico",
        state_abbrev="NM",
        agency_name="New Mexico Public Education Department",
        website="https://webnew.ped.state.nm.us",
        science_page="https://webnew.ped.state.nm.us/bureaus/math-science/nm-stem-ready-science/",
        ngss_status="direct_adoption",
        standards_name="NM STEM Ready! Science Standards",
        adoption_date="2018",

        documents=[
            StandardsDocument(
                title="NM STEM Ready! Science Standards",
                url="https://webnew.ped.state.nm.us/bureaus/math-science/nm-stem-ready-science/nm-stem-ready-science-standards/",
                grade_levels=["K", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12"],
                document_type="complete_k12",
                format="HTML",
                notes="NGSS plus six New Mexico-specific science standards"
            ),
        ],

        assessments=[
            Assessment(
                name="New Mexico Science Assessment",
                grade_levels=["5", "8", "11"],
                test_type="state",
                notes="NGSS-aligned assessment"
            ),
        ],

        contacts={
            "email": "science@ped.nm.gov"
        },

        notes="New Mexico approved NGSS in 2018, adding six New Mexico-specific science standards. Standards became effective July 1, 2018.",
        research_status="COMPLETE",
        last_updated="2026-02-04"
    ),

    "RI": StateStandards(
        state_name="Rhode Island",
        state_abbrev="RI",
        agency_name="Rhode Island Department of Education",
        website="https://ride.ri.gov",
        science_page="https://www.ride.ri.gov/instructionassessment/science.aspx",
        ngss_status="direct_adoption",
        standards_name="Rhode Island Next Generation Science Standards",
        adoption_date="Spring 2013 (Reaffirmed 2024)",

        documents=[
            StandardsDocument(
                title="Rhode Island NGSS Standards",
                url="https://www.nextgenscience.org/standards",
                grade_levels=["K", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12"],
                document_type="complete_k12",
                format="HTML",
                notes="Rhode Island was first state to adopt NGSS"
            ),
        ],

        assessments=[
            Assessment(
                name="Rhode Island Next Generation Science Assessment (NGSA)",
                grade_levels=["5", "8", "11"],
                url="https://ride.ri.gov/instruction-assessment/assessment/ngsa-assessment",
                test_type="state",
                notes="Administered since May 2018, replaced NECAP science assessments"
            ),
        ],

        contacts={
            "email": "science@ride.ri.gov"
        },

        notes="Rhode Island was the first state to adopt NGSS in spring 2013 and served as a Lead State Partner in NGSS development. Standards reaffirmed by Board of Education in 2024.",
        research_status="COMPLETE",
        last_updated="2026-02-04"
    ),

    "VT": StateStandards(
        state_name="Vermont",
        state_abbrev="VT",
        agency_name="Vermont Agency of Education",
        website="https://education.vermont.gov",
        science_page="https://education.vermont.gov/student-learning/content-areas/science",
        ngss_status="direct_adoption",
        standards_name="Vermont Next Generation Science Standards",
        adoption_date="2013",

        documents=[
            StandardsDocument(
                title="Vermont NGSS Standards",
                url="https://education.vermont.gov/student-learning/content-areas/science",
                grade_levels=["K", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12"],
                document_type="complete_k12",
                format="HTML",
                notes="Organized in grade bands K-2, 3-5, 6-8, 9-12"
            ),
        ],

        assessments=[
            Assessment(
                name="Vermont Science Assessment (VTSA)",
                grade_levels=["5", "8", "11"],
                test_type="state",
                notes="NGSS-aligned assessment"
            ),
        ],

        contacts={
            "email": "science@vermont.gov"
        },

        notes="Vermont was a Lead State Partner in NGSS development. Adopted NGSS in 2013 as foundation for K-12 science instruction.",
        research_status="COMPLETE",
        last_updated="2026-02-04"
    ),

    "AL": StateStandards(
        state_name="Alabama",
        state_abbrev="AL",
        agency_name="Alabama State Department of Education",
        website="https://www.alabamaachieves.org",
        science_page="https://www.alabamaachieves.org/acad-stand/",
        ngss_status="framework_based",
        standards_name="Alabama Course of Study: Science",
        adoption_date="2023",

        documents=[
            StandardsDocument(
                title="2023 Alabama Course of Study: Science",
                url="https://www.alabamaachieves.org/wp-content/uploads/2024/02/AS_20240213_2023-Alabama-Course-of-Study-Science_V1.0.pdf",
                grade_levels=["K", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12"],
                document_type="complete_k12",
                format="PDF",
                notes="Based on Framework for K-12 Science Education (NRC 2012)"
            ),
        ],

        assessments=[
            Assessment(
                name="Alabama Science Assessment",
                grade_levels=["4", "8"],
                test_type="state",
                notes="State science assessment"
            ),
        ],

        contacts={
            "email": "science@alsde.edu"
        },

        resources={
            "amsti": "https://www.amsti.org/science"
        },

        notes="Alabama's 2023 Course of Study reflects the NRC's Framework for K-12 Science Education, incorporating three dimensions: practices, crosscutting concepts, and disciplinary core ideas.",
        research_status="COMPLETE",
        last_updated="2026-02-04"
    ),

    "AZ": StateStandards(
        state_name="Arizona",
        state_abbrev="AZ",
        agency_name="Arizona Department of Education",
        website="https://www.azed.gov",
        science_page="https://www.azed.gov/standards-practices/k-12standards/standards-science",
        ngss_status="framework_based",
        standards_name="Arizona Science Standards",
        adoption_date="October 2018",

        documents=[
            StandardsDocument(
                title="Arizona Science Standards 2018 - Complete K-12",
                url="https://www.azed.gov/sites/default/files/2018/10/Full%20Set%20of%20Standards%20K_12_%20Updated_10_19_19.pdf",
                grade_levels=["K", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12"],
                document_type="complete_k12",
                format="PDF",
                notes="Three-dimensional approach based on Framework for K-12 Science Education"
            ),
        ],

        assessments=[
            Assessment(
                name="AzSCI (Arizona Science Assessment)",
                grade_levels=["5", "8"],
                test_type="state",
                notes="State science assessment"
            ),
            Assessment(
                name="AzSCI High School",
                grade_levels=["9", "10", "11", "12"],
                test_type="state",
                notes="Assessed once in high school"
            ),
        ],

        contacts={
            "email": "science@azed.gov"
        },

        notes="Arizona adopted science standards in October 2018 based on Framework for K-12 Science Education. Not an NGSS state but uses three-dimensional instruction approach.",
        research_status="COMPLETE",
        last_updated="2026-02-04"
    ),

    "CO": StateStandards(
        state_name="Colorado",
        state_abbrev="CO",
        agency_name="Colorado Department of Education",
        website="https://www.cde.state.co.us",
        science_page="https://www.cde.state.co.us/coscience/statestandards",
        ngss_status="framework_based",
        standards_name="Colorado Academic Standards (CAS) - Science",
        adoption_date="2020",

        documents=[
            StandardsDocument(
                title="2020 Colorado Academic Standards: Science",
                url="https://www.cde.state.co.us/coscience/2020cas-sc",
                grade_levels=["K", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12"],
                document_type="complete_k12",
                format="HTML",
                notes="Three main standards: Physical Science, Life Science, Earth/Space Science"
            ),
        ],

        assessments=[
            Assessment(
                name="Colorado Science Assessment (CMAS)",
                grade_levels=["5", "8", "11"],
                test_type="state",
                notes="Colorado Measures of Academic Success"
            ),
        ],

        contacts={
            "email": "science@cde.state.co.us"
        },

        notes="Colorado's science standards leverage Framework for K-12 Science Education. Full implementation in 2021-22 school year.",
        research_status="COMPLETE",
        last_updated="2026-02-04"
    ),

    "FL": StateStandards(
        state_name="Florida",
        state_abbrev="FL",
        agency_name="Florida Department of Education",
        website="https://www.fldoe.org",
        science_page="https://www.fldoe.org/academics/standards/subject-areas/math-science/science/",
        ngss_status="framework_based",
        standards_name="Next Generation Sunshine State Standards (NGSSS) for Science",
        adoption_date="February 2008",

        documents=[
            StandardsDocument(
                title="Florida NGSSS Science Standards",
                url="https://www.cpalms.org/public/search/Standard",
                grade_levels=["K", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12"],
                document_type="complete_k12",
                format="Interactive",
                notes="Searchable database via CPALMS. Four Bodies of Knowledge: Nature of Science, Life Science, Earth Science, Physical Science"
            ),
        ],

        assessments=[
            Assessment(
                name="Statewide Science Assessment",
                grade_levels=["5", "8"],
                url="https://www.fldoe.org/accountability/assessments/k-12-student-assessment/science.stml",
                test_type="state",
                notes="Measures achievement of NGSSS science benchmarks"
            ),
        ],

        contacts={
            "email": "science@fldoe.org"
        },

        resources={
            "cpalms": "https://www.cpalms.org/public/search/Standard"
        },

        notes="Florida adopted NGSSS in February 2008. Standards include 18 Big Ideas that thread throughout all grade levels.",
        research_status="COMPLETE",
        last_updated="2026-02-04"
    ),

    "GA": StateStandards(
        state_name="Georgia",
        state_abbrev="GA",
        agency_name="Georgia Department of Education",
        website="https://gadoe.org",
        science_page="https://gadoe.org/learning/science/",
        ngss_status="framework_based",
        standards_name="Georgia Standards of Excellence (GSE) - Science",
        adoption_date="2016 (Implemented 2017-18)",

        documents=[
            StandardsDocument(
                title="Georgia Science Standards of Excellence K-12",
                url="https://www.georgiastandards.org/Georgia-Standards/Pages/Science.aspx",
                grade_levels=["K", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12"],
                document_type="complete_k12",
                format="HTML",
                notes="Based on Framework for K-12 Science Education and Project 2061 Benchmarks"
            ),
        ],

        assessments=[
            Assessment(
                name="Georgia Milestones Science Assessment",
                grade_levels=["5", "8"],
                test_type="state",
                notes="Part of Georgia Milestones Assessment System"
            ),
        ],

        contacts={
            "email": "science@gadoe.org"
        },

        notes="Georgia science standards first implemented 2017-18 school year. Focus on disciplinary core ideas and crosscutting concepts.",
        research_status="COMPLETE",
        last_updated="2026-02-04"
    ),

    "IN": StateStandards(
        state_name="Indiana",
        state_abbrev="IN",
        agency_name="Indiana Department of Education",
        website="https://www.in.gov/doe",
        science_page="https://www.in.gov/doe/students/indiana-academic-standards/science-and-computer-science/",
        ngss_status="framework_based",
        standards_name="Indiana Academic Standards for Science",
        adoption_date="2023",

        documents=[
            StandardsDocument(
                title="Indiana Academic Standards for Science K-12",
                url="https://www.in.gov/doe/students/indiana-academic-standards/science-and-computer-science/",
                grade_levels=["K", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12"],
                document_type="complete_k12",
                format="HTML",
                notes="Based on Framework for K-12 Science Education and NGSS"
            ),
        ],

        assessments=[
            Assessment(
                name="Indiana Science Assessment (ILEARN)",
                grade_levels=["4", "6"],
                test_type="state",
                notes="Part of ILEARN assessment system"
            ),
            Assessment(
                name="Indiana Biology End of Course Assessment",
                grade_levels=["9", "10", "11", "12"],
                test_type="state",
                notes="High school biology EOC"
            ),
        ],

        contacts={
            "email": "science@doe.in.gov"
        },

        notes="Indiana adopted streamlined K-12 science standards in 2023, effective fall 2023. Three-dimensional standards integrate practices, crosscutting concepts, and core ideas.",
        research_status="COMPLETE",
        last_updated="2026-02-04"
    ),

    "MA": StateStandards(
        state_name="Massachusetts",
        state_abbrev="MA",
        agency_name="Massachusetts Department of Elementary and Secondary Education",
        website="https://www.doe.mass.edu",
        science_page="https://www.doe.mass.edu/stem/ste/standards.html",
        ngss_status="framework_based",
        standards_name="Massachusetts Science and Technology/Engineering Curriculum Framework",
        adoption_date="2016",

        documents=[
            StandardsDocument(
                title="Massachusetts Science and Technology/Engineering Curriculum Framework 2016",
                url="https://www.doe.mass.edu/frameworks/scitech/2016-04.pdf",
                grade_levels=["K", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12"],
                document_type="complete_k12",
                format="PDF",
                notes="Includes life, physical, Earth/space science, and technology/engineering"
            ),
        ],

        assessments=[
            Assessment(
                name="MCAS Science and Technology/Engineering",
                grade_levels=["5", "8"],
                test_type="state",
                notes="Massachusetts Comprehensive Assessment System"
            ),
            Assessment(
                name="MCAS Science and Technology/Engineering - High School",
                grade_levels=["9", "10"],
                test_type="state",
                notes="Typically taken in Grade 10 (Biology)"
            ),
        ],

        contacts={
            "email": "stem@doe.mass.edu"
        },

        notes="Massachusetts 2016 framework reflects changes in science education over past 15 years. Emphasizes mastery of disciplinary core ideas and science/engineering practices.",
        research_status="COMPLETE",
        last_updated="2026-02-04"
    ),

    "MN": StateStandards(
        state_name="Minnesota",
        state_abbrev="MN",
        agency_name="Minnesota Department of Education",
        website="https://education.mn.gov",
        science_page="https://education.mn.gov/MDE/dse/stds/sci/",
        ngss_status="framework_based",
        standards_name="Minnesota Academic Standards in Science",
        adoption_date="2019 (Implemented 2024-25)",

        documents=[
            StandardsDocument(
                title="Minnesota Academic Standards in Science 2019",
                url="https://education.mn.gov/MDE/dse/stds/sci/",
                grade_levels=["K", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12"],
                document_type="complete_k12",
                format="HTML",
                notes="Based on Framework for K-12 Science Education (NRC 2012)"
            ),
        ],

        assessments=[
            Assessment(
                name="Minnesota Comprehensive Assessments (MCA) Science",
                grade_levels=["5", "8"],
                test_type="state",
                notes="State science assessment"
            ),
            Assessment(
                name="MCA Science - High School",
                grade_levels=["10", "11"],
                test_type="state",
                notes="High school science assessment"
            ),
        ],

        contacts={
            "email": "science@state.mn.us"
        },

        notes="2019 standards adopted September 27, 2021, fully implemented 2024-25 school year. Emphasize three dimensions: practices, crosscutting concepts, and disciplinary core ideas.",
        research_status="COMPLETE",
        last_updated="2026-02-04"
    ),

    "NC": StateStandards(
        state_name="North Carolina",
        state_abbrev="NC",
        agency_name="North Carolina Department of Public Instruction",
        website="https://www.dpi.nc.gov",
        science_page="https://www.dpi.nc.gov/districts-schools/classroom-resources/academic-standards/standard-course-study/science",
        ngss_status="framework_based",
        standards_name="North Carolina Standard Course of Study - Science",
        adoption_date="2023 (Implemented 2024)",

        documents=[
            StandardsDocument(
                title="2023 North Carolina K-12 Science Standards",
                url="https://www.dpi.nc.gov/districts-schools/classroom-resources/academic-standards/standard-course-study/science",
                grade_levels=["K", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12"],
                document_type="complete_k12",
                format="HTML",
                notes="First update since 2009, emphasizes Science and Engineering Practices"
            ),
        ],

        assessments=[
            Assessment(
                name="North Carolina Science Assessment (EOG)",
                grade_levels=["5", "8"],
                test_type="state",
                notes="End of Grade science tests"
            ),
            Assessment(
                name="North Carolina Science EOC",
                grade_levels=["9", "10", "11", "12"],
                test_type="state",
                notes="Biology End of Course exam"
            ),
        ],

        contacts={
            "email": "science@dpi.nc.gov"
        },

        notes="North Carolina updated standards approved 2023, required implementation 2024. Designed to foster conceptual understanding and scientific literacy.",
        research_status="COMPLETE",
        last_updated="2026-02-04"
    ),

    "OH": StateStandards(
        state_name="Ohio",
        state_abbrev="OH",
        agency_name="Ohio Department of Education and Workforce",
        website="https://education.ohio.gov",
        science_page="https://education.ohio.gov/Topics/Learning-in-Ohio/Science/Ohios-Learning-Standards-and-MC",
        ngss_status="framework_based",
        standards_name="Ohio's Learning Standards for Science",
        adoption_date="February 2018",

        documents=[
            StandardsDocument(
                title="Ohio's Learning Standards for Science and Model Curriculum",
                url="https://education.ohio.gov/getattachment/Topics/Learning-in-Ohio/Science/Ohios-Learning-Standards-and-MC/SciFinalStandardsMC060719.pdf.aspx",
                grade_levels=["K", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12"],
                document_type="complete_k12",
                format="PDF",
                notes="Adopted February 2018, covers K-8 and high school"
            ),
        ],

        assessments=[
            Assessment(
                name="Ohio State Science Test",
                grade_levels=["5", "8"],
                test_type="state",
                notes="State science assessment"
            ),
        ],

        contacts={
            "email": "science@education.ohio.gov"
        },

        notes="Ohio's 2018 Learning Standards provide logical progression of science content incorporating nature of science and scientific thought processes.",
        research_status="COMPLETE",
        last_updated="2026-02-04"
    ),

    "PA": StateStandards(
        state_name="Pennsylvania",
        state_abbrev="PA",
        agency_name="Pennsylvania Department of Education",
        website="https://www.pa.gov/agencies/education",
        science_page="https://www.pa.gov/agencies/education/programs-and-services/instruction/elementary-and-secondary-education/curriculum/science/science-standards",
        ngss_status="framework_based",
        standards_name="Pennsylvania Integrated Standards for Science, Technology & Engineering, Environmental Literacy & Sustainability (STEELS)",
        adoption_date="January 2022",

        documents=[
            StandardsDocument(
                title="K-12 STEELS Standards",
                url="https://www.pa.gov/content/dam/copapwp-pagov/en/education/documents/instruction/assessment-and-accountability/pssa/assessment-anchors/k-12%20steels%20standards_2023.pdf",
                grade_levels=["K", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12"],
                document_type="complete_k12",
                format="PDF",
                notes="K-12 sequence across strands"
            ),
            StandardsDocument(
                title="Pennsylvania Integrated Standards K-5",
                url="https://www.pa.gov/content/dam/copapwp-pagov/en/stateboard/documents/regulations-and-statements/state-academic-standards/pa%20integrated%20standards%20for%20science%20environment%20ecology%20technology%20and%20engineering-%20k-5.pdf",
                grade_levels=["K", "1", "2", "3", "4", "5"],
                document_type="grade_band",
                format="PDF",
                notes="Elementary standards"
            ),
        ],

        assessments=[
            Assessment(
                name="Pennsylvania Science Assessment (PSSA)",
                grade_levels=["4", "8"],
                test_type="state",
                notes="Pennsylvania System of School Assessment"
            ),
        ],

        contacts={
            "email": "science@pa.gov"
        },

        resources={
            "steels_hub": "https://www.pdesas.org/Page/Viewer/ViewPage/58/"
        },

        notes="STEELS standards adopted January 2022, fully integrated by 2025-26 school year. Replaced 2002 Science and Technology and Environment and Ecology standards.",
        research_status="COMPLETE",
        last_updated="2026-02-04"
    ),

    "TN": StateStandards(
        state_name="Tennessee",
        state_abbrev="TN",
        agency_name="Tennessee Department of Education",
        website="https://www.tn.gov/education",
        science_page="https://www.tn.gov/education/districts/academic-standards/science-standards.html",
        ngss_status="framework_based",
        standards_name="Tennessee Academic Standards for Science",
        adoption_date="October 2022 (Implemented 2025-26)",

        documents=[
            StandardsDocument(
                title="Tennessee Academic Standards for Science",
                url="https://www.tn.gov/content/dam/tn/stateboardofeducation/documents/standards/science/New%2010-28-22%20Science%20Standards.pdf",
                grade_levels=["K", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12"],
                document_type="complete_k12",
                format="PDF",
                notes="Based on Framework for K-12 Science Education"
            ),
        ],

        assessments=[
            Assessment(
                name="Tennessee Science Assessment",
                grade_levels=["5", "8"],
                test_type="state",
                notes="State science assessment"
            ),
        ],

        contacts={
            "email": "science@tn.gov"
        },

        resources={
            "best_for_all": "https://bestforall.tnedu.gov/academic-standards/science"
        },

        notes="Tennessee adopted revised standards October 2022, implemented in classrooms 2025-26 school year. Four disciplinary core ideas: physical, life, earth/space, and engineering/technology.",
        research_status="COMPLETE",
        last_updated="2026-02-04"
    ),

    "UT": StateStandards(
        state_name="Utah",
        state_abbrev="UT",
        agency_name="Utah State Board of Education",
        website="https://schools.utah.gov",
        science_page="https://schools.utah.gov/curr/science",
        ngss_status="framework_based",
        standards_name="Utah Science with Engineering Education (SEEd) Standards",
        adoption_date="2019",

        documents=[
            StandardsDocument(
                title="Utah SEEd Standards",
                url="https://schools.utah.gov/curr/science/_science_/UtahSEEdStandards.pdf",
                grade_levels=["K", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12"],
                document_type="complete_k12",
                format="PDF",
                notes="Written by Utah educators using Framework for K-12 Science Education and NGSS"
            ),
        ],

        assessments=[
            Assessment(
                name="Utah Aspire Plus Science",
                grade_levels=["4", "5", "6", "8"],
                test_type="state",
                notes="State science assessment"
            ),
            Assessment(
                name="Utah Science High School",
                grade_levels=["9", "10", "11"],
                test_type="state",
                notes="Secondary science assessment"
            ),
        ],

        contacts={
            "email": "science@schools.utah.gov"
        },

        notes="Utah SEEd standards built on three dimensions: Science and Engineering Practices, Crosscutting Concepts, and Disciplinary Core Ideas. Utah OER textbooks available for K-12.",
        research_status="COMPLETE",
        last_updated="2026-02-04"
    ),

    "VA": StateStandards(
        state_name="Virginia",
        state_abbrev="VA",
        agency_name="Virginia Department of Education",
        website="https://www.doe.virginia.gov",
        science_page="https://www.doe.virginia.gov/teaching-learning-assessment/k-12-standards-instruction/science/standards-of-learning",
        ngss_status="framework_based",
        standards_name="Virginia Science Standards of Learning (SOL)",
        adoption_date="2018 (Expanded 2025)",

        documents=[
            StandardsDocument(
                title="2018 Science Standards of Learning K-Physics",
                url="https://www.doe.virginia.gov/teaching-learning-assessment/k-12-standards-instruction/science/standards-of-learning",
                grade_levels=["K", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12"],
                document_type="complete_k12",
                format="HTML",
                notes="Includes scientific and engineering practices connected to science concepts"
            ),
        ],

        assessments=[
            Assessment(
                name="Virginia Science SOL Test",
                grade_levels=["5", "8"],
                url="https://www.doe.virginia.gov/teaching-learning-assessment/k-12-standards-instruction/science/assessment-resources",
                test_type="state",
                notes="Standards of Learning tests"
            ),
            Assessment(
                name="Virginia Science EOC Assessments",
                grade_levels=["9", "10", "11", "12"],
                test_type="state",
                notes="Biology, Chemistry, Earth Science, Physics end-of-course tests"
            ),
        ],

        contacts={
            "email": "science@doe.virginia.gov"
        },

        notes="Virginia Board of Education approved 2025 Expanded High School Science SOL in December 2025. 2018 K-Physics standards remain unchanged.",
        research_status="COMPLETE",
        last_updated="2026-02-04"
    ),

    "WI": StateStandards(
        state_name="Wisconsin",
        state_abbrev="WI",
        agency_name="Wisconsin Department of Public Instruction",
        website="https://dpi.wi.gov",
        science_page="https://dpi.wi.gov/science/standards",
        ngss_status="framework_based",
        standards_name="Wisconsin Standards for Science",
        adoption_date="November 13, 2017",

        documents=[
            StandardsDocument(
                title="Wisconsin Standards for Science",
                url="https://dpi.wi.gov/sites/default/files/imce/standards/New%20pdfs/ScienceStandards2017.pdf",
                grade_levels=["K", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12"],
                document_type="complete_k12",
                format="PDF",
                notes="Built from NRC Framework and NGSS, organized in grade bands K-2, 3-5, 6-8, 9-12"
            ),
        ],

        assessments=[
            Assessment(
                name="Wisconsin Forward Exam - Science",
                grade_levels=["4", "8"],
                test_type="state",
                notes="State science assessment"
            ),
            Assessment(
                name="Wisconsin Science Assessment - High School",
                grade_levels=["10"],
                test_type="state",
                notes="High school science assessment"
            ),
        ],

        contacts={
            "email": "science@dpi.wi.gov"
        },

        notes="Wisconsin Standards for Science adopted November 13, 2017. Districts have option to use Wisconsin Standards or NGSS. Goal: students make sense of phenomena and solve problems using three-dimensional learning.",
        research_status="COMPLETE",
        last_updated="2026-02-04"
    ),

    "AK": StateStandards(
        state_name="Alaska",
        state_abbrev="AK",
        agency_name="Alaska Department of Education and Early Development",
        website="https://education.alaska.gov",
        science_page="https://education.alaska.gov/standards/science",
        ngss_status="framework_based",
        standards_name="Science Standards for Alaska",
        adoption_date="2019",

        documents=[
            StandardsDocument(
                title="K-12 Science Standards for Alaska",
                url="https://education.alaska.gov/akstandards/science/science-standards-for-alaska.pdf",
                grade_levels=["K", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12"],
                document_type="complete_k12",
                format="PDF",
                notes="Based on NGSS with strong focus on Alaskan contexts"
            ),
        ],

        assessments=[
            Assessment(
                name="Alaska Science Assessment (ASA)",
                grade_levels=["5", "8", "11"],
                url="https://education.alaska.gov/assessments/science",
                test_type="state",
                notes="State science assessment"
            ),
        ],

        contacts={
            "email": "science@alaska.gov"
        },

        notes="Alaska adopted science standards in 2019, shaped around NGSS with strong focus on relevance to Alaskan contexts. Three-dimensional design for science sense making.",
        research_status="COMPLETE",
        last_updated="2026-02-04"
    ),

    "ID": StateStandards(
        state_name="Idaho",
        state_abbrev="ID",
        agency_name="Idaho State Department of Education",
        website="https://www.sde.idaho.gov",
        science_page="https://www.sde.idaho.gov/about-us/departments/content-and-curriculum/science/",
        ngss_status="framework_based",
        standards_name="Idaho K-12 State Standards for Science",
        adoption_date="2022",

        documents=[
            StandardsDocument(
                title="Idaho K-12 State Standards for Science",
                url="https://www.sde.idaho.gov/wp-content/uploads/2025/09/Idaho-K-12-State-Standards-for-Science.pdf",
                grade_levels=["K", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12"],
                document_type="complete_k12",
                format="PDF",
                notes="Three dimensions: disciplinary core ideas, crosscutting concepts, and science/engineering practices"
            ),
        ],

        assessments=[
            Assessment(
                name="Idaho Standards Achievement Test (ISAT) - Science",
                grade_levels=["5", "7", "10"],
                test_type="state",
                notes="State science assessment"
            ),
        ],

        contacts={
            "email": "science@sde.idaho.gov"
        },

        notes="Idaho 2022 standards structured around three dimensions. Organized by grade level K-12 with Physical Science, Life Science, and Earth/Space Science at each grade.",
        research_status="COMPLETE",
        last_updated="2026-02-04"
    ),

    "LA": StateStandards(
        state_name="Louisiana",
        state_abbrev="LA",
        agency_name="Louisiana Department of Education",
        website="https://doe.louisiana.gov",
        science_page="https://doe.louisiana.gov/educators/instructional-support/planning-resources/k-12-science-resources",
        ngss_status="framework_based",
        standards_name="Louisiana Student Standards for Science (LSSS)",
        adoption_date="2017",

        documents=[
            StandardsDocument(
                title="K-12 Louisiana Student Standards for Science",
                url="https://doe.louisiana.gov/educators/instructional-support/planning-resources/k-12-science-resources",
                grade_levels=["K", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12"],
                document_type="complete_k12",
                format="HTML",
                notes="Louisiana Student Standards for Science"
            ),
        ],

        assessments=[
            Assessment(
                name="Louisiana Educational Assessment Program (LEAP) Science",
                grade_levels=["5", "8"],
                test_type="state",
                notes="State science assessment"
            ),
        ],

        contacts={
            "email": "science@la.gov"
        },

        notes="Louisiana Student Standards for Science include sample scope and sequence documents for K-12 implementation.",
        research_status="COMPLETE",
        last_updated="2026-02-04"
    ),

    "MS": StateStandards(
        state_name="Mississippi",
        state_abbrev="MS",
        agency_name="Mississippi Department of Education",
        website="https://mdek12.org",
        science_page="https://mdek12.org/secondaryeducation/science/",
        ngss_status="framework_based",
        standards_name="Mississippi College- and Career-Readiness Standards (MS CCRS) for Science",
        adoption_date="2018",

        documents=[
            StandardsDocument(
                title="2018 MS College- and Career-Readiness Standards for Science K-12",
                url="https://www.mdek12.org/sites/default/files/documents/Secondary%20Ed/2018-ms_ccrs---sci_k-12_final_20171006.pdf",
                grade_levels=["K", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12"],
                document_type="complete_k12",
                format="PDF",
                notes="Based on Framework for K-12 Science Education (NRC 2012)"
            ),
        ],

        assessments=[
            Assessment(
                name="Mississippi Academic Assessment Program (MAAP) Science",
                grade_levels=["5", "8"],
                test_type="state",
                notes="State science assessment"
            ),
        ],

        contacts={
            "email": "science@mdek12.org"
        },

        notes="2018 MS CCRS for Science built by adapting Framework for K-12 Science Education and combining with Mississippi's previous framework. Three basic content strands: life, physical, and Earth/space science.",
        research_status="COMPLETE",
        last_updated="2026-02-04"
    ),

    "MO": StateStandards(
        state_name="Missouri",
        state_abbrev="MO",
        agency_name="Missouri Department of Elementary and Secondary Education",
        website="https://dese.mo.gov",
        science_page="https://dese.mo.gov/college-career-readiness/curriculum/science",
        ngss_status="framework_based",
        standards_name="Missouri Learning Standards for Science",
        adoption_date="April 19, 2016",

        documents=[
            StandardsDocument(
                title="Missouri Learning Standards Science K-12",
                url="https://dese.mo.gov/media/file/curr-mls-standards-sci-k-12-sboe-2016",
                grade_levels=["K", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12"],
                document_type="complete_k12",
                format="Excel",
                notes="Three-dimensional standards adapted from Framework for K-12 Science Education"
            ),
        ],

        assessments=[
            Assessment(
                name="Missouri Assessment Program (MAP) Science",
                grade_levels=["5", "8"],
                test_type="state",
                notes="State science assessment"
            ),
        ],

        contacts={
            "email": "science@dese.mo.gov"
        },

        notes="Missouri Learning Standards approved April 19, 2016 for implementation beginning 2016-17 school year. Adapted from Framework for K-12 Science Education (NRC 2012).",
        research_status="COMPLETE",
        last_updated="2026-02-04"
    ),

    "MT": StateStandards(
        state_name="Montana",
        state_abbrev="MT",
        agency_name="Montana Office of Public Instruction",
        website="https://opi.mt.gov",
        science_page="https://opi.mt.gov/Educators/Teaching-Learning/K-12-Content-Standards",
        ngss_status="framework_based",
        standards_name="Montana Science Content Standards",
        adoption_date="September 16, 2016",

        documents=[
            StandardsDocument(
                title="Montana Science Content Standards 2016",
                url="https://opi.mt.gov/Portals/182/Page%20Files/K-12%20Content%20Standards%20&%20Revision/Science/Montana-Science-Content-Standards-2016.pdf",
                grade_levels=["K", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12"],
                document_type="complete_k12",
                format="PDF",
                notes="Includes crosscutting concepts and science/engineering practices"
            ),
            StandardsDocument(
                title="Montana Science Model Curriculum Guide",
                url="https://opi.mt.gov/Portals/182/Page%20Files/K-12%20Content%20Standards%20&%20Revision/Science/Montana-Science-Standard-Model-Curriculum-Guide-2016.pdf",
                grade_levels=["K", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12"],
                document_type="complete_k12",
                format="PDF",
                notes="Implementation guide"
            ),
        ],

        assessments=[
            Assessment(
                name="Montana Comprehensive Assessment System (MontCAS) Science",
                grade_levels=["5", "8"],
                test_type="state",
                notes="State science assessment"
            ),
        ],

        contacts={
            "email": "science@mt.gov"
        },

        notes="Montana was a Lead State Partner in NGSS development. Standards adopted September 16, 2016. Encompasses scientific ideas and practices for college/career readiness.",
        research_status="COMPLETE",
        last_updated="2026-02-04"
    ),

    "NE": StateStandards(
        state_name="Nebraska",
        state_abbrev="NE",
        agency_name="Nebraska Department of Education",
        website="https://www.education.ne.gov",
        science_page="https://www.education.ne.gov/science/standards-and-supporting-documents/",
        ngss_status="framework_based",
        standards_name="Nebraska College and Career Ready Standards for Science (NCCRS-S)",
        adoption_date="September 6, 2024",

        documents=[
            StandardsDocument(
                title="Nebraska College and Career Ready Standards for Science",
                url="https://cdn.education.ne.gov/wp-content/uploads/2017/10/Nebraska_Science_Standards_Final_10_23.pdf",
                grade_levels=["K", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12"],
                document_type="complete_k12",
                format="PDF",
                notes="Written at four grade bands: K-2, 3-5, 6-8, 9-12. Based on Framework for K-12 Science Education"
            ),
        ],

        assessments=[
            Assessment(
                name="Nebraska State Accountability Science (NSCAS) Science",
                grade_levels=["5", "8", "11"],
                test_type="state",
                notes="State science assessment"
            ),
        ],

        contacts={
            "email": "science@nebraska.gov"
        },

        notes="Nebraska adopted 2024 standards guided by Framework for K-12 Science Education. Written at grade bands K-2, 3-5, 6-8, 9-12.",
        research_status="COMPLETE",
        last_updated="2026-02-04"
    ),

    "ND": StateStandards(
        state_name="North Dakota",
        state_abbrev="ND",
        agency_name="North Dakota Department of Public Instruction",
        website="https://www.nd.gov/dpi",
        science_page="https://www.nd.gov/dpi/districtsschools/north-dakota-education-content-standards/science",
        ngss_status="framework_based",
        standards_name="North Dakota Science Content Standards",
        adoption_date="February 2019",

        documents=[
            StandardsDocument(
                title="North Dakota Science Content Standards K-12",
                url="https://www.nd.gov/dpi/sites/www/files/documents/Academic%20Support/FINAL%20ND%20Science%20Content%20Standards_rev2.12.10.19.pdf",
                grade_levels=["K", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12"],
                document_type="complete_k12",
                format="PDF",
                notes="Multi-dimensional standards based on Framework for K-12 Science Education"
            ),
        ],

        assessments=[
            Assessment(
                name="North Dakota State Assessment (NDSA) Science",
                grade_levels=["4", "8", "10"],
                test_type="state",
                notes="State science assessment at grades 4, 8, and 10"
            ),
        ],

        contacts={
            "email": "science@nd.gov"
        },

        notes="North Dakota Science Content Standards published February 2019. Each performance standard incorporates three dimensions from Framework for K-12 Science Education. Includes North Dakota-specific local, regional, and state contexts.",
        research_status="COMPLETE",
        last_updated="2026-02-04"
    ),

    "OK": StateStandards(
        state_name="Oklahoma",
        state_abbrev="OK",
        agency_name="Oklahoma State Department of Education",
        website="https://oklahoma.gov/education",
        science_page="https://oklahoma.gov/education/services/standards-learning/science.html",
        ngss_status="framework_based",
        standards_name="Oklahoma Academic Standards for Science",
        adoption_date="2020",

        documents=[
            StandardsDocument(
                title="2020 Oklahoma Academic Standards for Science PreK-12",
                url="https://oklahoma.gov/content/dam/ok/en/osde/documents/services/literacy-policy-and-programs/oklahoma-academic-standards/2020-OAS-Science-Standards.pdf",
                grade_levels=["K", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12"],
                document_type="complete_k12",
                format="PDF",
                notes="Informed by Framework for K-12 Science Education and NGSS"
            ),
        ],

        assessments=[
            Assessment(
                name="Oklahoma School Testing Program (OSTP) Science",
                grade_levels=["5", "8"],
                test_type="state",
                notes="State science assessment"
            ),
        ],

        contacts={
            "email": "science@sde.ok.gov"
        },

        notes="2020 Oklahoma Academic Standards informed by Framework for K-12 Science Education and NGSS. Emphasizes students as active learners doing science through investigations, observations, and analysis.",
        research_status="COMPLETE",
        last_updated="2026-02-04"
    ),

    "SC": StateStandards(
        state_name="South Carolina",
        state_abbrev="SC",
        agency_name="South Carolina Department of Education",
        website="https://ed.sc.gov",
        science_page="https://ed.sc.gov/instruction/standards/science/",
        ngss_status="framework_based",
        standards_name="South Carolina College- and Career-Ready Science Standards",
        adoption_date="2021",

        documents=[
            StandardsDocument(
                title="South Carolina College- and Career-Ready Science Standards 2021",
                url="https://ed.sc.gov/instruction/standards/science/standards/",
                grade_levels=["K", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12"],
                document_type="complete_k12",
                format="HTML",
                notes="Three-dimensional approach across four science/engineering domains"
            ),
        ],

        assessments=[
            Assessment(
                name="SC READY Science",
                grade_levels=["4", "6"],
                url="https://ed.sc.gov/instruction/standards/science/",
                test_type="state",
                notes="State science assessment"
            ),
            Assessment(
                name="SCPASS (SC Palmetto Assessment of State Standards)",
                grade_levels=["4", "6"],
                test_type="state",
                notes="Performance-based assessment"
            ),
        ],

        contacts={
            "email": "bcwhite@ed.sc.gov",
            "name": "Brent White, Elementary Science"
        },

        notes="South Carolina 2021 standards use three-dimensional approach: Science and Engineering Practices, Crosscutting Concepts, and Disciplinary Core Ideas.",
        research_status="COMPLETE",
        last_updated="2026-02-04"
    ),

    "SD": StateStandards(
        state_name="South Dakota",
        state_abbrev="SD",
        agency_name="South Dakota Department of Education",
        website="https://doe.sd.gov",
        science_page="https://doe.sd.gov/contentstandards/science.aspx",
        ngss_status="framework_based",
        standards_name="South Dakota Science Standards",
        adoption_date="April 22, 2024",

        documents=[
            StandardsDocument(
                title="South Dakota Science Standards 2024",
                url="https://doe.sd.gov/contentstandards/documents/24-SciStandards.pdf",
                grade_levels=["K", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12"],
                document_type="complete_k12",
                format="PDF",
                notes="Four domains: Life, Physical, Earth/Space, and Engineering/Technology. Based on Framework for K-12 Science Education"
            ),
        ],

        assessments=[
            Assessment(
                name="South Dakota Science Assessment",
                grade_levels=["5", "8", "11"],
                test_type="state",
                notes="State science assessment"
            ),
        ],

        contacts={
            "email": "science@state.sd.us"
        },

        notes="South Dakota Science Standards adopted April 22, 2024. Three dimensions of science (Practices, Core Ideas, Crosscutting Concepts) in parentheses in every standard. Built coherently from K-12.",
        research_status="COMPLETE",
        last_updated="2026-02-04"
    ),

    "WV": StateStandards(
        state_name="West Virginia",
        state_abbrev="WV",
        agency_name="West Virginia Department of Education",
        website="https://wvde.us",
        science_page="https://wvde.us/middle-secondary-learning/science/standards/",
        ngss_status="framework_based",
        standards_name="West Virginia College- and Career-Readiness Standards for Science",
        adoption_date="August 2021 (Implemented 2022-23)",

        documents=[
            StandardsDocument(
                title="WV College- and Career-Readiness Standards for Science",
                url="https://wvde.us/middle-secondary-learning/science/standards-and-guidance/",
                grade_levels=["K", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12"],
                document_type="complete_k12",
                format="HTML",
                notes="Based on Framework for K-12 Science Education"
            ),
        ],

        assessments=[
            Assessment(
                name="West Virginia General Summative Assessment (WVGSA) Science",
                grade_levels=["5", "8"],
                test_type="state",
                notes="State science assessment"
            ),
        ],

        contacts={
            "email": "science@k12.wv.us"
        },

        notes="West Virginia adopted NGSS in 2015, then adopted College- and Career-Readiness Standards in August 2021 (Policy 2520.3C), implemented 2022-23 school year.",
        research_status="COMPLETE",
        last_updated="2026-02-04"
    ),

    "WY": StateStandards(
        state_name="Wyoming",
        state_abbrev="WY",
        agency_name="Wyoming Department of Education",
        website="https://edu.wyoming.gov",
        science_page="https://edu.wyoming.gov/for-district-leadership/standards/science/",
        ngss_status="framework_based",
        standards_name="Wyoming Content and Performance Standards (WYCPS) for Science",
        adoption_date="July 17, 2024 (Implemented 2025-26)",

        documents=[
            StandardsDocument(
                title="2023 Wyoming Content and Performance Standards for Science",
                url="https://edu.wyoming.gov/for-district-leadership/standards/science/",
                grade_levels=["K", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12"],
                document_type="complete_k12",
                format="HTML",
                notes="Three dimensions: Crosscutting Concepts, Disciplinary Core Ideas, Science and Engineering Practices"
            ),
        ],

        assessments=[
            Assessment(
                name="WY-TOPP Science",
                grade_levels=["5", "8", "10"],
                test_type="state",
                notes="Wyoming Test of Proficiency and Progress. First administered Spring 2026."
            ),
        ],

        contacts={
            "email": "science@wyo.gov"
        },

        notes="Wyoming 2023 standards approved July 17, 2024 for implementation 2025-26. Modeled after NGSS with input from 41 Wyoming educators and stakeholders. Based on Framework for K-12 Science Education.",
        research_status="COMPLETE",
        last_updated="2026-02-04"
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
