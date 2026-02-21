"""
Reports Routes - Report Management
Author: Osman Yildiz
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from backend1.app import db
from backend1.app.models.user import User
from backend1.app.models.report import Report
from backend1.app.models.activity import Activity
import os
import io
import pandas as pd
from fpdf import FPDF
from flask import current_app, send_file
from werkzeug.utils import secure_filename

bp = Blueprint('reports', __name__, url_prefix='/api/reports')


@bp.route('/', methods=['GET'])
@jwt_required()
def get_reports():
    """Get all reports (filtered by user role)"""
    try:
        user_id = int(get_jwt_identity())
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Admins see all reports, users see only their own
        if user.role == 'admin':
            reports = Report.query.order_by(Report.created_at.desc()).all()
        else:
            reports = Report.query.filter_by(created_by=user_id).order_by(Report.created_at.desc()).all()
        
        return jsonify({
            'reports': [report.to_dict() for report in reports],
            'total': len(reports)
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to retrieve reports.'}), 500


@bp.route('/<int:report_id>', methods=['GET'])
@jwt_required()
def get_report(report_id):
    """Get specific report by ID"""
    try:
        user_id = int(get_jwt_identity())
        user = User.query.get(user_id)
        
        report = Report.query.get(report_id)
        if not report:
            return jsonify({'error': 'Report not found'}), 404
        
        # Check permissions
        if user.role != 'admin' and report.created_by != user_id:
            return jsonify({'error': 'Access denied'}), 403
        
        # Get creator and reviewer info
        creator = User.query.get(report.created_by)
        reviewer = User.query.get(report.reviewed_by) if report.reviewed_by else None
        
        report_data = report.to_dict()
        report_data['creator'] = creator.to_dict() if creator else None
        report_data['reviewer'] = reviewer.to_dict() if reviewer else None
        
        return jsonify(report_data), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to retrieve report.'}), 500


def allowed_file(filename):
    """Check if file extension is allowed"""
    ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'xlsx', 'csv', 'txt'}
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@bp.route('/', methods=['POST'])
@jwt_required()
def create_report():
    """Create a new report"""
    try:
        user_id = int(get_jwt_identity())
        
        # Handle form data (multipart/form-data)
        if 'title' not in request.form or 'report_type' not in request.form:
             # Fallback to JSON if no form data (backward compatibility)
            data = request.get_json() if request.is_json else request.form
        else:
            data = request.form

        # Validate required fields
        if not data.get('title') or not data.get('report_type'):
            return jsonify({'error': 'Missing required fields: title, report_type'}), 400
            
        file_path = None
        if 'file' in request.files:
            file = request.files['file']
            if file and file.filename != '':
                # Validate file type
                if not allowed_file(file.filename):
                    return jsonify({'error': 'File type not allowed. Accepted: pdf, doc, docx, xlsx, csv, txt'}), 400
                
                filename = secure_filename(file.filename)
                
                # Reject if secure_filename returns empty (malicious filename)
                if not filename:
                    return jsonify({'error': 'Invalid filename'}), 400
                
                upload_folder = os.path.join(current_app.root_path, 'static', 'uploads')
                os.makedirs(upload_folder, exist_ok=True)
                
                # Save file
                file_path = os.path.join(upload_folder, filename)
                file.save(file_path)
                
                # Store relative path for serving
                file_path = f'uploads/{filename}'
        
        # Create new report
        report = Report(
            title=data['title'],
            description=data.get('description', ''),
            report_type=data['report_type'],
            status=data.get('status', 'draft'),
            priority=data.get('priority', 'medium'),
            created_by=user_id,
            file_path=file_path
        )
        
        db.session.add(report)
        db.session.commit()
        
        return jsonify({
            'message': 'Report created successfully',
            'report': report.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to create report.'}), 500


@bp.route('/<int:report_id>', methods=['PUT'])
@jwt_required()
def update_report(report_id):
    """Update a report"""
    try:
        user_id = int(get_jwt_identity())
        user = User.query.get(user_id)
        
        report = Report.query.get(report_id)
        if not report:
            return jsonify({'error': 'Report not found'}), 404
        
        # Check permissions
        if user.role != 'admin' and report.created_by != user_id:
            return jsonify({'error': 'Access denied'}), 403
        
        data = request.get_json()
        
        warning_message = None
        
        # Handle approval workflow
        if 'status' in data and data['status'] == 'approved':
            # Extract company name and year from the request
            company_name = data.get('company_name', '').strip()
            report_year = data.get('report_year')
            
            warning_message = None
            
            if company_name and report_year:
                from backend1.app.models.company import Company
                from backend1.app.models.annual_report import AnnualReport
                
                # Check if company exists by name (case-insensitive)
                company = Company.query.filter(Company.name.ilike(company_name)).first()
                
                if company:
                    # Company exists, check if report year already exists
                    existing_report = AnnualReport.query.filter_by(
                        company_id=company.id,
                        year=report_year
                    ).first()
                    
                    if existing_report:
                        # Report year already exists - warn user
                        warning_message = f"Warning: Company '{company_name}' already has a report for year {report_year}"
                    else:
                        # Add new annual report to existing company
                        new_annual_report = AnnualReport(
                            company_id=company.id,
                            year=report_year,
                            title=report.title,
                            report_type='Annual Report',
                            pdf_url=f"https://www.annualreports.com/Companies?search={company.ticker}" if company.ticker else None
                        )
                        db.session.add(new_annual_report)
                        report.company_id = company.id
                        report.source_annual_report_id = new_annual_report.id
                        
                else:
                    # Company doesn't exist - create new company
                    # Extract ticker from filename if available
                    ticker = None
                    if report.file_path:
                        filename = report.file_path.split('/')[-1]
                        import re
                        match = re.match(r'(?:NYSE_|NASDAQ_)?([A-Za-z]+)(?:_\d{4})?\.pdf', filename, re.IGNORECASE)
                        if match:
                            ticker = match.group(1).upper()
                    
                    new_company = Company(
                        name=company_name,
                        ticker=ticker,
                        source_url=f"https://www.annualreports.com/Companies?search={ticker}" if ticker else "https://www.annualreports.com/"
                    )
                    db.session.add(new_company)
                    db.session.flush()  # Get the company ID
                    
                    # Add annual report for the new company
                    new_annual_report = AnnualReport(
                        company_id=new_company.id,
                        year=report_year,
                        title=report.title,
                        report_type='Annual Report',
                        pdf_url=f"https://www.annualreports.com/Companies?search={ticker}" if ticker else None
                    )
                    db.session.add(new_annual_report)
                    report.company_id = new_company.id
                    report.source_annual_report_id = new_annual_report.id
        
        # Update fields if provided
        if 'title' in data:
            report.title = data['title']
        if 'description' in data:
            report.description = data['description']
        if 'report_type' in data:
            report.report_type = data['report_type']
        if 'status' in data:
            report.status = data['status']
        if 'priority' in data:
            report.priority = data['priority']
        
        db.session.commit()
        
        response_data = {
            'message': 'Report updated successfully',
            'report': report.to_dict()
        }
        
        if warning_message:
            response_data['warning'] = warning_message
        
        return jsonify(response_data), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@bp.route('/<int:report_id>/review', methods=['POST'])
@jwt_required()
def review_report(report_id):
    """Review a report (admin only)"""
    try:
        user_id = int(get_jwt_identity())
        user = User.query.get(user_id)
        
        if user.role != 'admin':
            return jsonify({'error': 'Admin access required'}), 403
        
        report = Report.query.get(report_id)
        if not report:
            return jsonify({'error': 'Report not found'}), 404
        
        data = request.get_json()
        
        # Update review fields
        report.reviewed_by = user_id
        report.reviewed_at = datetime.utcnow()
        report.review_notes = data.get('review_notes', '')
        report.compliance_score = data.get('compliance_score')
        report.status = data.get('status', 'reviewed')
        
        db.session.commit()
        
        return jsonify({
            'message': 'Report reviewed successfully',
            'report': report.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to review report.'}), 500


@bp.route('/download/<int:report_id>', methods=['GET'])
@jwt_required()
def download_report(report_id):
    """Download an uploaded file for an approved report"""
    try:
        report = Report.query.get(report_id)
        if not report:
            return jsonify({'error': 'Report not found'}), 404
        
        if report.status != 'approved':
            return jsonify({'error': 'Only approved reports can be downloaded'}), 403
        
        if not report.file_path:
            return jsonify({'error': 'No file attached to this report'}), 404
        
        # Build absolute file path
        file_abs_path = os.path.join(current_app.root_path, 'static', report.file_path)
        
        if not os.path.exists(file_abs_path):
            return jsonify({'error': 'File not found on server'}), 404
        
        from flask import send_file
        filename = report.file_path.split('/')[-1]
        return send_file(file_abs_path, as_attachment=True, download_name=filename)
        
    except Exception as e:
        return jsonify({'error': 'Failed to download file.'}), 500


@bp.route('/<int:report_id>', methods=['DELETE'])
@jwt_required()
def delete_report(report_id):
    """Delete a report"""
    try:
        user_id = int(get_jwt_identity())
        user = User.query.get(user_id)
        
        report = Report.query.get(report_id)
        if not report:
            return jsonify({'error': 'Report not found'}), 404
        
        # Check permissions
        if user.role != 'admin' and report.created_by != user_id:
            return jsonify({'error': 'Access denied'}), 403
        
        db.session.delete(report)
        db.session.commit()
        
        return jsonify({'message': 'Report deleted successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@bp.route('/stats', methods=['GET'])
@jwt_required()
def get_report_stats():
    """Get report statistics"""
    try:
        user_id = int(get_jwt_identity())
        user = User.query.get(user_id)
        
        # Get base query
        if user.role == 'admin':
            base_query = Report.query
        else:
            base_query = Report.query.filter_by(created_by=user_id)
        
        # Calculate statistics
        total = base_query.count()
        draft = base_query.filter_by(status='draft').count()
        submitted = base_query.filter_by(status='submitted').count()
        reviewed = base_query.filter_by(status='reviewed').count()
        approved = base_query.filter_by(status='approved').count()
        
        high_priority = base_query.filter_by(priority='high').count()
        critical_priority = base_query.filter_by(priority='critical').count()
        
        return jsonify({
            'total_reports': total,
            'by_status': {
                'draft': draft,
                'submitted': submitted,
                'reviewed': reviewed,
                'approved': approved
            },
            'high_priority': high_priority,
            'critical_priority': critical_priority
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to retrieve report statistics.'}), 500


@bp.route('/export/<fmt>', methods=['GET'])
@jwt_required()
def export_reports(fmt):
    """Export reports to CSV, Excel, or PDF"""
    try:
        user_id = int(get_jwt_identity())
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
            
        # Get data based on role
        if user.role == 'admin':
            reports = Report.query.all()
        else:
            reports = Report.query.filter_by(created_by=user_id).all()
            
        data = [r.to_dict() for r in reports]
        if not data:
            return jsonify({'error': 'No data to export'}), 404
            
        df = pd.DataFrame(data)
        
        # Log activity
        activity = Activity(
            user_id=user_id,
            action='export_reports',
            description=f'Exported {len(reports)} reports to {fmt}'
        )
        db.session.add(activity)
        db.session.commit()
        
        if fmt == 'csv':
            output = io.BytesIO()
            df.to_csv(output, index=False)
            output.seek(0)
            return send_file(
                output,
                mimetype='text/csv',
                as_attachment=True,
                download_name=f'compliance_report_{datetime.now().strftime("%Y%m%d")}.csv'
            )
            
        elif fmt == 'excel':
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name='Compliance Reports')
            output.seek(0)
            return send_file(
                output,
                mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                as_attachment=True,
                download_name=f'compliance_report_{datetime.now().strftime("%Y%m%d")}.xlsx'
            )
            
        elif fmt == 'pdf':
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", 'B', 16)
            pdf.cell(0, 10, f"Compliance Reports - {datetime.now().strftime('%Y-%m-%d')}", ln=True, align='C')
            pdf.ln(10)
            
            pdf.set_font("Arial", 'B', 10)
            # Headers
            headers = ['ID', 'Title', 'Type', 'Status', 'Creator']
            col_width = pdf.epw / 5
            for header in headers:
                pdf.cell(col_width, 10, header, border=1)
            pdf.ln()
            
            pdf.set_font("Arial", '', 9)
            for r in reports:
                # Add rows (truncating titles if too long)
                title = (r.title[:25] + '..') if len(r.title) > 25 else r.title
                pdf.cell(col_width, 10, str(r.id), border=1)
                pdf.cell(col_width, 10, title, border=1)
                pdf.cell(col_width, 10, r.report_type, border=1)
                pdf.cell(col_width, 10, r.status, border=1)
                pdf.cell(col_width, 10, str(r.created_by), border=1)
                pdf.ln()
                
            pdf_output = pdf.output()
            # output() in fpdf2 returns bytes by default if no dest is provided
            return send_file(
                io.BytesIO(pdf_output),
                mimetype='application/pdf',
                as_attachment=True,
                download_name=f'compliance_report_{datetime.now().strftime("%Y%m%d")}.pdf'
            )
            
        else:
            return jsonify({'error': 'Invalid format'}), 400
            
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Export failed: {str(e)}'}), 500