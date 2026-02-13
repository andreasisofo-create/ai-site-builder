"""
Quality Control Report Models.
Data classes for QC pipeline results, issues, and fix tracking.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone


@dataclass
class QCIssue:
    """Single quality issue found during validation."""
    type: str          # 'animation', 'color', 'text', 'accessibility', 'layout', 'section', 'structure'
    severity: str      # 'critical', 'warning', 'info'
    element: str       # CSS selector or description of the affected element
    description: str   # Human-readable description
    auto_fixable: bool # Whether this can be auto-fixed

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": self.type,
            "severity": self.severity,
            "element": self.element,
            "description": self.description,
            "auto_fixable": self.auto_fixable,
        }


@dataclass
class QCFixResult:
    """Result of a single fix operation."""
    issue_type: str
    issues_fixed: int
    description: str
    success: bool

    def to_dict(self) -> Dict[str, Any]:
        return {
            "issue_type": self.issue_type,
            "issues_fixed": self.issues_fixed,
            "description": self.description,
            "success": self.success,
        }


@dataclass
class QCReport:
    """Complete QC pipeline report for a generated site."""
    site_id: str
    overall_score: float                        # 1-10 from AI critique
    automated_issues: List[QCIssue] = field(default_factory=list)
    ai_critique: Dict[str, Any] = field(default_factory=dict)
    fixes_applied: List[QCFixResult] = field(default_factory=list)
    final_score: float = 0.0
    passed: bool = False                        # True if final_score >= 7
    iterations: int = 0
    html_before: str = ""
    html_after: str = ""
    needs_manual_review: bool = False
    timestamp: str = ""

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now(timezone.utc).isoformat()

    @property
    def critical_count(self) -> int:
        return sum(1 for i in self.automated_issues if i.severity == "critical")

    @property
    def warning_count(self) -> int:
        return sum(1 for i in self.automated_issues if i.severity == "warning")

    @property
    def fixable_count(self) -> int:
        return sum(1 for i in self.automated_issues if i.auto_fixable)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "site_id": self.site_id,
            "overall_score": self.overall_score,
            "final_score": self.final_score,
            "passed": self.passed,
            "iterations": self.iterations,
            "needs_manual_review": self.needs_manual_review,
            "timestamp": self.timestamp,
            "automated_issues": [i.to_dict() for i in self.automated_issues],
            "ai_critique": self.ai_critique,
            "fixes_applied": [f.to_dict() for f in self.fixes_applied],
            "issue_summary": {
                "total": len(self.automated_issues),
                "critical": self.critical_count,
                "warning": self.warning_count,
                "auto_fixable": self.fixable_count,
            },
        }
