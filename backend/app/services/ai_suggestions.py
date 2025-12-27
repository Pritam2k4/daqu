"""
AI Suggestions Service
Uses Groq or OpenAI to generate intelligent data fix suggestions
"""
from typing import Dict, Any, List
import json


class AISuggestionGenerator:
    """Generates AI-powered suggestions for data quality issues"""
    
    def __init__(self, use_groq: bool = True):
        self.use_groq = use_groq
        self.client = None
    
    def _initialize_client(self):
        """Initialize AI client (Groq or OpenAI)"""
        try:
            if self.use_groq:
                from groq import Groq
                from app.config import settings
                if settings.GROQ_API_KEY:
                    self.client = Groq(api_key=settings.GROQ_API_KEY)
            else:
                from openai import OpenAI
                from app.config import settings
                if settings.OPENAI_API_KEY:
                    self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        except Exception as e:
            print(f"AI client initialization failed: {e}")
            self.client = None
    
    def generate_suggestions(self, quality_report: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate suggestions based on quality report"""
        suggestions = []
        
        # 1. Missing value suggestions
        if quality_report.get("missing_values"):
            missing = quality_report["missing_values"]
            for col_info in missing.get("details", []):
                if col_info["missing_percent"] > 0:
                    suggestion = self._suggest_missing_fix(col_info)
                    suggestions.append(suggestion)
        
        # 2. Duplicate suggestions
        if quality_report.get("duplicates"):
            dups = quality_report["duplicates"]
            if dups.get("duplicate_rows", 0) > 0:
                suggestions.append(self._suggest_duplicate_fix(dups))
        
        # 3. Outlier suggestions
        if quality_report.get("outliers"):
            outliers = quality_report["outliers"]
            for col, data in outliers.get("details", {}).items():
                suggestions.append(self._suggest_outlier_fix(col, data))
        
        # 4. Type issue suggestions
        if quality_report.get("type_issues"):
            for issue in quality_report["type_issues"].get("details", []):
                suggestions.append(self._suggest_type_fix(issue))
        
        # 5. High correlation suggestions
        if quality_report.get("correlations"):
            for corr in quality_report["correlations"].get("high_correlations", [])[:3]:
                suggestions.append(self._suggest_correlation_fix(corr))
        
        return suggestions
    
    def _suggest_missing_fix(self, col_info: Dict) -> Dict:
        """Generate suggestion for missing values"""
        column = col_info["column"]
        missing_pct = col_info["missing_percent"]
        dtype = col_info.get("dtype", "object")
        
        if missing_pct > 50:
            fix_type = "drop_column"
            fix_description = f"Drop column '{column}' - over 50% missing"
            code_snippet = f"df = df.drop(columns=['{column}'])"
            confidence = 0.9
        elif "float" in dtype or "int" in dtype:
            fix_type = "impute_numeric"
            fix_description = f"Fill missing values in '{column}' with median"
            code_snippet = f"df['{column}'] = df['{column}'].fillna(df['{column}'].median())"
            confidence = 0.85
        else:
            fix_type = "impute_mode"
            fix_description = f"Fill missing values in '{column}' with most frequent value"
            code_snippet = f"df['{column}'] = df['{column}'].fillna(df['{column}'].mode()[0])"
            confidence = 0.8
        
        return {
            "id": f"missing_{column}",
            "issue_type": "missing_values",
            "column": column,
            "severity": "high" if missing_pct > 10 else "medium",
            "description": f"Column '{column}' has {missing_pct}% missing values",
            "suggested_fix": fix_description,
            "fix_type": fix_type,
            "code_snippet": code_snippet,
            "confidence": confidence,
            "impact": f"Will affect {col_info['missing_count']} rows"
        }
    
    def _suggest_duplicate_fix(self, dups: Dict) -> Dict:
        """Generate suggestion for duplicates"""
        return {
            "id": "duplicates",
            "issue_type": "duplicates",
            "column": None,
            "severity": "medium" if dups["duplicate_percent"] < 5 else "high",
            "description": f"Found {dups['duplicate_rows']} duplicate rows ({dups['duplicate_percent']}%)",
            "suggested_fix": "Remove duplicate rows, keeping first occurrence",
            "fix_type": "drop_duplicates",
            "code_snippet": "df = df.drop_duplicates(keep='first')",
            "confidence": 0.95,
            "impact": f"Will remove {dups['duplicate_rows']} rows"
        }
    
    def _suggest_outlier_fix(self, column: str, data: Dict) -> Dict:
        """Generate suggestion for outliers"""
        return {
            "id": f"outlier_{column}",
            "issue_type": "outliers",
            "column": column,
            "severity": "medium" if data["percent"] < 5 else "high",
            "description": f"Column '{column}' has {data['count']} outliers ({data['percent']}%)",
            "suggested_fix": f"Cap outliers to range [{data['lower_bound']}, {data['upper_bound']}]",
            "fix_type": "cap_outliers",
            "code_snippet": f"df['{column}'] = df['{column}'].clip(lower={data['lower_bound']}, upper={data['upper_bound']})",
            "confidence": 0.75,
            "impact": f"Will modify {data['count']} values"
        }
    
    def _suggest_type_fix(self, issue: Dict) -> Dict:
        """Generate suggestion for type issues"""
        column = issue["column"]
        suggested = issue["suggested_type"]
        
        if suggested == "datetime":
            code = f"df['{column}'] = pd.to_datetime(df['{column}'])"
        elif suggested == "numeric":
            code = f"df['{column}'] = pd.to_numeric(df['{column}'], errors='coerce')"
        elif suggested == "string":
            code = f"df['{column}'] = df['{column}'].astype(str)"
        else:
            code = f"# Convert '{column}' to {suggested}"
        
        return {
            "id": f"type_{column}",
            "issue_type": "type_mismatch",
            "column": column,
            "severity": "low",
            "description": issue["issue"],
            "suggested_fix": f"Convert '{column}' from {issue['current_type']} to {suggested}",
            "fix_type": "convert_type",
            "code_snippet": code,
            "confidence": 0.9,
            "impact": "Better data type handling"
        }
    
    def _suggest_correlation_fix(self, corr: Dict) -> Dict:
        """Generate suggestion for high correlations"""
        return {
            "id": f"corr_{corr['column1']}_{corr['column2']}",
            "issue_type": "high_correlation",
            "column": f"{corr['column1']}, {corr['column2']}",
            "severity": "low",
            "description": f"High correlation ({corr['correlation']}) between '{corr['column1']}' and '{corr['column2']}'",
            "suggested_fix": f"Consider dropping one column to reduce multicollinearity",
            "fix_type": "drop_correlated",
            "code_snippet": f"df = df.drop(columns=['{corr['column2']}'])  # Keep '{corr['column1']}'",
            "confidence": 0.6,
            "impact": "Reduces feature redundancy for ML models"
        }
    
    async def generate_ai_explanation(self, suggestion: Dict) -> str:
        """Use AI to generate detailed explanation (optional - requires API key)"""
        if not self.client:
            self._initialize_client()
        
        if not self.client:
            return suggestion.get("suggested_fix", "")
        
        try:
            prompt = f"""
            Given this data quality issue:
            - Issue: {suggestion['description']}
            - Suggested Fix: {suggestion['suggested_fix']}
            - Code: {suggestion['code_snippet']}
            
            Provide a brief (2-3 sentences) explanation of why this fix is recommended and any potential side effects.
            """
            
            response = self.client.chat.completions.create(
                model="llama-3.3-70b-versatile" if self.use_groq else "gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=150
            )
            
            return response.choices[0].message.content
        except Exception as e:
            print(f"AI explanation failed: {e}")
            return suggestion.get("suggested_fix", "")


def generate_suggestions_for_report(quality_report: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Helper function to generate suggestions"""
    generator = AISuggestionGenerator()
    return generator.generate_suggestions(quality_report)
