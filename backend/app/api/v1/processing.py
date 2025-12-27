from fastapi import APIRouter, HTTPException, Response
from typing import Optional
from app.services.ai_suggestions import generate_suggestions_for_report
from app.services.data_export import generate_quality_report_export
from app.api.v1.quality import _temp_storage

router = APIRouter()


@router.post("/apply-fixes")
async def apply_data_fixes(source_id: str, fixes: list = []):
    """Apply approved fixes to the data"""
    
    if source_id not in _temp_storage and source_id != "demo":
        return {
            "status": "error",
            "message": f"No data found for source_id: {source_id}"
        }
    
    return {
        "status": "success",
        "message": f"Ready to apply {len(fixes)} fixes",
        "source_id": source_id,
        "fixes_to_apply": fixes,
        "note": "Full implementation coming soon"
    }


@router.get("/history/{source_id}")
async def get_processing_history(source_id: str):
    """Get processing history for a data source"""
    
    # Demo history
    history = [
        {
            "id": "1",
            "timestamp": "2024-01-15T10:30:00Z",
            "action": "File uploaded",
            "details": "sample_data.csv uploaded and analyzed"
        },
        {
            "id": "2", 
            "timestamp": "2024-01-15T10:31:00Z",
            "action": "Quality analysis",
            "details": "Generated quality report with score 78.5%"
        }
    ]
    
    return {
        "status": "success",
        "source_id": source_id,
        "history": history
    }


@router.get("/suggestions/{source_id}")
async def get_ai_suggestions(source_id: str):
    """Get AI-generated fix suggestions for a data source"""
    
    # Get the report
    if source_id == "demo":
        # Use demo report
        from app.api.v1.quality import get_demo_report
        response = await get_demo_report()
        report = response["report"]
    elif source_id in _temp_storage:
        report = _temp_storage[source_id]
    else:
        return {
            "status": "error",
            "message": f"No data found for source_id: {source_id}"
        }
    
    # Generate suggestions
    suggestions = generate_suggestions_for_report(report)
    
    return {
        "status": "success",
        "source_id": source_id,
        "suggestions_count": len(suggestions),
        "suggestions": suggestions
    }


@router.get("/export/{source_id}")
async def export_quality_report(
    source_id: str,
    format: str = "json"
):
    """Export quality report"""
    
    # Get the report
    if source_id == "demo":
        from app.api.v1.quality import get_demo_report
        response = await get_demo_report()
        report = response["report"]
    elif source_id in _temp_storage:
        report = _temp_storage[source_id]
    else:
        raise HTTPException(status_code=404, detail="Report not found")
    
    # Generate export
    export_result = generate_quality_report_export(report)
    
    if not export_result["success"]:
        raise HTTPException(status_code=400, detail=export_result.get("error"))
    
    # Return as downloadable file
    filename = f"quality_report_{source_id}.json"
    
    return Response(
        content=export_result["content"],
        media_type=export_result["content_type"],
        headers={
            "Content-Disposition": f"attachment; filename={filename}"
        }
    )
