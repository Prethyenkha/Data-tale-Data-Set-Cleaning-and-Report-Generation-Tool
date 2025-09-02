import os
import io
import json
import pandas as pd
from datetime import datetime
from flask import Flask, render_template, request, jsonify, send_file, session
from werkzeug.utils import secure_filename
from autoclean.cleaner import clean_dataframe, build_audit_summary
from ai_story_generator import story_generator

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # Change this in production

# Configure upload folder
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def ai_explain(audit: dict, api_key: str = None) -> str | None:
    """
    Generate intelligent AI summary using local template-based analysis
    No external API calls required - completely free and offline
    """
    try:
        # Analyze the audit data
        rows_before = audit['rows_before']
        rows_after = audit['rows_after']
        duplicates_removed = audit.get('duplicates_removed', 0)
        columns = audit['columns']
        column_changes = audit['column_changes']
        
        # Calculate key metrics
        total_changes = sum(len([v for v in info.values() if v not in (None, 0, "", [], {}, False)]) 
                           for info in column_changes.values())
        
        # Identify significant changes
        significant_changes = []
        data_quality_issues = []
        improvements_made = []
        
        for col, info in column_changes.items():
            if info.get('imputed_missing', 0) > 0:
                significant_changes.append(f"• **{col}**: Imputed {info['imputed_missing']} missing values")
                data_quality_issues.append(f"Missing data in {col}")
                
            if info.get('new_nulls_from_empty_strings', 0) > 0:
                significant_changes.append(f"• **{col}**: Converted {info['new_nulls_from_empty_strings']} empty strings to nulls")
                data_quality_issues.append(f"Empty strings in {col}")
                
            if info.get('parsed_to_datetime', 0) > 0:
                significant_changes.append(f"• **{col}**: Parsed {info['parsed_to_datetime']} values as dates")
                improvements_made.append(f"Date parsing in {col}")
                
            if info.get('emails_valid_after', 0) > 0:
                significant_changes.append(f"• **{col}**: Normalized {info['emails_valid_after']} email addresses")
                improvements_made.append(f"Email normalization in {col}")
        
        # Generate executive summary
        summary_parts = []
        
        # Overview
        summary_parts.append("## 📊 **Data Cleaning Overview**")
        summary_parts.append(f"Your dataset has been successfully cleaned and optimized for analysis.")
        summary_parts.append(f"")
        
        # Key metrics
        summary_parts.append("## 📈 **Key Metrics**")
        summary_parts.append(f"• **Dataset Size**: {rows_before} → {rows_after} rows ({rows_after - rows_before:+d} change)")
        summary_parts.append(f"• **Data Quality**: {total_changes} improvements applied across {len(columns)} columns")
        summary_parts.append(f"• **Duplicates**: {duplicates_removed} duplicate records removed")
        summary_parts.append(f"")
        
        # Data quality assessment
        if data_quality_issues:
            summary_parts.append("## ⚠️ **Data Quality Issues Identified**")
            for issue in data_quality_issues[:5]:  # Limit to top 5
                summary_parts.append(f"• {issue}")
            summary_parts.append(f"")
        
        # Improvements made
        if improvements_made:
            summary_parts.append("## ✅ **Improvements Applied**")
            for improvement in improvements_made[:5]:  # Limit to top 5
                summary_parts.append(f"• {improvement}")
            summary_parts.append(f"")
        
        # Significant changes
        if significant_changes:
            summary_parts.append("## 🔧 **Significant Changes**")
            for change in significant_changes[:8]:  # Limit to top 8
                summary_parts.append(change)
            summary_parts.append(f"")
        
        # Recommendations
        summary_parts.append("## 💡 **Recommendations**")
        if duplicates_removed > 0:
            summary_parts.append("• **Duplicate Prevention**: Consider implementing data validation to prevent future duplicates")
        
        if any(info.get('imputed_missing', 0) > 0 for info in column_changes.values()):
            summary_parts.append("• **Data Collection**: Review data collection processes to reduce missing values")
        
        if any(info.get('new_nulls_from_empty_strings', 0) > 0 for info in column_changes.values()):
            summary_parts.append("• **Input Validation**: Add form validation to prevent empty string submissions")
        
        summary_parts.append("• **Regular Monitoring**: Schedule periodic data quality audits")
        summary_parts.append("• **Documentation**: Update data dictionaries with cleaning rules applied")
        summary_parts.append(f"")
        
        # Action items
        summary_parts.append("## 🎯 **Next Steps**")
        summary_parts.append("• Download the cleaned dataset for analysis")
        summary_parts.append("• Review the detailed column-by-column report")
        summary_parts.append("• Implement suggested data quality improvements")
        summary_parts.append("• Consider setting up automated data validation")
        
        return "\n".join(summary_parts)
        
    except Exception as e:
        return f"⚠️ **Summary Generation Error**\n\nUnable to generate summary: {str(e)}\n\nYour data has been cleaned successfully! You can still download the cleaned CSV and detailed report."

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if not file.filename.endswith('.csv'):
        return jsonify({'error': 'Please upload a CSV file'}), 400
    
    try:
        # Read the CSV file
        df = pd.read_csv(file)
        
        # Clean the dataframe
        cleaned, audit = clean_dataframe(df)
        summary = build_audit_summary(audit)
        
        # Store results in session for download
        session['cleaned_data'] = cleaned.to_csv(index=False)
        session['summary'] = summary
        
        # Generate AI summary (local template-based)
        send_to_ai = request.form.get('send_to_ai')
        print(f"Debug: send_to_ai value: {send_to_ai}")
        print(f"Debug: send_to_ai type: {type(send_to_ai)}")
        
        ai_summary = None
        if send_to_ai == 'true':
            print("Debug: Attempting to generate AI summary...")
            try:
                ai_summary = ai_explain(summary)
                print(f"Debug: AI summary generated: {bool(ai_summary)}")
            except Exception as e:
                print(f"Debug: Error generating AI summary: {e}")
                ai_summary = f"⚠️ **AI Summary Error**\n\nUnable to generate AI summary: {str(e)}\n\nYour data has been cleaned successfully! You can still download the cleaned CSV and detailed report."
        
        # Prepare response data
        response_data = {
            'success': True,
            'summary': summary,
            'ai_summary': ai_summary,
            'columns': list(cleaned.columns),
            'rows_before': summary['rows_before'],
            'rows_after': summary['rows_after'],
            'duplicates_removed': summary['duplicates_removed']
        }
        
        return jsonify(response_data)
        
    except Exception as e:
        return jsonify({'error': f'Error processing file: {str(e)}'}), 500

@app.route('/download/csv')
def download_csv():
    if 'cleaned_data' not in session:
        return jsonify({'error': 'No cleaned data available'}), 400
    
    # Create a file-like object
    output = io.BytesIO()
    output.write(session['cleaned_data'].encode('utf-8'))
    output.seek(0)
    
    return send_file(
        output,
        mimetype='text/csv',
        as_attachment=True,
        download_name='cleaned.csv'
    )

@app.route('/download/report')
def download_report():
    if 'summary' not in session:
        return jsonify({'error': 'No report data available'}), 400
    
    summary = session['summary']
    
    # Generate report content
    report_lines = [
        "# Data Tale Report",
        "",
        f"Generated: {datetime.utcnow().isoformat()}Z",
        "",
        "## Dataset Overview",
        f"- Rows before: **{summary['rows_before']}**",
        f"- Rows after: **{summary['rows_after']}**",
        f"- Columns: **{len(summary['columns'])}**",
        "",
        f"### Duplicates Removed: {summary['duplicates_removed']}",
        "",
        "## Column-by-Column Changes"
    ]
    
    for col, info in summary["column_changes"].items():
        report_lines.append(f"### `{col}`")
        for k, v in info.items():
            if v not in (None, 0, "", [], {}, False):
                report_lines.append(f"- **{k.replace('_',' ').title()}**: {v}")
        report_lines.append("")
    
    report_content = "\n".join(report_lines)
    
    # Create a file-like object
    output = io.BytesIO()
    output.write(report_content.encode('utf-8'))
    output.seek(0)
    
    return send_file(
        output,
        mimetype='text/markdown',
        as_attachment=True,
        download_name='report.md'
    )

@app.route('/generate-story', methods=['POST'])
def generate_story():
    """Generate AI-powered narrative story from data cleaning results."""
    try:
        data = request.get_json()
        style = data.get('style', 'executive')  # executive, technical, casual
        
        if 'summary' not in session:
            return jsonify({'error': 'No data available for story generation'}), 400
        
        summary = session['summary']
        
        # Generate AI story
        story = story_generator.generate_story(summary, style)
        
        return jsonify({
            'success': True,
            'story': story,
            'style': style,
            'generated_at': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': f'Error generating story: {str(e)}'}), 500

@app.route('/download-story', methods=['POST'])
def download_story():
    """Download AI-generated story as markdown file."""
    try:
        data = request.get_json()
        style = data.get('style', 'executive')
        
        if 'summary' not in session:
            return jsonify({'error': 'No data available for story generation'}), 400
        
        summary = session['summary']
        
        # Generate AI story
        story = story_generator.generate_story(summary, style)
        
        # Create filename based on style
        style_names = {
            'executive': 'Executive_Report',
            'technical': 'Technical_Analysis', 
            'casual': 'Friendly_Summary'
        }
        filename = f"{style_names.get(style, 'AI_Story')}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.md"
        
        # Create in-memory file
        story_buffer = io.BytesIO()
        story_buffer.write(story.encode('utf-8'))
        story_buffer.seek(0)
        
        return send_file(
            story_buffer,
            mimetype='text/markdown',
            as_attachment=True,
            download_name=filename
        )
        
    except Exception as e:
        return jsonify({'error': f'Error downloading story: {str(e)}'}), 500

if __name__ == '__main__':
    # Get port from environment variable (for deployment)
    port = int(os.environ.get('PORT', 5000))
    # Run in debug mode only in development
    debug = os.environ.get('FLASK_ENV') == 'development'
    app.run(debug=debug, host='0.0.0.0', port=port)
