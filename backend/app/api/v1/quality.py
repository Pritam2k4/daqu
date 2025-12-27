from fastapi import APIRouter, HTTPException
from typing import Optional
from app.services.ml_templates import MLTemplateAnalyzer, get_available_templates

router = APIRouter()

# Store for reports - in production this would be from database
_temp_storage = {}


@router.post("/analyze")
async def analyze_data_quality(source_id: str):
    """Analyze data quality and generate a report"""
    
    if source_id not in _temp_storage:
        return {
            "status": "error",
            "message": f"No data found for source_id: {source_id}. Please upload a file first."
        }
    
    report = _temp_storage[source_id]
    return {
        "status": "success",
        "source_id": source_id,
        "report": report
    }


@router.get("/report/{source_id}")
async def get_quality_report(source_id: str):
    """Get quality report for a data source"""
    
    if source_id not in _temp_storage:
        return {
            "status": "error", 
            "message": f"No report found for source_id: {source_id}"
        }
    
    return {
        "status": "success",
        "source_id": source_id,
        "report": _temp_storage[source_id]
    }


@router.get("/templates")
async def get_ml_templates():
    """Get available ML dataset templates"""
    return {
        "status": "success",
        "templates": get_available_templates()
    }


@router.get("/demo-report")
async def get_demo_report():
    """
    Get a demo quality report using REAL industry-standard metrics.
    Based on DAMA Data Quality Framework and ISO 25024 standards.
    """
    
    demo_report = {
        "filename": "customer_churn_dataset.csv",
        "generated_at": "2024-12-27T13:30:00",
        "status": "success",
        
        # Dataset Overview
        "overview": {
            "filename": "customer_churn_dataset.csv",
            "rows": 10000,
            "columns": 14,
            "memory_usage_mb": 1.45,
            "column_types": {
                "numeric": 6,
                "categorical": 7,
                "datetime": 1,
                "boolean": 0
            },
            "column_names": [
                "customer_id", "name", "email", "phone", "age", "gender",
                "tenure_months", "monthly_charges", "total_charges", 
                "contract_type", "payment_method", "churn_date", "support_tickets", "churn"
            ]
        },
        
        # Overall Quality Score (Industry Standard Weighted)
        "quality_score": {
            "overall_score": 76.8,
            "grade": "C",
            "grade_description": "Fair - Several Issues to Address",
            "dimension_scores": {
                "completeness": 87.5,
                "uniqueness": 96.8,
                "validity": 82.0,
                "consistency": 71.0,
                "accuracy": 68.5,
                "timeliness": 85.0
            },
            "weights": {
                "completeness": 0.25,
                "uniqueness": 0.15,
                "validity": 0.15,
                "consistency": 0.15,
                "accuracy": 0.20,
                "timeliness": 0.10
            },
            "ml_readiness_score": 72,
            "ml_readiness_status": "needs_improvement"
        },
        
        # COMPLETENESS (DAMA Dimension 1)
        "completeness": {
            "dimension": "Completeness",
            "description": "Measures extent to which required data is present",
            "score": 87.5,
            "total_cells": 140000,
            "non_null_cells": 122500,
            "null_cells": 17500,
            "columns_below_threshold": 3,
            "column_details": [
                {"column": "phone", "non_null_count": 8500, "null_count": 1500, "completeness_ratio": 85.0, "status": "warning"},
                {"column": "churn_date", "non_null_count": 2700, "null_count": 7300, "completeness_ratio": 27.0, "status": "fail"},
                {"column": "total_charges", "non_null_count": 9720, "null_count": 280, "completeness_ratio": 97.2, "status": "pass"},
                {"column": "age", "non_null_count": 9650, "null_count": 350, "completeness_ratio": 96.5, "status": "pass"},
                {"column": "customer_id", "non_null_count": 10000, "null_count": 0, "completeness_ratio": 100.0, "status": "pass"}
            ],
            "threshold": 95,
            "status": "warning"
        },
        
        # UNIQUENESS (DAMA Dimension 2)
        "uniqueness": {
            "dimension": "Uniqueness",
            "description": "Measures absence of duplicate records",
            "score": 96.8,
            "total_rows": 10000,
            "unique_rows": 9680,
            "duplicate_rows": 320,
            "duplicate_percentage": 3.2,
            "column_cardinality": [
                {"column": "customer_id", "unique_values": 10000, "cardinality_ratio": 100.0, "is_potential_key": True},
                {"column": "email", "unique_values": 9950, "cardinality_ratio": 99.5, "is_potential_key": False},
                {"column": "name", "unique_values": 8876, "cardinality_ratio": 88.76, "is_potential_key": False},
                {"column": "contract_type", "unique_values": 3, "cardinality_ratio": 0.03, "is_potential_key": False},
                {"column": "churn", "unique_values": 2, "cardinality_ratio": 0.02, "is_potential_key": False}
            ],
            "potential_key_columns": ["customer_id"],
            "threshold": 95,
            "status": "pass"
        },
        
        # VALIDITY (DAMA Dimension 3)
        "validity": {
            "dimension": "Validity",
            "description": "Measures conformance to defined formats and business rules",
            "score": 82.0,
            "total_checks": 25,
            "passed_checks": 20,
            "failed_checks": 5,
            "issues": [
                {"column": "email", "dtype": "object", "issues": ["156 invalid email formats"], "severity": "medium"},
                {"column": "phone", "dtype": "object", "issues": ["423 potentially invalid phone numbers"], "severity": "medium"},
                {"column": "age", "dtype": "float64", "issues": ["12 unexpected negative values"], "severity": "high"}
            ],
            "threshold": 90,
            "status": "warning"
        },
        
        # CONSISTENCY (DAMA Dimension 4)
        "consistency": {
            "dimension": "Consistency",
            "description": "Measures uniformity and logical coherence across data",
            "score": 71.0,
            "issues_found": 4,
            "issues": [
                {"column": "gender", "issue": "Case inconsistency detected", "description": "Same values with different capitalization (Male/MALE/male)", "impact": -2},
                {"column": "contract_type", "issue": "Whitespace inconsistency", "description": "Values have leading/trailing whitespace", "impact": -1},
                {"column": "monthly_charges", "issue": "Range inconsistency", "description": "89 extreme outliers detected", "impact": -3}
            ],
            "threshold": 85,
            "status": "fail"
        },
        
        # ACCURACY (DAMA Dimension 5)
        "accuracy": {
            "dimension": "Accuracy",
            "description": "Measures correctness of data (proxy via outlier analysis)",
            "score": 68.5,
            "note": "True accuracy requires ground truth comparison",
            "outlier_analysis": [
                {"column": "age", "outlier_count": 45, "outlier_percentage": 0.47, "lower_bound": 18.0, "upper_bound": 85.0, "mean": 39.2, "median": 37.0, "std": 15.8, "skewness": 0.32, "status": "pass"},
                {"column": "monthly_charges", "outlier_count": 234, "outlier_percentage": 2.41, "lower_bound": 18.5, "upper_bound": 145.0, "mean": 64.8, "median": 70.2, "std": 30.1, "skewness": -0.15, "status": "warning"},
                {"column": "total_charges", "outlier_count": 567, "outlier_percentage": 5.83, "lower_bound": 50.0, "upper_bound": 8500.0, "mean": 2283.0, "median": 1397.0, "std": 2266.0, "skewness": 1.12, "status": "fail"},
                {"column": "tenure_months", "outlier_count": 0, "outlier_percentage": 0.0, "lower_bound": 0, "upper_bound": 72, "mean": 32.4, "median": 29.0, "std": 24.6, "skewness": 0.24, "status": "pass"},
                {"column": "support_tickets", "outlier_count": 189, "outlier_percentage": 1.93, "lower_bound": 0, "upper_bound": 12, "mean": 3.2, "median": 2.0, "std": 2.8, "skewness": 1.45, "status": "pass"}
            ],
            "threshold": 85,
            "status": "fail"
        },
        
        # TIMELINESS (DAMA Dimension 6)
        "timeliness": {
            "dimension": "Timeliness",
            "description": "Measures currency and freshness of data",
            "score": 85.0,
            "datetime_columns_found": 1,
            "analysis": [
                {
                    "column": "churn_date",
                    "earliest_date": "2023-01-15",
                    "latest_date": "2024-12-15",
                    "days_since_latest": 12,
                    "timespan_days": 700,
                    "freshness": "current"
                }
            ],
            "threshold": 80,
            "status": "pass"
        },
        
        # ML READINESS (ML-Specific Metrics)
        "ml_readiness": {
            "dimension": "ML Readiness",
            "description": "Specialized metrics for machine learning training data",
            "score": 72,
            "status": "needs_improvement",
            "high_correlations": [
                {"column1": "tenure_months", "column2": "total_charges", "correlation": 0.826, "risk": "high_correlation"},
                {"column1": "monthly_charges", "column2": "total_charges", "correlation": 0.651, "risk": "high_correlation"}
            ],
            "multicollinearity_risk": 0,
            "class_balance_analysis": [
                {
                    "column": "churn",
                    "num_classes": 2,
                    "imbalance_ratio": 2.7,
                    "majority_class_pct": 73.0,
                    "minority_class_pct": 27.0,
                    "status": "balanced"
                },
                {
                    "column": "contract_type",
                    "num_classes": 3,
                    "imbalance_ratio": 2.1,
                    "majority_class_pct": 48.5,
                    "minority_class_pct": 23.2,
                    "status": "balanced"
                }
            ],
            "low_variance_features": [],
            "recommendations": [
                "High correlation between tenure_months and total_charges - consider feature selection",
                "Target variable 'churn' is reasonably balanced (73/27 split)",
                "Consider handling outliers in total_charges column before training"
            ]
        },
        
        # Column Profiles
        "column_profiles": [
            {"name": "customer_id", "dtype": "int64", "non_null_count": 10000, "null_count": 0, "null_percentage": 0.0, "unique_count": 10000, "unique_percentage": 100.0, "is_numeric": True, "stats": {"mean": 5000.5, "std": 2886.9, "min": 1, "max": 10000, "median": 5000.5}},
            {"name": "name", "dtype": "object", "non_null_count": 10000, "null_count": 0, "null_percentage": 0.0, "unique_count": 8876, "unique_percentage": 88.76, "is_numeric": False},
            {"name": "email", "dtype": "object", "non_null_count": 10000, "null_count": 0, "null_percentage": 0.0, "unique_count": 9950, "unique_percentage": 99.5, "is_numeric": False},
            {"name": "age", "dtype": "float64", "non_null_count": 9650, "null_count": 350, "null_percentage": 3.5, "unique_count": 62, "unique_percentage": 0.62, "is_numeric": True, "stats": {"mean": 39.2, "std": 15.8, "min": 18, "max": 85, "median": 37.0, "q1": 27.0, "q3": 50.0}},
            {"name": "tenure_months", "dtype": "int64", "non_null_count": 10000, "null_count": 0, "null_percentage": 0.0, "unique_count": 73, "unique_percentage": 0.73, "is_numeric": True, "stats": {"mean": 32.4, "std": 24.6, "min": 0, "max": 72, "median": 29.0}},
            {"name": "monthly_charges", "dtype": "float64", "non_null_count": 10000, "null_count": 0, "null_percentage": 0.0, "unique_count": 1234, "unique_percentage": 12.34, "is_numeric": True, "stats": {"mean": 64.8, "std": 30.1, "min": 18.5, "max": 118.75, "median": 70.2}},
            {"name": "churn", "dtype": "object", "non_null_count": 10000, "null_count": 0, "null_percentage": 0.0, "unique_count": 2, "unique_percentage": 0.02, "is_numeric": False, "value_distribution": [{"value": "No", "count": 7300, "percentage": 73.0}, {"value": "Yes", "count": 2700, "percentage": 27.0}]}
        ],
        
        # Sample Data
        "sample_data": [
            {"customer_id": "1001", "name": "John Smith", "email": "john.smith@email.com", "age": "34", "tenure_months": "24", "monthly_charges": "65.50", "churn": "No"},
            {"customer_id": "1002", "name": "Jane Doe", "email": "jane.doe@email.com", "age": "28", "tenure_months": "12", "monthly_charges": "89.00", "churn": "No"},
            {"customer_id": "1003", "name": "Bob Wilson", "email": "bob.w@email.com", "age": "45", "tenure_months": "36", "monthly_charges": "45.25", "churn": "Yes"}
        ]
    }
    
    return {
        "status": "success",
        "report": demo_report
    }


# Helper to store report (used by upload endpoint)
def store_report(source_id: str, report: dict):
    """Store report in temp storage"""
    _temp_storage[source_id] = report
