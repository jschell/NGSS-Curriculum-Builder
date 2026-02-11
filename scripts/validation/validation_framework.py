#!/usr/bin/env python3
"""
Validation Framework for NGSS Curriculum Builder
Reusable base classes and runner for all validators.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional


# =============================================================================
# SEVERITY
# =============================================================================

class Severity(str, Enum):
    ERROR = "ERROR"
    WARNING = "WARNING"
    INFO = "INFO"

    def __lt__(self, other):
        order = {Severity.ERROR: 0, Severity.WARNING: 1, Severity.INFO: 2}
        return order[self] < order[other]


# =============================================================================
# ISSUE
# =============================================================================

@dataclass
class Issue:
    severity: Severity
    code: str
    state: str
    message: str
    field: Optional[str] = None
    suggestion: Optional[str] = None

    def __str__(self):
        parts = [f"[{self.severity.value}][{self.code}]", f"{self.state}:"]
        if self.field:
            parts.append(f"({self.field})")
        parts.append(self.message)
        if self.suggestion:
            parts.append(f"-> {self.suggestion}")
        return " ".join(parts)


# =============================================================================
# BASE VALIDATOR
# =============================================================================

class Validator:
    """Base class for all validators."""

    name: str = "BaseValidator"

    def validate(self, data: Dict[str, Any]) -> List[Issue]:
        raise NotImplementedError

    def report(self, issues: List[Issue]) -> str:
        if not issues:
            return f"{self.name}: No issues found\n"
        lines = [f"{self.name}: {len(issues)} issue(s)"]
        for issue in sorted(issues, key=lambda i: (0 if i.severity==Severity.ERROR else 1 if i.severity==Severity.WARNING else 2, i.state)):
            lines.append(f"  {issue}")
        return "\n".join(lines) + "\n"


# =============================================================================
# VALIDATION RUNNER
# =============================================================================

@dataclass
class ValidationRunner:
    validators: List[Validator] = field(default_factory=list)

    def add_validator(self, validator: Validator) -> "ValidationRunner":
        self.validators.append(validator)
        return self

    def run(self, data: Dict[str, Any], states: Optional[List[str]] = None,
            min_severity: Severity = Severity.INFO) -> List[Issue]:
        all_issues: List[Issue] = []

        if states:
            states_upper = [s.upper() for s in states]
            scoped_data = {k: v for k, v in data.items() if k in states_upper}
        else:
            scoped_data = data

        for validator in self.validators:
            try:
                found = validator.validate(scoped_data)
                all_issues.extend(found)
            except Exception as exc:
                all_issues.append(Issue(
                    severity=Severity.ERROR,
                    code="VRUN001",
                    state="GLOBAL",
                    message=f"Validator '{validator.name}' crashed: {exc}",
                ))

        severity_order = {Severity.ERROR: 0, Severity.WARNING: 1, Severity.INFO: 2}
        max_level = severity_order[min_severity]
        return [i for i in all_issues if severity_order[i.severity] <= max_level]

    def report(self, issues: List[Issue]) -> str:
        errors = [i for i in issues if i.severity == Severity.ERROR]
        warnings = [i for i in issues if i.severity == Severity.WARNING]
        infos = [i for i in issues if i.severity == Severity.INFO]

        lines = [
            "=" * 72,
            "NGSS Curriculum Builder - Validation Report",
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "=" * 72,
            "",
            "SUMMARY",
            "-" * 40,
            f"Total Issues: {len(issues)} ({len(errors)} errors, {len(warnings)} warnings, {len(infos)} info)",
            "",
        ]

        if errors:
            lines += [f"ERRORS ({len(errors)})", "-" * 40]
            for i in errors:
                lines.append(f"  {i}")
            lines.append("")

        if warnings:
            lines += [f"WARNINGS ({len(warnings)})", "-" * 40]
            for i in warnings:
                lines.append(f"  {i}")
            lines.append("")

        if infos:
            lines += [f"INFO ({len(infos)})", "-" * 40]
            for i in infos:
                lines.append(f"  {i}")
            lines.append("")

        return "\n".join(lines)


# =============================================================================
# HELPERS
# =============================================================================

def load_states(path: str = "data/states.json") -> Dict[str, Any]:
    """Load states.json, searching from this file upward."""
    here = Path(__file__).resolve()
    for parent in [here.parent, here.parent.parent, here.parent.parent.parent]:
        candidate = parent / path
        if candidate.exists():
            with open(candidate, encoding="utf-8") as f:
                return json.load(f)
    raise FileNotFoundError(f"Could not find {path} from {here}")
