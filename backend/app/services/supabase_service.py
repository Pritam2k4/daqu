"""
Supabase Service
Handles our app's database operations (users, reports, history)
"""
from typing import Dict, Any, Optional, List
from datetime import datetime
import json


class SupabaseService:
    """
    Service for interacting with our Supabase database.
    Stores user data, quality reports, and processing history.
    """
    
    def __init__(self):
        self.client = None
        self._initialize()
    
    def _initialize(self):
        """Initialize Supabase client"""
        try:
            from supabase import create_client
            from app.config import settings
            
            if settings.SUPABASE_URL and settings.SUPABASE_KEY:
                self.client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
        except Exception as e:
            print(f"Supabase initialization failed: {e}")
            self.client = None
    
    def is_connected(self) -> bool:
        """Check if Supabase is connected"""
        return self.client is not None
    
    # ==========================================
    # DATA SOURCES
    # ==========================================
    
    async def save_data_source(self, user_id: str, source_data: Dict[str, Any]) -> Dict[str, Any]:
        """Save a new data source (file upload or database connection)"""
        if not self.client:
            return {"error": "Supabase not configured"}
        
        try:
            data = {
                "user_id": user_id,
                "name": source_data.get("name", "Unnamed"),
                "source_type": source_data.get("source_type", "file"),  # file or database
                "file_type": source_data.get("file_type"),
                "file_size": source_data.get("file_size"),
                "row_count": source_data.get("row_count"),
                "column_count": source_data.get("column_count"),
                "connection_config": json.dumps(source_data.get("connection_config", {})),
                "created_at": datetime.utcnow().isoformat()
            }
            
            result = self.client.table("data_sources").insert(data).execute()
            return {"success": True, "data": result.data[0] if result.data else None}
        except Exception as e:
            return {"error": str(e)}
    
    async def get_user_data_sources(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all data sources for a user"""
        if not self.client:
            return []
        
        try:
            result = self.client.table("data_sources")\
                .select("*")\
                .eq("user_id", user_id)\
                .order("created_at", desc=True)\
                .execute()
            return result.data
        except Exception as e:
            print(f"Error fetching data sources: {e}")
            return []
    
    # ==========================================
    # QUALITY REPORTS
    # ==========================================
    
    async def save_quality_report(self, source_id: str, report: Dict[str, Any]) -> Dict[str, Any]:
        """Save a quality report"""
        if not self.client:
            return {"error": "Supabase not configured"}
        
        try:
            data = {
                "source_id": source_id,
                "overall_score": report.get("quality_score", {}).get("overall_score"),
                "grade": report.get("quality_score", {}).get("grade"),
                "completeness_score": report.get("completeness", {}).get("score"),
                "uniqueness_score": report.get("uniqueness", {}).get("score"),
                "validity_score": report.get("validity", {}).get("score"),
                "consistency_score": report.get("consistency", {}).get("score"),
                "accuracy_score": report.get("accuracy", {}).get("score"),
                "timeliness_score": report.get("timeliness", {}).get("score"),
                "ml_readiness_score": report.get("ml_readiness", {}).get("score"),
                "full_report": json.dumps(report),
                "created_at": datetime.utcnow().isoformat()
            }
            
            result = self.client.table("quality_reports").insert(data).execute()
            return {"success": True, "data": result.data[0] if result.data else None}
        except Exception as e:
            return {"error": str(e)}
    
    async def get_quality_reports(self, source_id: str) -> List[Dict[str, Any]]:
        """Get all quality reports for a data source"""
        if not self.client:
            return []
        
        try:
            result = self.client.table("quality_reports")\
                .select("*")\
                .eq("source_id", source_id)\
                .order("created_at", desc=True)\
                .execute()
            return result.data
        except Exception as e:
            print(f"Error fetching reports: {e}")
            return []
    
    async def get_latest_report(self, source_id: str) -> Optional[Dict[str, Any]]:
        """Get the latest quality report for a data source"""
        reports = await self.get_quality_reports(source_id)
        return reports[0] if reports else None
    
    # ==========================================
    # PROCESSING HISTORY
    # ==========================================
    
    async def save_processing_action(self, source_id: str, action: Dict[str, Any]) -> Dict[str, Any]:
        """Save a processing action"""
        if not self.client:
            return {"error": "Supabase not configured"}
        
        try:
            data = {
                "source_id": source_id,
                "action_type": action.get("action_type"),
                "description": action.get("description"),
                "affected_rows": action.get("affected_rows"),
                "affected_columns": action.get("affected_columns"),
                "before_snapshot": json.dumps(action.get("before_snapshot", {})),
                "after_snapshot": json.dumps(action.get("after_snapshot", {})),
                "created_at": datetime.utcnow().isoformat()
            }
            
            result = self.client.table("processing_history").insert(data).execute()
            return {"success": True, "data": result.data[0] if result.data else None}
        except Exception as e:
            return {"error": str(e)}
    
    async def get_processing_history(self, source_id: str) -> List[Dict[str, Any]]:
        """Get processing history for a data source"""
        if not self.client:
            return []
        
        try:
            result = self.client.table("processing_history")\
                .select("*")\
                .eq("source_id", source_id)\
                .order("created_at", desc=True)\
                .execute()
            return result.data
        except Exception as e:
            print(f"Error fetching history: {e}")
            return []
    
    # ==========================================
    # AI SUGGESTIONS
    # ==========================================
    
    async def save_ai_suggestions(self, report_id: str, suggestions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Save AI-generated suggestions"""
        if not self.client:
            return {"error": "Supabase not configured"}
        
        try:
            data = [{
                "report_id": report_id,
                "suggestion_type": s.get("issue_type"),
                "column_name": s.get("column"),
                "severity": s.get("severity"),
                "description": s.get("description"),
                "suggested_fix": s.get("suggested_fix"),
                "code_snippet": s.get("code_snippet"),
                "confidence": s.get("confidence"),
                "status": "pending",  # pending, applied, rejected
                "created_at": datetime.utcnow().isoformat()
            } for s in suggestions]
            
            result = self.client.table("ai_suggestions").insert(data).execute()
            return {"success": True, "count": len(result.data)}
        except Exception as e:
            return {"error": str(e)}
    
    async def update_suggestion_status(self, suggestion_id: str, status: str) -> Dict[str, Any]:
        """Update suggestion status (applied/rejected)"""
        if not self.client:
            return {"error": "Supabase not configured"}
        
        try:
            result = self.client.table("ai_suggestions")\
                .update({"status": status})\
                .eq("id", suggestion_id)\
                .execute()
            return {"success": True}
        except Exception as e:
            return {"error": str(e)}
    
    # ==========================================
    # USER STATS
    # ==========================================
    
    async def get_user_stats(self, user_id: str) -> Dict[str, Any]:
        """Get usage statistics for a user"""
        if not self.client:
            return {
                "total_sources": 0,
                "total_reports": 0,
                "avg_quality_score": 0,
                "total_fixes_applied": 0
            }
        
        try:
            # Get data sources count
            sources = await self.get_user_data_sources(user_id)
            
            # Calculate average quality score from all reports
            total_score = 0
            report_count = 0
            for source in sources:
                reports = await self.get_quality_reports(source.get("id"))
                for report in reports:
                    if report.get("overall_score"):
                        total_score += report["overall_score"]
                        report_count += 1
            
            return {
                "total_sources": len(sources),
                "total_reports": report_count,
                "avg_quality_score": round(total_score / report_count, 1) if report_count > 0 else 0,
                "total_fixes_applied": 0  # Would need to count from processing_history
            }
        except Exception as e:
            print(f"Error getting stats: {e}")
            return {
                "total_sources": 0,
                "total_reports": 0,
                "avg_quality_score": 0,
                "total_fixes_applied": 0
            }


# Global instance
supabase_service = SupabaseService()
