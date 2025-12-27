"""
Visualization Generator Service
Creates matplotlib charts and saves them for frontend display
"""
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd
from typing import Dict, Any, List, Optional
import os
import io
import base64
from datetime import datetime
import uuid


class VisualizationGenerator:
    """
    Generates ML visualizations using matplotlib/seaborn.
    Saves as base64 or files for frontend display.
    """
    
    # Chart style configuration
    STYLE_CONFIG = {
        'figure.facecolor': '#09090b',
        'axes.facecolor': '#18181b',
        'axes.edgecolor': '#3f3f46',
        'axes.labelcolor': '#a1a1aa',
        'text.color': '#fafafa',
        'xtick.color': '#a1a1aa',
        'ytick.color': '#a1a1aa',
        'grid.color': '#27272a',
        'legend.facecolor': '#18181b',
        'legend.edgecolor': '#3f3f46'
    }
    
    COLORS = {
        'primary': '#a855f7',
        'secondary': '#8b5cf6',
        'success': '#22c55e',
        'warning': '#f59e0b',
        'danger': '#ef4444',
        'info': '#3b82f6',
        'gradient': ['#a855f7', '#8b5cf6', '#6366f1', '#3b82f6', '#22c55e']
    }
    
    def __init__(self, output_dir: str = None):
        self.output_dir = output_dir or "static/charts"
        os.makedirs(self.output_dir, exist_ok=True)
        plt.rcParams.update(self.STYLE_CONFIG)
        sns.set_style("darkgrid")
    
    def _save_figure(self, fig, name: str) -> Dict[str, str]:
        """Save figure and return paths/base64"""
        # Generate unique filename
        filename = f"{name}_{uuid.uuid4().hex[:8]}.png"
        filepath = os.path.join(self.output_dir, filename)
        
        # Save to file
        fig.savefig(filepath, dpi=150, bbox_inches='tight', facecolor='#09090b')
        
        # Also get base64
        buffer = io.BytesIO()
        fig.savefig(buffer, format='png', dpi=150, bbox_inches='tight', facecolor='#09090b')
        buffer.seek(0)
        base64_img = base64.b64encode(buffer.getvalue()).decode()
        
        plt.close(fig)
        
        return {
            "filename": filename,
            "filepath": filepath,
            "base64": f"data:image/png;base64,{base64_img}"
        }
    
    def confusion_matrix_chart(self, cm: List[List[int]], labels: List[str] = None) -> Dict:
        """Generate confusion matrix heatmap"""
        fig, ax = plt.subplots(figsize=(8, 6))
        
        cm_array = np.array(cm)
        sns.heatmap(
            cm_array, annot=True, fmt='d', cmap='Purples',
            xticklabels=labels or [f'Class {i}' for i in range(len(cm))],
            yticklabels=labels or [f'Class {i}' for i in range(len(cm))],
            ax=ax
        )
        
        ax.set_xlabel('Predicted', fontsize=12)
        ax.set_ylabel('Actual', fontsize=12)
        ax.set_title('Confusion Matrix', fontsize=14, fontweight='bold')
        
        return self._save_figure(fig, 'confusion_matrix')
    
    def feature_importance_chart(self, importance: Dict[str, float], top_n: int = 15) -> Dict:
        """Generate feature importance bar chart"""
        # Sort and get top N
        sorted_imp = sorted(importance.items(), key=lambda x: x[1], reverse=True)[:top_n]
        features = [x[0] for x in sorted_imp][::-1]
        values = [x[1] for x in sorted_imp][::-1]
        
        fig, ax = plt.subplots(figsize=(10, 8))
        
        # Create gradient colors
        colors = plt.cm.Purples(np.linspace(0.4, 0.9, len(features)))
        
        bars = ax.barh(features, values, color=colors)
        
        ax.set_xlabel('Importance Score', fontsize=12)
        ax.set_title('Feature Importance', fontsize=14, fontweight='bold')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        
        # Add value labels
        for bar, val in zip(bars, values):
            ax.text(val + 0.01, bar.get_y() + bar.get_height()/2, 
                   f'{val:.3f}', va='center', fontsize=9, color='white')
        
        plt.tight_layout()
        return self._save_figure(fig, 'feature_importance')
    
    def metrics_comparison_chart(self, results: List[Dict]) -> Dict:
        """Compare metrics across multiple models"""
        model_names = [r['model_name'] for r in results if 'metrics' in r]
        
        if not model_names:
            return {"error": "No valid results to plot"}
        
        task_type = results[0].get('task_type', 'classification')
        
        fig, ax = plt.subplots(figsize=(12, 6))
        
        if task_type == 'classification':
            metrics = ['accuracy', 'precision', 'recall', 'f1_score']
        else:
            metrics = ['r2_score', 'rmse', 'mae']
        
        x = np.arange(len(model_names))
        width = 0.8 / len(metrics)
        
        colors = self.COLORS['gradient'][:len(metrics)]
        
        for i, metric in enumerate(metrics):
            values = [r.get('metrics', {}).get(metric, 0) for r in results if 'metrics' in r]
            bars = ax.bar(x + i * width, values, width, label=metric.replace('_', ' ').title(), color=colors[i])
        
        ax.set_xlabel('Model', fontsize=12)
        ax.set_ylabel('Score', fontsize=12)
        ax.set_title('Model Comparison', fontsize=14, fontweight='bold')
        ax.set_xticks(x + width * (len(metrics) - 1) / 2)
        ax.set_xticklabels([name.replace('_', ' ').title() for name in model_names], rotation=15)
        ax.legend(loc='upper right')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        
        plt.tight_layout()
        return self._save_figure(fig, 'model_comparison')
    
    def actual_vs_predicted_chart(self, y_actual: np.ndarray, y_predicted: np.ndarray) -> Dict:
        """Scatter plot of actual vs predicted (for regression)"""
        fig, ax = plt.subplots(figsize=(8, 8))
        
        ax.scatter(y_actual, y_predicted, alpha=0.5, color=self.COLORS['primary'], s=50)
        
        # Perfect prediction line
        min_val = min(y_actual.min(), y_predicted.min())
        max_val = max(y_actual.max(), y_predicted.max())
        ax.plot([min_val, max_val], [min_val, max_val], 'r--', linewidth=2, label='Perfect Prediction')
        
        ax.set_xlabel('Actual Values', fontsize=12)
        ax.set_ylabel('Predicted Values', fontsize=12)
        ax.set_title('Actual vs Predicted', fontsize=14, fontweight='bold')
        ax.legend()
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        
        plt.tight_layout()
        return self._save_figure(fig, 'actual_vs_predicted')
    
    def residual_distribution_chart(self, y_actual: np.ndarray, y_predicted: np.ndarray) -> Dict:
        """Histogram of residuals (for regression)"""
        residuals = y_actual - y_predicted
        
        fig, ax = plt.subplots(figsize=(10, 6))
        
        ax.hist(residuals, bins=50, color=self.COLORS['primary'], alpha=0.7, edgecolor='white')
        ax.axvline(0, color=self.COLORS['danger'], linestyle='--', linewidth=2, label='Zero Line')
        
        ax.set_xlabel('Residual (Actual - Predicted)', fontsize=12)
        ax.set_ylabel('Frequency', fontsize=12)
        ax.set_title('Residual Distribution', fontsize=14, fontweight='bold')
        ax.legend()
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        
        plt.tight_layout()
        return self._save_figure(fig, 'residual_distribution')
    
    def cv_scores_chart(self, cv_scores: List[float], model_name: str) -> Dict:
        """Cross-validation scores visualization"""
        fig, ax = plt.subplots(figsize=(10, 5))
        
        folds = [f'Fold {i+1}' for i in range(len(cv_scores))]
        colors = [self.COLORS['primary'] if score >= np.mean(cv_scores) else self.COLORS['secondary'] 
                  for score in cv_scores]
        
        bars = ax.bar(folds, cv_scores, color=colors, edgecolor='white', alpha=0.8)
        
        # Add mean line
        mean_score = np.mean(cv_scores)
        ax.axhline(mean_score, color=self.COLORS['warning'], linestyle='--', 
                   linewidth=2, label=f'Mean: {mean_score:.3f}')
        
        ax.set_xlabel('Fold', fontsize=12)
        ax.set_ylabel('Score', fontsize=12)
        ax.set_title(f'Cross-Validation Scores - {model_name}', fontsize=14, fontweight='bold')
        ax.legend()
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        
        # Add value labels
        for bar, score in zip(bars, cv_scores):
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01,
                   f'{score:.3f}', ha='center', fontsize=10, color='white')
        
        plt.tight_layout()
        return self._save_figure(fig, 'cv_scores')
    
    def training_summary_chart(self, results: Dict) -> Dict:
        """Summary dashboard chart for a single model"""
        fig = plt.figure(figsize=(14, 10))
        
        # Create grid
        gs = fig.add_gridspec(2, 3, hspace=0.3, wspace=0.3)
        
        metrics = results.get('metrics', {})
        task_type = results.get('task_type', 'classification')
        
        # 1. Metrics radar/bar
        ax1 = fig.add_subplot(gs[0, 0])
        if task_type == 'classification':
            metric_names = ['Accuracy', 'Precision', 'Recall', 'F1']
            metric_values = [metrics.get('accuracy', 0), metrics.get('precision', 0),
                           metrics.get('recall', 0), metrics.get('f1_score', 0)]
        else:
            metric_names = ['R² Score', 'RMSE', 'MAE']
            metric_values = [metrics.get('r2_score', 0), 
                           1 - min(metrics.get('rmse', 0) / 100, 1),  # Normalized
                           1 - min(metrics.get('mae', 0) / 100, 1)]   # Normalized
        
        colors = [self.COLORS['gradient'][i] for i in range(len(metric_names))]
        ax1.barh(metric_names, metric_values, color=colors)
        ax1.set_xlim(0, 1)
        ax1.set_title('Performance Metrics', fontweight='bold')
        
        # 2. Feature importance (top 5)
        ax2 = fig.add_subplot(gs[0, 1:])
        importance = results.get('feature_importance', {})
        if importance:
            top_features = list(importance.items())[:8]
            features = [f[0][:15] + '...' if len(f[0]) > 15 else f[0] for f in top_features][::-1]
            values = [f[1] for f in top_features][::-1]
            ax2.barh(features, values, color=self.COLORS['primary'])
        ax2.set_title('Top Feature Importance', fontweight='bold')
        
        # 3. CV Scores
        ax3 = fig.add_subplot(gs[1, 0])
        cv = results.get('cv_scores', {})
        if cv.get('scores'):
            ax3.bar(range(len(cv['scores'])), cv['scores'], color=self.COLORS['secondary'])
            ax3.axhline(cv['mean'], color='red', linestyle='--', label=f'Mean: {cv["mean"]:.3f}')
            ax3.legend()
        ax3.set_title('Cross-Validation', fontweight='bold')
        ax3.set_xlabel('Fold')
        
        # 4. Confusion matrix or residuals
        ax4 = fig.add_subplot(gs[1, 1])
        if task_type == 'classification' and 'confusion_matrix' in metrics:
            cm = np.array(metrics['confusion_matrix'])
            sns.heatmap(cm, annot=True, fmt='d', cmap='Purples', ax=ax4)
            ax4.set_title('Confusion Matrix', fontweight='bold')
        else:
            ax4.text(0.5, 0.5, f"R² = {metrics.get('r2_score', 'N/A')}\nRMSE = {metrics.get('rmse', 'N/A')}",
                    ha='center', va='center', fontsize=16, transform=ax4.transAxes)
            ax4.set_title('Regression Metrics', fontweight='bold')
        
        # 5. Model info
        ax5 = fig.add_subplot(gs[1, 2])
        ax5.axis('off')
        info_text = f"""
Model: {results.get('model_name', '').replace('_', ' ').title()}
Task: {task_type.title()}
Training Time: {results.get('training_time_seconds', 0)}s
Train Samples: {results.get('train_samples', 0)}
Test Samples: {results.get('test_samples', 0)}
Features: {len(results.get('features_used', []))}
CV Mean: {cv.get('mean', 'N/A')}
        """
        ax5.text(0.1, 0.9, info_text, transform=ax5.transAxes, fontsize=11,
                verticalalignment='top', fontfamily='monospace',
                bbox=dict(boxstyle='round', facecolor='#27272a', alpha=0.8))
        ax5.set_title('Model Summary', fontweight='bold')
        
        fig.suptitle(f"Training Results - {results.get('model_name', '').replace('_', ' ').title()}", 
                    fontsize=16, fontweight='bold', y=1.02)
        
        return self._save_figure(fig, 'training_summary')


# Helper functions
def generate_training_visualizations(results: Dict) -> Dict[str, Dict]:
    """Generate all relevant visualizations for training results"""
    viz = VisualizationGenerator()
    charts = {}
    
    # Feature importance
    if results.get('feature_importance'):
        charts['feature_importance'] = viz.feature_importance_chart(results['feature_importance'])
    
    # CV scores
    if results.get('cv_scores', {}).get('scores'):
        charts['cv_scores'] = viz.cv_scores_chart(
            results['cv_scores']['scores'], 
            results.get('model_name', 'Model')
        )
    
    # Confusion matrix (classification)
    if results.get('metrics', {}).get('confusion_matrix'):
        charts['confusion_matrix'] = viz.confusion_matrix_chart(
            results['metrics']['confusion_matrix']
        )
    
    # Training summary
    charts['summary'] = viz.training_summary_chart(results)
    
    return charts


def generate_comparison_charts(results: List[Dict]) -> Dict[str, Dict]:
    """Generate comparison charts for multiple models"""
    viz = VisualizationGenerator()
    return {
        'comparison': viz.metrics_comparison_chart(results)
    }
