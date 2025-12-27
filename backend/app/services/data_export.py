"""
Data Export Service
Exports processed data in various formats
"""
import pandas as pd
import json
from io import BytesIO, StringIO
from typing import Dict, Any, Optional


class DataExporter:
    """Handles data export in multiple formats"""
    
    SUPPORTED_FORMATS = ["csv", "json", "excel", "parquet"]
    
    def __init__(self, df: pd.DataFrame):
        self.df = df
    
    def export(self, format: str, filename: Optional[str] = None) -> Dict[str, Any]:
        """Export data to specified format"""
        format = format.lower()
        
        if format not in self.SUPPORTED_FORMATS:
            return {
                "success": False,
                "error": f"Unsupported format: {format}. Supported: {', '.join(self.SUPPORTED_FORMATS)}"
            }
        
        try:
            if format == "csv":
                return self._export_csv()
            elif format == "json":
                return self._export_json()
            elif format == "excel":
                return self._export_excel()
            elif format == "parquet":
                return self._export_parquet()
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def _export_csv(self) -> Dict[str, Any]:
        """Export to CSV"""
        buffer = StringIO()
        self.df.to_csv(buffer, index=False)
        
        return {
            "success": True,
            "format": "csv",
            "content": buffer.getvalue(),
            "content_type": "text/csv",
            "extension": ".csv"
        }
    
    def _export_json(self) -> Dict[str, Any]:
        """Export to JSON"""
        content = self.df.to_json(orient="records", indent=2)
        
        return {
            "success": True,
            "format": "json",
            "content": content,
            "content_type": "application/json",
            "extension": ".json"
        }
    
    def _export_excel(self) -> Dict[str, Any]:
        """Export to Excel"""
        buffer = BytesIO()
        self.df.to_excel(buffer, index=False, engine='openpyxl')
        buffer.seek(0)
        
        return {
            "success": True,
            "format": "excel",
            "content": buffer.getvalue(),
            "content_type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            "extension": ".xlsx",
            "is_binary": True
        }
    
    def _export_parquet(self) -> Dict[str, Any]:
        """Export to Parquet"""
        buffer = BytesIO()
        self.df.to_parquet(buffer, index=False)
        buffer.seek(0)
        
        return {
            "success": True,
            "format": "parquet",
            "content": buffer.getvalue(),
            "content_type": "application/octet-stream",
            "extension": ".parquet",
            "is_binary": True
        }
    
    def get_export_preview(self, format: str, n_rows: int = 5) -> Dict[str, Any]:
        """Get preview of export"""
        sample_df = self.df.head(n_rows)
        exporter = DataExporter(sample_df)
        result = exporter.export(format)
        
        if result["success"]:
            result["preview"] = True
            result["rows_in_preview"] = n_rows
            result["total_rows"] = len(self.df)
        
        return result


def generate_quality_report_export(report: Dict[str, Any]) -> Dict[str, Any]:
    """Generate exportable quality report"""
    export_data = {
        "report_summary": {
            "filename": report.get("filename", "unknown"),
            "rows": report.get("basic_stats", {}).get("rows", 0),
            "columns": report.get("basic_stats", {}).get("columns", 0),
            "quality_score": report.get("quality_score", {}).get("overall_score", 0),
            "grade": report.get("quality_score", {}).get("grade", "N/A")
        },
        "quality_metrics": report.get("quality_score", {}),
        "missing_values": report.get("missing_values", {}),
        "duplicates": report.get("duplicates", {}),
        "outliers": report.get("outliers", {}),
        "type_issues": report.get("type_issues", {}),
        "column_analysis": report.get("column_analysis", [])
    }
    
    return {
        "success": True,
        "format": "json",
        "content": json.dumps(export_data, indent=2),
        "content_type": "application/json"
    }
