"""
Platform Context Service
Aggregates all platform data for the AI assistant
"""
from typing import Dict, Any, List, Optional
from datetime import datetime
import json

# Import storage
from app.api.v1.quality import _temp_storage
from app.api.v1.models import _model_storage


class PlatformContext:
    """
    Gathers all platform data into a unified context
    for the AI assistant to access.
    """
    
    def __init__(self):
        self.session_data = {
            "uploads": [],
            "quality_reports": {},
            "training_history": [],
            "current_source_id": None
        }
    
    def get_full_context(self) -> Dict[str, Any]:
        """Get complete platform context"""
        return {
            "uploads": self._get_uploads_summary(),
            "quality_reports": self._get_quality_summary(),
            "training_history": self._get_training_summary(),
            "platform_stats": self._get_platform_stats(),
            "timestamp": datetime.now().isoformat()
        }
    
    def _get_uploads_summary(self) -> List[Dict]:
        """Get summary of all uploaded files"""
        uploads = []
        
        for source_id, data in _temp_storage.items():
            if source_id == "demo":
                continue
            
            uploads.append({
                "source_id": source_id,
                "filename": data.get("overview", {}).get("filename", "Unknown"),
                "rows": data.get("overview", {}).get("rows", 0),
                "columns": data.get("overview", {}).get("columns", 0),
                "quality_score": data.get("quality_score", {}).get("overall_score"),
                "grade": data.get("quality_score", {}).get("grade")
            })
        
        return uploads
    
    def _get_quality_summary(self) -> Dict[str, Any]:
        """Get summary of quality reports"""
        if not _temp_storage:
            return {"status": "No quality reports yet"}
        
        # Get latest report
        reports = list(_temp_storage.values())
        if not reports:
            return {"status": "No quality reports yet"}
        
        # Find report with quality score
        for report in reports:
            if "quality_score" in report:
                qs = report.get("quality_score", {})
                return {
                    "latest_score": qs.get("overall_score"),
                    "grade": qs.get("grade"),
                    "grade_description": qs.get("grade_description"),
                    "completeness": report.get("completeness", {}).get("score"),
                    "uniqueness": report.get("uniqueness", {}).get("score"),
                    "validity": report.get("validity", {}).get("score"),
                    "ml_readiness": report.get("ml_readiness", {}).get("score"),
                    "total_reports": len(_temp_storage)
                }
        
        return {"status": "No quality scores calculated"}
    
    def _get_training_summary(self) -> List[Dict]:
        """Get summary of ML training history"""
        history = []
        
        for training_id, data in _model_storage.items():
            results = data.get("results", {})
            history.append({
                "training_id": training_id,
                "model_name": results.get("model_name"),
                "task_type": results.get("task_type"),
                "accuracy": results.get("metrics", {}).get("accuracy"),
                "r2_score": results.get("metrics", {}).get("r2_score"),
                "training_time": results.get("training_time_seconds"),
                "timestamp": results.get("timestamp")
            })
        
        return history
    
    def _get_platform_stats(self) -> Dict[str, Any]:
        """Get overall platform statistics"""
        uploads = self._get_uploads_summary()
        training = self._get_training_summary()
        
        return {
            "total_uploads": len(uploads),
            "total_models_trained": len(training),
            "has_active_data": len(uploads) > 0 or "demo" in _temp_storage,
            "demo_available": True
        }
    
    def get_context_for_llm(self) -> str:
        """Get formatted context string for LLM"""
        ctx = self.get_full_context()
        
        context_parts = ["\n=== PLATFORM CONTEXT ==="]
        
        # Stats
        stats = ctx["platform_stats"]
        context_parts.append(f"""
Platform Stats:
- Files uploaded: {stats['total_uploads']}
- Models trained: {stats['total_models_trained']}
- Demo data: Available""")

        # Uploads
        if ctx["uploads"]:
            context_parts.append("\nUploaded Files:")
            for u in ctx["uploads"][:5]:
                context_parts.append(f"- {u['filename']}: {u['rows']} rows, {u['columns']} cols, Score: {u.get('quality_score', 'N/A')}")
        
        # Quality
        qr = ctx["quality_reports"]
        if qr.get("latest_score"):
            context_parts.append(f"""
Latest Quality Report:
- Overall Score: {qr['latest_score']}% (Grade {qr['grade']})
- Completeness: {qr.get('completeness', 'N/A')}%
- Uniqueness: {qr.get('uniqueness', 'N/A')}%
- ML Readiness: {qr.get('ml_readiness', 'N/A')}%""")
        
        # Training
        if ctx["training_history"]:
            context_parts.append("\nRecent Training:")
            for t in ctx["training_history"][:3]:
                metric = t.get('accuracy') or t.get('r2_score') or 'N/A'
                context_parts.append(f"- {t['model_name']}: {metric}")
        
        return "\n".join(context_parts)
    
    def answer_platform_question(self, question: str) -> Optional[str]:
        """Try to answer platform-specific questions directly"""
        q = question.lower()
        ctx = self.get_full_context()
        
        # File/upload questions
        if any(kw in q for kw in ["how many file", "upload", "files uploaded"]):
            count = ctx["platform_stats"]["total_uploads"]
            if count == 0:
                return "You haven't uploaded any files yet. Try uploading a CSV, Excel, or JSON file!"
            uploads = ctx["uploads"]
            files = ", ".join([f"**{u['filename']}** ({u['rows']} rows)" for u in uploads[:3]])
            return f"You've uploaded **{count}** file(s): {files}"
        
        # Quality score questions
        if any(kw in q for kw in ["quality score", "data quality", "my score", "grade"]):
            qr = ctx["quality_reports"]
            if qr.get("latest_score"):
                return f"Your data quality score is **{qr['latest_score']}%** (Grade **{qr['grade']}**). Completeness: {qr.get('completeness')}%, ML Readiness: {qr.get('ml_readiness')}%."
            return "No quality report yet. Upload a file or try the demo data!"
        
        # Training questions
        if any(kw in q for kw in ["model trained", "training", "trained models", "best model"]):
            history = ctx["training_history"]
            if not history:
                return "No models trained yet. Would you like me to train one?"
            
            best = max(history, key=lambda x: x.get('accuracy') or x.get('r2_score') or 0)
            metric = best.get('accuracy') or best.get('r2_score')
            return f"You've trained **{len(history)}** model(s). Best: **{best['model_name']}** with {metric:.1%} accuracy."
        
        return None  # Let LLM handle it


# Global instance
platform_context = PlatformContext()


def get_platform_context() -> Dict[str, Any]:
    """Get full platform context"""
    return platform_context.get_full_context()


def get_llm_context() -> str:
    """Get formatted context for LLM"""
    return platform_context.get_context_for_llm()


def try_direct_answer(question: str) -> Optional[str]:
    """Try to answer platform questions directly"""
    return platform_context.answer_platform_question(question)
