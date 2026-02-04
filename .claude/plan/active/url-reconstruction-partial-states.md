# Plan: Fix Partial State URLs Using Website Navigation Discovery

**Status:** Not Started
**Created:** 2026-02-04
**Estimated Duration:** 2-3 hours
**Priority:** High
**Depends On:** Plan 1 (URL Validation) and Plan 2 (Workflow Documentation)

---

## Context

After validating all 80 URLs (Plan 1), we identified that many states have partial URL failures where some documents work and others don't. This plan focuses on fixing states with **at least one working link** by:
1. Starting from a known working URL as the crawl seed
2. Iteratively discovering related documents through web crawling
3. Testing discovered URLs to find correct replacements
4. Building complete and correct sets of links

**Current State:**
- ✅ URL validation complete (80 URLs tested)
- ✅ Broken URLs identified with priorities
- ✅ Workflow documentation exists (Plan 2)
- ❌ Many states have partial failures (some working, some broken)
- ❌ No automated URL discovery mechanism
- ❌ No systematic website navigation approach

**Example Use Case - Washington (WA):**
- **NGSS Status:** Direct adoption (ideal for testing)
- **State Website:** `https://ospi.k12.wa.us` (from states.json)
- **Science Page:** `https://ospi.k12.wa.us/student-success/resources-subject-area/science` (from states.json)
- **Broken:** 3 documents (all HTTP 403 - likely bot detection)
- **Approach:** 
  - Test `state.website` (OSPI homepage)
  - Navigate to `state.science_page` (science resources page)
  - Discover all science standards document links
  - Test each document URL
  - Match to expected titles in states.json
  - Apply working URLs to states.json

**Goal:** Systematically fix states with partial URL failures using structured website navigation and URL discovery.

**Out of Scope:**
- States with 100% failure (Tier 1 critical) - these need manual URL research
- States with 100% working (no fixes needed)
- Non-URL related issues (parser bugs, data model changes)

---

## Prerequisites

- [x] Plan 1 complete (validation_results.json exists)
- [x] Plan 2 complete (workflow documentation exists)
- [x] URL_UPDATE_PRIORITIES.md identifies states with partial failures
- [ ] States with at least one working URL identified
- [ ] Working URL patterns extracted
- [ ] URL reconstruction script created
- [ ] Test suite for reconstructed URLs

**Verification:**
```bash
# Verify Plan 1 & 2 outputs exist
ls -lh validation_results.json docs/URL_UPDATE_PRIORITIES.md

# Verify validation identified partial failures
python -c "
import json
val = json.load(open('validation_results.json'))
partial = [r for r in val['results'].values() 
            if r['http_status'] == 200 and r['content_type'] == 'pdf']
print(f'States with working URLs: {len(set(r[\"state_abbrev\"] for r in partial))}')
"
# Should show > 0

# Verify states.json is valid
python -m json.tool data/states.json > /dev/null && echo "JSON valid"
```

---

## Implementation Steps

### Step 1: Identify States with Partial Failures

**Action:** Extract list of states with at least one working URL and at least one broken URL

**Files to create:** `docs/partial_states_analysis.md`

**Process:**
1. Parse validation_results.json
2. Group URLs by state abbreviation
3. For each state:
   - Count working URLs (HTTP 200, PDF, confidence >= 0.8)
   - Count broken URLs (HTTP != 200 OR wrong format)
   - Flag if both working > 0 AND broken > 0
4. Prioritize:
   - NGSS-aligned states first (direct_adoption)
   - States with higher working:broken ratio
   - States with clear URL patterns

**Output structure:**
```markdown
# Partial States Analysis

## States with Mixed Results

### Oregon (OR) - NGSS Direct Adoption
- **Working:** 1 (Grade 3)
- **Broken:** 6 (K, 1, 2, 4, 5, K-12)
- **Working Ratio:** 14%
- **URL Pattern:** Grade-specific: `.../Grade%20[N]%20Science%20Standards...`
- **Pattern Confidence:** High (consistent structure)
- **Priority:** 1 (NGSS + clear pattern + working example)

[... more states ...]

## Pattern Analysis

### Common URL Patterns Detected
1. **Grade-specific:** `.../grade[N].pdf` or `.../Grade%20[N]%20...`
2. **Complete K-12:** Single PDF covering all grades
3. **Range-based:** `.../grades[K-5].pdf` or `.../grades[6-8].pdf`
4. **DCI/Topic arrangements:** Alternative organizations of same content

### Reconstruction Strategies
1. **Direct substitution:** Replace grade number in working URL
2. **Pattern matching:** Infer URL structure from working example
3. **Server directory listing:** Test if `.../Documents/` listing available
4. **Archive analysis:** Check Wayback Machine for historical working URLs
```

**Tests required:**
- All partial states identified
- Working/broken counts accurate
- NGSS status correctly identified
- URL patterns documented

**Validation:**
```bash
# Verify analysis created
ls -lh docs/partial_states_analysis.md

# Verify partial states counted correctly
python -c "
import json
val = json.load(open('validation_results.json'))
states = {}
for r in val['results'].values():
    s = r['state_abbrev']
    if s not in states:
        states[s] = {'working': 0, 'broken': 0}
    if r['http_status'] == 200 and r['content_type'] == 'pdf':
        states[s]['working'] += 1
    else:
        states[s]['broken'] += 1
partial = [s for s,v in states.items() if v['working'] > 0 and v['broken'] > 0]
print(f'Partial states found: {len(partial)}')
print(f'Partial states: {sorted(partial)}')
"
# Expected: Multiple states including OR
```

**Commit message:** `docs(analysis): identify states with partial URL failures and document patterns`

**Expected duration:** 25 minutes

---

### Step 2: Discover URLs via State Website Navigation

**Action:** Navigate state website → science page → discover documents

**Files to create:** `scripts/discover_urls_from_website.py`

**Script functionality:**
```python
#!/usr/bin/env python3
"""
Discover URLs by navigating state website structure.
Starts with state.website, moves to state.science_page, finds document links.
"""

import json
import httpx
import re
from urllib.parse import urljoin, urlparse
from typing import List, Dict
import asyncio

class StateWebsiteNavigator:
    """Navigate state website to discover document URLs"""
    
    def __init__(self, timeout: int = 10):
        self.timeout = timeout
        self.client = None
    
    async def get_client(self) -> httpx.AsyncClient:
        if self.client is None:
            self.client = httpx.AsyncClient(
                timeout=self.timeout,
                follow_redirects=True,
                headers={
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                }
            )
        return self.client
    
    async def test_url(self, url: str) -> Dict:
        """Test if URL is valid and returns PDF"""
        try:
            client = await self.get_client()
            response = await client.head(url, follow_redirects=True)
            
            is_valid = (response.status_code == 200 and 
                       'pdf' in response.headers.get('content-type', '').lower())
            
            return {
                'url': url,
                'status_code': response.status_code,
                'content_type': response.headers.get('content-type', ''),
                'is_pdf': is_valid,
                'success': is_valid
            }
        except Exception as e:
            return {
                'url': url,
                'status_code': 0,
                'content_type': '',
                'is_pdf': False,
                'success': False,
                'error': str(e)
            }
    
    async def test_homepage(self, homepage_url: str) -> bool:
        """Test if state website homepage is accessible"""
        print(f"\n[1] Testing state website...")
        print(f"    URL: {homepage_url}")
        
        try:
            client = await self.get_client()
            response = await client.get(homepage_url, follow_redirects=True)
            
            success = response.status_code == 200
            print(f"    Result: {'✓ Accessible' if success else '✗ Failed'} (HTTP {response.status_code})")
            return success
            
        except Exception as e:
            print(f"    Result: ✗ Error - {e}")
            return False
    
    async def navigate_to_science_page(self, science_page_url: str) -> Dict:
        """
        Navigate to science standards page and discover document links.
        """
        print(f"\n[2] Navigating to science page...")
        print(f"    URL: {science_page_url}")
        
        try:
            client = await self.get_client()
            response = await client.get(science_page_url, follow_redirects=True)
            
            if response.status_code != 200:
                print(f"    Result: ✗ Failed (HTTP {response.status_code})")
                return {
                    'accessible': False,
                    'documents': [],
                    'error': f'HTTP {response.status_code}'
                }
            
            print(f"    Result: ✓ Accessible (HTTP {response.status_code})")
            print(f"\n[3] Discovering document links...")
            
            # Parse HTML for PDF links
            discovered_links = []
            content = response.text
            
            # Find all href links
            href_pattern = r'href\s*=\s*["\']([^"\']+)["\']'
            links = re.findall(href_pattern, content)
            
            base_parsed = urlparse(science_page_url)
            base_domain = base_parsed.netloc
            
            for link in links:
                # Skip non-HTTP links and fragments
                if link.startswith('#') or not link.startswith(('http', '/')):
                    continue
                
                # Make absolute URL
                absolute_url = urljoin(science_page_url, link)
                link_parsed = urlparse(absolute_url)
                
                # Only follow same domain (don't go to external sites)
                if link_parsed.netloc != base_domain:
                    continue
                
                # Only care about PDFs
                if '.pdf' not in absolute_url.lower():
                    continue
                
                discovered_links.append(absolute_url)
            
            print(f"    Found {len(discovered_links)} PDF links")
            return {
                'accessible': True,
                'documents': discovered_links,
                'error': None
            }
            
        except Exception as e:
            print(f"    Result: ✗ Error - {e}")
            return {
                'accessible': False,
                'documents': [],
                'error': str(e)
            }
    
    async def test_discovered_urls(self, urls: List[str]) -> List[Dict]:
        """Test all discovered URLs to find working ones"""
        print(f"\n[4] Testing discovered URLs...")
        
        results = []
        for i, url in enumerate(urls, 1):
            print(f"    Testing {i}/{len(urls)}...")
            result = await self.test_url(url)
            results.append(result)
            
            if result['success']:
                print(f"      ✓ {url[:60]}...")
            else:
                status_msg = f"HTTP {result['status_code']}" if result['status_code'] != 0 else "Connection error"
                print(f"      ✗ {status_msg}")
        
        working_count = sum(1 for r in results if r['success'])
        print(f"\n    Summary: {working_count}/{len(urls)} URLs working")
        
        return results
    
    async def match_to_expected_docs(self, test_results: List[Dict], expected_docs: List[str]) -> Dict:
        """Match discovered working URLs to expected document titles"""
        print(f"\n[5] Matching URLs to expected documents...")
        
        doc_mapping = {}
        
        for doc_title in expected_docs:
            title_lower = doc_title.lower()
            
            # Try to match based on URL content
            for result in test_results:
                if not result['success']:
                    continue
                
                url = result['url']
                
                # Extract filename and path from URL
                parsed = urlparse(url)
                path_lower = parsed.path.lower()
                filename = parsed.path.split('/')[-1].lower().replace('%20', ' ')
                
                # Check for grade match
                if 'grade' in title_lower:
                    grade_match = re.search(r'grade\s*(\d+)', title_lower)
                    if grade_match:
                        grade_num = grade_match.group(1)
                        if f'grade{grade_num}' in path_lower or f'grade {grade_num}' in filename:
                            doc_mapping[doc_title] = url
                            print(f"  ✓ Matched by grade: {doc_title[:40]}")
                            break
                
                # Check for K-12 match
                elif 'k-12' in title_lower or 'k12' in title_lower:
                    if 'k-12' in path_lower or 'k12' in path_lower:
                        doc_mapping[doc_title] = url
                        print(f"  ✓ Matched by K-12: {doc_title[:40]}")
                        break
                
                # Check for science standards keywords
                elif 'science' in filename and 'standard' in filename:
                    # Additional check for state name
                    state_abbrev = expected_docs[0] if expected_docs else ''
                    # Would need to pass state info to match properly
                    if len(doc_mapping) < len(expected_docs):
                        doc_mapping[doc_title] = url
                        print(f"  ✓ Matched by keywords: {doc_title[:40]}")
                        break
        
        matched_count = len(doc_mapping)
        print(f"\n    Matched {matched_count}/{len(expected_docs)} documents")
        return doc_mapping
    
    async def discover_for_state(self, state_data: Dict) -> Dict:
        """
        Complete discovery process for a state.
        
        Process:
        1. Test state.website
        2. Navigate to state.science_page
        3. Discover all PDF links
        4. Test each discovered URL
        5. Match to expected documents in states.json
        """
        state_abbrev = state_data['state_abbrev']
        state_name = state_data['state_name']
        homepage_url = state_data['website']
        science_page_url = state_data['science_page']
        
        print("\n" + "="*70)
        print(f"URL Discovery for {state_name} ({state_abbrev})")
        print("="*70)
        
        # Step 1: Test homepage
        homepage_accessible = await self.test_homepage(homepage_url)
        
        if not homepage_accessible:
            return {
                'state': state_abbrev,
                'homepage_accessible': False,
                'science_page_accessible': False,
                'discovered_urls': [],
                'working_urls': [],
                'matched_docs': {},
                'error': f'Homepage not accessible: {homepage_url}'
            }
        
        # Step 2: Navigate to science page
        science_result = await self.navigate_to_science_page(science_page_url)
        
        if not science_result['accessible']:
            return {
                'state': state_abbrev,
                'homepage_accessible': True,
                'science_page_accessible': False,
                'discovered_urls': [],
                'working_urls': [],
                'matched_docs': {},
                'error': science_result['error']
            }
        
        # Step 3: Test discovered URLs
        test_results = await self.test_discovered_urls(science_result['documents'])
        
        # Step 4: Match to expected documents
        expected_docs = [doc['title'] for doc in state_data['documents']]
        doc_mapping = await self.match_to_expected_docs(test_results, expected_docs)
        
        working_urls = [r['url'] for r in test_results if r['success']]
        
        return {
            'state': state_abbrev,
            'homepage_accessible': True,
            'science_page_accessible': True,
            'discovered_urls': science_result['documents'],
            'working_urls': working_urls,
            'matched_docs': doc_mapping,
            'error': None
        }

async def main():
    # Load states data
    with open('data/states.json') as f:
        states = json.load(f)
    
    # Focus on Washington as proof-of-concept (NGSS direct adoption)
    target_state = 'WA'
    state_data = states[target_state]
    
    # Discover URLs
    navigator = StateWebsiteNavigator()
    result = await navigator.discover_for_state(state_data)
    
    # Save results
    with open('docs/discovered_urls.json', 'w') as f:
        json.dump(result, f, indent=2)
    
    # Print summary
    print("\n" + "="*70)
    print("DISCOVERY SUMMARY")
    print("="*70)
    print(f"State: {result['state']} - {states[result['state']]['state_name']}")
    print(f"NGSS Status: {states[result['state']]['ngss_status']}")
    print(f"\nAccessibility:")
    print(f"  Homepage: {'✓' if result['homepage_accessible'] else '✗'}")
    print(f"  Science Page: {'✓' if result['science_page_accessible'] else '✗'}")
    print(f"\nURL Discovery:")
    print(f"  Expected documents: {len(state_data['documents'])}")
    print(f"  Discovered PDFs: {len(result['discovered_urls'])}")
    print(f"  Working PDFs: {len(result['working_urls'])}")
    print(f"  Matched documents: {len(result['matched_docs'])}")
    
    if result['error']:
        print(f"\nError: {result['error']}")
    
    print("\nMatched Documents:")
    for title, url in result['matched_docs'].items():
        print(f"  - {title[:50]}")
        print(f"    {url[:70]}...")
    
    success_rate = len(result['matched_docs']) / len(state_data['documents']) if state_data['documents'] else 0
    print(f"\nSuccess Rate: {success_rate*100:.1f}%")

if __name__ == "__main__":
    asyncio.run(main())
```

**Tests required:**
- Script runs without errors
- Homepage is tested
- Science page navigation works
- All PDF links discovered
- Discovered URLs are tested
- Results saved as valid JSON

**Validation:**
```bash
# Run URL discovery script
python scripts/discover_urls_from_website.py

# Verify output created
ls -lh docs/discovered_urls.json

# Check JSON validity
python -m json.tool docs/discovered_urls.json > /dev/null && echo "Valid JSON"

# Verify discovery results
python -c "
import json
data = json.load(open('docs/discovered_urls.json'))
print(f'State: {data[\"state\"]}')
print(f'Homepage accessible: {data[\"homepage_accessible\"]}')
print(f'Science page accessible: {data[\"science_page_accessible\"]}')
print(f'Expected documents: {len(json.load(open(\"data/states.json\"))[data[\"state\"]][\"documents\"])}')
print(f'Discovered PDFs: {len(data[\"discovered_urls\"])}')
print(f'Working PDFs: {len(data[\"working_urls\"])}')
print(f'Matched documents: {len(data[\"matched_docs\"])}')
"
```

**Commit message:** `feat(discovery): add state website navigation URL discovery`

**Expected duration:** 40 minutes

---

### Step 3: Create URL Reconstruction Tester

**Action:** Build script to test reconstructed URLs for broken documents

**Files to create:** `scripts/test_reconstructed_urls.py`

**Script functionality:**
```python
#!/usr/bin/env python3
"""
Test reconstructed URLs for broken documents.
Uses working URL patterns to generate and test candidate URLs.
"""

import json
import httpx
import asyncio
from urllib.parse import quote

async def test_url(url: str, timeout: int = 10) -> dict:
    """
    Test a single URL with HEAD request.
    
    Returns:
        dict with status_code, content_type, success
    """
    try:
        async with httpx.AsyncClient(timeout=timeout, follow_redirects=True) as client:
            response = await client.head(url, headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            })
            return {
                'url': url,
                'status_code': response.status_code,
                'content_type': response.headers.get('content-type', ''),
                'success': response.status_code == 200 and 'pdf' in response.headers.get('content-type', '').lower()
            }
    except Exception as e:
        return {
            'url': url,
            'status_code': 0,
            'content_type': '',
            'success': False,
            'error': str(e)
        }

def reconstruct_url(pattern: str, grade: str) -> str:
    """
    Reconstruct URL by substituting grade in pattern.
    
    Examples:
      - Pattern: .../Grade%20[GRADE]%20Science...
      - Grade: 2
      - Result: .../Grade%202%20Science...
    """
    # URL-encode the grade number
    grade_encoded = quote(f"Grade {grade}", safe='')
    return pattern.replace('[GRADE]', grade_encoded)

async def main():
    # Load validation results
    with open('validation_results.json') as f:
        val = json.load(f)
    
    # Load states data
    with open('data/states.json') as f:
        states = json.load(f)
    
    # Focus on Oregon as first test case
    target_state = 'OR'
    working_pattern = "https://www.oregon.gov/ode/educator-resources/standards/science/Documents/Grade%20[GRADE]%20Science%20Standards%20with%20Guidance.pdf"
    
    print(f"# URL Reconstruction Test: {states[target_state]['state_name']}")
    print()
    
    # Find broken documents for target state
    broken_docs = []
    for doc in states[target_state]['documents']:
        url = doc['url']
        val_result = val['results'].get(url, {})
        
        if val_result.get('http_status', 0) != 200 or val_result.get('content_type') != 'pdf':
            broken_docs.append(doc)
    
    print(f"Found {len(broken_docs)} broken documents")
    print()
    
    # Test reconstructed URLs
    results = []
    for doc in broken_docs:
        grade = doc['grade_levels'][0] if doc['grade_levels'] else None
        
        if grade and grade.isdigit():
            # Reconstruct URL using pattern
            reconstructed_url = reconstruct_url(working_pattern, grade)
            
            print(f"## {doc['title']}")
            print(f"**Original URL:** `{doc['url']}`")
            print(f"**Original Status:** {val['results'].get(doc['url'], {}).get('http_status', 'Unknown')}")
            print(f"**Reconstructed URL:** `{reconstructed_url}`")
            
            # Test reconstructed URL
            result = await test_url(reconstructed_url)
            results.append({
                'title': doc['title'],
                'original_url': doc['url'],
                'reconstructed_url': reconstructed_url,
                'status_code': result['status_code'],
                'success': result['success']
            })
            
            if result['success']:
                print(f"**Result:** ✓ Success (HTTP {result['status_code']})")
            else:
                print(f"**Result:** ✗ Failed (HTTP {result['status_code']})")
            print()
    
    # Summary
    successful = sum(1 for r in results if r['success'])
    print(f"## Summary")
    print(f"- Total tested: {len(results)}")
    print(f"- Successful: {successful}")
    print(f"- Failed: {len(results) - successful}")
    print(f"- Success rate: {successful/len(results)*100:.1f}%")
    
    # Output JSON for batch updates
    with open('docs/reconstructed_urls.json', 'w') as f:
        json.dump({
            'state': target_state,
            'test_date': '2026-02-04',
            'results': results
        }, f, indent=2)
    
    print()
    print(f"Results saved to: docs/reconstructed_urls.json")

if __name__ == "__main__":
    asyncio.run(main())
```

**Tests required:**
- Script runs without errors
- Reconstructed URLs generated correctly
- HTTP testing works
- JSON output is valid
- Results saved successfully

**Validation:**
```bash
# Run URL reconstruction tester
python scripts/test_reconstructed_urls.py

# Verify output created
ls -lh docs/reconstructed_urls.json

# Check JSON validity
python -m json.tool docs/reconstructed_urls.json > /dev/null && echo "Valid JSON"

# Verify reconstructed URLs generated
python -c "
import json
data = json.load(open('docs/reconstructed_urls.json'))
print(f'Test results: {len(data[\"results\"])} URLs')
for r in data['results']:
    print(f'  {r[\"title\"][:40]}: {\"Success\" if r[\"success\"] else \"Failed\"}')
"
```

**Commit message:** `feat(test): add URL reconstruction tester for automated URL fixing`

**Expected duration:** 35 minutes

---

### Step 4: Run Discovery Test on Washington

**Action:** Execute website navigation discovery on Washington (WA) as proof-of-concept

**Files to modify:** None (test run)
**Files to generate:** `docs/discovered_urls.json`

**Process:**
1. Run `scripts/discover_urls_from_website.py`
2. Analyze success rate of discovery
3. Document which documents were matched
4. Identify any navigation issues
5. Adjust strategy if needed

**Expected outcomes:**
- Homepage and science page accessible
- Multiple PDF links discovered
- Some documents matched to expected titles
- Working URLs identified
- Success rate indicates strategy effectiveness

**Tests required:**
- Script completes without errors
- Results JSON is valid
- Success rate calculated
- Discovery process documented

**Validation:**
```bash
# Run discovery test
python scripts/discover_urls_from_website.py > docs/washington_discovery_test.md

# Verify results
python -c "
import json
data = json.load(open('docs/discovered_urls.json'))
print(f'State: {data[\"state\"]}')
print(f'Homepage accessible: {data[\"homepage_accessible\"]}')
print(f'Science page accessible: {data[\"science_page_accessible\"]}')
print(f'Discovered PDFs: {len(data[\"discovered_urls\"])}')
print(f'Working PDFs: {len(data[\"working_urls\"])}')
print(f'Matched documents: {len(data[\"matched_docs\"])}')
print(f'Success rate: {len(data[\"matched_docs\"]/len(json.load(open(\"data/states.json\"))[data[\"state\"]][\"documents\"])*100:.1f}%')
"

# Review test output
cat docs/washington_discovery_test.md
```

**Commit message:** `test(discovery): run state website navigation on Washington as proof-of-concept`

**Expected duration:** 15 minutes

---

### Step 5: Apply Discovered URLs to states.json

**Action:** Update states.json with URLs discovered through website navigation

**Files to modify:** `data/states.json`

**Process:**
1. Parse `docs/discovered_urls.json`
2. Extract matched document URLs
3. Create backup: `cp data/states.json data/states.json.backup`
4. For each matched document:
   - Find document by title in states.json
   - Update URL field with discovered URL
   - Add `url_source` field with science page URL
   - Add `last_verified` field with current date
5. Validate updated JSON
6. Test CLI with updated state
7. Commit changes

**Update script:**
```python
#!/usr/bin/env python3
"""
Apply discovered URLs to states.json.
Updates states.json with working URLs found through website discovery.
"""

import json
from datetime import datetime

def main():
    # Load data
    with open('data/states.json') as f:
        states = json.load(f)
    
    with open('docs/discovered_urls.json') as f:
        discovery = json.load(f)
    
    # Apply discovered URLs
    state = discovery['state']
    matched_docs = discovery['matched_docs']
    updates_made = 0
    
    for doc_title, new_url in matched_docs.items():
        # Find document by title
        for doc in states[state]['documents']:
            if doc['title'] == doc_title:
                old_url = doc['url']
                doc['url'] = new_url
                doc['url_source'] = states[state]['science_page']
                doc['last_verified'] = datetime.now().strftime('%Y-%m-%d')
                updates_made += 1
                print(f"Updated: {doc['title'][:40]}")
                print(f"  Old: {old_url[:60]}...")
                print(f"  New: {new_url[:60]}...")
                print()
    
    # Save updated states.json
    with open('data/states.json', 'w') as f:
        json.dump(states, f, indent=2)
    
    print(f"Total updates: {updates_made}")
    print(f"Please validate: python -m json.tool data/states.json")

if __name__ == "__main__":
    main()
```

**Tests required:**
- Backup created before changes
- JSON remains valid after updates
- All matched URLs applied
- CLI works with updated state
- Document count unchanged

**Validation:**
```bash
# Create backup first
cp data/states.json data/states.json.backup

# Apply updates
python scripts/apply_discovered_urls.py

# Verify JSON valid
python -m json.tool data/states.json > /dev/null && echo "JSON valid"

# Verify state count unchanged
python -c "import json; print(f'States: {len(json.load(open(\"data/states.json\")))}'); print(f'Expected: 51')"

# Test CLI
python state_science_standards_system.py state WA

# Re-validate updated URLs
uv run validate_urls.py --states WA
```

**Commit message:** `fix(urls): apply discovered URLs to Washington state`

**Expected duration:** 20 minutes

---

### Step 6: Re-Validate Updated State

**Action:** Run validation on updated state to confirm fixes

**Files to modify:** None
**Files to generate:** `validation_results_wa_updated.json`

**Process:**
1. Run `uv run validate_urls.py --states WA`
2. Compare new results with original
3. Verify broken URLs are now working
4. Confirm working URLs still work
5. Document improvement metrics

**Expected outcome:**
- Previously broken URLs now work
- No regression on working URLs
- Higher overall success rate

**Tests required:**
- Validation completes
- New results show improvements
- JSON output is valid
- Comparison metrics calculated

**Validation:**
```bash
# Run validation on updated state
uv run validate_urls.py --states WA > validation_results_wa_updated.json

# Compare with original results
python -c "
import json
orig = json.load(open('validation_results.json'))
new = json.load(open('validation_results_wa_updated.json'))

# Count working URLs
orig_working = sum(1 for r in orig['results'].values() if r['state_abbrev'] == 'WA' and r['http_status'] == 200)
new_working = sum(1 for r in new['results'].values() if r['state_abbrev'] == 'WA' and r['http_status'] == 200)

print(f'Original working: {orig_working}')
print(f'Updated working: {new_working}')
print(f'Improvement: +{new_working - orig_working}')
print(f'Success rate change: {(new_working - orig_working)/3*100:.1f}%')
"
```

**Commit message:** `test(validation): re-verify Washington after URL discovery`

**Expected duration:** 15 minutes

---

### Step 7: Document URL Discovery Strategy for Other States

**Action:** Create guide for applying website navigation to other partial states

**Files to create:** `docs/URL_DISCOVERY_STRATEGY.md`

**Guide structure:**
```markdown
# URL Discovery Strategy Guide

## Purpose

This guide documents the URL discovery process for fixing states with partial URL failures. The strategy uses state website navigation to systematically find working document URLs.

## When to Use Website Discovery

**Good candidates:**
- States with partial URL failures (some working, some broken)
- NGSS-aligned states (consistent URL structures expected)
- States with documented `website` and `science_page` fields
- States with grade-specific or range-based documents

**Poor candidates:**
- States with 100% failure (homepage may be broken too)
- States with 100% working (no fixes needed)
- States without website field in states.json
- States using external hosting exclusively (nextgenscience.org, etc.)

## Discovery Process

### Navigation Strategy: Step-by-Step

**Process Overview:**
1. **Test State Website** - Verify state.website is accessible
2. **Navigate to Science Page** - Access state.science_page
3. **Discover Document Links** - Find all PDF URLs on science page
4. **Test Discovered URLs** - Validate each URL returns working PDF
5. **Match to Expected Documents** - Link working URLs to states.json entries

### Step 1: Test State Website

**Goal:** Verify state education agency website is accessible

**What to test:**
- HTTP status (should be 200)
- Content loads correctly
- No major errors in HTML

**Example (Washington):**
```
Homepage: https://ospi.k12.wa.us
Test: GET request
Expected: HTTP 200, HTML loads
```

**If homepage fails:**
- Check for alternate URLs
- Look for website restructure
- Mark state for manual investigation

### Step 2: Navigate to Science Page

**Goal:** Access the science standards/resources page

**What to expect:**
- HTTP 200 OK
- Links to science standards documents
- May have grade-level or document organization

**Example (Washington):**
```
Science Page: https://ospi.k12.wa.us/student-success/resources-subject-area/science
Expected: Links to WSSLS documents, DCI/Topic arrangements
```

**If science page fails:**
- Look for alternate navigation paths
- Check for moved content
- Document in discovery results

### Step 3: Discover Document Links

**Goal:** Find all PDF links on the science page

**Discovery methods:**

**Method A: Parse HTML for PDF Links**
- Search for all `href` attributes
- Filter for `.pdf` extension
- Filter for same domain only
- Extract absolute URLs

**Method B: Follow Section Links**
- Many pages organize by grade range (K-5, 6-8, 9-12)
- Navigate each section
- Discover documents within sections

**Method C: Look for Download Directories**
- Some sites have `/downloads/` or `/documents/` folders
- Try accessing directory listing
- List all PDF files

**What to capture:**
- Full URL for each PDF
- Document title (from link text or filename)
- File size (if available)

### Step 4: Test Discovered URLs

**Goal:** Validate each discovered URL returns working PDF

**Testing approach:**
1. HTTP HEAD request (fast)
2. Verify status code 200
3. Verify Content-Type: application/pdf
4. Optionally: Download small portion to verify

**Expected success criteria:**
- HTTP 200 OK
- Content-Type: application/pdf
- No authentication required
- File size reasonable (> 10 KB, < 50 MB)

**Common failures:**
- 404 Not Found: Document moved or renamed
- 403 Forbidden: Bot detection or access restrictions
- 500 Server Error: Temporary server issue

### Step 5: Match to Expected Documents

**Goal:** Link discovered working URLs to states.json entries

**Matching strategies:**

**Strategy A: Exact Title Match**
- Compare discovered link text to document titles
- Look for exact or near-exact matches
- Best for documents with clear names

**Strategy B: Grade Level Match**
- Extract grade number from URL path/filename
- Match to document's `grade_levels` field
- Works for grade-specific documents

**Strategy C: Range Match**
- Match "K-12" URLs to complete documents
- Match "K-5", "6-8" URLs to range documents
- Works for documents with multiple grades

**Strategy D: Keyword Match**
- Look for "science", "standards", "ngss" in URL
- Match to state name if present
- Works for documents with generic names

**Matching priority:**
1. Exact title match (highest confidence)
2. Grade level match
3. Range match
4. Keyword match (lowest confidence)

## Applying Discovered URLs

### Safety First

Before applying any discovered URLs:
1. **Create backup:** `cp data/states.json data/states.json.backup`
2. **Validate backup:** `python -m json.tool data/states.json.backup`
3. **Document findings:** Use docs/templates/url_update_template.md
4. **Review matches:** Verify manually before applying
5. **Low confidence matches:** Require human review

### Application Process

Use `scripts/apply_discovered_urls.py`:
```bash
python scripts/apply_discovered_urls.py
```

**What the script does:**
1. Loads discovery results
2. Extracts matched documents
3. Updates states.json with new URLs
4. Adds `url_source` field (science page URL)
5. Adds `last_verified` field (current date)

### Validation After Updates

Always run:
```bash
# Validate JSON
python -m json.tool data/states.json

# Test CLI
python state_science_standards_system.py state [STATE]

# Re-validate URLs
uv run validate_urls.py --states [STATE]
```

## Success Criteria

A discovery attempt is successful when:
- [ ] State website homepage accessible
- [ ] Science standards page accessible
- [ ] PDF links discovered (at least 1)
- [ ] Discovered URLs tested and validated
- [ ] At least 1 URL matched to expected document
- [ ] Matched URLs return working PDFs
- [ ] Content matches expected grade level

## Failure Analysis

### If Discovery Fails at Homepage

**Document findings:**
1. HTTP status code and error message
2. Any alternate URLs found
3. Check if URL structure changed

**Next steps:**
1. Check Wayback Machine for old working homepage
2. Google search state education agency
3. Look for news about website migration
4. Mark for manual investigation

### If Discovery Fails at Science Page

**Document findings:**
1. Science page URL error
2. Navigation paths tried
3. Any alternate science pages found

**Next steps:**
1. Look for science content in different section
2. Check for recent website restructure
3. Try site search for "science standards"
4. Mark for manual research

### If No Matches Found

**Document findings:**
1. URLs discovered and tested
2. Expected documents vs available documents
3. Matching strategy gaps

**Next steps:**
1. Try different matching strategies
2. Look for alternate naming conventions
3. Check if documents exist under different organization
4. Mark for manual review

## State-by-State Strategy

Based on partial states analysis:

### Washington (WA) - Proof of Concept
- **NGSS Status:** Direct adoption
- **Website:** https://ospi.k12.wa.us
- **Science Page:** https://ospi.k12.wa.us/student-success/resources-subject-area/science
- **Expected documents:** 3 (K-12 WSSLS, DCI Arrangement, Topic Arrangement)
- **Discovery strategy:** Parse science page for PDF links
- **Expected success:** 2-3 documents fixed
- **Estimated time:** 1 hour

[... other states documented similarly ...]

## Lessons Learned

From Washington discovery:
1. [Lesson 1: what worked]
2. [Lesson 2: what didn't work]
3. [Lesson 3: navigation improvements]
4. [Lesson 4: recommendations for other states]

## Automation Potential

Future enhancements:
1. **Multi-state discovery:** Apply to all partial states in sequence
2. **Intelligent matching:** Use title similarity algorithms
3. **Success rate tracking:** Track which strategies work best
4. **Auto-apply:** Automatically apply high-confidence matches (> 0.9)
5. **Human review queue:** Flag low-confidence matches for review
```

**Tests required:**
- Guide covers all discovery steps
- Examples are accurate (Washington results)
- Safety procedures documented
- Testing procedures clear

**Validation:**
```bash
# Verify guide created
ls -lh docs/URL_DISCOVERY_STRATEGY.md

# Check sections present
grep "^##" docs/URL_DISCOVERY_STRATEGY.md | head -20
# Expected: Purpose, When to Use, Discovery Process, etc.
```

**Commit message:** `docs(workflow): create URL discovery strategy guide for partial state fixes`

**Expected duration:** 25 minutes

---

## Validation Strategy

### After Each Step
- Verify scripts run without errors
- Check output files created and valid
- Ensure JSON structure maintained
- Run validation after updates

### Final Validation
```bash
# Verify all scripts created
ls -lh scripts/extract_url_patterns.py scripts/test_reconstructed_urls.py scripts/apply_reconstructions.py

# Verify all documentation created
ls -lh docs/partial_states_analysis.md docs/url_patterns_analysis.md docs/URL_RECONSTRUCTION_GUIDE.md

# Verify scripts run
python scripts/extract_url_patterns.py | head -20
python scripts/test_reconstructed_urls.py --help

# Verify states.json unchanged (backup only)
diff data/states.json data/states.json.backup
# Expected: Identical (only backup created)

# Verify no regressions
python -m json.tool data/states.json > /dev/null && echo "JSON valid"
```

---

## Success Criteria

- [ ] Partial states identified and documented
- [ ] Website navigation scripts created and tested
- [ ] Discovery process works on Washington proof-of-concept
- [ ] Discovered URLs are validated as working PDFs
- [ ] Successful URLs applied to states.json
- [ ] Updated URLs re-validated and confirmed working
- [ ] Discovery strategy guide documented
- [ ] Process ready for application to other states
- [ ] All changes committed with proper messages
- [ ] states.json maintains data integrity

**Definition of "Done":**

This plan is complete when:
- Partial states analysis identifies all states with mixed results
- Website navigation scripts work on Washington proof-of-concept
- At least 1 state has URLs successfully discovered and validated
- Discovery guide is comprehensive and reusable
- Process is documented for application to other states
- All working URLs remain working (no regressions)

---

## Rollback Plan

**If discovery breaks states.json:**
```bash
# Restore from backup
cp data/states.json.backup data/states.json

# Verify restoration
python -m json.tool data/states.json > /dev/null && echo "Restored"

# Re-attempt discovery more carefully
```

**If script has bugs:**
```bash
# Revert script commits
git revert HEAD~N

# Fix script
# (edit script files)

# Re-commit
git add scripts/
git commit -m "fix: repair discovery script"
```

---

## Potential Blockers

**Stop Conditions:**

- **If homepage/science page not accessible:** Website may be down or moved, need manual investigation
- **If no PDF links discovered:** Content organization different, need manual research
- **If discovery success rate < 20%:** Navigation approach ineffective, need strategy adjustment
- **If states.json becomes corrupted:** Restore from backup, review script logic

**When blocked:**
1. Document which step failed
2. Log discovery rates and error patterns
3. Preserve all analysis and scripts
4. Alert human with findings
5. Wait for intervention

---

## Notes

### Dependencies for Future Work

This plan enables:
- Systematic fixing of partial states (5-10 states)
- Reduced manual URL research time (estimated 50% reduction)
- Automated URL testing and validation
- Reusable website navigation methodology

### Not Included

- Manual URL research for 100% failed states (separate plan)
- Content validation enhancements (already implemented)
- Parser updates (separate feature)
- CLI new commands (separate feature)

### Estimated Impact

- **States affected:** 5-10 partial states
- **Documents potentially fixed:** 15-30 documents
- **Time saved:** ~30-60 hours of manual research
- **Automation benefit:** Reusable process for future URL issues

---

**Ready for execution approval**
**This plan has clear steps and validation gates**
