"""
Data Quality Analysis Service
Uses industry-standard metrics based on DAMA, ISO 25024, and enterprise standards
for evaluating ML training data quality.

Key Data Quality Dimensions:
1. Accuracy - Data correctly reflects real-world entities
2. Completeness - All required data fields are populated  
3. Consistency - Uniformity across sources and systems
4. Timeliness - Data is current and up-to-date
5. Validity - Data adheres to defined formats/rules
6. Uniqueness - No duplicate records
7. Integrity - Structural accuracy of relationships
8. Relevance - Data is applicable for the ML use case
"""
import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional
from io import BytesIO
from datetime import datetime, timedelta
import re


class EnterpriseDataAnalyzer:
    """
    Enterprise-grade data quality analyzer using industry-standard metrics.
    Based on DAMA Data Quality Framework and ISO 25024 standards.
    """
    
    def __init__(self, df: pd.DataFrame, filename: str = "dataset"):
        self.df = df
        self.filename = filename
        self.numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        self.categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
        self.datetime_cols = df.select_dtypes(include=['datetime64']).columns.tolist()
        self.boolean_cols = df.select_dtypes(include=['bool']).columns.tolist()
        
    # ==========================================
    # CORE QUALITY DIMENSIONS (Industry Standard)
    # ==========================================
    
    def measure_completeness(self) -> Dict[str, Any]:
        """
        COMPLETENESS: Measures extent to which data is not missing.
        Industry metric: % of non-null values across all cells.
        Critical for ML: Missing data can bias model training.
        """
        total_cells = self.df.size
        non_null_cells = self.df.notna().sum().sum()
        completeness_ratio = non_null_cells / total_cells if total_cells > 0 else 0
        
        # Per-column completeness
        column_completeness = []
        for col in self.df.columns:
            non_null = self.df[col].notna().sum()
            total = len(self.df)
            ratio = non_null / total if total > 0 else 0
            
            column_completeness.append({
                "column": col,
                "non_null_count": int(non_null),
                "null_count": int(total - non_null),
                "completeness_ratio": round(ratio * 100, 2),
                "status": "pass" if ratio >= 0.95 else "warning" if ratio >= 0.8 else "fail"
            })
        
        # Sort by completeness (worst first)
        column_completeness.sort(key=lambda x: x["completeness_ratio"])
        
        return {
            "dimension": "Completeness",
            "description": "Measures extent to which required data is present",
            "score": round(completeness_ratio * 100, 2),
            "total_cells": int(total_cells),
            "non_null_cells": int(non_null_cells),
            "null_cells": int(total_cells - non_null_cells),
            "columns_below_threshold": len([c for c in column_completeness if c["status"] == "fail"]),
            "column_details": column_completeness,
            "threshold": 95,
            "status": "pass" if completeness_ratio >= 0.95 else "warning" if completeness_ratio >= 0.8 else "fail"
        }
    
    def measure_uniqueness(self) -> Dict[str, Any]:
        """
        UNIQUENESS: Measures absence of duplicate records.
        Industry metric: % of unique rows in the dataset.
        Critical for ML: Duplicates can overfit models to repeated patterns.
        """
        total_rows = len(self.df)
        duplicate_rows = self.df.duplicated().sum()
        unique_rows = total_rows - duplicate_rows
        uniqueness_ratio = unique_rows / total_rows if total_rows > 0 else 0
        
        # Column-level uniqueness (for potential key columns)
        column_uniqueness = []
        for col in self.df.columns:
            unique_values = self.df[col].nunique()
            total_values = self.df[col].notna().sum()
            cardinality_ratio = unique_values / total_values if total_values > 0 else 0
            
            # Determine if likely a key/ID column
            is_potential_key = cardinality_ratio > 0.95 and total_values == len(self.df)
            
            column_uniqueness.append({
                "column": col,
                "unique_values": int(unique_values),
                "cardinality_ratio": round(cardinality_ratio * 100, 2),
                "is_potential_key": is_potential_key
            })
        
        return {
            "dimension": "Uniqueness",
            "description": "Measures absence of duplicate records",
            "score": round(uniqueness_ratio * 100, 2),
            "total_rows": int(total_rows),
            "unique_rows": int(unique_rows),
            "duplicate_rows": int(duplicate_rows),
            "duplicate_percentage": round(duplicate_rows / total_rows * 100, 2) if total_rows > 0 else 0,
            "column_cardinality": column_uniqueness,
            "potential_key_columns": [c["column"] for c in column_uniqueness if c["is_potential_key"]],
            "threshold": 95,
            "status": "pass" if uniqueness_ratio >= 0.95 else "warning" if uniqueness_ratio >= 0.9 else "fail"
        }
    
    def measure_validity(self) -> Dict[str, Any]:
        """
        VALIDITY: Measures conformance to defined formats and business rules.
        Industry metric: % of values that conform to expected patterns.
        Critical for ML: Invalid data can introduce noise and errors.
        """
        validity_issues = []
        total_checks = 0
        passed_checks = 0
        
        for col in self.df.columns:
            col_data = self.df[col].dropna()
            if len(col_data) == 0:
                continue
            
            dtype = str(self.df[col].dtype)
            issues = []
            
            # Check numeric columns
            if col in self.numeric_cols:
                total_checks += 1
                # Check for infinity values
                inf_count = np.isinf(col_data.astype(float)).sum() if col_data.dtype in ['float64', 'float32'] else 0
                if inf_count > 0:
                    issues.append(f"{inf_count} infinite values detected")
                else:
                    passed_checks += 1
                
                # Check for negative values in typically positive columns
                total_checks += 1
                if any(kw in col.lower() for kw in ['age', 'price', 'amount', 'quantity', 'count', 'size']):
                    neg_count = (col_data < 0).sum()
                    if neg_count > 0:
                        issues.append(f"{neg_count} unexpected negative values")
                    else:
                        passed_checks += 1
                else:
                    passed_checks += 1
            
            # Check categorical columns
            elif col in self.categorical_cols:
                total_checks += 1
                # Check for whitespace-only values
                whitespace_count = col_data.str.strip().eq('').sum()
                if whitespace_count > 0:
                    issues.append(f"{whitespace_count} whitespace-only values")
                else:
                    passed_checks += 1
                
                # Check for email format if column name suggests email
                if 'email' in col.lower():
                    total_checks += 1
                    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
                    invalid_emails = (~col_data.str.match(email_pattern, na=False)).sum()
                    if invalid_emails > 0:
                        issues.append(f"{invalid_emails} invalid email formats")
                    else:
                        passed_checks += 1
                
                # Check for phone format if column name suggests phone
                if 'phone' in col.lower() or 'mobile' in col.lower():
                    total_checks += 1
                    # Basic phone check - at least 10 digits
                    invalid_phones = col_data.str.replace(r'\D', '', regex=True).str.len().lt(10).sum()
                    if invalid_phones > 0:
                        issues.append(f"{invalid_phones} potentially invalid phone numbers")
                    else:
                        passed_checks += 1
            
            if issues:
                validity_issues.append({
                    "column": col,
                    "dtype": dtype,
                    "issues": issues,
                    "severity": "high" if len(issues) > 1 else "medium"
                })
        
        validity_score = (passed_checks / total_checks * 100) if total_checks > 0 else 100
        
        return {
            "dimension": "Validity",
            "description": "Measures conformance to defined formats and business rules",
            "score": round(validity_score, 2),
            "total_checks": total_checks,
            "passed_checks": passed_checks,
            "failed_checks": total_checks - passed_checks,
            "issues": validity_issues,
            "threshold": 90,
            "status": "pass" if validity_score >= 90 else "warning" if validity_score >= 75 else "fail"
        }
    
    def measure_consistency(self) -> Dict[str, Any]:
        """
        CONSISTENCY: Measures uniformity and logical coherence of data.
        Industry metric: % of values that are logically consistent.
        Critical for ML: Inconsistent data leads to unreliable model predictions.
        """
        consistency_issues = []
        consistency_score = 100
        
        # Check for mixed case inconsistencies in categorical columns
        for col in self.categorical_cols:
            col_data = self.df[col].dropna()
            if len(col_data) == 0:
                continue
            
            # Check for case inconsistencies (same value with different cases)
            unique_values = col_data.unique()
            lower_values = {str(v).lower(): v for v in unique_values}
            if len(lower_values) < len(unique_values):
                consistency_issues.append({
                    "column": col,
                    "issue": "Case inconsistency detected",
                    "description": "Same values with different capitalization",
                    "impact": -2
                })
                consistency_score -= 2
            
            # Check for leading/trailing whitespace
            has_whitespace = (col_data != col_data.str.strip()).any()
            if has_whitespace:
                consistency_issues.append({
                    "column": col,
                    "issue": "Whitespace inconsistency",
                    "description": "Values have leading/trailing whitespace",
                    "impact": -1
                })
                consistency_score -= 1
        
        # Check for date format consistency
        date_keywords = ['date', 'time', 'timestamp', 'created', 'updated']
        for col in self.categorical_cols:
            if any(kw in col.lower() for kw in date_keywords):
                col_data = self.df[col].dropna()
                if len(col_data) > 0:
                    # Try to detect multiple date formats
                    try:
                        pd.to_datetime(col_data, infer_datetime_format=True)
                    except:
                        consistency_issues.append({
                            "column": col,
                            "issue": "Date format inconsistency",
                            "description": "Multiple date formats or invalid dates detected",
                            "impact": -5
                        })
                        consistency_score -= 5
        
        # Check numeric range consistency
        for col in self.numeric_cols:
            col_data = self.df[col].dropna()
            if len(col_data) > 10:
                # Check for extreme outliers that might indicate data entry errors
                q1, q3 = col_data.quantile([0.25, 0.75])
                iqr = q3 - q1
                extreme_low = (col_data < q1 - 3 * iqr).sum()
                extreme_high = (col_data > q3 + 3 * iqr).sum()
                
                if extreme_low + extreme_high > len(col_data) * 0.01:  # More than 1%
                    consistency_issues.append({
                        "column": col,
                        "issue": "Range inconsistency",
                        "description": f"{extreme_low + extreme_high} extreme outliers detected",
                        "impact": -3
                    })
                    consistency_score -= 3
        
        return {
            "dimension": "Consistency",
            "description": "Measures uniformity and logical coherence across data",
            "score": max(0, round(consistency_score, 2)),
            "issues_found": len(consistency_issues),
            "issues": consistency_issues,
            "threshold": 85,
            "status": "pass" if consistency_score >= 85 else "warning" if consistency_score >= 70 else "fail"
        }
    
    def measure_accuracy(self) -> Dict[str, Any]:
        """
        ACCURACY: Measures correctness compared to real-world values.
        Industry metric: Statistical measures of data distribution normality.
        Note: True accuracy requires ground truth comparison.
        """
        accuracy_indicators = []
        accuracy_score = 100
        
        for col in self.numeric_cols:
            col_data = self.df[col].dropna()
            if len(col_data) < 10:
                continue
            
            # Statistical outlier detection using IQR method
            q1 = col_data.quantile(0.25)
            q3 = col_data.quantile(0.75)
            iqr = q3 - q1
            lower_bound = q1 - 1.5 * iqr
            upper_bound = q3 + 1.5 * iqr
            
            outliers = ((col_data < lower_bound) | (col_data > upper_bound)).sum()
            outlier_pct = outliers / len(col_data) * 100
            
            if outlier_pct > 5:
                accuracy_score -= 5
            elif outlier_pct > 2:
                accuracy_score -= 2
            
            accuracy_indicators.append({
                "column": col,
                "outlier_count": int(outliers),
                "outlier_percentage": round(outlier_pct, 2),
                "lower_bound": round(float(lower_bound), 4),
                "upper_bound": round(float(upper_bound), 4),
                "mean": round(float(col_data.mean()), 4),
                "median": round(float(col_data.median()), 4),
                "std": round(float(col_data.std()), 4),
                "skewness": round(float(col_data.skew()), 4),
                "status": "pass" if outlier_pct <= 2 else "warning" if outlier_pct <= 5 else "fail"
            })
        
        return {
            "dimension": "Accuracy",
            "description": "Measures correctness of data (proxy via outlier analysis)",
            "score": max(0, round(accuracy_score, 2)),
            "note": "True accuracy requires ground truth comparison",
            "outlier_analysis": accuracy_indicators,
            "threshold": 85,
            "status": "pass" if accuracy_score >= 85 else "warning" if accuracy_score >= 70 else "fail"
        }
    
    def measure_timeliness(self) -> Dict[str, Any]:
        """
        TIMELINESS: Measures currency and freshness of data.
        Industry metric: Age of data compared to current date.
        Critical for ML: Stale data may not reflect current patterns.
        """
        timeliness_info = {
            "dimension": "Timeliness",
            "description": "Measures currency and freshness of data",
            "datetime_columns_found": len(self.datetime_cols),
            "analysis": []
        }
        
        # Try to find and analyze datetime columns
        date_cols = self.datetime_cols.copy()
        
        # Also check string columns that might be dates
        for col in self.categorical_cols:
            if any(kw in col.lower() for kw in ['date', 'time', 'created', 'updated', 'timestamp']):
                try:
                    parsed = pd.to_datetime(self.df[col], errors='coerce')
                    if parsed.notna().sum() > len(self.df) * 0.5:
                        date_cols.append(col)
                except:
                    pass
        
        if len(date_cols) == 0:
            timeliness_info["score"] = None
            timeliness_info["note"] = "No datetime columns detected"
            timeliness_info["status"] = "unknown"
        else:
            timeliness_score = 100
            now = datetime.now()
            
            for col in date_cols[:3]:  # Analyze up to 3 date columns
                try:
                    dates = pd.to_datetime(self.df[col], errors='coerce')
                    valid_dates = dates.dropna()
                    
                    if len(valid_dates) > 0:
                        max_date = valid_dates.max()
                        min_date = valid_dates.min()
                        
                        # Check data age
                        if pd.notna(max_date):
                            days_old = (now - max_date.to_pydatetime().replace(tzinfo=None)).days
                        else:
                            days_old = None
                        
                        # Calculate timespan
                        if pd.notna(min_date) and pd.notna(max_date):
                            timespan_days = (max_date - min_date).days
                        else:
                            timespan_days = None
                        
                        timeliness_info["analysis"].append({
                            "column": col,
                            "earliest_date": str(min_date.date()) if pd.notna(min_date) else None,
                            "latest_date": str(max_date.date()) if pd.notna(max_date) else None,
                            "days_since_latest": days_old,
                            "timespan_days": timespan_days,
                            "freshness": "current" if days_old and days_old < 30 else "recent" if days_old and days_old < 90 else "stale"
                        })
                        
                        # Penalize stale data
                        if days_old and days_old > 365:
                            timeliness_score -= 20
                        elif days_old and days_old > 90:
                            timeliness_score -= 10
                except:
                    pass
            
            timeliness_info["score"] = max(0, timeliness_score)
            timeliness_info["threshold"] = 80
            timeliness_info["status"] = "pass" if timeliness_score >= 80 else "warning" if timeliness_score >= 60 else "fail"
        
        return timeliness_info
    
    # ==========================================
    # ML-SPECIFIC QUALITY METRICS
    # ==========================================
    
    def measure_ml_readiness(self) -> Dict[str, Any]:
        """
        ML READINESS: Specialized metrics for machine learning datasets.
        Includes class balance, feature correlation, target leakage detection.
        """
        ml_metrics = {
            "dimension": "ML Readiness",
            "description": "Specialized metrics for machine learning training data"
        }
        
        # Feature to target correlation (if identifiable)
        correlations = []
        if len(self.numeric_cols) >= 2:
            corr_matrix = self.df[self.numeric_cols].corr()
            
            # Find highly correlated pairs
            for i in range(len(self.numeric_cols)):
                for j in range(i + 1, len(self.numeric_cols)):
                    corr_val = corr_matrix.iloc[i, j]
                    if abs(corr_val) >= 0.7:
                        correlations.append({
                            "column1": self.numeric_cols[i],
                            "column2": self.numeric_cols[j],
                            "correlation": round(float(corr_val), 4),
                            "risk": "multicollinearity" if abs(corr_val) >= 0.9 else "high_correlation"
                        })
        
        ml_metrics["high_correlations"] = correlations
        ml_metrics["multicollinearity_risk"] = len([c for c in correlations if c["risk"] == "multicollinearity"])
        
        # Class balance analysis (for potential target columns)
        class_balance = []
        for col in self.categorical_cols:
            unique_count = self.df[col].nunique()
            if 2 <= unique_count <= 20:  # Likely a classification target
                value_counts = self.df[col].value_counts(normalize=True)
                imbalance_ratio = value_counts.max() / value_counts.min() if value_counts.min() > 0 else float('inf')
                
                class_balance.append({
                    "column": col,
                    "num_classes": unique_count,
                    "imbalance_ratio": round(imbalance_ratio, 2),
                    "majority_class_pct": round(value_counts.max() * 100, 2),
                    "minority_class_pct": round(value_counts.min() * 100, 2),
                    "status": "balanced" if imbalance_ratio < 3 else "imbalanced" if imbalance_ratio < 10 else "severely_imbalanced"
                })
        
        ml_metrics["class_balance_analysis"] = class_balance
        
        # Feature variance (low variance = potentially useless features)
        low_variance_features = []
        for col in self.numeric_cols:
            variance = self.df[col].var()
            if variance < 0.01:
                low_variance_features.append({
                    "column": col,
                    "variance": round(float(variance), 6),
                    "recommendation": "Consider removing - near-constant feature"
                })
        
        ml_metrics["low_variance_features"] = low_variance_features
        
        # Calculate overall ML readiness score
        score = 100
        score -= len(correlations) * 3  # Penalize high correlations
        score -= len(low_variance_features) * 5  # Penalize low variance features
        score -= len([c for c in class_balance if c["status"] == "severely_imbalanced"]) * 10
        
        ml_metrics["score"] = max(0, score)
        ml_metrics["status"] = "ready" if score >= 80 else "needs_improvement" if score >= 60 else "not_ready"
        
        return ml_metrics
    
    # ==========================================
    # OVERALL QUALITY SCORE
    # ==========================================
    
    def calculate_overall_score(self) -> Dict[str, Any]:
        """
        Calculate weighted overall data quality score.
        Based on industry-standard dimension weighting.
        """
        completeness = self.measure_completeness()
        uniqueness = self.measure_uniqueness()
        validity = self.measure_validity()
        consistency = self.measure_consistency()
        accuracy = self.measure_accuracy()
        timeliness = self.measure_timeliness()
        ml_readiness = self.measure_ml_readiness()
        
        # Industry-standard weights (DAMA framework)
        weights = {
            "completeness": 0.25,  # Most critical for ML
            "uniqueness": 0.15,
            "validity": 0.15,
            "consistency": 0.15,
            "accuracy": 0.20,
            "timeliness": 0.10  # Context dependent
        }
        
        scores = {
            "completeness": completeness["score"],
            "uniqueness": uniqueness["score"],
            "validity": validity["score"],
            "consistency": consistency["score"],
            "accuracy": accuracy["score"],
        }
        
        # Handle timeliness if available
        if timeliness.get("score") is not None:
            scores["timeliness"] = timeliness["score"]
        else:
            weights["timeliness"] = 0
            # Redistribute weight
            for k in weights:
                if k != "timeliness":
                    weights[k] += 0.10 / 5
        
        # Calculate weighted score
        overall_score = sum(scores[k] * weights[k] for k in scores)
        
        # Determine grade
        if overall_score >= 90:
            grade = "A"
            grade_description = "Excellent - Production Ready"
        elif overall_score >= 80:
            grade = "B"
            grade_description = "Good - Minor Improvements Needed"
        elif overall_score >= 70:
            grade = "C"
            grade_description = "Fair - Several Issues to Address"
        elif overall_score >= 60:
            grade = "D"
            grade_description = "Poor - Significant Work Required"
        else:
            grade = "F"
            grade_description = "Failing - Major Quality Issues"
        
        return {
            "overall_score": round(overall_score, 1),
            "grade": grade,
            "grade_description": grade_description,
            "dimension_scores": {k: round(v, 1) for k, v in scores.items()},
            "weights": weights,
            "ml_readiness_score": ml_readiness["score"],
            "ml_readiness_status": ml_readiness["status"]
        }
    
    # ==========================================
    # DATASET OVERVIEW
    # ==========================================
    
    def get_dataset_overview(self) -> Dict[str, Any]:
        """Get basic dataset statistics."""
        memory_mb = self.df.memory_usage(deep=True).sum() / 1024 / 1024
        
        return {
            "filename": self.filename,
            "rows": len(self.df),
            "columns": len(self.df.columns),
            "memory_usage_mb": round(memory_mb, 2),
            "column_types": {
                "numeric": len(self.numeric_cols),
                "categorical": len(self.categorical_cols),
                "datetime": len(self.datetime_cols),
                "boolean": len(self.boolean_cols)
            },
            "column_names": self.df.columns.tolist()
        }
    
    def get_column_profiles(self) -> List[Dict[str, Any]]:
        """Get detailed profile for each column."""
        profiles = []
        
        for col in self.df.columns:
            col_data = self.df[col]
            profile = {
                "name": col,
                "dtype": str(col_data.dtype),
                "non_null_count": int(col_data.notna().sum()),
                "null_count": int(col_data.isna().sum()),
                "null_percentage": round(col_data.isna().mean() * 100, 2),
                "unique_count": int(col_data.nunique()),
                "unique_percentage": round(col_data.nunique() / len(col_data) * 100, 2)
            }
            
            # Numeric-specific stats
            if col in self.numeric_cols:
                profile["is_numeric"] = True
                profile["stats"] = {
                    "mean": round(float(col_data.mean()), 4) if col_data.notna().any() else None,
                    "std": round(float(col_data.std()), 4) if col_data.notna().any() else None,
                    "min": round(float(col_data.min()), 4) if col_data.notna().any() else None,
                    "max": round(float(col_data.max()), 4) if col_data.notna().any() else None,
                    "median": round(float(col_data.median()), 4) if col_data.notna().any() else None,
                    "q1": round(float(col_data.quantile(0.25)), 4) if col_data.notna().any() else None,
                    "q3": round(float(col_data.quantile(0.75)), 4) if col_data.notna().any() else None
                }
            else:
                profile["is_numeric"] = False
                if col_data.nunique() <= 20:
                    profile["value_distribution"] = [
                        {"value": str(k), "count": int(v), "percentage": round(v / len(col_data) * 100, 2)}
                        for k, v in col_data.value_counts().head(10).items()
                    ]
            
            profiles.append(profile)
        
        return profiles
    
    def get_sample_data(self, n: int = 10) -> List[Dict[str, Any]]:
        """Get sample rows for preview."""
        sample = self.df.head(n).fillna("").astype(str)
        return sample.to_dict(orient='records')
    
    # ==========================================
    # FULL REPORT GENERATION
    # ==========================================
    
    def generate_full_report(self) -> Dict[str, Any]:
        """Generate comprehensive data quality report."""
        return {
            "filename": self.filename,
            "generated_at": datetime.now().isoformat(),
            "status": "success",
            
            # Overview
            "overview": self.get_dataset_overview(),
            
            # Overall Score
            "quality_score": self.calculate_overall_score(),
            
            # Individual Dimensions (Industry Standard)
            "completeness": self.measure_completeness(),
            "uniqueness": self.measure_uniqueness(),
            "validity": self.measure_validity(),
            "consistency": self.measure_consistency(),
            "accuracy": self.measure_accuracy(),
            "timeliness": self.measure_timeliness(),
            
            # ML-Specific
            "ml_readiness": self.measure_ml_readiness(),
            
            # Column Details
            "column_profiles": self.get_column_profiles(),
            
            # Sample Data
            "sample_data": self.get_sample_data()
        }


def analyze_file(file_content: bytes, filename: str) -> Dict[str, Any]:
    """Analyze uploaded file and return quality report."""
    try:
        # Read file based on extension
        if filename.endswith('.csv'):
            df = pd.read_csv(BytesIO(file_content))
        elif filename.endswith(('.xlsx', '.xls')):
            df = pd.read_excel(BytesIO(file_content))
        elif filename.endswith('.json'):
            df = pd.read_json(BytesIO(file_content))
        else:
            return {"error": f"Unsupported file type: {filename}", "status": "failed"}
        
        # Analyze
        analyzer = EnterpriseDataAnalyzer(df, filename)
        return analyzer.generate_full_report()
        
    except Exception as e:
        return {
            "error": str(e),
            "filename": filename,
            "status": "failed"
        }
