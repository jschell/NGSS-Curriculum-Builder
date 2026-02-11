"""Apply URL fixes and metadata updates for 16 states needing corrections."""
import json
from pathlib import Path

DATA_FILE = Path(__file__).parent.parent / "data" / "states.json"
data = json.loads(DATA_FILE.read_text(encoding="utf-8"))

updates = {
    "CO": {
        "url": "https://www.cde.state.co.us/coscience/cas-sc-standards-p12-2018",
        "format": "PDF",
        "page_range": {"P-5": "10-67", "6-8": "68-114", "9-12": "115-200"},
        "notes": "Organized by grade band: P-2, 3-5, MS (6-8), HS (9-12). P-5 starts p.10, 6-8 starts p.68, 9-12 starts p.115.",
    },
    "CT": {
        "url": "https://portal.ct.gov/sde/science/science-standards-and-resources",
        "format": "HTML",
        "notes": "Connecticut adopted NGSS directly (Nov 2015). Standards and resources page.",
    },
    "DE": {
        "notes": "Delaware uses topical arrangement of NGSS for grades 3-12 (not grade-organized). URL points to topical PDF.",
    },
    "GA": {
        "url": "https://www.georgiastandards.org/Georgia-Standards/Pages/Science.aspx",
        "format": "HTML",
        "notes": "Georgia Science Standards of Excellence. Grade-band PDFs: K-5, 6-8, 9-12 each with separate docs per course.",
    },
    "IN": {
        "url": "https://www.in.gov/doe/students/indiana-academic-standards/science-and-computer-science/",
        "format": "HTML",
        "notes": "Indiana 2023 Academic Standards for Science. Grade/course-specific individual PDFs. No single K-12 document.",
    },
    "KS": {
        "url": "https://community.ksde.gov/science/KansasScienceStandards/KSScienceStandards.aspx",
        "notes": "Kansas adopted NGSS directly in June 2013 as Kansas College and Career Ready Standards for Science.",
    },
    "LA": {
        "url": "https://doe.louisiana.gov/educators/instructional-support/planning-resources/k-12-science-resources",
        "format": "HTML",
        "notes": "Louisiana Student Standards for Science (LSS, adopted March 2017). Individual grade PDFs in ZIP. HS by course.",
    },
    "MD": {
        "url": "https://www.marylandpublicschools.org/about/Pages/DCAA/Science/index.aspx",
        "format": "HTML",
        "page_range": None,
        "notes": "Maryland adopted NGSS directly as Maryland Science Standards. No single K-12 PDF document.",
    },
    "ME": {
        "url": "https://www.maine.gov/doe/learning/content/science/review",
        "notes": "Maine Science and Engineering Standards (NGSS-based, 2017). Grade bands: K-2, 3-5, 6-8, 9-12.",
    },
    "MN": {
        "url": "https://education.mn.gov/mdeprod/idcplg?IdcService=GET_FILE&dDocName=PROD059214&RevisionSelectionMethod=latestReleased&Rendition=primary",
        "format": "PDF",
        "title": "2019 Minnesota Academic Standards in Science (Final)",
    },
    "MO": {
        "url": "https://dese.mo.gov/college-career-readiness/curriculum/science",
        "format": "HTML",
        "notes": "Missouri Learning Standards for Science. Separate K-5 and 6-12 PDFs from standards page.",
    },
    "NC": {
        "url": "https://www.dpi.nc.gov/districts-schools/classroom-resources/office-teaching-and-learning/standard-course-study/science",
        "notes": "2023 NC K-12 Science Standards. Grade and course-specific PDFs. No single K-12 combined document.",
    },
    "NH": {
        "url": "https://www.education.nh.gov/who-we-are/division-of-learner-support/bureau-of-instructional-support/science",
        "notes": "New Hampshire adopted NGSS directly.",
    },
    "NM": {
        "url": "https://web.ped.nm.gov/bureaus/math-and-science-bureau/nm-stem-ready-science/nm-stem-ready-science-standards/",
        "format": "HTML",
        "title": "NM STEM Ready! Science Standards",
        "notes": "NM STEM Ready! = NGSS + 6 New Mexico-specific standards. Standards page with resources.",
    },
    "RI": {
        "url": "https://www.ride.ri.gov/StudentsFamilies/RIEducationData/RIAcademicStandards.aspx",
        "notes": "Rhode Island adopted NGSS directly.",
    },
    "VA": {
        "url": "https://www.doe.virginia.gov/teaching-learning-assessment/k-12-standards-instruction/science/standards-of-learning",
        "format": "HTML",
        "notes": "2018 Science Standards of Learning (K-Physics). Grade-specific PDFs from standards page.",
    },
    "VT": {
        "url": "https://education.vermont.gov/student-learning/curriculum/science-technology-engineering-math/science-education",
        "notes": "Vermont adopted NGSS directly as Vermont Science Standards.",
    },
    "WV": {
        "url": "https://wvde.us/academics/middle-secondary-education/science/standards",
        "notes": "WV College- and Career-Readiness Standards for Science (Policy 2520.3C, August 2021). Framework-based NGSS.",
    },
}

for abbr, fields in updates.items():
    if abbr not in data:
        print(f"  SKIP {abbr}: not in data")
        continue
    docs = data[abbr].get("documents", [])
    if not docs:
        print(f"  SKIP {abbr}: no documents")
        continue
    doc = docs[0]
    for key, val in fields.items():
        doc[key] = val
    print(f"  {abbr}: updated {list(fields.keys())}")

DATA_FILE.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
print("\nAll updates saved to data/states.json")
