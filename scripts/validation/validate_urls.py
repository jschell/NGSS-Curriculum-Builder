#!/usr/bin/env python3
# /// script
# dependencies = [
#     "httpx>=0.27.0",
# ]
# ///
"""
URL Validation Enhancement - Step 2 of Comprehensive Validation Suite

Refactored to use validation_framework.py. Adds:
  - HTTP vs HTTPS consistency checks
  - Redirect chain detection
  - SSL certificate validation
  - Common URL typo detection
  - Deprecated domain flagging
  - Response caching (per run)
  - Parallel checking via asyncio.gather
  - --verbose / --state / --severity CLI flags
"""

from __future__ import annotations

import asyncio
import re
import ssl
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse

import httpx

# ---------------------------------------------------------------------------
# Framework import (searches upward from this file)
# ---------------------------------------------------------------------------
sys.path.insert(0, str(Path(__file__).resolve().parent))
from validation_framework import Issue, Severity, Validator, ValidationRunner, load_states

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

DEPRECATED_DOMAINS: List[str] = [
    "www.achieve.org",           # merged into other orgs
    "ngss.nsta.org",             # old NSTA NGSS hub
    "www.nextgenscience.org",    # retired - redirects
    "rpdp.net",                  # Nevada old domain
    "ped.state.nm.us",           # NM old domain
    "dc.doe.gov",                # DC old domain
]

TYPO_PATTERNS: List[tuple[str, str]] = [
    (r"^htpp://",  "Typo: 'htpp://' should be 'http://'"),
    (r"^htps://",  "Typo: 'htps://' should be 'https://'"),
    (r"^htp://",   "Typo: 'htp://' should be 'http://'"),
    (r"^https?:/[^/]", "Typo: missing double-slash after scheme"),
    (r"\.pdf\.pdf$",   "Typo: double .pdf extension"),
    (r"\s",            "Whitespace in URL"),
]

# Concurrency limit so we don't hammer servers
CONCURRENCY = 8


# ---------------------------------------------------------------------------
# URLValidator
# ---------------------------------------------------------------------------

class URLValidator(Validator):
    """
    Validates all document URLs in states.json.

    Checks performed per URL
    ------------------------
    U001  Typo in URL scheme or format
    U002  HTTP used where HTTPS is available
    U003  URL points to a deprecated domain
    U004  HTTP error (4xx / 5xx / network failure)
    U005  Redirect chain detected (informational)
    U006  SSL certificate invalid / untrusted
    U007  Response is HTML/error page instead of expected document
    """

    name = "URLValidator"

    def __init__(self, timeout: int = 20, verbose: bool = False):
        self.timeout = timeout
        self.verbose = verbose
        # Simple in-process cache: url -> (http_status, final_url, content_type, ssl_ok, error)
        self._cache: Dict[str, dict] = {}

    # ------------------------------------------------------------------
    # Main entry point (sync wrapper around async logic)
    # ------------------------------------------------------------------

    def validate(self, data: Dict[str, Any]) -> List[Issue]:
        return asyncio.run(self._validate_async(data))

    # ------------------------------------------------------------------
    # Async core
    # ------------------------------------------------------------------

    async def _validate_async(self, data: Dict[str, Any]) -> List[Issue]:
        items = self._collect_urls(data)
        sem = asyncio.Semaphore(CONCURRENCY)
        limits = httpx.Limits(max_connections=CONCURRENCY, max_keepalive_connections=CONCURRENCY)

        async with httpx.AsyncClient(
            timeout=self.timeout,
            limits=limits,
            follow_redirects=True,
            verify=False,   # we check SSL manually below
            headers={
                "User-Agent": (
                    "Mozilla/5.0 (compatible; NGSS-Validator/1.0; "
                    "+https://github.com/jschell/NGSS-Curriculum-Builder)"
                ),
                "Accept": "application/pdf,text/html,*/*",
            },
        ) as client:
            tasks = [
                self._check_url(client, sem, state, doc_title, url)
                for state, doc_title, url in items
            ]
            results = await asyncio.gather(*tasks, return_exceptions=True)

        issues: List[Issue] = []
        for (state, doc_title, url), result in zip(items, results):
            if isinstance(result, Exception):
                issues.append(Issue(
                    severity=Severity.ERROR,
                    code="U004",
                    state=state,
                    field=doc_title,
                    message=f"Unexpected error checking URL: {result}",
                    suggestion="Inspect URL manually",
                ))
                continue
            issues.extend(result)

        return issues

    def _collect_urls(self, data: Dict[str, Any]) -> List[tuple[str, str, str]]:
        items = []
        for state_abbrev, state_data in data.items():
            for doc in state_data.get("documents", []):
                url = doc.get("url", "").strip()
                title = doc.get("title", "untitled")
                if url:
                    items.append((state_abbrev, title, url))
        return items

    # ------------------------------------------------------------------
    # Per-URL checks
    # ------------------------------------------------------------------

    async def _check_url(
        self,
        client: httpx.AsyncClient,
        sem: asyncio.Semaphore,
        state: str,
        doc_title: str,
        url: str,
    ) -> List[Issue]:
        issues: List[Issue] = []
        field = doc_title[:60]

        # 1. Static checks (no network)
        issues.extend(self._check_typos(state, field, url))
        issues.extend(self._check_deprecated_domain(state, field, url))

        # 2. Network checks (cached)
        async with sem:
            net = await self._fetch(client, url)

        if self.verbose:
            print(f"  [{state}] {url[:60]}... -> {net['status']} {net.get('error','')}")

        # 3. SSL check (independent of redirect; checks *original* URL if HTTPS)
        issues.extend(self._check_ssl(state, field, url, net))

        # 4. HTTP -> HTTPS upgrade opportunity
        issues.extend(self._check_http_vs_https(state, field, url, net))

        # 5. Network error / HTTP error
        if net["error"] and net["status"] == 0:
            issues.append(Issue(
                severity=Severity.ERROR,
                code="U004",
                state=state,
                field=field,
                message=f"Network failure: {net['error']}",
                suggestion="Check internet connectivity or retry later",
            ))
        elif net["status"] not in (0, 200, 206):
            severity = Severity.ERROR if net["status"] >= 400 else Severity.WARNING
            issues.append(Issue(
                severity=severity,
                code="U004",
                state=state,
                field=field,
                message=f"HTTP {net['status']} for {url}",
                suggestion="Find updated URL on state education agency website",
            ))

        # 6. Redirect chain (informational)
        if net.get("redirects"):
            chain = " -> ".join(net["redirects"])
            issues.append(Issue(
                severity=Severity.INFO,
                code="U005",
                state=state,
                field=field,
                message=f"Redirect chain: {chain}",
                suggestion="Consider updating URL to final destination",
            ))

        # 7. HTML returned instead of document
        if net["status"] == 200 and "html" in net.get("content_type", ""):
            issues.append(Issue(
                severity=Severity.WARNING,
                code="U007",
                state=state,
                field=field,
                message=f"URL returns HTML (expected PDF/document): {url}",
                suggestion="Verify this is the correct direct-download link",
            ))

        return issues

    # ------------------------------------------------------------------
    # Static checks
    # ------------------------------------------------------------------

    def _check_typos(self, state: str, field: str, url: str) -> List[Issue]:
        issues = []
        for pattern, description in TYPO_PATTERNS:
            if re.search(pattern, url, re.IGNORECASE):
                issues.append(Issue(
                    severity=Severity.ERROR,
                    code="U001",
                    state=state,
                    field=field,
                    message=f"{description}: {url}",
                    suggestion="Fix URL format",
                ))
        return issues

    def _check_deprecated_domain(self, state: str, field: str, url: str) -> List[Issue]:
        parsed = urlparse(url)
        host = parsed.netloc.lower()
        for domain in DEPRECATED_DOMAINS:
            if host == domain or host.endswith("." + domain):
                return [Issue(
                    severity=Severity.WARNING,
                    code="U003",
                    state=state,
                    field=field,
                    message=f"URL uses deprecated domain '{domain}': {url}",
                    suggestion="Find replacement URL on current state education website",
                )]
        return []

    # ------------------------------------------------------------------
    # Network-dependent checks
    # ------------------------------------------------------------------

    def _check_ssl(
        self, state: str, field: str, url: str, net: dict
    ) -> List[Issue]:
        if not url.startswith("https://"):
            return []
        if net.get("ssl_error"):
            return [Issue(
                severity=Severity.WARNING,
                code="U006",
                state=state,
                field=field,
                message=f"SSL issue for {url}: {net['ssl_error']}",
                suggestion="Verify SSL certificate is valid and not expired",
            )]
        return []

    def _check_http_vs_https(
        self, state: str, field: str, url: str, net: dict
    ) -> List[Issue]:
        if not url.startswith("http://"):
            return []
        # Check if the final URL ended up as HTTPS (server upgraded it)
        final = net.get("final_url", "")
        if final.startswith("https://"):
            return [Issue(
                severity=Severity.WARNING,
                code="U002",
                state=state,
                field=field,
                message=f"URL uses HTTP but server serves HTTPS: {url}",
                suggestion=f"Update URL to HTTPS: {final}",
            )]
        # Even if no upgrade, flag plain HTTP as a warning
        return [Issue(
            severity=Severity.INFO,
            code="U002",
            state=state,
            field=field,
            message=f"URL uses plain HTTP (not HTTPS): {url}",
            suggestion="Verify whether an HTTPS version is available",
        )]

    # ------------------------------------------------------------------
    # HTTP fetch (cached)
    # ------------------------------------------------------------------

    async def _fetch(self, client: httpx.AsyncClient, url: str) -> dict:
        if url in self._cache:
            return self._cache[url]

        result: dict = {
            "status": 0,
            "final_url": url,
            "content_type": "",
            "redirects": [],
            "error": None,
            "ssl_error": None,
        }

        # Separate SSL check against the original URL
        if url.startswith("https://"):
            result["ssl_error"] = await self._check_ssl_cert(url)

        try:
            response = await client.head(url, follow_redirects=True)
            result["status"] = response.status_code
            result["final_url"] = str(response.url)
            result["content_type"] = response.headers.get("content-type", "")

            # Capture redirect chain
            for h in response.history:
                result["redirects"].append(str(h.url))
            if result["redirects"]:
                result["redirects"].append(str(response.url))

        except httpx.TimeoutException:
            result["error"] = "Timeout"
        except httpx.ConnectError as e:
            result["error"] = f"ConnectError: {e}"
        except Exception as e:
            result["error"] = f"{type(e).__name__}: {e}"

        self._cache[url] = result
        return result

    async def _check_ssl_cert(self, url: str) -> Optional[str]:
        """Return error string if SSL cert is invalid, else None."""
        parsed = urlparse(url)
        host = parsed.hostname or ""
        port = parsed.port or 443
        try:
            ctx = ssl.create_default_context()
            loop = asyncio.get_event_loop()
            conn = await loop.run_in_executor(
                None, lambda: ctx.wrap_socket(
                    __import__("socket").create_connection((host, port), timeout=10),
                    server_hostname=host,
                )
            )
            conn.close()
            return None
        except ssl.SSLCertVerificationError as e:
            return f"Certificate verification failed: {e.reason}"
        except ssl.SSLError as e:
            return f"SSL error: {e}"
        except Exception:
            return None  # Network error handled separately


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def parse_args(argv: List[str]) -> dict:
    args = {
        "states": None,
        "severity": "INFO",
        "verbose": False,
    }
    i = 0
    while i < len(argv):
        arg = argv[i]
        if arg in ("--verbose", "-v"):
            args["verbose"] = True
        elif arg == "--state" and i + 1 < len(argv):
            args["states"] = [s.strip().upper() for s in argv[i + 1].split(",")]
            i += 1
        elif arg == "--severity" and i + 1 < len(argv):
            args["severity"] = argv[i + 1].upper()
            i += 1
        i += 1
    return args


def main() -> int:
    argv = sys.argv[1:]

    if "--help" in argv or "-h" in argv:
        print(__doc__)
        print("Usage: uv run validate_urls.py [--verbose] [--state WA,OR] [--severity ERROR|WARNING|INFO]")
        return 0

    args = parse_args(argv)
    severity_map = {
        "ERROR": Severity.ERROR,
        "WARNING": Severity.WARNING,
        "INFO": Severity.INFO,
    }
    min_severity = severity_map.get(args["severity"], Severity.INFO)

    data = load_states()
    print(f"Loaded {len(data)} states.")

    validator = URLValidator(verbose=args["verbose"])
    runner = ValidationRunner()
    runner.add_validator(validator)

    issues = runner.run(data, states=args["states"], min_severity=min_severity)
    print(runner.report(issues))

    errors = [i for i in issues if i.severity == Severity.ERROR]
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
