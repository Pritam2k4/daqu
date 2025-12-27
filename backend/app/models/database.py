from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class DataSource(BaseModel):
    id: Optional[str] = None
    user_id: str
    source_type: str  # 'file_upload' or 'database_connection'
    name: str
    
    # File upload fields
    file_path: Optional[str] = None
    file_size: Optional[int] = None
    file_type: Optional[str] = None
    
    # Database connection fields
    db_type: Optional[str] = None
    db_host: Optional[str] = None
    db_port: Optional[int] = None
    db_name: Optional[str] = None
    
    status: str = 'pending'
    metadata: dict = {}
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class QualityReport(BaseModel):
    id: Optional[str] = None
    source_id: str
    overall_score: Optional[float] = None
    completeness_score: Optional[float] = None
    consistency_score: Optional[float] = None
    accuracy_score: Optional[float] = None
    
    missing_values: dict = {}
    duplicates_count: int = 0
    outliers: list = []
    type_mismatches: dict = {}
    column_insights: dict = {}
    report_data: Optional[dict] = None
    created_at: Optional[datetime] = None


class ProcessingHistory(BaseModel):
    id: Optional[str] = None
    source_id: str
    user_id: str
    action_type: str
    transformations_applied: list = []
    suggestions_used: list = []
    before_stats: Optional[dict] = None
    after_stats: Optional[dict] = None
    status: str = 'in_progress'
    error_message: Optional[str] = None
    created_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
