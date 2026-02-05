import json
from datetime import datetime
from pathlib import Path

# Load validation results
with open("validation_results.json") as f:
    data = json.load(f)

# Load states.json to get state names
with open("data/states.json") as f:
    states_data = json.load(f)

# Extract results by state
state_results = {}
for url, result in data["results"].items():
    state = result["state_abbrev"]
    if state not in state_results:
        state_results[state] = {
            "state_name": states_data.get(state, {}).get("state_name", state),
            "documents": [],
        }
    state_results[state]["documents"].append(result)

# Classify states by priority
tier1_critical = []
tier2_partial = []
tier3_warnings = []
tier4_verified = []

for state_abbrev, state_data in state_results.items():
    docs = state_data["documents"]
    total = len(docs)

    # Count issues
    broken_404 = sum(1 for d in docs if d.get("http_status") == 404)
    broken_403 = sum(1 for d in docs if d.get("http_status") == 403)
    broken_500 = sum(1 for d in docs if d.get("http_status") == 500)
    broken_connection = sum(1 for d in docs if d.get("http_status") == 0)
    broken_202 = sum(1 for d in docs if d.get("http_status") == 202)
    html_format = sum(1 for d in docs if d.get("content_type") == "html")

    total_broken = (
        broken_404
        + broken_403
        + broken_500
        + broken_connection
        + broken_202
        + html_format
    )

    # Check content validation
    low_confidence = sum(
        1
        for d in docs
        if d.get("content_validation")
        and d["content_validation"].get("confidence_score", 0) < 0.5
    )
    medium_confidence = sum(
        1
        for d in docs
        if d.get("content_validation")
        and 0.5 <= d["content_validation"].get("confidence_score", 0) < 0.8
    )

    working_pdfs = sum(
        1
        for d in docs
        if d.get("http_status") == 200 and d.get("content_type") == "pdf"
    )

    if total_broken == total and total > 0:
        tier1_critical.append(
            (
                state_abbrev,
                state_data["state_name"],
                total,
                broken_404,
                broken_403,
                broken_connection,
                html_format,
            )
        )
    elif total_broken > 0 or low_confidence > 0:
        tier2_partial.append(
            (
                state_abbrev,
                state_data["state_name"],
                total_broken + low_confidence,
                total,
                broken_404,
                broken_403,
                broken_connection,
                html_format,
                low_confidence,
                medium_confidence,
            )
        )
    elif medium_confidence > 0:
        tier3_warnings.append(
            (
                state_abbrev,
                state_data["state_name"],
                total,
                medium_confidence,
                working_pdfs,
            )
        )
    elif working_pdfs == total:
        tier4_verified.append((state_abbrev, state_data["state_name"], total))

# Generate priorities report
report_lines = [
    "# URL Update Priorities",
    "",
    f"**Validation Date:** {datetime.now().strftime('%Y-%m-%d')}",
    f"**Total URLs Tested:** {data['total_urls']}",
    "**Validator Version:** 1.0",
    "",
    "---",
    "",
]

# Tier 1: Critical
report_lines.extend(
    [
        "## Tier 1: Critical - All Documents Broken (Highest Priority)",
        "",
        "These states have all documents failing with 404, 403, connection errors, or wrong format.",
        "",
    ]
)

if tier1_critical:
    for (
        state_abbrev,
        state_name,
        total,
        broken_404,
        broken_403,
        broken_connection,
        html_format,
    ) in sorted(tier1_critical, key=lambda x: x[0]):
        issues = []
        if broken_404 > 0:
            issues.append(f"{broken_404} HTTP 404")
        if broken_403 > 0:
            issues.append(f"{broken_403} HTTP 403 (bot detection)")
        if broken_connection > 0:
            issues.append(f"{broken_connection} connection errors")
        if html_format > 0:
            issues.append(f"{html_format} HTML (wrong format)")

        report_lines.extend(
            [
                f"### {state_name} ({state_abbrev})",
                f"- **Documents Affected:** {total}/{total} (100%)",
                f"- **Issue:** {'; '.join(issues)}",
                f"- **Root Cause:** URL structure changed or server blocks automated requests",
                f"- **Recommended Action:** Manual investigation of state education website, find current standards pages, locate correct PDF URLs",
                f"- **Estimated Effort:** 2-3 hours",
                "",
            ]
        )
else:
    report_lines.append("*No states with 100% failure rate*")
    report_lines.append("")

# Tier 2: Partial Issues
report_lines.extend(
    [
        "---",
        "",
        "## Tier 2: Partial - Some Documents Broken or Questionable (Medium Priority)",
        "",
        "These states have some broken URLs or content validation issues.",
        "",
    ]
)

if tier2_partial:
    for item in sorted(tier2_partial, key=lambda x: (-x[2], x[0])):
        (
            state_abbrev,
            state_name,
            broken,
            total,
            broken_404,
            broken_403,
            broken_connection,
            html_format,
            low_conf,
            medium_conf,
        ) = item
        percentage = broken * 100 // total

        issues = []
        if broken_404 > 0:
            issues.append(f"{broken_404} HTTP 404")
        if broken_403 > 0:
            issues.append(f"{broken_403} HTTP 403 (bot detection)")
        if broken_connection > 0:
            issues.append(f"{broken_connection} connection errors")
        if html_format > 0:
            issues.append(f"{html_format} HTML (wrong format)")
        if low_conf > 0:
            issues.append(f"{low_conf} low confidence (<0.5)")
        if medium_conf > 0:
            issues.append(f"{medium_conf} questionable (0.5-0.8 confidence)")

        report_lines.extend(
            [
                f"### {state_name} ({state_abbrev})",
                f"- **Documents Affected:** {broken}/{total} ({percentage}%)",
                f"- **Issue:** {'; '.join(issues)}",
                f"- **Recommended Action:** Verify broken URLs manually, research state standards page, cross-reference with verified URLs",
                f"- **Estimated Effort:** 1-2 hours",
                "",
            ]
        )
else:
    report_lines.append("*No states with partial issues*")
    report_lines.append("")

# Tier 3: Warnings
report_lines.extend(
    [
        "---",
        "",
        "## Tier 3: Verified with Minor Warnings (Low Priority)",
        "",
        "States with working URLs but requiring manual review for confidence issues.",
        "",
    ]
)

if tier3_warnings:
    for state_abbrev, state_name, total, medium_conf, working_pdfs in sorted(
        tier3_warnings, key=lambda x: x[0]
    ):
        if medium_conf > 0:
            report_lines.extend(
                [
                    f"### {state_name} ({state_abbrev})",
                    f"- **Documents:** {total}",
                    f"- **Working PDFs:** {working_pdfs}",
                    f"- **Questionable (0.5-0.8 confidence):** {medium_conf}",
                    f"- **Recommended Action:** Manual review of questionable documents to verify content correctness",
                    f"- **Estimated Effort:** 30-45 minutes",
                    "",
                ]
            )
else:
    report_lines.append("*No states with warnings*")
    report_lines.append("")

# Tier 4: All Verified
report_lines.extend(
    [
        "---",
        "",
        "## Tier 4: All Verified - No Action Needed",
        "",
        "States with all documents verified as working PDFs with high confidence.",
        "",
    ]
)

if tier4_verified:
    for state_abbrev, state_name, total in sorted(tier4_verified, key=lambda x: x[0]):
        report_lines.append(
            f"- **{state_name} ({state_abbrev})** - All {total} documents verified"
        )
else:
    report_lines.append("*No states with all verified URLs*")

# Summary
report_lines.extend(
    [
        "",
        "---",
        "",
        "## Summary",
        "",
        f"- **Tier 1 (Critical):** {len(tier1_critical)} states - Immediate attention required",
        f"- **Tier 2 (Partial):** {len(tier2_partial)} states - Medium priority",
        f"- **Tier 3 (Warnings):** {len(tier3_warnings)} states - Low priority",
        f"- **Tier 4 (Verified):** {len(tier4_verified)} states - No action needed",
        f"- **Total States:** {len(tier1_critical) + len(tier2_partial) + len(tier3_warnings) + len(tier4_verified)}",
        "",
    ]
)

# Content Validation Summary
report_lines.extend(
    [
        "## Content Validation Summary",
        "",
        "Based on PDF text extraction for grade level, state name and science keywords",
        "",
    ]
)

summary = data["summary"]
report_lines.extend(
    [
        f"- **High confidence (≥ 0.8):** {summary['content_verified']} documents - Verified correct",
        f"- **Medium confidence (0.5-0.8):** {summary['content_questionable']} documents - Needs manual review",
        f"- **Low confidence (< 0.5):** {summary['wrong_document']} documents - Likely wrong document",
        "",
    ]
)

# HTTP Status Breakdown
status_breakdown = {}
for result in data["results"].values():
    status = result.get("http_status", 0)
    status_breakdown[status] = status_breakdown.get(status, 0) + 1

report_lines.extend(
    [
        "## HTTP Status Breakdown",
        "",
        f"- **Connection Errors (0):** {status_breakdown.get(0, 0)}",
        f"- **HTTP 200 (OK):** {status_breakdown.get(200, 0)} (of which {summary['working_pdf']} are PDFs)",
        f"- **HTTP 202 (Accepted):** {status_breakdown.get(202, 0)}",
        f"- **HTTP 403 (Forbidden):** {status_breakdown.get(403, 0)}",
        f"- **HTTP 404 (Not Found):** {status_breakdown.get(404, 0)}",
        f"- **HTTP 500 (Server Error):** {status_breakdown.get(500, 0)}",
        "",
    ]
)

# Estimated Total Effort
tier1_effort = len(tier1_critical) * 2.5
tier2_effort = len(tier2_partial) * 1.5
tier3_effort = len(tier3_warnings) * 0.5
total_effort = tier1_effort + tier2_effort + tier3_effort

report_lines.extend(
    [
        "## Estimated Total Effort",
        "",
        f"- **Tier 1 (Critical):** {tier1_effort:.1f}-{tier1_effort + len(tier1_critical):.1f} hours",
        f"- **Tier 2 (Partial):** {tier2_effort:.1f}-{tier2_effort + len(tier2_partial):.1f} hours",
        f"- **Tier 3 (Warnings):** {tier3_effort:.1f}-{tier3_effort + len(tier3_warnings):.1f} hours",
        f"- **Total:** {total_effort:.1f}-{total_effort + len(tier1_critical) + len(tier2_partial) + len(tier3_warnings):.1f} hours of URL research and updates",
        "",
    ]
)

# Next Steps
report_lines.extend(
    [
        "## Next Steps",
        "",
        "### Immediate Actions",
        "1. Start with Tier 1 states - investigate broken URLs manually",
        "2. Research current state education websites for affected documents",
        "3. Use browser-based testing to bypass potential bot detection",
        "4. Document correct URLs found through manual research",
        "",
        "### Medium Priority",
        "1. Review Tier 2 states with partial issues",
        "2. Verify questionable documents with medium confidence scores",
        "3. Cross-reference with known good URLs from Tier 4 states",
        "",
        "### Data Model Enhancements",
        "1. Add `last_verified` timestamp field",
        "2. Add `url_source` documentation field",
        "3. Add `validation_status` field to track URL health",
        "",
        "### Future Improvements",
        "1. Implement periodic re-validation (every 3-6 months)",
        "2. Add automated health monitoring",
        "3. Consider document mirroring for critical states",
        "",
        "---",
        "",
        f"*Report generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*",
    ]
)

# Write report
output_path = Path("docs/URL_UPDATE_PRIORITIES.md")
output_path.parent.mkdir(parents=True, exist_ok=True)
output_path.write_text("\n".join(report_lines), encoding="utf-8")
print(f"Report generated: {output_path}")
