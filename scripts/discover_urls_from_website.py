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
                },
            )
        return self.client

    async def test_url(self, url: str) -> Dict:
        """Test if URL is valid and returns PDF"""
        try:
            client = await self.get_client()
            response = await client.head(url, follow_redirects=True)

            is_valid = (
                response.status_code == 200
                and "pdf" in response.headers.get("content-type", "").lower()
            )

            return {
                "url": url,
                "status_code": response.status_code,
                "content_type": response.headers.get("content-type", ""),
                "is_pdf": is_valid,
                "success": is_valid,
            }
        except Exception as e:
            return {
                "url": url,
                "status_code": 0,
                "content_type": "",
                "is_pdf": False,
                "success": False,
                "error": str(e),
            }

    async def test_homepage(self, homepage_url: str) -> bool:
        """Test if state website homepage is accessible"""
        print(f"\n[1] Testing state website...")
        print(f"    URL: {homepage_url}")

        try:
            client = await self.get_client()
            response = await client.get(homepage_url, follow_redirects=True)

            success = response.status_code == 200
            print(
                f"    Result: {'OK Accessible' if success else 'FAILED Accessible'} (HTTP {response.status_code})"
            )
            return success

        except Exception as e:
            print(f"    Result: FAILED Error - {e}")
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
                print(f"    Result: FAILED (HTTP {response.status_code})")
                return {
                    "accessible": False,
                    "documents": [],
                    "error": f"HTTP {response.status_code}",
                }

            print(f"    Result: OK Accessible (HTTP {response.status_code})")
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
                if link.startswith("#") or not link.startswith(("http", "/")):
                    continue

                # Make absolute URL
                absolute_url = urljoin(science_page_url, link)
                link_parsed = urlparse(absolute_url)

                # Only follow same domain (don't go to external sites)
                if link_parsed.netloc != base_domain:
                    continue

                # Only care about PDFs
                if ".pdf" not in absolute_url.lower():
                    continue

                if absolute_url not in discovered_links:
                    discovered_links.append(absolute_url)

            print(f"    Found {len(discovered_links)} PDF links")
            return {"accessible": True, "documents": discovered_links, "error": None}

        except Exception as e:
            print(f"    Result: FAILED Error - {e}")
            return {"accessible": False, "documents": [], "error": str(e)}

    async def test_discovered_urls(self, urls: List[str]) -> List[Dict]:
        """Test all discovered URLs to find working ones"""
        print(f"\n[4] Testing discovered URLs...")

        results = []
        for i, url in enumerate(urls, 1):
            print(f"    Testing {i}/{len(urls)}...")
            result = await self.test_url(url)
            results.append(result)

            if result["success"]:
                print(f"      OK {url[:60]}...")
            else:
                status_msg = (
                    f"HTTP {result['status_code']}"
                    if result["status_code"] != 0
                    else "Connection error"
                )
                print(f"      FAILED {status_msg}")

        working_count = sum(1 for r in results if r["success"])
        print(f"\n    Summary: {working_count}/{len(urls)} URLs working")

        return results

    async def match_to_expected_docs(
        self, test_results: List[Dict], expected_docs: List[str]
    ) -> Dict:
        """Match discovered working URLs to expected document titles"""
        print(f"\n[5] Matching URLs to expected documents...")

        doc_mapping = {}

        for doc_title in expected_docs:
            title_lower = doc_title.lower()

            # Try to match based on URL content
            for result in test_results:
                if not result["success"]:
                    continue

                url = result["url"]

                # Extract filename and path from URL
                parsed = urlparse(url)
                path_lower = parsed.path.lower()
                filename = parsed.path.split("/")[-1].lower().replace("%20", " ")

                # Check for grade match
                if "grade" in title_lower:
                    grade_match = re.search(r"grade\s*(\d+)", title_lower)
                    if grade_match:
                        grade_num = grade_match.group(1)
                        if (
                            f"grade{grade_num}" in path_lower
                            or f"grade {grade_num}" in filename
                        ):
                            doc_mapping[doc_title] = url
                            print(f"  OK Matched by grade: {doc_title[:40]}")
                            break

                # Check for K-12 match
                elif "k-12" in title_lower or "k12" in title_lower:
                    if "k-12" in path_lower or "k12" in path_lower:
                        doc_mapping[doc_title] = url
                        print(f"  OK Matched by K-12: {doc_title[:40]}")
                        break

                # Check for science standards keywords
                elif "science" in filename and "standard" in filename:
                    # Additional check for state name
                    state_abbrev = expected_docs[0] if expected_docs else ""
                    # Would need to pass state info to match properly
                    if len(doc_mapping) < len(expected_docs):
                        doc_mapping[doc_title] = url
                        print(f"  OK Matched by keywords: {doc_title[:40]}")
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
        state_abbrev = state_data["state_abbrev"]
        state_name = state_data["state_name"]
        homepage_url = state_data["website"]
        science_page_url = state_data["science_page"]

        print("\n" + "=" * 70)
        print(f"URL Discovery for {state_name} ({state_abbrev})")
        print("=" * 70)

        # Step 1: Test homepage
        homepage_accessible = await self.test_homepage(homepage_url)

        if not homepage_accessible:
            return {
                "state": state_abbrev,
                "homepage_accessible": False,
                "science_page_accessible": False,
                "discovered_urls": [],
                "working_urls": [],
                "matched_docs": {},
                "error": f"Homepage not accessible: {homepage_url}",
            }

        # Step 2: Navigate to science page
        science_result = await self.navigate_to_science_page(science_page_url)

        if not science_result["accessible"]:
            return {
                "state": state_abbrev,
                "homepage_accessible": True,
                "science_page_accessible": False,
                "discovered_urls": [],
                "working_urls": [],
                "matched_docs": {},
                "error": science_result["error"],
            }

        # Step 3: Test discovered URLs
        test_results = await self.test_discovered_urls(science_result["documents"])

        # Step 4: Match to expected documents
        expected_docs = [doc["title"] for doc in state_data["documents"]]
        doc_mapping = await self.match_to_expected_docs(test_results, expected_docs)

        working_urls = [r["url"] for r in test_results if r["success"]]

        return {
            "state": state_abbrev,
            "homepage_accessible": True,
            "science_page_accessible": True,
            "discovered_urls": science_result["documents"],
            "working_urls": working_urls,
            "matched_docs": doc_mapping,
            "error": None,
        }


async def main():
    # Load states data
    with open("data/states.json") as f:
        states = json.load(f)

    # Focus on Oregon as proof-of-concept (NGSS direct adoption)
    target_state = "OR"
    state_data = states[target_state]

    # Discover URLs
    navigator = StateWebsiteNavigator()
    result = await navigator.discover_for_state(state_data)

    # Save results
    with open("docs/discovered_urls.json", "w") as f:
        json.dump(result, f, indent=2)

    # Print summary
    print("\n" + "=" * 70)
    print("DISCOVERY SUMMARY")
    print("=" * 70)
    print(f"State: {result['state']} - {states[result['state']]['state_name']}")
    print(f"NGSS Status: {states[result['state']]['ngss_status']}")
    print(f"\nAccessibility:")
    print(f"  Homepage: {'OK' if result['homepage_accessible'] else 'FAILED'}")
    print(f"  Science Page: {'OK' if result['science_page_accessible'] else 'FAILED'}")
    print(f"\nURL Discovery:")
    print(f"  Expected documents: {len(state_data['documents'])}")
    print(f"  Discovered PDFs: {len(result['discovered_urls'])}")
    print(f"  Working PDFs: {len(result['working_urls'])}")
    print(f"  Matched documents: {len(result['matched_docs'])}")

    if result["error"]:
        print(f"\nError: {result['error']}")

    print("\nMatched Documents:")
    for title, url in result["matched_docs"].items():
        print(f"  - {title[:50]}")
        print(f"    {url[:70]}...")

    success_rate = (
        len(result["matched_docs"]) / len(state_data["documents"])
        if state_data["documents"]
        else 0
    )
    print(f"\nSuccess Rate: {success_rate * 100:.1f}%")


if __name__ == "__main__":
    asyncio.run(main())
