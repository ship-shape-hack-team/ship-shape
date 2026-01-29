"""Trend analyzer for historical quality tracking."""

from datetime import datetime, timedelta
from typing import Dict, List, Optional

from ..models.assessment import Assessment


class TrendAnalyzer:
    """Analyze quality trends over time."""

    def calculate_trend(
        self,
        assessments: List[Assessment],
        days: int = 90,
    ) -> Dict[str, any]:
        """Calculate quality trend over a time period.

        Args:
            assessments: List of assessments (sorted by date)
            days: Number of days to analyze

        Returns:
            Dictionary with trend information
        """
        if not assessments:
            return {
                "trend": "no_data",
                "change": 0,
                "assessments_analyzed": 0,
            }

        # Filter assessments within time period
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        recent_assessments = [
            a for a in assessments
            if a.started_at >= cutoff_date
        ]

        if len(recent_assessments) < 2:
            return {
                "trend": "insufficient_data",
                "change": 0,
                "assessments_analyzed": len(recent_assessments),
            }

        # Calculate trend
        oldest = recent_assessments[0]
        newest = recent_assessments[-1]
        
        change = newest.overall_score - oldest.overall_score
        
        if change > 5:
            trend = "improving"
        elif change < -5:
            trend = "declining"
        else:
            trend = "stable"

        return {
            "trend": trend,
            "change": change,
            "oldest_score": oldest.overall_score,
            "newest_score": newest.overall_score,
            "assessments_analyzed": len(recent_assessments),
            "period_days": days,
        }

    def get_assessment_history(
        self,
        assessments: List[Assessment],
        limit: Optional[int] = None,
    ) -> List[Dict[str, any]]:
        """Get assessment history formatted for trend charts.

        Args:
            assessments: List of assessments
            limit: Optional limit on number of assessments

        Returns:
            List of dictionaries with timestamp and score
        """
        sorted_assessments = sorted(assessments, key=lambda a: a.started_at)
        
        if limit:
            sorted_assessments = sorted_assessments[-limit:]

        return [
            {
                "timestamp": a.started_at.isoformat(),
                "score": a.overall_score,
                "status": a.status,
            }
            for a in sorted_assessments
        ]

    def compare_periods(
        self,
        assessments: List[Assessment],
        period1_days: int = 30,
        period2_days: int = 60,
    ) -> Dict[str, any]:
        """Compare two time periods.

        Args:
            assessments: List of assessments
            period1_days: Recent period (e.g., last 30 days)
            period2_days: Older period (e.g., 30-60 days ago)

        Returns:
            Comparison dictionary
        """
        now = datetime.utcnow()
        
        # Recent period
        recent_cutoff = now - timedelta(days=period1_days)
        recent = [a for a in assessments if a.started_at >= recent_cutoff]
        
        # Older period
        older_cutoff = now - timedelta(days=period2_days)
        older = [
            a for a in assessments
            if older_cutoff <= a.started_at < recent_cutoff
        ]

        recent_avg = sum(a.overall_score for a in recent) / len(recent) if recent else 0
        older_avg = sum(a.overall_score for a in older) / len(older) if older else 0

        return {
            "recent_period_days": period1_days,
            "recent_average": recent_avg,
            "recent_count": len(recent),
            "older_period_days": f"{period1_days}-{period2_days}",
            "older_average": older_avg,
            "older_count": len(older),
            "change": recent_avg - older_avg,
            "trend": "improving" if recent_avg > older_avg else "declining" if recent_avg < older_avg else "stable",
        }
