"""Export API routes for assessment data."""

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import Response

from ...storage.assessment_store import AssessmentStore

router = APIRouter()


@router.get("/export/assessments/{assessment_id}")
async def export_assessment(
    assessment_id: str,
    format: str = Query("json", regex="^(json|csv|pdf)$"),
):
    """Export assessment data in various formats.

    Args:
        assessment_id: Assessment UUID
        format: Export format (json, csv, pdf)

    Returns:
        Exported data in requested format
    """
    store = AssessmentStore()

    assessment_data = store.get(assessment_id)

    if not assessment_data:
        raise HTTPException(status_code=404, detail="Assessment not found")

    if format == "json":
        import json

        return Response(
            content=json.dumps(assessment_data, indent=2, default=str),
            media_type="application/json",
            headers={"Content-Disposition": f"attachment; filename=assessment-{assessment_id}.json"},
        )

    elif format == "csv":
        # Simple CSV export
        csv_lines = [
            "Assessment ID,Repository,Overall Score,Status,Started At,Completed At",
            f"{assessment_data['id']},{assessment_data['repo_url']},{assessment_data['overall_score']},{assessment_data['status']},{assessment_data['started_at']},{assessment_data.get('completed_at', 'N/A')}",
        ]

        return Response(
            content="\n".join(csv_lines),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename=assessment-{assessment_id}.csv"},
        )

    elif format == "pdf":
        # PDF export would require reportlab or similar
        raise HTTPException(status_code=501, detail="PDF export not yet implemented")

    return assessment_data
