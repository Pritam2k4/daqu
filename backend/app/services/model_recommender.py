"""
Model Recommender Service
AI-powered model recommendation based on data analysis
Provides chatbot-like responses for model selection
"""
import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional
from datetime import datetime


class ModelRecommender:
    """
    Analyzes data characteristics and recommends
    the best ML models with explanations.
    """
    
    MODEL_INFO = {
        "xgboost": {
            "name": "XGBoost",
            "emoji": "🚀",
            "description": "Extreme Gradient Boosting - Industry standard for tabular data",
            "strengths": ["Handles missing values", "Fast training", "High accuracy", "Feature importance"],
            "best_for": ["Large datasets", "Imbalanced classes", "Mixed feature types"],
            "complexity": "Medium",
            "interpretability": "Medium"
        },
        "lightgbm": {
            "name": "LightGBM",
            "emoji": "⚡",
            "description": "Light Gradient Boosting Machine - Optimized for speed and memory",
            "strengths": ["Fastest training", "Handles large data", "Low memory usage"],
            "best_for": ["Very large datasets", "Quick iterations", "Categorical features"],
            "complexity": "Medium",
            "interpretability": "Medium"
        },
        "catboost": {
            "name": "CatBoost",
            "emoji": "🐱",
            "description": "Categorical Boosting - Native categorical feature handling",
            "strengths": ["No encoding needed", "Handles categories natively", "Robust to overfitting"],
            "best_for": ["Many categorical columns", "Mixed data types", "Quick setup"],
            "complexity": "Low",
            "interpretability": "Medium"
        },
        "random_forest": {
            "name": "Random Forest",
            "emoji": "🌲",
            "description": "Ensemble of decision trees - Reliable and interpretable",
            "strengths": ["Rarely overfits", "Handles non-linear relationships", "Feature importance"],
            "best_for": ["General purpose", "Exploratory analysis", "Feature selection"],
            "complexity": "Low",
            "interpretability": "High"
        },
        "logistic_regression": {
            "name": "Logistic Regression",
            "emoji": "📊",
            "description": "Statistical model for binary/multiclass classification",
            "strengths": ["Fast", "Interpretable coefficients", "Probabilistic output"],
            "best_for": ["Binary classification", "Smaller datasets", "Explainability required"],
            "complexity": "Low",
            "interpretability": "Very High"
        },
        "linear_regression": {
            "name": "Linear Regression",
            "emoji": "📈",
            "description": "Simple statistical model for numerical prediction",
            "strengths": ["Very fast", "Fully interpretable", "Statistical significance"],
            "best_for": ["Simple relationships", "Baseline model", "Stakeholder reports"],
            "complexity": "Very Low",
            "interpretability": "Very High"
        },
        "gradient_boosting": {
            "name": "Gradient Boosting",
            "emoji": "🔥",
            "description": "Scikit-learn's gradient boosting implementation",
            "strengths": ["Good accuracy", "Built into sklearn", "Stable"],
            "best_for": ["Medium datasets", "When XGBoost unavailable"],
            "complexity": "Medium",
            "interpretability": "Medium"
        }
    }
    
    def __init__(self, df: pd.DataFrame, target_column: str = None):
        self.df = df
        self.target_column = target_column
        self.data_profile = self._analyze_data()
    
    def _analyze_data(self) -> Dict[str, Any]:
        """Analyze data characteristics"""
        profile = {
            "rows": len(self.df),
            "columns": len(self.df.columns),
            "memory_mb": round(self.df.memory_usage(deep=True).sum() / 1024 / 1024, 2)
        }
        
        # Column types
        numeric_cols = self.df.select_dtypes(include=[np.number]).columns.tolist()
        categorical_cols = self.df.select_dtypes(include=['object', 'category']).columns.tolist()
        datetime_cols = self.df.select_dtypes(include=['datetime64']).columns.tolist()
        
        profile["numeric_columns"] = len(numeric_cols)
        profile["categorical_columns"] = len(categorical_cols)
        profile["datetime_columns"] = len(datetime_cols)
        
        # Missing values
        missing_pct = (self.df.isna().sum().sum() / self.df.size) * 100
        profile["missing_percentage"] = round(missing_pct, 2)
        profile["has_missing"] = missing_pct > 0
        
        # Target analysis
        if self.target_column and self.target_column in self.df.columns:
            target = self.df[self.target_column]
            profile["target_column"] = self.target_column
            
            if target.dtype == 'object' or target.nunique() <= 20:
                profile["task_type"] = "classification"
                profile["num_classes"] = target.nunique()
                
                # Class imbalance
                value_counts = target.value_counts(normalize=True)
                imbalance_ratio = value_counts.max() / value_counts.min() if value_counts.min() > 0 else 999
                profile["imbalance_ratio"] = round(imbalance_ratio, 2)
                profile["is_imbalanced"] = imbalance_ratio > 3
                profile["majority_class_pct"] = round(value_counts.max() * 100, 1)
            else:
                profile["task_type"] = "regression"
                profile["target_mean"] = round(target.mean(), 4)
                profile["target_std"] = round(target.std(), 4)
                profile["target_skewness"] = round(target.skew(), 4)
        else:
            profile["task_type"] = "unknown"
        
        # Data size category
        if profile["rows"] < 1000:
            profile["size_category"] = "small"
        elif profile["rows"] < 100000:
            profile["size_category"] = "medium"
        else:
            profile["size_category"] = "large"
        
        return profile
    
    def get_recommendations(self, top_n: int = 3) -> List[Dict[str, Any]]:
        """Get model recommendations based on data profile"""
        scores = {}
        
        task = self.data_profile.get("task_type", "unknown")
        
        if task == "classification":
            available_models = ["xgboost", "lightgbm", "catboost", "random_forest", 
                              "logistic_regression", "gradient_boosting"]
        elif task == "regression":
            available_models = ["xgboost", "lightgbm", "catboost", "random_forest",
                              "linear_regression", "gradient_boosting"]
        else:
            available_models = ["random_forest", "xgboost", "lightgbm"]
        
        for model in available_models:
            score = self._score_model(model)
            scores[model] = score
        
        # Sort by score
        sorted_models = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        
        recommendations = []
        for i, (model_id, score) in enumerate(sorted_models[:top_n]):
            info = self.MODEL_INFO[model_id].copy()
            info["id"] = model_id
            info["rank"] = i + 1
            info["score"] = score
            info["why"] = self._generate_recommendation_reason(model_id)
            recommendations.append(info)
        
        return recommendations
    
    def _score_model(self, model_id: str) -> float:
        """Score a model based on data characteristics"""
        score = 50  # Base score
        profile = self.data_profile
        
        # Size considerations
        if model_id == "lightgbm" and profile["size_category"] == "large":
            score += 20
        if model_id == "logistic_regression" and profile["size_category"] == "small":
            score += 15
        if model_id in ["xgboost", "lightgbm", "catboost"] and profile["size_category"] == "medium":
            score += 10
        
        # Categorical considerations
        if model_id == "catboost" and profile["categorical_columns"] > 3:
            score += 25
        if model_id == "lightgbm" and profile["categorical_columns"] > 5:
            score += 15
        
        # Missing value handling
        if profile["has_missing"] and model_id in ["xgboost", "lightgbm", "catboost"]:
            score += 10
        
        # Imbalance handling
        if profile.get("is_imbalanced") and model_id == "xgboost":
            score += 15
        
        # General boosting preference for tabular data
        if model_id in ["xgboost", "lightgbm", "catboost"]:
            score += 10
        
        # Baseline models get slight penalty in ranking but still included
        if model_id in ["logistic_regression", "linear_regression"]:
            score -= 5
        
        return score
    
    def _generate_recommendation_reason(self, model_id: str) -> str:
        """Generate natural language reason for recommendation"""
        profile = self.data_profile
        reasons = []
        
        if model_id == "xgboost":
            if profile.get("is_imbalanced"):
                reasons.append("handles class imbalance well")
            if profile["has_missing"]:
                reasons.append("handles missing values natively")
            reasons.append("industry standard with best accuracy")
        
        elif model_id == "lightgbm":
            if profile["size_category"] == "large":
                reasons.append("optimized for large datasets")
            reasons.append("fastest training time")
            reasons.append("memory efficient")
        
        elif model_id == "catboost":
            if profile["categorical_columns"] > 3:
                reasons.append(f"native handling for your {profile['categorical_columns']} categorical columns")
            reasons.append("no manual encoding needed")
        
        elif model_id == "random_forest":
            reasons.append("robust and rarely overfits")
            reasons.append("provides feature importance")
            reasons.append("good for understanding data")
        
        elif model_id == "logistic_regression":
            reasons.append("fully interpretable coefficients")
            reasons.append("fast baseline for comparison")
            reasons.append("probabilistic predictions")
        
        elif model_id == "linear_regression":
            reasons.append("simple and fully explainable")
            reasons.append("good baseline model")
            reasons.append("easy to explain to stakeholders")
        
        return ", ".join(reasons[:3]).capitalize()
    
    def generate_chat_response(self) -> Dict[str, Any]:
        """Generate a chatbot-style response about data and recommendations"""
        profile = self.data_profile
        recommendations = self.get_recommendations(3)
        
        # Build data summary message
        data_summary = f"""I've analyzed your dataset. Here's what I found:

📊 **Dataset Overview**
• **{profile['rows']:,}** rows × **{profile['columns']}** columns
• **{profile['numeric_columns']}** numeric, **{profile['categorical_columns']}** categorical columns
• Memory usage: **{profile['memory_mb']} MB**
• Missing data: **{profile['missing_percentage']}%**"""

        if profile.get("target_column"):
            if profile["task_type"] == "classification":
                data_summary += f"""

🎯 **Target: {profile['target_column']}** (Classification)
• **{profile['num_classes']}** classes
• Majority class: **{profile['majority_class_pct']}%**
• {'⚠️ Imbalanced dataset detected' if profile.get('is_imbalanced') else '✅ Reasonably balanced'}"""
            else:
                data_summary += f"""

🎯 **Target: {profile['target_column']}** (Regression)
• Mean: **{profile['target_mean']}**, Std: **{profile['target_std']}**
• Skewness: **{profile['target_skewness']}**"""

        # Build recommendations message
        rec_message = "\n\n🤖 **Recommended Models**\n"
        for rec in recommendations:
            rec_message += f"\n{rec['rank']}. {rec['emoji']} **{rec['name']}**\n"
            rec_message += f"   _Why: {rec['why']}_\n"
        
        rec_message += "\n\nWould you like me to train any of these models?"
        
        return {
            "type": "analysis",
            "data_profile": profile,
            "recommendations": recommendations,
            "message": data_summary + rec_message,
            "actions": [
                {"label": f"Train {r['name']}", "action": "train", "model": r['id']}
                for r in recommendations
            ] + [
                {"label": "Compare All Models", "action": "compare", "model": None}
            ],
            "timestamp": datetime.now().isoformat()
        }
    
    def answer_question(self, question: str) -> Dict[str, Any]:
        """Answer user questions about data or models"""
        question_lower = question.lower()
        profile = self.data_profile
        
        # Data questions
        if any(kw in question_lower for kw in ["how many rows", "dataset size", "how big"]):
            answer = f"Your dataset has **{profile['rows']:,}** rows and **{profile['columns']}** columns."
        
        elif any(kw in question_lower for kw in ["missing", "null", "nan"]):
            answer = f"Your dataset has **{profile['missing_percentage']}%** missing values."
            if profile['has_missing']:
                answer += " I recommend using XGBoost, LightGBM, or CatBoost as they handle missing values natively."
        
        elif any(kw in question_lower for kw in ["categorical", "text column"]):
            answer = f"You have **{profile['categorical_columns']}** categorical columns."
            if profile['categorical_columns'] > 3:
                answer += " CatBoost would be ideal as it handles categorical features natively without encoding."
        
        elif any(kw in question_lower for kw in ["imbalance", "unbalanced", "class distribution"]):
            if profile.get('is_imbalanced'):
                answer = f"Yes, your data is imbalanced with a **{profile['imbalance_ratio']:.1f}:1** ratio. XGBoost with `scale_pos_weight` or SMOTE is recommended."
            else:
                answer = "Your classes appear reasonably balanced. Standard training should work well."
        
        # Model questions
        elif any(kw in question_lower for kw in ["which model", "best model", "recommend"]):
            recs = self.get_recommendations(1)
            answer = f"Based on your data, I recommend **{recs[0]['name']}** because: {recs[0]['why']}."
        
        elif "xgboost" in question_lower:
            answer = "**XGBoost** is the industry standard for tabular data. It handles missing values, provides feature importance, and consistently achieves top accuracy."
        
        elif "lightgbm" in question_lower:
            answer = "**LightGBM** is optimized for speed and memory efficiency. Best for large datasets or when you need fast iterations."
        
        elif "catboost" in question_lower:
            answer = "**CatBoost** excels at handling categorical features natively without manual encoding. Great if you have many text/category columns."
        
        elif any(kw in question_lower for kw in ["explain", "interpretable", "understand"]):
            answer = "For maximum interpretability, use **Logistic Regression** (classification) or **Linear Regression** (regression). Random Forest also provides good feature importance."
        
        else:
            answer = "I can help you understand your data and choose the right model. Try asking about:\n• Dataset size and missing values\n• Which model is best for your data\n• Specific model capabilities"
        
        return {
            "type": "answer",
            "question": question,
            "answer": answer,
            "timestamp": datetime.now().isoformat()
        }


def analyze_and_recommend(df: pd.DataFrame, target_column: str) -> Dict[str, Any]:
    """Helper function to analyze data and get recommendations"""
    recommender = ModelRecommender(df, target_column)
    return recommender.generate_chat_response()


def answer_model_question(df: pd.DataFrame, target_column: str, question: str) -> Dict[str, Any]:
    """Helper function to answer questions"""
    recommender = ModelRecommender(df, target_column)
    return recommender.answer_question(question)
