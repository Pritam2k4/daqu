from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import List
import uuid
from app.services.data_analyzer import analyze_file
from app.api.v1.quality import store_report

router = APIRouter()


@router.post("/file")
async def upload_file(file: UploadFile = File(...)):
    """Upload a CSV, Excel, or JSON file for processing"""
    
    # Validate file type
    allowed_extensions = ['.csv', '.xlsx', '.xls', '.json']
    file_ext = '.' + file.filename.split('.')[-1].lower() if '.' in file.filename else ''
    
    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"File type {file_ext} not supported. Please upload CSV, Excel, or JSON."
        )
    
    # Read file content
    content = await file.read()
    
    # Generate source ID
    source_id = str(uuid.uuid4())
    
    # Analyze the file
    report = analyze_file(content, file.filename)
    
    if report.get("status") == "failed":
        raise HTTPException(
            status_code=400,
            detail=f"Failed to analyze file: {report.get('error')}"
        )
    
    # Store the report
    store_report(source_id, report)
    
    return {
        "status": "success",
        "message": "File uploaded and analyzed successfully",
        "source_id": source_id,
        "filename": file.filename,
        "summary": {
            "rows": report.get("basic_stats", {}).get("rows", 0),
            "columns": report.get("basic_stats", {}).get("columns", 0),
            "quality_score": report.get("quality_score", {}).get("overall_score", 0),
            "grade": report.get("quality_score", {}).get("grade", "N/A")
        }
    }


@router.post("/database")
async def connect_database(connection_details: dict):
    """Connect to a live database (PostgreSQL, MySQL, MongoDB)"""
    
    db_type = connection_details.get("type", "postgresql")
    host = connection_details.get("host", "localhost")
    port = connection_details.get("port", 5432)
    database = connection_details.get("database", "")
    
    # Generate source ID for tracking
    source_id = str(uuid.uuid4())
    
    return {
        "status": "success",
        "message": "Database connection endpoint ready",
        "source_id": source_id,
        "connection": {
            "type": db_type,
            "host": host,
            "port": port,
            "database": database
        },
        "note": "Full database connection implementation coming soon"
    }
