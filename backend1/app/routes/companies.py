"""
Companies Routes - Company Data Management
Author: Osman Yildiz
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from backend1.app import db
from backend1.app.models.user import User
from backend1.app.models.company import Company
from backend1.app.models.annual_report import AnnualReport
from backend1.app.services.scraper import AnnualReportsScraper

bp = Blueprint('companies', __name__, url_prefix='/api/companies')


@bp.route('/', methods=['GET'])
@jwt_required()
def get_companies():
    """Get all companies with optional filters"""
    try:
        # Get query parameters
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        search = request.args.get('search', '', type=str)
        industry = request.args.get('industry', '', type=str)
        
        # Build query
        query = Company.query
        
        if search:
            query = query.filter(
                db.or_(
                    Company.name.ilike(f'%{search}%'),
                    Company.ticker.ilike(f'%{search}%')
                )
            )
        
        if industry:
            query = query.filter(Company.industry.ilike(f'%{industry}%'))
        
        # Paginate
        pagination = query.order_by(Company.name).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'companies': [company.to_dict() for company in pagination.items],
            'total': pagination.total,
            'pages': pagination.pages,
            'current_page': page
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/<int:company_id>', methods=['GET'])
@jwt_required()
def get_company(company_id):
    """Get specific company with annual reports"""
    try:
        company = Company.query.get(company_id)
        if not company:
            return jsonify({'error': 'Company not found'}), 404
        
        return jsonify(company.to_dict(include_reports=True)), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/<int:company_id>/reports', methods=['GET'])
@jwt_required()
def get_company_reports(company_id):
    """Get annual reports for a specific company"""
    try:
        company = Company.query.get(company_id)
        if not company:
            return jsonify({'error': 'Company not found'}), 404
        
        reports = AnnualReport.query.filter_by(company_id=company_id).order_by(
            AnnualReport.year.desc()
        ).all()
        
        return jsonify({
            'company': company.to_dict(),
            'reports': [report.to_dict() for report in reports],
            'total': len(reports)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/scrape', methods=['POST'])
@jwt_required()
def scrape_company():
    """Scrape a company from AnnualReports.com (admin only)"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if user.role != 'admin':
            return jsonify({'error': 'Admin access required'}), 403
        
        data = request.get_json()
        
        if not data.get('slug'):
            return jsonify({'error': 'Company slug is required'}), 400
        
        slug = data['slug']
        
        # Check if company already exists
        existing = Company.query.filter_by(source_url=f"https://www.annualreports.com/Company/{slug}").first()
        if existing and not data.get('force_update', False):
            return jsonify({
                'message': 'Company already exists',
                'company': existing.to_dict(include_reports=True)
            }), 200
        
        # Scrape company data
        scraper = AnnualReportsScraper()
        company_data = scraper.scrape_company(slug)
        
        if not company_data:
            return jsonify({'error': 'Failed to scrape company data'}), 500
        
        # Update existing or create new company
        if existing:
            company = existing
            company.name = company_data['name']
            company.ticker = company_data['ticker']
            company.exchange = company_data['exchange']
            company.industry = company_data['industry']
            company.sector = company_data['sector']
            company.description = company_data['description']
            company.website = company_data['website']
            company.last_scraped_at = datetime.utcnow()
        else:
            company = Company(
                name=company_data['name'],
                ticker=company_data['ticker'],
                exchange=company_data['exchange'],
                industry=company_data['industry'],
                sector=company_data['sector'],
                description=company_data['description'],
                website=company_data['website'],
                source_url=company_data['source_url']
            )
            db.session.add(company)
        
        db.session.flush()  # Get company ID
        
        # Add annual reports
        for report_data in company_data['annual_reports']:
            # Check if report already exists
            existing_report = AnnualReport.query.filter_by(
                company_id=company.id,
                year=report_data['year']
            ).first()
            
            if existing_report:
                # Update existing report
                existing_report.title = report_data['title']
                existing_report.report_type = report_data['report_type']
                existing_report.pdf_url = report_data['pdf_url']
                existing_report.html_url = report_data['html_url']
                existing_report.view_url = report_data['view_url']
            else:
                # Create new report
                annual_report = AnnualReport(
                    company_id=company.id,
                    year=report_data['year'],
                    title=report_data['title'],
                    report_type=report_data['report_type'],
                    pdf_url=report_data['pdf_url'],
                    html_url=report_data['html_url'],
                    view_url=report_data['view_url']
                )
                db.session.add(annual_report)
        
        db.session.commit()
        
        return jsonify({
            'message': 'Company scraped successfully',
            'company': company.to_dict(include_reports=True)
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@bp.route('/search', methods=['GET'])
@jwt_required()
def search_companies_online():
    """Search for companies on AnnualReports.com"""
    try:
        query = request.args.get('q', '', type=str)
        
        if not query:
            return jsonify({'error': 'Query parameter is required'}), 400
        
        scraper = AnnualReportsScraper()
        results = scraper.search_companies(query)
        
        return jsonify({
            'results': results,
            'total': len(results)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/<int:company_id>', methods=['DELETE'])
@jwt_required()
def delete_company(company_id):
    """Delete a company and its annual reports (admin only)"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if user.role != 'admin':
            return jsonify({'error': 'Admin access required'}), 403
        
        company = Company.query.get(company_id)
        if not company:
            return jsonify({'error': 'Company not found'}), 404
        
        db.session.delete(company)
        db.session.commit()
        
        return jsonify({'message': 'Company deleted successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
