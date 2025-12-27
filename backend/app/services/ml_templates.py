"""
ML Dataset Templates
Specialized analysis for different types of ML datasets
"""
import pandas as pd
import numpy as np
from typing import Dict, Any, List


class MLTemplateAnalyzer:
    """Template-based analysis for ML datasets"""
    
    TEMPLATES = {
        "classification": {
            "name": "Classification Dataset",
            "description": "For datasets with target labels (binary or multi-class)",
            "icon": "target"
        },
        "regression": {
            "name": "Regression Dataset", 
            "description": "For datasets with continuous target values",
            "icon": "trending-up"
        },
        "timeseries": {
            "name": "Time Series Dataset",
            "description": "For datasets with temporal ordering",
            "icon": "clock"
        },
        "text": {
            "name": "Text/NLP Dataset",
            "description": "For datasets with text content",
            "icon": "file-text"
        },
        "general": {
            "name": "General Tabular",
            "description": "Standard tabular data analysis",
            "icon": "table"
        }
    }
    
    def __init__(self, df: pd.DataFrame):
        self.df = df
        self.numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        self.categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
    
    def detect_template(self) -> str:
        """Auto-detect the best template for the dataset"""
        # Check for datetime columns (time series)
        datetime_cols = self.df.select_dtypes(include=['datetime64']).columns
        if len(datetime_cols) > 0:
            return "timeseries"
        
        # Check for date-like column names
        date_keywords = ['date', 'time', 'timestamp', 'datetime', 'day', 'month', 'year']
        for col in self.df.columns:
            if any(kw in col.lower() for kw in date_keywords):
                try:
                    pd.to_datetime(self.df[col].head(100))
                    return "timeseries"
                except:
                    pass
        
        # Check for text-heavy data
        text_cols = [col for col in self.categorical_cols 
                     if self.df[col].dropna().str.len().mean() > 50]
        if len(text_cols) > len(self.df.columns) * 0.3:
            return "text"
        
        # Check for classification (last column is categorical with few classes)
        if len(self.categorical_cols) > 0:
            last_col = self.df.columns[-1]
            if last_col in self.categorical_cols:
                if self.df[last_col].nunique() <= 20:
                    return "classification"
        
        # Check for regression (last column is numeric)
        if len(self.numeric_cols) > 0:
            last_col = self.df.columns[-1]
            if last_col in self.numeric_cols:
                return "regression"
        
        return "general"
    
    def analyze_classification(self, target_col: str = None) -> Dict[str, Any]:
        """Analysis for classification datasets"""
        if target_col is None:
            # Try to detect target column
            target_col = self.df.columns[-1]
        
        if target_col not in self.df.columns:
            return {"error": f"Target column '{target_col}' not found"}
        
        target = self.df[target_col]
        class_dist = target.value_counts().to_dict()
        class_pct = target.value_counts(normalize=True).mul(100).round(2).to_dict()
        
        # Calculate class imbalance
        majority_class_pct = max(class_pct.values())
        minority_class_pct = min(class_pct.values())
        imbalance_ratio = round(majority_class_pct / max(minority_class_pct, 0.01), 2)
        
        # Determine imbalance severity
        if imbalance_ratio > 10:
            imbalance_severity = "severe"
        elif imbalance_ratio > 3:
            imbalance_severity = "moderate"
        else:
            imbalance_severity = "balanced"
        
        return {
            "template": "classification",
            "target_column": target_col,
            "num_classes": len(class_dist),
            "class_distribution": [
                {"class": str(k), "count": int(v), "percent": float(class_pct[k])}
                for k, v in class_dist.items()
            ],
            "imbalance_ratio": imbalance_ratio,
            "imbalance_severity": imbalance_severity,
            "recommendations": self._get_classification_recommendations(imbalance_ratio, len(class_dist)),
            "feature_columns": [c for c in self.df.columns if c != target_col],
            "feature_count": len(self.df.columns) - 1
        }
    
    def analyze_regression(self, target_col: str = None) -> Dict[str, Any]:
        """Analysis for regression datasets"""
        if target_col is None:
            # Try last numeric column
            if self.numeric_cols:
                target_col = self.numeric_cols[-1]
            else:
                return {"error": "No numeric columns found for regression"}
        
        target = self.df[target_col].dropna()
        
        # Distribution analysis
        skewness = float(target.skew())
        kurtosis = float(target.kurtosis())
        
        # Check for normality
        if abs(skewness) < 0.5 and abs(kurtosis) < 3:
            distribution = "approximately normal"
        elif skewness > 1:
            distribution = "right-skewed"
        elif skewness < -1:
            distribution = "left-skewed"
        else:
            distribution = "moderately skewed"
        
        # Value range analysis
        value_range = float(target.max() - target.min())
        
        return {
            "template": "regression",
            "target_column": target_col,
            "statistics": {
                "mean": round(float(target.mean()), 4),
                "std": round(float(target.std()), 4),
                "min": round(float(target.min()), 4),
                "max": round(float(target.max()), 4),
                "median": round(float(target.median()), 4),
                "range": round(value_range, 4)
            },
            "distribution": {
                "skewness": round(skewness, 4),
                "kurtosis": round(kurtosis, 4),
                "shape": distribution
            },
            "histogram": self._get_histogram_data(target),
            "recommendations": self._get_regression_recommendations(skewness, value_range),
            "feature_columns": [c for c in self.df.columns if c != target_col],
            "feature_count": len(self.df.columns) - 1
        }
    
    def analyze_timeseries(self, date_col: str = None) -> Dict[str, Any]:
        """Analysis for time series datasets"""
        # Find date column
        if date_col is None:
            datetime_cols = self.df.select_dtypes(include=['datetime64']).columns
            if len(datetime_cols) > 0:
                date_col = datetime_cols[0]
            else:
                # Try to find and parse date column
                for col in self.df.columns:
                    try:
                        pd.to_datetime(self.df[col])
                        date_col = col
                        break
                    except:
                        pass
        
        if date_col is None:
            return {"error": "No date column found"}
        
        dates = pd.to_datetime(self.df[date_col])
        
        # Time range analysis
        date_range = dates.max() - dates.min()
        
        # Frequency detection
        if len(dates) > 1:
            diffs = dates.diff().dropna()
            median_diff = diffs.median()
            
            if median_diff <= pd.Timedelta(hours=1):
                frequency = "hourly or sub-hourly"
            elif median_diff <= pd.Timedelta(days=1):
                frequency = "daily"
            elif median_diff <= pd.Timedelta(days=7):
                frequency = "weekly"
            elif median_diff <= pd.Timedelta(days=31):
                frequency = "monthly"
            else:
                frequency = "irregular"
        else:
            frequency = "unknown"
        
        # Check for gaps
        if len(dates) > 1:
            expected = pd.date_range(dates.min(), dates.max(), freq=diffs.mode()[0] if len(diffs.mode()) > 0 else 'D')
            missing_dates = len(expected) - len(dates)
        else:
            missing_dates = 0
        
        return {
            "template": "timeseries",
            "date_column": date_col,
            "time_range": {
                "start": str(dates.min()),
                "end": str(dates.max()),
                "duration_days": int(date_range.days)
            },
            "frequency": frequency,
            "data_points": len(dates),
            "missing_dates": max(0, missing_dates),
            "value_columns": [c for c in self.numeric_cols if c != date_col],
            "recommendations": self._get_timeseries_recommendations(frequency, missing_dates)
        }
    
    def analyze_text(self) -> Dict[str, Any]:
        """Analysis for text/NLP datasets"""
        text_cols = []
        
        for col in self.categorical_cols:
            col_data = self.df[col].dropna()
            if len(col_data) > 0:
                avg_len = col_data.str.len().mean()
                if avg_len > 20:  # Likely text content
                    text_cols.append({
                        "column": col,
                        "avg_length": round(avg_len, 1),
                        "max_length": int(col_data.str.len().max()),
                        "min_length": int(col_data.str.len().min()),
                        "empty_count": int((col_data == "").sum()),
                        "avg_word_count": round(col_data.str.split().str.len().mean(), 1)
                    })
        
        return {
            "template": "text",
            "text_columns": text_cols,
            "has_labels": any(self.df[c].nunique() <= 20 for c in self.categorical_cols if c not in [t["column"] for t in text_cols]),
            "recommendations": self._get_text_recommendations(text_cols)
        }
    
    def analyze_general(self) -> Dict[str, Any]:
        """General tabular data analysis"""
        return {
            "template": "general",
            "column_types": {
                "numeric": self.numeric_cols,
                "categorical": self.categorical_cols,
                "total": len(self.df.columns)
            },
            "recommendations": self._get_general_recommendations()
        }
    
    def get_template_analysis(self, template: str = None, **kwargs) -> Dict[str, Any]:
        """Get analysis based on template"""
        if template is None:
            template = self.detect_template()
        
        template_info = self.TEMPLATES.get(template, self.TEMPLATES["general"])
        
        analyzers = {
            "classification": self.analyze_classification,
            "regression": self.analyze_regression,
            "timeseries": self.analyze_timeseries,
            "text": self.analyze_text,
            "general": self.analyze_general
        }
        
        analysis = analyzers.get(template, self.analyze_general)(**kwargs)
        analysis["template_info"] = template_info
        
        return analysis
    
    def _get_histogram_data(self, series: pd.Series, bins: int = 20) -> List[Dict]:
        """Generate histogram data for charts"""
        counts, edges = np.histogram(series.dropna(), bins=bins)
        return [
            {"bin": f"{round(edges[i], 2)}-{round(edges[i+1], 2)}", "count": int(counts[i])}
            for i in range(len(counts))
        ]
    
    def _get_classification_recommendations(self, imbalance_ratio: float, num_classes: int) -> List[str]:
        """Get recommendations for classification datasets"""
        recs = []
        if imbalance_ratio > 3:
            recs.append("Consider using SMOTE or other oversampling techniques for class imbalance")
            recs.append("Use stratified train-test split to maintain class distribution")
        if num_classes > 10:
            recs.append("Consider using hierarchical classification or grouping rare classes")
        if imbalance_ratio > 10:
            recs.append("Use class weights in your model or consider undersampling majority class")
        return recs
    
    def _get_regression_recommendations(self, skewness: float, value_range: float) -> List[str]:
        """Get recommendations for regression datasets"""
        recs = []
        if abs(skewness) > 1:
            recs.append("Consider log transformation for skewed target variable")
        if value_range > 1000:
            recs.append("Consider normalizing or standardizing target values")
        recs.append("Check for and handle outliers in target variable")
        return recs
    
    def _get_timeseries_recommendations(self, frequency: str, missing_dates: int) -> List[str]:
        """Get recommendations for time series datasets"""
        recs = []
        if missing_dates > 0:
            recs.append(f"Found approximately {missing_dates} missing time points - consider imputation")
        if frequency == "irregular":
            recs.append("Irregular time intervals detected - consider resampling to regular frequency")
        recs.append("Check for seasonality and trends before modeling")
        return recs
    
    def _get_text_recommendations(self, text_cols: list) -> List[str]:
        """Get recommendations for text datasets"""
        recs = ["Consider text preprocessing: lowercasing, punctuation removal, stopwords"]
        if any(col.get("avg_length", 0) > 500 for col in text_cols):
            recs.append("Long texts detected - consider text summarization or chunking")
        recs.append("Use tokenization and embeddings for ML models")
        return recs
    
    def _get_general_recommendations(self) -> List[str]:
        """Get general recommendations"""
        return [
            "Check for missing values and decide on imputation strategy",
            "Identify and encode categorical variables",
            "Normalize or standardize numeric features",
            "Check for and handle outliers"
        ]


def get_available_templates() -> List[Dict[str, Any]]:
    """Return list of available templates"""
    return [
        {"id": k, **v} 
        for k, v in MLTemplateAnalyzer.TEMPLATES.items()
    ]
