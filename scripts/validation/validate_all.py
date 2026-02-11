#!/usr/bin/env python3
# /// script
# dependencies = [
#     "httpx>=0.27.0",
# ]
# ///
"""
Master Validation Script - Step 6 of Comprehensive Validation Suite

Runs all validators and produces a combined report.

Usage
-----
    uv run validate_all.py                          # full suite
    uv run validate_all.py --quick                  # skip URL network checks
    uv run validate_all.py --state WA,OR            # single/multiple states
    uv run validate_all.py --severity ERROR         # errors only
    uv run validate_all.py --report report.html     # save HTML report
    uv run validate_all.py --report report.md       # save Markdown report
"""

from __future__ import annotations

import sys
import time
from datetime import datetime
from pathlib import Path
from typing import List, Optional

sys.path.insert(0, str(Path(__file__).resolve().parent))
from validation_framework import Issue, Severity, ValidationRunner, load_states
from validate_page_ranges import PageRangeValidator
from validate_data_integrity import DataIntegrityValidator
from validate_special_structures import SpecialStructureValidator


# ---------------------------------------------------------------------------
# HTML report
# ---------------------------------------------------------------------------

def _severity_color(sev: Severity) -> str:
    return {"ERROR": "#c0392b", "WARNING": "#e67e22", "INFO": "#2980b9"}[sev.value]


def _severity_bg(sev: Severity) -> str:
    return {"ERROR": "#fdecea", "WARNING": "#fef9e7", "INFO": "#eaf4fb"}[sev.value]


def generate_html_report(
    issues: List[Issue],
    states_data: dict,
    elapsed: float,
    quick: bool,
) -> str:
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    errors = [i for i in issues if i.severity == Severity.ERROR]
    warnings = [i for i in issues if i.severity == Severity.WARNING]
    infos = [i for i in issues if i.severity == Severity.INFO]

    total_docs = sum(len(s.get("documents", [])) for s in states_data.values())
    docs_with_pr = sum(
        1 for s in states_data.values()
        for doc in s.get("documents", [])
        if isinstance(doc.get("page_range"), dict)
    )
    complete_k12_states = sum(
        1 for s in states_data.values()
        if any(d.get("document_type") == "complete_k12" for d in s.get("documents", []))
    )

    def issue_rows(issue_list: List[Issue]) -> str:
        rows = []
        for i in issue_list:
            bg = _severity_bg(i.severity)
            color = _severity_color(i.severity)
            field = i.field or ""
            suggestion = i.suggestion or ""
            rows.append(
                f'<tr style="background:{bg}">'
                f'<td style="color:{color};font-weight:bold;white-space:nowrap">[{i.severity.value}][{i.code}]</td>'
                f'<td><b>{i.state}</b></td>'
                f'<td>{field}</td>'
                f'<td>{i.message}</td>'
                f'<td style="color:#555"><em>{suggestion}</em></td>'
                f'</tr>'
            )
        return "\n".join(rows)

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>NGSS Validation Report — {now}</title>
<style>
  body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; margin: 0; padding: 20px; background: #f5f5f5; color: #333; }}
  h1 {{ color: #2c3e50; border-bottom: 3px solid #3498db; padding-bottom: 10px; }}
  h2 {{ color: #2c3e50; margin-top: 30px; }}
  .summary-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(160px, 1fr)); gap: 15px; margin: 20px 0; }}
  .card {{ background: white; border-radius: 8px; padding: 15px; text-align: center; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
  .card .number {{ font-size: 2em; font-weight: bold; }}
  .card .label {{ font-size: 0.85em; color: #666; margin-top: 4px; }}
  .error   {{ color: #c0392b; }}
  .warning {{ color: #e67e22; }}
  .info    {{ color: #2980b9; }}
  .ok      {{ color: #27ae60; }}
  table {{ width: 100%; border-collapse: collapse; background: white; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
  th {{ background: #2c3e50; color: white; padding: 10px 12px; text-align: left; font-size: 0.9em; }}
  td {{ padding: 8px 12px; border-bottom: 1px solid #eee; font-size: 0.9em; vertical-align: top; }}
  tr:last-child td {{ border-bottom: none; }}
  .meta {{ color: #888; font-size: 0.85em; margin-bottom: 20px; }}
  .quick-badge {{ background: #e67e22; color: white; border-radius: 4px; padding: 2px 8px; font-size: 0.8em; }}
</style>
</head>
<body>
<h1>NGSS Curriculum Builder — Validation Report</h1>
<p class="meta">
  Generated: {now} &nbsp;|&nbsp; Duration: {elapsed:.1f}s
  {"&nbsp;|&nbsp; <span class='quick-badge'>QUICK MODE — URL checks skipped</span>" if quick else ""}
</p>

<h2>Summary</h2>
<div class="summary-grid">
  <div class="card"><div class="number">{len(states_data)}</div><div class="label">States</div></div>
  <div class="card"><div class="number">{total_docs}</div><div class="label">Documents</div></div>
  <div class="card"><div class="number error">{len(errors)}</div><div class="label">Errors</div></div>
  <div class="card"><div class="number warning">{len(warnings)}</div><div class="label">Warnings</div></div>
  <div class="card"><div class="number info">{len(infos)}</div><div class="label">Info</div></div>
  <div class="card"><div class="number ok">{docs_with_pr}</div><div class="label">Docs with page_range</div></div>
  <div class="card"><div class="number ok">{complete_k12_states}</div><div class="label">Complete K-12 states</div></div>
</div>
"""

    for label, issue_list in [("Errors", errors), ("Warnings", warnings), ("Info", infos)]:
        if not issue_list:
            continue
        css_class = label.lower().rstrip("s")
        html += f"""
<h2 class="{css_class}">{label} ({len(issue_list)})</h2>
<table>
<thead><tr>
  <th>Severity / Code</th><th>State</th><th>Field / Document</th>
  <th>Message</th><th>Suggestion</th>
</tr></thead>
<tbody>
{issue_rows(issue_list)}
</tbody>
</table>
"""

    html += "\n</body>\n</html>\n"
    return html


# ---------------------------------------------------------------------------
# Markdown report
# ---------------------------------------------------------------------------

def generate_markdown_report(
    issues: List[Issue],
    states_data: dict,
    elapsed: float,
    quick: bool,
) -> str:
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    errors = [i for i in issues if i.severity == Severity.ERROR]
    warnings = [i for i in issues if i.severity == Severity.WARNING]
    infos = [i for i in issues if i.severity == Severity.INFO]

    total_docs = sum(len(s.get("documents", [])) for s in states_data.values())
    docs_with_pr = sum(
        1 for s in states_data.values()
        for doc in s.get("documents", [])
        if isinstance(doc.get("page_range"), dict)
    )

    lines = [
        "# NGSS Curriculum Builder — Validation Report",
        "",
        f"**Generated:** {now}  ",
        f"**Duration:** {elapsed:.1f}s  ",
        f"**Mode:** {'Quick (URL checks skipped)' if quick else 'Full'}",
        "",
        "## Summary",
        "",
        f"| Metric | Value |",
        f"|--------|-------|",
        f"| States | {len(states_data)} |",
        f"| Documents | {total_docs} |",
        f"| Errors | {len(errors)} |",
        f"| Warnings | {len(warnings)} |",
        f"| Info | {len(infos)} |",
        f"| Docs with page_range | {docs_with_pr} |",
        "",
    ]

    for label, issue_list in [("Errors", errors), ("Warnings", warnings), ("Info", infos)]:
        if not issue_list:
            continue
        lines += [f"## {label} ({len(issue_list)})", ""]
        lines += ["| Code | State | Field | Message | Suggestion |",
                  "|------|-------|-------|---------|------------|"]
        for i in issue_list:
            field = (i.field or "").replace("|", "\\|")
            msg = i.message.replace("|", "\\|")
            sug = (i.suggestion or "").replace("|", "\\|")
            lines.append(f"| [{i.severity.value}][{i.code}] | {i.state} | {field} | {msg} | {sug} |")
        lines.append("")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def parse_args(argv: List[str]) -> dict:
    args = {
        "states": None,
        "severity": "INFO",
        "quick": False,
        "report": None,
        "verbose": False,
    }
    i = 0
    while i < len(argv):
        a = argv[i]
        if a == "--quick":
            args["quick"] = True
        elif a in ("--verbose", "-v"):
            args["verbose"] = True
        elif a == "--state" and i + 1 < len(argv):
            args["states"] = [s.strip().upper() for s in argv[i+1].split(",")]
            i += 1
        elif a == "--severity" and i + 1 < len(argv):
            args["severity"] = argv[i+1].upper()
            i += 1
        elif a == "--report" and i + 1 < len(argv):
            args["report"] = argv[i+1]
            i += 1
        i += 1
    return args


def main() -> int:
    argv = sys.argv[1:]
    if "--help" in argv or "-h" in argv:
        print(__doc__)
        return 0

    args = parse_args(argv)
    severity_map = {"ERROR": Severity.ERROR, "WARNING": Severity.WARNING, "INFO": Severity.INFO}
    min_severity = severity_map.get(args["severity"], Severity.INFO)

    data = load_states()
    state_count = len(args["states"]) if args["states"] else len(data)
    print(f"NGSS Validation Suite — {state_count} state(s)")
    print(f"Mode: {'quick' if args['quick'] else 'full'}")
    print()

    runner = ValidationRunner()
    runner.add_validator(PageRangeValidator(verbose=args["verbose"]))
    runner.add_validator(DataIntegrityValidator())
    runner.add_validator(SpecialStructureValidator())

    if not args["quick"]:
        try:
            from validate_urls import URLValidator
            runner.add_validator(URLValidator(verbose=args["verbose"]))
        except ImportError:
            print("Warning: validate_urls.py not available — skipping URL checks")

    start = time.time()
    issues = runner.run(data, states=args["states"], min_severity=min_severity)
    elapsed = time.time() - start

    # Console output
    print(runner.report(issues))
    print(f"Completed in {elapsed:.1f}s")

    # File report
    report_path = args.get("report")
    if report_path:
        path = Path(report_path)
        if path.suffix.lower() == ".html":
            content = generate_html_report(issues, data, elapsed, args["quick"])
        else:
            content = generate_markdown_report(issues, data, elapsed, args["quick"])
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        print(f"Report saved: {path}")

    errors = [i for i in issues if i.severity == Severity.ERROR]
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
