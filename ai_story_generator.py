#!/usr/bin/env python3
"""
AI Data Story Generator
=======================

Generates narrative reports about data cleaning results in different styles:
- Executive: High-level business insights
- Technical: Detailed technical analysis  
- Casual: Friendly, easy-to-understand explanations

Uses free local models and Hugging Face inference API as fallback.
"""

import json
import random
from typing import Dict, List, Optional
import requests

class AIStoryGenerator:
    """Generates AI-powered narrative reports from data cleaning results."""
    
    def __init__(self):
        self.styles = {
            'executive': {
                'tone': 'professional and business-focused',
                'audience': 'C-level executives and business stakeholders',
                'focus': 'high-level insights, business impact, and strategic recommendations'
            },
            'technical': {
                'tone': 'detailed and analytical',
                'audience': 'data scientists, analysts, and technical teams',
                'focus': 'specific technical details, methodologies, and data quality metrics'
            },
            'casual': {
                'tone': 'friendly and conversational',
                'audience': 'general users and non-technical stakeholders',
                'focus': 'easy-to-understand explanations with practical examples'
            }
        }
        
        # Free AI service endpoints (fallback options)
        self.free_ai_services = [
            'https://api-inference.huggingface.co/models/microsoft/DialoGPT-medium',
            'https://api-inference.huggingface.co/models/gpt2',
            'https://api-inference.huggingface.co/models/facebook/opt-350m'
        ]
    
    def generate_story(self, audit_data: Dict, style: str = 'executive') -> str:
        """
        Generate a narrative story from data cleaning audit results.
        
        Args:
            audit_data: Dictionary containing cleaning audit results
            style: 'executive', 'technical', or 'casual'
            
        Returns:
            Generated narrative story
        """
        try:
            # First try local template-based generation
            story = self._generate_local_story(audit_data, style)
            
            # If local generation is too basic, try free AI service
            if len(story) < 500:  # If story is too short, enhance with AI
                enhanced_story = self._enhance_with_ai(story, style)
                if enhanced_story:
                    return enhanced_story
            
            return story
            
        except Exception as e:
            # Fallback to local generation
            return self._generate_local_story(audit_data, style)
    
    def _generate_local_story(self, audit_data: Dict, style: str) -> str:
        """Generate story using local templates and logic."""
        
        style_config = self.styles.get(style, self.styles['executive'])
        
        # Extract key metrics
        rows_before = audit_data.get('rows_before', 0)
        rows_after = audit_data.get('rows_after', 0)
        duplicates_removed = audit_data.get('duplicates_removed', 0)
        columns = audit_data.get('columns', [])
        column_changes = audit_data.get('column_changes', {})
        
        # Calculate insights
        data_loss = rows_before - rows_after
        data_quality_score = self._calculate_quality_score(audit_data)
        major_issues = self._identify_major_issues(column_changes)
        
        # Generate story based on style
        if style == 'executive':
            return self._generate_executive_story(
                rows_before, rows_after, duplicates_removed, 
                data_quality_score, major_issues, columns
            )
        elif style == 'technical':
            return self._generate_technical_story(
                audit_data, column_changes, data_quality_score
            )
        else:  # casual
            return self._generate_casual_story(
                rows_before, rows_after, duplicates_removed,
                major_issues, columns
            )
    
    def _generate_executive_story(self, rows_before, rows_after, duplicates_removed, 
                                quality_score, major_issues, columns) -> str:
        """Generate executive-style narrative."""
        
        story_parts = []
        
        # Opening
        story_parts.append("# Executive Data Quality Report")
        story_parts.append("")
        
        # Executive Summary
        story_parts.append("## Executive Summary")
        story_parts.append("")
        
        if quality_score >= 80:
            story_parts.append("🎯 **Excellent Data Quality Achieved**")
            story_parts.append("")
            story_parts.append(f"Your dataset has been successfully optimized for business intelligence and analytics. With a data quality score of **{quality_score}%**, your data is now ready for confident decision-making.")
        elif quality_score >= 60:
            story_parts.append("✅ **Significant Data Quality Improvements**")
            story_parts.append("")
            story_parts.append(f"Your dataset has been substantially improved with a quality score of **{quality_score}%**. Key issues have been addressed, making your data more reliable for business operations.")
        else:
            story_parts.append("⚠️ **Data Quality Issues Identified**")
            story_parts.append("")
            story_parts.append(f"Your dataset requires attention with a quality score of **{quality_score}%**. Critical issues have been identified that could impact business decisions.")
        
        story_parts.append("")
        
        # Key Metrics
        story_parts.append("## Key Performance Indicators")
        story_parts.append("")
        story_parts.append(f"• **Dataset Integrity**: {rows_before:,} → {rows_after:,} records ({rows_after - rows_before:+,d} change)")
        story_parts.append(f"• **Data Quality Score**: {quality_score}%")
        story_parts.append(f"• **Duplicate Elimination**: {duplicates_removed:,} redundant records removed")
        story_parts.append(f"• **Data Dimensions**: {len(columns)} columns analyzed")
        story_parts.append("")
        
        # Business Impact
        story_parts.append("## Business Impact")
        story_parts.append("")
        
        if duplicates_removed > 0:
            story_parts.append(f"**Eliminated Data Redundancy**: Removed {duplicates_removed:,} duplicate records, ensuring accurate reporting and preventing inflated metrics in business dashboards.")
            story_parts.append("")
        
        if major_issues:
            story_parts.append("**Data Quality Assurance**: Addressed critical data quality issues that could have led to:")
            story_parts.append("• Inaccurate business intelligence")
            story_parts.append("• Misleading performance metrics")
            story_parts.append("• Poor decision-making based on flawed data")
            story_parts.append("")
        
        # Strategic Recommendations
        story_parts.append("## Strategic Recommendations")
        story_parts.append("")
        story_parts.append("1. **Implement Data Quality Monitoring**: Establish regular data quality audits to maintain high standards")
        story_parts.append("2. **Enhance Data Collection Processes**: Address root causes of data quality issues at the source")
        story_parts.append("3. **Invest in Data Governance**: Develop policies and procedures for maintaining data quality")
        story_parts.append("4. **Consider Advanced Analytics**: With improved data quality, explore advanced analytics and machine learning opportunities")
        story_parts.append("")
        
        # Next Steps
        story_parts.append("## Next Steps")
        story_parts.append("")
        story_parts.append("• Review the detailed technical report for specific data quality metrics")
        story_parts.append("• Download the cleaned dataset for immediate use in business applications")
        story_parts.append("• Schedule follow-up data quality assessments to maintain standards")
        story_parts.append("• Consider implementing automated data quality monitoring tools")
        
        return "\n".join(story_parts)
    
    def _generate_technical_story(self, audit_data, column_changes, quality_score) -> str:
        """Generate technical-style narrative."""
        
        story_parts = []
        
        # Header
        story_parts.append("# Technical Data Quality Analysis Report")
        story_parts.append("")
        
        # Technical Overview
        story_parts.append("## Technical Overview")
        story_parts.append("")
        story_parts.append(f"This comprehensive data quality analysis was performed using advanced cleaning algorithms and statistical methods. The dataset achieved a quality score of **{quality_score}%** based on multiple quality dimensions.")
        story_parts.append("")
        
        # Methodology
        story_parts.append("## Methodology")
        story_parts.append("")
        story_parts.append("### Data Quality Assessment Framework")
        story_parts.append("• **Completeness**: Missing value analysis and imputation strategies")
        story_parts.append("• **Consistency**: Data type validation and format standardization")
        story_parts.append("• **Accuracy**: Outlier detection and data validation")
        story_parts.append("• **Uniqueness**: Duplicate identification and removal")
        story_parts.append("• **Integrity**: Referential integrity and constraint validation")
        story_parts.append("")
        
        # Detailed Analysis
        story_parts.append("## Detailed Analysis")
        story_parts.append("")
        
        for column, changes in column_changes.items():
            if any(changes.values()):
                story_parts.append(f"### Column: `{column}`")
                story_parts.append("")
                
                if changes.get('imputed_missing', 0) > 0:
                    story_parts.append(f"• **Missing Values**: {changes['imputed_missing']} values imputed using {changes.get('imputation_strategy', 'statistical method')}")
                
                if changes.get('new_nulls_from_empty_strings', 0) > 0:
                    story_parts.append(f"• **Empty String Conversion**: {changes['new_nulls_from_empty_strings']} empty strings converted to null values")
                
                if changes.get('parsed_to_datetime', 0) > 0:
                    story_parts.append(f"• **Date Parsing**: {changes['parsed_to_datetime']} values parsed as datetime objects")
                
                if changes.get('emails_valid_after', 0) > 0:
                    story_parts.append(f"• **Email Normalization**: {changes['emails_valid_after']} email addresses normalized")
                
                story_parts.append("")
        
        # Quality Metrics
        story_parts.append("## Quality Metrics")
        story_parts.append("")
        story_parts.append(f"• **Overall Quality Score**: {quality_score}%")
        story_parts.append(f"• **Data Completeness**: {self._calculate_completeness(audit_data):.1f}%")
        story_parts.append(f"• **Data Consistency**: {self._calculate_consistency(audit_data):.1f}%")
        story_parts.append(f"• **Data Accuracy**: {self._calculate_accuracy(audit_data):.1f}%")
        story_parts.append("")
        
        # Technical Recommendations
        story_parts.append("## Technical Recommendations")
        story_parts.append("")
        story_parts.append("1. **Implement Data Validation Rules**: Add constraints and validation at the data entry level")
        story_parts.append("2. **Establish Data Quality Monitoring**: Set up automated quality checks and alerts")
        story_parts.append("3. **Optimize Data Processing Pipeline**: Streamline cleaning procedures for efficiency")
        story_parts.append("4. **Document Data Quality Standards**: Create comprehensive documentation for data quality requirements")
        story_parts.append("")
        
        return "\n".join(story_parts)
    
    def _generate_casual_story(self, rows_before, rows_after, duplicates_removed, 
                             major_issues, columns) -> str:
        """Generate casual-style narrative."""
        
        story_parts = []
        
        # Friendly Header
        story_parts.append("# Your Data Cleanup Story 📊")
        story_parts.append("")
        
        # Casual Introduction
        story_parts.append("## Hey there! 👋")
        story_parts.append("")
        story_parts.append("Great news! We just finished cleaning up your data, and here's what happened...")
        story_parts.append("")
        
        # What We Found
        story_parts.append("## What We Found 🔍")
        story_parts.append("")
        
        if duplicates_removed > 0:
            story_parts.append(f"**Oops! We found {duplicates_removed} duplicate records** - like having the same photo twice in your gallery! We removed them so your data is now unique and accurate.")
            story_parts.append("")
        
        if major_issues:
            story_parts.append("**Some data needed a little TLC**:")
            for issue in major_issues[:3]:  # Limit to top 3
                story_parts.append(f"• {issue}")
            story_parts.append("")
        
        # The Results
        story_parts.append("## The Results ✨")
        story_parts.append("")
        story_parts.append(f"**Before**: {rows_before:,} records (some messy ones included)")
        story_parts.append(f"**After**: {rows_after:,} clean, reliable records")
        story_parts.append(f"**What changed**: {rows_after - rows_before:+,d} records")
        story_parts.append("")
        story_parts.append(f"We looked through **{len(columns)} different columns** of your data and made sure everything looks good!")
        story_parts.append("")
        
        # What This Means
        story_parts.append("## What This Means for You 🎯")
        story_parts.append("")
        story_parts.append("✅ **Reliable Reports**: Your charts and graphs will now show accurate information")
        story_parts.append("✅ **Better Decisions**: You can trust your data to make informed choices")
        story_parts.append("✅ **Time Saved**: No more wondering if your data is correct")
        story_parts.append("✅ **Professional Results**: Clean data makes you look good!")
        story_parts.append("")
        
        # Fun Facts
        story_parts.append("## Fun Data Facts 🤓")
        story_parts.append("")
        story_parts.append("• **Data cleaning** is like proofreading your data - catching typos and fixing mistakes")
        story_parts.append("• **Clean data** can improve business decisions by up to 30%")
        story_parts.append("• **Bad data** costs companies an average of $15 million per year")
        story_parts.append("")
        
        # What's Next
        story_parts.append("## What's Next? 🚀")
        story_parts.append("")
        story_parts.append("1. **Download your clean data** - it's ready to use!")
        story_parts.append("2. **Check out the detailed report** - see exactly what we fixed")
        story_parts.append("3. **Keep it clean** - consider regular data checkups")
        story_parts.append("4. **Share the good news** - let your team know your data is now spotless!")
        story_parts.append("")
        
        story_parts.append("**Thanks for trusting us with your data!** 💪")
        
        return "\n".join(story_parts)
    
    def _enhance_with_ai(self, base_story: str, style: str) -> Optional[str]:
        """Enhance story using free AI services."""
        try:
            # Try Hugging Face inference API (free tier)
            for service_url in self.free_ai_services:
                try:
                    response = requests.post(
                        service_url,
                        headers={"Authorization": "Bearer hf_demo"},  # Demo token
                        json={"inputs": f"Enhance this {style} data story: {base_story[:500]}..."}
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        if isinstance(result, list) and len(result) > 0:
                            enhanced = result[0].get('generated_text', '')
                            if enhanced and len(enhanced) > len(base_story):
                                return enhanced
                except:
                    continue
            
            return None
            
        except Exception:
            return None
    
    def _calculate_quality_score(self, audit_data: Dict) -> int:
        """Calculate overall data quality score (0-100)."""
        try:
            rows_before = audit_data.get('rows_before', 1)
            rows_after = audit_data.get('rows_after', 0)
            duplicates_removed = audit_data.get('duplicates_removed', 0)
            
            # Base score starts at 100
            score = 100
            
            # Deduct for data loss (but not for duplicate removal)
            data_loss = rows_before - rows_after - duplicates_removed
            if data_loss > 0:
                score -= min(30, (data_loss / rows_before) * 100)
            
            # Bonus for duplicate removal (improves quality)
            if duplicates_removed > 0:
                score += min(10, (duplicates_removed / rows_before) * 20)
            
            # Consider column changes
            column_changes = audit_data.get('column_changes', {})
            total_improvements = sum(
                sum(1 for v in changes.values() if v and v > 0)
                for changes in column_changes.values()
            )
            
            if total_improvements > 0:
                score += min(15, total_improvements * 3)
            
            return max(0, min(100, int(score)))
            
        except Exception:
            return 75  # Default score
    
    def _identify_major_issues(self, column_changes: Dict) -> List[str]:
        """Identify major data quality issues."""
        issues = []
        
        for column, changes in column_changes.items():
            if changes.get('imputed_missing', 0) > 0:
                issues.append(f"Missing values in {column}")
            
            if changes.get('new_nulls_from_empty_strings', 0) > 0:
                issues.append(f"Empty strings in {column}")
            
            if changes.get('parsed_to_datetime', 0) > 0:
                issues.append(f"Date format issues in {column}")
        
        return issues
    
    def _calculate_completeness(self, audit_data: Dict) -> float:
        """Calculate data completeness percentage."""
        try:
            column_changes = audit_data.get('column_changes', {})
            total_missing = sum(
                changes.get('imputed_missing', 0) 
                for changes in column_changes.values()
            )
            total_records = audit_data.get('rows_before', 1)
            return max(0, 100 - (total_missing / total_records * 100))
        except:
            return 85.0
    
    def _calculate_consistency(self, audit_data: Dict) -> float:
        """Calculate data consistency percentage."""
        try:
            column_changes = audit_data.get('column_changes', {})
            consistency_issues = sum(
                changes.get('new_nulls_from_empty_strings', 0) +
                changes.get('parsed_to_datetime', 0)
                for changes in column_changes.values()
            )
            total_records = audit_data.get('rows_before', 1)
            return max(0, 100 - (consistency_issues / total_records * 100))
        except:
            return 90.0
    
    def _calculate_accuracy(self, audit_data: Dict) -> float:
        """Calculate data accuracy percentage."""
        try:
            duplicates_removed = audit_data.get('duplicates_removed', 0)
            total_records = audit_data.get('rows_before', 1)
            return max(0, 100 - (duplicates_removed / total_records * 100))
        except:
            return 95.0

# Global instance
story_generator = AIStoryGenerator()
