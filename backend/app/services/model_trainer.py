"""
Model Trainer Service
Trains ML models and generates performance metrics
"""
import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional, Tuple
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, confusion_matrix, classification_report,
    mean_squared_error, mean_absolute_error, r2_score
)
import json
from datetime import datetime
import uuid
import warnings
warnings.filterwarnings('ignore')


class ModelTrainer:
    """
    Unified model trainer supporting multiple algorithms
    for classification and regression tasks.
    """
    
    SUPPORTED_MODELS = {
        "classification": [
            "xgboost", "lightgbm", "catboost", "random_forest", 
            "logistic_regression", "gradient_boosting"
        ],
        "regression": [
            "xgboost", "lightgbm", "catboost", "random_forest",
            "linear_regression", "ridge", "lasso", "gradient_boosting"
        ]
    }
    
    def __init__(self, df: pd.DataFrame, target_column: str):
        self.df = df.copy()
        self.target_column = target_column
        self.task_type = self._detect_task_type()
        self.model = None
        self.model_name = None
        self.metrics = {}
        self.feature_importance = {}
        self.encoders = {}
        self.scaler = None
        self.training_id = str(uuid.uuid4())
        
    def _detect_task_type(self) -> str:
        """Detect if this is classification or regression"""
        target = self.df[self.target_column]
        
        # If object or category, it's classification
        if target.dtype == 'object' or target.dtype.name == 'category':
            return "classification"
        
        # If numeric with few unique values, likely classification
        unique_ratio = target.nunique() / len(target)
        if target.nunique() <= 20 and unique_ratio < 0.05:
            return "classification"
        
        return "regression"
    
    def _prepare_data(self) -> Tuple[pd.DataFrame, pd.Series]:
        """Prepare features and target"""
        X = self.df.drop(columns=[self.target_column])
        y = self.df[self.target_column]
        
        # Encode categorical target for classification
        if self.task_type == "classification" and y.dtype == 'object':
            le = LabelEncoder()
            y = pd.Series(le.fit_transform(y), name=self.target_column)
            self.encoders['target'] = le
        
        # Handle categorical features
        for col in X.select_dtypes(include=['object', 'category']).columns:
            le = LabelEncoder()
            X[col] = le.fit_transform(X[col].astype(str))
            self.encoders[col] = le
        
        # Fill missing values
        X = X.fillna(X.median(numeric_only=True))
        
        return X, y
    
    def _get_model(self, model_name: str):
        """Get model instance based on name"""
        
        if model_name == "xgboost":
            try:
                import xgboost as xgb
                if self.task_type == "classification":
                    return xgb.XGBClassifier(
                        n_estimators=100, max_depth=6, learning_rate=0.1,
                        use_label_encoder=False, eval_metric='logloss',
                        random_state=42
                    )
                else:
                    return xgb.XGBRegressor(
                        n_estimators=100, max_depth=6, learning_rate=0.1,
                        random_state=42
                    )
            except ImportError:
                raise ImportError("XGBoost not installed. Run: pip install xgboost")
        
        elif model_name == "lightgbm":
            try:
                import lightgbm as lgb
                if self.task_type == "classification":
                    return lgb.LGBMClassifier(
                        n_estimators=100, max_depth=6, learning_rate=0.1,
                        random_state=42, verbose=-1
                    )
                else:
                    return lgb.LGBMRegressor(
                        n_estimators=100, max_depth=6, learning_rate=0.1,
                        random_state=42, verbose=-1
                    )
            except ImportError:
                raise ImportError("LightGBM not installed. Run: pip install lightgbm")
        
        elif model_name == "catboost":
            try:
                from catboost import CatBoostClassifier, CatBoostRegressor
                if self.task_type == "classification":
                    return CatBoostClassifier(
                        iterations=100, depth=6, learning_rate=0.1,
                        random_state=42, verbose=False
                    )
                else:
                    return CatBoostRegressor(
                        iterations=100, depth=6, learning_rate=0.1,
                        random_state=42, verbose=False
                    )
            except ImportError:
                raise ImportError("CatBoost not installed. Run: pip install catboost")
        
        elif model_name == "random_forest":
            from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
            if self.task_type == "classification":
                return RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42)
            else:
                return RandomForestRegressor(n_estimators=100, max_depth=10, random_state=42)
        
        elif model_name == "gradient_boosting":
            from sklearn.ensemble import GradientBoostingClassifier, GradientBoostingRegressor
            if self.task_type == "classification":
                return GradientBoostingClassifier(n_estimators=100, max_depth=6, random_state=42)
            else:
                return GradientBoostingRegressor(n_estimators=100, max_depth=6, random_state=42)
        
        elif model_name == "logistic_regression":
            from sklearn.linear_model import LogisticRegression
            return LogisticRegression(max_iter=1000, random_state=42)
        
        elif model_name == "linear_regression":
            from sklearn.linear_model import LinearRegression
            return LinearRegression()
        
        elif model_name == "ridge":
            from sklearn.linear_model import Ridge
            return Ridge(alpha=1.0, random_state=42)
        
        elif model_name == "lasso":
            from sklearn.linear_model import Lasso
            return Lasso(alpha=1.0, random_state=42)
        
        else:
            raise ValueError(f"Unknown model: {model_name}")
    
    def train(self, model_name: str, test_size: float = 0.2) -> Dict[str, Any]:
        """Train a model and return results"""
        
        self.model_name = model_name
        X, y = self._prepare_data()
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=42
        )
        
        # Get and train model
        self.model = self._get_model(model_name)
        
        start_time = datetime.now()
        self.model.fit(X_train, y_train)
        training_time = (datetime.now() - start_time).total_seconds()
        
        # Predictions
        y_pred = self.model.predict(X_test)
        
        # Calculate metrics
        if self.task_type == "classification":
            self.metrics = self._calculate_classification_metrics(y_test, y_pred)
            # Probabilities for ROC
            if hasattr(self.model, 'predict_proba'):
                y_prob = self.model.predict_proba(X_test)
                if y_prob.shape[1] == 2:
                    self.metrics['roc_auc'] = round(roc_auc_score(y_test, y_prob[:, 1]), 4)
        else:
            self.metrics = self._calculate_regression_metrics(y_test, y_pred)
        
        # Feature importance
        self.feature_importance = self._get_feature_importance(X.columns.tolist())
        
        # Cross-validation score
        cv_scores = cross_val_score(
            self._get_model(model_name), X, y, cv=5,
            scoring='accuracy' if self.task_type == "classification" else 'r2'
        )
        
        # Store predictions for visualization
        self.y_test = y_test.values if hasattr(y_test, 'values') else y_test
        self.y_pred = y_pred
        
        return {
            "training_id": self.training_id,
            "model_name": model_name,
            "task_type": self.task_type,
            "training_time_seconds": round(training_time, 2),
            "test_size": test_size,
            "train_samples": len(X_train),
            "test_samples": len(X_test),
            "features_used": X.columns.tolist(),
            "metrics": self.metrics,
            "cv_scores": {
                "mean": round(cv_scores.mean(), 4),
                "std": round(cv_scores.std(), 4),
                "scores": cv_scores.tolist()
            },
            "feature_importance": self.feature_importance,
            "timestamp": datetime.now().isoformat()
        }
    
    def _calculate_classification_metrics(self, y_true, y_pred, y_prob=None) -> Dict:
        """Calculate comprehensive classification metrics"""
        from sklearn.metrics import (
            accuracy_score, precision_score, recall_score, f1_score,
            confusion_matrix, matthews_corrcoef, cohen_kappa_score,
            balanced_accuracy_score, log_loss
        )
        
        cm = confusion_matrix(y_true, y_pred)
        
        metrics = {
            # Basic metrics
            "accuracy": round(accuracy_score(y_true, y_pred), 4),
            "precision": round(precision_score(y_true, y_pred, average='weighted', zero_division=0), 4),
            "recall": round(recall_score(y_true, y_pred, average='weighted', zero_division=0), 4),
            "f1_score": round(f1_score(y_true, y_pred, average='weighted', zero_division=0), 4),
            
            # Advanced metrics
            "balanced_accuracy": round(balanced_accuracy_score(y_true, y_pred), 4),
            "mcc": round(matthews_corrcoef(y_true, y_pred), 4),  # Matthews Correlation Coefficient
            "cohen_kappa": round(cohen_kappa_score(y_true, y_pred), 4),
            
            # Per-class metrics
            "precision_macro": round(precision_score(y_true, y_pred, average='macro', zero_division=0), 4),
            "recall_macro": round(recall_score(y_true, y_pred, average='macro', zero_division=0), 4),
            "f1_macro": round(f1_score(y_true, y_pred, average='macro', zero_division=0), 4),
            
            # Confusion matrix
            "confusion_matrix": cm.tolist(),
            "true_positives": int(cm.diagonal().sum()),
            "total_samples": int(cm.sum())
        }
        
        # Binary classification specific
        if len(cm) == 2:
            tn, fp, fn, tp = cm.ravel()
            metrics["specificity"] = round(tn / (tn + fp) if (tn + fp) > 0 else 0, 4)
            metrics["sensitivity"] = round(tp / (tp + fn) if (tp + fn) > 0 else 0, 4)  # Same as recall
            metrics["npv"] = round(tn / (tn + fn) if (tn + fn) > 0 else 0, 4)  # Negative Predictive Value
            metrics["fpr"] = round(fp / (fp + tn) if (fp + tn) > 0 else 0, 4)  # False Positive Rate
            metrics["fnr"] = round(fn / (fn + tp) if (fn + tp) > 0 else 0, 4)  # False Negative Rate
        
        return metrics
    
    def _calculate_regression_metrics(self, y_true, y_pred) -> Dict:
        """Calculate comprehensive regression metrics"""
        from sklearn.metrics import (
            r2_score, mean_squared_error, mean_absolute_error,
            mean_absolute_percentage_error, explained_variance_score,
            max_error, median_absolute_error
        )
        
        # Basic metrics
        mse = mean_squared_error(y_true, y_pred)
        rmse = np.sqrt(mse)
        mae = mean_absolute_error(y_true, y_pred)
        
        # Avoid MAPE issues with zeros
        try:
            mape = mean_absolute_percentage_error(y_true, y_pred)
        except:
            mape = 0
        
        metrics = {
            # Core metrics
            "r2_score": round(r2_score(y_true, y_pred), 4),
            "adjusted_r2": round(1 - (1 - r2_score(y_true, y_pred)) * (len(y_true) - 1) / (len(y_true) - 1 - 1), 4),
            "mse": round(mse, 4),
            "rmse": round(rmse, 4),
            "mae": round(mae, 4),
            
            # Advanced metrics
            "mape": round(mape * 100, 2),  # As percentage
            "explained_variance": round(explained_variance_score(y_true, y_pred), 4),
            "max_error": round(float(max_error(y_true, y_pred)), 4),
            "median_ae": round(median_absolute_error(y_true, y_pred), 4),
            
            # Error statistics
            "residual_mean": round(float(np.mean(y_true - y_pred)), 4),
            "residual_std": round(float(np.std(y_true - y_pred)), 4),
            
            # Normalized metrics
            "nrmse": round(rmse / (np.max(y_true) - np.min(y_true)) if (np.max(y_true) - np.min(y_true)) > 0 else 0, 4),
            "cv_rmse": round(rmse / np.mean(y_true) if np.mean(y_true) > 0 else 0, 4)  # Coefficient of Variation RMSE
        }
        
        return metrics
    
    def _get_feature_importance(self, feature_names: List[str]) -> Dict:
        """Extract feature importance from trained model"""
        importance = {}
        
        if hasattr(self.model, 'feature_importances_'):
            importances = self.model.feature_importances_
            for name, imp in zip(feature_names, importances):
                importance[name] = round(float(imp), 4)
        elif hasattr(self.model, 'coef_'):
            coefs = self.model.coef_
            if len(coefs.shape) > 1:
                coefs = coefs[0]
            for name, coef in zip(feature_names, coefs):
                importance[name] = round(abs(float(coef)), 4)
        
        # Sort by importance
        importance = dict(sorted(importance.items(), key=lambda x: x[1], reverse=True))
        return importance
    
    def train_multiple(self, model_names: List[str] = None) -> List[Dict[str, Any]]:
        """Train multiple models for comparison"""
        if model_names is None:
            model_names = self.SUPPORTED_MODELS[self.task_type][:4]  # Top 4
        
        results = []
        for name in model_names:
            try:
                result = self.train(name)
                results.append(result)
            except Exception as e:
                results.append({
                    "model_name": name,
                    "error": str(e),
                    "status": "failed"
                })
        
        # Sort by primary metric
        if self.task_type == "classification":
            results.sort(key=lambda x: x.get("metrics", {}).get("accuracy", 0), reverse=True)
        else:
            results.sort(key=lambda x: x.get("metrics", {}).get("r2_score", 0), reverse=True)
        
        return results


def train_model_on_data(df: pd.DataFrame, target_column: str, model_name: str) -> Dict[str, Any]:
    """Helper function to train a single model"""
    trainer = ModelTrainer(df, target_column)
    return trainer.train(model_name)


def compare_models(df: pd.DataFrame, target_column: str, model_names: List[str] = None) -> List[Dict[str, Any]]:
    """Helper function to compare multiple models"""
    trainer = ModelTrainer(df, target_column)
    return trainer.train_multiple(model_names)
