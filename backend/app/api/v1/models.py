from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import pandas as pd
from io import BytesIO
import os

from app.api.v1.quality import _temp_storage
from app.services.model_trainer import ModelTrainer, train_model_on_data, compare_models
from app.services.model_recommender import ModelRecommender, analyze_and_recommend, answer_model_question
from app.services.visualization_generator import generate_training_visualizations, generate_comparison_charts

router = APIRouter()

# Store for trained models and results
_model_storage = {}


class TrainRequest(BaseModel):
    source_id: str
    model_name: str
    target_column: str
    test_size: Optional[float] = 0.2


class CompareRequest(BaseModel):
    source_id: str
    target_column: str
    model_names: Optional[List[str]] = None


class ChatRequest(BaseModel):
    source_id: str
    target_column: str
    question: Optional[str] = None


@router.get("/supported")
async def get_supported_models():
    """Get list of supported models with info"""
    models = {
        "classification": [
            {"id": "xgboost", "name": "XGBoost", "emoji": "🚀", "description": "Industry standard gradient boosting"},
            {"id": "lightgbm", "name": "LightGBM", "emoji": "⚡", "description": "Fast and memory efficient"},
            {"id": "catboost", "name": "CatBoost", "emoji": "🐱", "description": "Native categorical handling"},
            {"id": "random_forest", "name": "Random Forest", "emoji": "🌲", "description": "Reliable ensemble"},
            {"id": "logistic_regression", "name": "Logistic Regression", "emoji": "📊", "description": "Interpretable baseline"},
            {"id": "gradient_boosting", "name": "Gradient Boosting", "emoji": "🔥", "description": "Sklearn boosting"}
        ],
        "regression": [
            {"id": "xgboost", "name": "XGBoost", "emoji": "🚀", "description": "Industry standard gradient boosting"},
            {"id": "lightgbm", "name": "LightGBM", "emoji": "⚡", "description": "Fast and memory efficient"},
            {"id": "catboost", "name": "CatBoost", "emoji": "🐱", "description": "Native categorical handling"},
            {"id": "random_forest", "name": "Random Forest", "emoji": "🌲", "description": "Reliable ensemble"},
            {"id": "linear_regression", "name": "Linear Regression", "emoji": "📈", "description": "Simple baseline"},
            {"id": "ridge", "name": "Ridge Regression", "emoji": "📉", "description": "Regularized linear"},
            {"id": "gradient_boosting", "name": "Gradient Boosting", "emoji": "🔥", "description": "Sklearn boosting"}
        ]
    }
    return {"status": "success", "models": models}


@router.post("/recommend")
async def get_model_recommendations(request: ChatRequest):
    """Get AI-powered model recommendations based on data analysis"""
    
    # Get data
    df = _get_dataframe(request.source_id)
    if df is None:
        raise HTTPException(status_code=404, detail="Data source not found")
    
    # Analyze and recommend
    result = analyze_and_recommend(df, request.target_column)
    
    return {
        "status": "success",
        "source_id": request.source_id,
        **result
    }


@router.post("/chat")
async def chat_with_assistant(request: ChatRequest):
    """Chat interface for model-related questions - now with LLM support"""
    
    # Get data
    df = _get_dataframe(request.source_id)
    if df is None:
        raise HTTPException(status_code=404, detail="Data source not found")
    
    # Get data profile and recommendations for context
    recommender = ModelRecommender(df, request.target_column)
    data_profile = recommender.data_profile
    recommendations = recommender.get_recommendations(3)
    
    if request.question:
        # Try LLM first
        try:
            from app.services.llm_chat import chat_with_llm, is_llm_available
            
            if is_llm_available():
                llm_response = chat_with_llm(
                    request.question,
                    data_profile,
                    recommendations
                )
                return {
                    "status": "success",
                    "source_id": request.source_id,
                    "type": "answer",
                    "question": request.question,
                    "answer": llm_response.get("answer", ""),
                    "provider": llm_response.get("provider", "unknown"),
                    "llm_enabled": True
                }
        except Exception as e:
            print(f"LLM error: {e}")
        
        # Fallback to rule-based
        result = answer_model_question(df, request.target_column, request.question)
        result["llm_enabled"] = False
    else:
        result = analyze_and_recommend(df, request.target_column)
        result["llm_enabled"] = False
    
    return {
        "status": "success",
        "source_id": request.source_id,
        **result
    }


@router.post("/train")
async def train_model(request: TrainRequest):
    """Train a specific model"""
    
    # Get data
    df = _get_dataframe(request.source_id)
    if df is None:
        raise HTTPException(status_code=404, detail="Data source not found")
    
    if request.target_column not in df.columns:
        raise HTTPException(status_code=400, detail=f"Target column '{request.target_column}' not found")
    
    try:
        # Train model
        trainer = ModelTrainer(df, request.target_column)
        results = trainer.train(request.model_name, request.test_size)
        
        # Generate visualizations
        charts = generate_training_visualizations(results)
        results["charts"] = {k: v.get("base64") for k, v in charts.items()}
        
        # Store results
        training_id = results["training_id"]
        _model_storage[training_id] = {
            "results": results,
            "trainer": trainer,
            "charts": charts
        }
        
        return {
            "status": "success",
            "training_id": training_id,
            "results": results
        }
    except ImportError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/compare")
async def compare_multiple_models(request: CompareRequest):
    """Train and compare multiple models"""
    
    # Get data
    df = _get_dataframe(request.source_id)
    if df is None:
        raise HTTPException(status_code=404, detail="Data source not found")
    
    if request.target_column not in df.columns:
        raise HTTPException(status_code=400, detail=f"Target column '{request.target_column}' not found")
    
    try:
        # Compare models
        results = compare_models(df, request.target_column, request.model_names)
        
        # Generate comparison charts
        charts = generate_comparison_charts(results)
        
        # Find best model
        successful_results = [r for r in results if 'metrics' in r and 'error' not in r]
        task_type = successful_results[0]['task_type'] if successful_results else 'classification'
        
        if task_type == 'classification':
            best = max(successful_results, key=lambda x: x['metrics'].get('accuracy', 0))
        else:
            best = max(successful_results, key=lambda x: x['metrics'].get('r2_score', 0))
        
        return {
            "status": "success",
            "source_id": request.source_id,
            "task_type": task_type,
            "models_trained": len(successful_results),
            "best_model": {
                "name": best["model_name"],
                "metrics": best["metrics"]
            },
            "results": results,
            "comparison_chart": charts.get("comparison", {}).get("base64")
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/results/{training_id}")
async def get_training_results(training_id: str):
    """Get results for a specific training run"""
    
    if training_id not in _model_storage:
        raise HTTPException(status_code=404, detail="Training results not found")
    
    stored = _model_storage[training_id]
    return {
        "status": "success",
        "training_id": training_id,
        "results": stored["results"]
    }


@router.get("/chart/{training_id}/{chart_type}")
async def get_chart(training_id: str, chart_type: str):
    """Get a specific chart for a training run"""
    
    if training_id not in _model_storage:
        raise HTTPException(status_code=404, detail="Training results not found")
    
    charts = _model_storage[training_id].get("charts", {})
    
    if chart_type not in charts:
        raise HTTPException(status_code=404, detail=f"Chart '{chart_type}' not found")
    
    return {
        "status": "success",
        "chart_type": chart_type,
        "chart": charts[chart_type]
    }


@router.get("/demo-analysis")
async def get_demo_model_analysis():
    """Get demo model analysis for testing"""
    
    return {
        "status": "success",
        "type": "analysis",
        "data_profile": {
            "rows": 10000,
            "columns": 14,
            "numeric_columns": 6,
            "categorical_columns": 7,
            "datetime_columns": 1,
            "missing_percentage": 4.5,
            "has_missing": True,
            "target_column": "churn",
            "task_type": "classification",
            "num_classes": 2,
            "imbalance_ratio": 2.7,
            "is_imbalanced": False,
            "majority_class_pct": 73.0,
            "size_category": "medium"
        },
        "recommendations": [
            {
                "id": "xgboost",
                "name": "XGBoost",
                "emoji": "🚀",
                "rank": 1,
                "score": 85,
                "why": "Handles missing values natively, industry standard with best accuracy, great for classification"
            },
            {
                "id": "lightgbm",
                "name": "LightGBM",
                "emoji": "⚡",
                "rank": 2,
                "score": 75,
                "why": "Fastest training time, memory efficient, handles large datasets well"
            },
            {
                "id": "catboost",
                "name": "CatBoost",
                "emoji": "🐱",
                "rank": 3,
                "score": 70,
                "why": "Native handling for your 7 categorical columns, no manual encoding needed"
            }
        ],
        "message": """I've analyzed your dataset. Here's what I found:

📊 **Dataset Overview**
• **10,000** rows × **14** columns
• **6** numeric, **7** categorical columns
• Memory usage: **1.45 MB**
• Missing data: **4.5%**

🎯 **Target: churn** (Classification)
• **2** classes
• Majority class: **73.0%**
• ✅ Reasonably balanced

🤖 **Recommended Models**

1. 🚀 **XGBoost**
   _Why: Handles missing values natively, industry standard with best accuracy_

2. ⚡ **LightGBM**
   _Why: Fastest training time, memory efficient_

3. 🐱 **CatBoost**
   _Why: Native handling for your 7 categorical columns_

Would you like me to train any of these models?""",
        "actions": [
            {"label": "Train XGBoost", "action": "train", "model": "xgboost"},
            {"label": "Train LightGBM", "action": "train", "model": "lightgbm"},
            {"label": "Train CatBoost", "action": "train", "model": "catboost"},
            {"label": "Compare All Models", "action": "compare", "model": None}
        ]
    }


def _get_dataframe(source_id: str) -> Optional[pd.DataFrame]:
    """Get DataFrame from storage or demo data"""
    
    # Check if exists in temp storage
    if source_id in _temp_storage:
        report = _temp_storage[source_id]
        if 'dataframe' in report:
            return report['dataframe']
        # Try to reconstruct from sample data
        if 'sample_data' in report:
            return pd.DataFrame(report['sample_data'])
    
    # Return demo data for testing
    if source_id == "demo":
        return _create_demo_dataframe()
    
    return None


def _create_demo_dataframe() -> pd.DataFrame:
    """Create demo dataframe for testing"""
    import numpy as np
    
    np.random.seed(42)
    n = 1000
    
    df = pd.DataFrame({
        'customer_id': range(1, n+1),
        'age': np.random.randint(18, 70, n),
        'tenure_months': np.random.randint(0, 72, n),
        'monthly_charges': np.random.uniform(20, 120, n),
        'total_charges': np.random.uniform(100, 8000, n),
        'support_tickets': np.random.randint(0, 12, n),
        'gender': np.random.choice(['Male', 'Female'], n),
        'contract_type': np.random.choice(['Month-to-month', 'One year', 'Two year'], n),
        'payment_method': np.random.choice(['Credit card', 'Bank transfer', 'Electronic check', 'Mailed check'], n),
        'churn': np.random.choice(['Yes', 'No'], n, p=[0.27, 0.73])
    })
    
    # Add some missing values
    for col in ['age', 'total_charges']:
        mask = np.random.random(n) < 0.03
        df.loc[mask, col] = np.nan
    
    return df
