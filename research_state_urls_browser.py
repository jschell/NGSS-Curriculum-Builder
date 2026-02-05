#!/usr/bin/env python3
"""
Browser-based URL research for the 35 broken states

This script coordinates with Claude's browser automation to:
1. Visit each state's education website
2. Search for science standards
3. Find working PDF URLs
4. Extract metadata
5. Generate update recommendations
"""

import json
from pathlib import Path
from typing import Dict, List


# States needing research (35 broken + metadata states)
BROKEN_STATES = {
    'AK': 'Alaska',
    'AR': 'Arkansas',
    'AZ': 'Arizona',
    'CO': 'Colorado',
    'CT': 'Connecticut',
    'FL': 'Florida',
    'GA': 'Georgia',
    'ID': 'Idaho',
    'IN': 'Indiana',
    'LA': 'Louisiana',
    'MA': 'Massachusetts',
    'MD': 'Maryland',
    'ME': 'Maine',
    'MN': 'Minnesota',
    'MO': 'Missouri',
    'MS': 'Mississippi',
    'MT': 'Montana',
    'NC': 'North Carolina',
    'ND': 'North Dakota',
    'NE': 'Nebraska',
    'NH': 'New Hampshire',
    'NJ': 'New Jersey',
    'NV': 'Nevada',
    'OH': 'Ohio',
    'OK': 'Oklahoma',
    'PA': 'Pennsylvania',
    'RI': 'Rhode Island',
    'SC': 'South Carolina',
    'SD': 'South Dakota',
    'TN': 'Tennessee',
    'UT': 'Utah',
    'VA': 'Virginia',
    'WI': 'Wisconsin',
    'WV': 'West Virginia',
    'WY': 'Wyoming',
}


# State education department URL patterns
STATE_DOE_URLS = {
    'AK': 'https://education.alaska.gov/',
    'AL': 'https://www.alsde.edu/',
    'AR': 'https://adeducation.k12.ar.us/',
    'AZ': 'https://www.azed.gov/',
    'CO': 'https://www.cde.state.co.us/',
    'CT': 'https://portal.ct.gov/SDE',
    'FL': 'https://www.fldoe.org/',
    'GA': 'https://www.gadoe.org/',
    'ID': 'https://www.sde.idaho.gov/',
    'IN': 'https://www.in.gov/doe/',
    'LA': 'https://www.louisianabelieves.com/',
    'MA': 'https://www.doe.mass.edu/',
    'MD': 'https://www.marylandpublicschools.org/',
    'ME': 'https://www.maine.gov/doe/',
    'MN': 'https://education.mn.gov/',
    'MO': 'https://dese.mo.gov/',
    'MS': 'https://www.mdek12.org/',
    'MT': 'https://opi.mt.gov/',
    'NC': 'https://www.dpi.nc.gov/',
    'ND': 'https://www.nd.gov/dpi/',
    'NE': 'https://www.education.ne.gov/',
    'NH': 'https://www.education.nh.gov/',
    'NJ': 'https://www.nj.gov/education/',
    'NV': 'https://doe.nv.gov/',
    'OH': 'https://education.ohio.gov/',
    'OK': 'https://sde.ok.gov/',
    'PA': 'https://www.education.pa.gov/',
    'RI': 'https://www.ride.ri.gov/',
    'SC': 'https://ed.sc.gov/',
    'SD': 'https://doe.sd.gov/',
    'TN': 'https://www.tn.gov/education/',
    'UT': 'https://www.schools.utah.gov/',
    'VA': 'https://www.doe.virginia.gov/',
    'WI': 'https://dpi.wi.gov/',
    'WV': 'https://wvde.us/',
    'WY': 'https://edu.wyoming.gov/',
}


def load_current_data():
    """Load current states.json data"""
    states_file = Path(__file__).parent / "data" / "states.json"
    with open(states_file) as f:
        return json.load(f)


def get_state_info(state_abbr: str) -> Dict:
    """Get current state information from states.json"""
    data = load_current_data()
    return data.get(state_abbr, {})


def generate_research_plan(state_abbr: str) -> Dict:
    """Generate research plan for a single state"""
    state_info = get_state_info(state_abbr)
    state_name = BROKEN_STATES.get(state_abbr, state_abbr)
    doe_url = STATE_DOE_URLS.get(state_abbr, f'https://www.google.com/search?q={state_name}+department+of+education')

    documents = state_info.get('documents', [])

    return {
        'state_abbr': state_abbr,
        'state_name': state_name,
        'doe_url': doe_url,
        'documents': documents,
        'search_terms': [
            f'{state_name} science standards',
            f'{state_name} NGSS',
            'science standards PDF',
            'K-12 science',
        ],
        'expected_docs': len(documents),
    }


def main():
    """Main research coordination function"""
    print("=" * 80)
    print("STATE URL RESEARCH PLAN - Browser Automation")
    print("=" * 80)
    print()
    print(f"States to research: {len(BROKEN_STATES)}")
    print()

    # Generate research plan for all states
    research_plans = []
    for state_abbr in sorted(BROKEN_STATES.keys()):
        plan = generate_research_plan(state_abbr)
        research_plans.append(plan)

        print(f"{state_abbr} ({plan['state_name']})")
        print(f"  DOE URL: {plan['doe_url']}")
        print(f"  Documents needed: {plan['expected_docs']}")
        print()

    # Save research plan
    output_file = Path(__file__).parent / "state_url_research_plan.json"
    with open(output_file, 'w') as f:
        json.dump({
            'total_states': len(BROKEN_STATES),
            'states': research_plans,
        }, f, indent=2)

    print(f"Research plan saved to: {output_file}")
    print()
    print("Next: Use browser automation to research each state")
    print("Estimated time: 20-30 min per state")
    print(f"Total estimated time: {len(BROKEN_STATES) * 25 / 60:.1f} hours")


if __name__ == "__main__":
    main()
