#!/usr/bin/env python3
import json
from pathlib import Path

working_urls = {
    "WV": "https://apps.sos.wv.gov/adlaw/csr/readfile.aspx?DocId=54673&Format=PDF",
    "VA": "https://www.doe.virginia.gov/teaching-learning-assessment/k-12-standards-instruction/science/standards-of-learning",
    "WA": "https://ospi.k12.wa.us/student-success/resources-subject-area/science/science-k-12-learning-standards",
    "NE": "https://cdn.education.ne.gov/wp-content/uploads/2017/10/Nebraska_Science_Standards_Final_10_23.pdf",
    "KY": "https://education.ky.gov/curriculum/standards/kyacadstand/Documents/Kentucky_Academic_Standards_for_Science_2022.pdf",
    "AZ": "https://www.azed.gov/sites/default/files/2018/10/Full%20Set%20of%20Standards%20K_12_%20Updated_10_19_19.pdf",
    "FL": "https://info.fldoe.org/docushare/dsweb/Get/Document/6516/dps2012-140b.pdf",
    "HI": "https://manoa.hawaii.edu/sealearning/sites/default/files/NGSSReduced.pdf",
    "ID": "https://www.sde.idaho.gov/wp-content/uploads/2025/09/Idaho-K-12-State-Standards-for-Science.pdf",
    "OR": "https://www.ode.state.or.us/wma/totalstandards/oregon-common-core-state-standards.pdf",
    "AK": "https://education.alaska.gov/akstandards/science/science-standards-for-alaska.pdf",
}

states_file = Path(__file__).parent / "data" / "states.json"

with open(states_file, "r", encoding="utf-8") as f:
    states_data = json.load(f)

updated_count = 0
for state_abbr, url in working_urls.items():
    if state_abbr not in states_data:
        print(f"SKIP: State {state_abbr} not found")
        continue

    state_data = states_data[state_abbr]

    documents = state_data.get("documents", [])
    if not documents:
        print(f"SKIP: No documents found for {state_abbr}")
        continue

    doc = documents[0]
    doc["url"] = url
    doc["url_source"] = ""
    doc["last_verified"] = "2026-02-05"
    updated_count += 1
    print(f"{state_abbr}: Updated {doc.get('title', 'Unknown')}")

save_states_data(states_data)

print(f"Updated {updated_count} states")
