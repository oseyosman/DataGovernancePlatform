"""
Populate Database with 20+ Companies from AnnualReports.com
Unified script - scrapes real company data with 3 most recent reports each

Author: Data Governance Platform
Usage: python seed_companies.py
"""
import sys
sys.path.insert(0, '.')

from backend1.app import create_app, db
from backend1.app.models.company import Company
from backend1.app.models.annual_report import AnnualReport
from backend1.app.services.scraper import AnnualReportsScraper
from datetime import datetime


def clean_existing_bad_companies():
    """Remove any placeholder companies with no real data"""
    bad_companies = Company.query.filter_by(
        name='Annual reports for 10,379 international companies'
    ).all()
    
    if bad_companies:
        print(f"Removing {len(bad_companies)} placeholder entries...")
        for c in bad_companies:
            db.session.delete(c)
        db.session.commit()


def populate_companies(target_count=20):
    """
    Populate database with real company data from AnnualReports.com
    
    Args:
        target_count: Number of companies to add (default: 20)
    """
    app = create_app()
    ctx = app.app_context()
    ctx.push()
    
    # Clean up any bad entries first
    clean_existing_bad_companies()
    
    scraper = AnnualReportsScraper(rate_limit_delay=0.5)
    
    # Comprehensive list of major companies (verified to have data)
    companies_to_scrape = [
        # Tech Giants
        'apple-inc',
        'tesla-inc',
        'meta-platforms-inc',
        'cisco-systems-inc',
        
        # Financial Services
        'paypal-holdings-inc',
        'visa-inc',
        'goldman-sachs-group-inc',
        
        # Retail & Consumer
        'walmart-inc',
        'target-corp',
        'starbucks-corp',
        'lowes-companies-inc',
        
        # Consumer Goods
        'pepsico-inc',
        'procter-gamble-co',
        'johnson-johnson',
        
        # Pharmaceuticals
        'pfizer-inc',
        'merck-co-inc',
        'abbvie-inc',
        
        # Industrial
        'caterpillar-inc',
        'deere-co',
        
        # Technology Hardware
        'dell-technologies-inc',
    ]
    
    current_count = Company.query.count()
    print("=" * 80)
    print(f"Company Database Population")
    print(f"Current: {current_count} companies")
    print(f"Target: {target_count} companies")
    print(f"Max 3 reports per company")
    print("=" * 80)
    
    if current_count >= target_count:
        print(f"\n[INFO] Already have {current_count} companies (target: {target_count})")
        print("Database is already populated.")
        print_summary()
        ctx.pop()
        return
    
    success_count = 0
    skip_count = 0
    error_count = 0
    
    for slug in companies_to_scrape:
        current_total = Company.query.count()
        
        if current_total >= target_count:
            print(f"\n[TARGET REACHED] {current_total} companies")
            break
        
        print(f"\n[{current_total + 1}/{target_count}] Scraping: {slug}")
        
        try:
            # Scrape company data
            company_data = scraper.scrape_company(slug)
            
            # Validate data quality
            if not company_data or not company_data.get('name'):
                print(f"  [FAILED] No data returned")
                error_count += 1
                continue
            
            # Skip generic placeholder pages
            if company_data['name'] == 'Annual reports for 10,379 international companies':
                print(f"  [SKIP] Generic page, no specific company data")
                skip_count += 1
                continue
            
            # Skip if no reports available
            if not company_data.get('annual_reports') or len(company_data.get('annual_reports', [])) == 0:
                print(f"  [SKIP] No annual reports found")
                skip_count += 1
                continue
            
            # Check if company already exists
            existing = Company.query.filter_by(source_url=company_data['source_url']).first()
            if existing:
                print(f"  [SKIP] {company_data['name']} already exists")
                skip_count += 1
                continue
            
            # Create company record
            company = Company(
                name=company_data['name'],
                ticker=company_data.get('ticker') if company_data.get('ticker') else None,
                exchange=company_data.get('exchange'),
                industry=company_data.get('industry'),
                sector=company_data.get('sector'),
                description=company_data.get('description'),
                employee_count=company_data.get('employee_count'),
                website=company_data.get('website'),
                source_url=company_data['source_url'],
                last_scraped_at=datetime.utcnow()
            )
            db.session.add(company)
            db.session.flush()  # Get company ID
            
            # Add only the 3 most recent annual reports
            all_reports = company_data.get('annual_reports', [])
            sorted_reports = sorted(all_reports, key=lambda x: x.get('year', 0), reverse=True)
            recent_reports = sorted_reports[:3]
            
            reports_added = 0
            for report_data in recent_reports:
                if report_data.get('year'):
                    annual_report = AnnualReport(
                        company_id=company.id,
                        year=report_data['year'],
                        title=report_data.get('title', f"{report_data['year']} Annual Report"),
                        report_type=report_data.get('report_type', 'Annual Report'),
                        pdf_url=report_data.get('pdf_url'),
                        html_url=report_data.get('html_url'),
                        view_url=report_data.get('view_url')
                    )
                    db.session.add(annual_report)
                    reports_added += 1
            
            db.session.commit()
            success_count += 1
            
            print(f"  [SUCCESS] {company_data['name']}")
            print(f"     Reports: {reports_added} (of {len(all_reports)} available)")
            if company_data.get('website'):
                print(f"     Website: {company_data['website']}")
            
        except Exception as e:
            db.session.rollback()
            error_count += 1
            print(f"  [ERROR] {str(e)[:100]}")
            continue
    
    # Final summary
    print("\n" + "=" * 80)
    print_summary()
    print(f"\nThis Run:")
    print(f"  Added: {success_count}")
    print(f"  Skipped: {skip_count}")
    print(f"  Errors: {error_count}")
    print("=" * 80)
    
    ctx.pop()


def print_summary():
    """Print current database statistics"""
    total_companies = Company.query.count()
    total_reports = AnnualReport.query.count()
    
    print(f"\nDatabase Summary:")
    print(f"  Total Companies: {total_companies}")
    print(f"  Total Annual Reports: {total_reports}")
    
    if total_companies > 0:
        avg_reports = total_reports / total_companies
        print(f"  Average Reports per Company: {avg_reports:.1f}")


def list_companies():
    """List all companies in the database"""
    app = create_app()
    ctx = app.app_context()
    ctx.push()
    
    companies = Company.query.order_by(Company.name).all()
    
    print("\n" + "=" * 80)
    print(f"Companies in Database ({len(companies)} total)")
    print("=" * 80)
    
    for i, company in enumerate(companies, 1):
        report_count = len(company.annual_reports)
        print(f"{i:2}. {company.name:45} - {report_count:2} reports")
    
    print_summary()
    ctx.pop()


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Populate companies database')
    parser.add_argument('--list', action='store_true', help='List existing companies')
    parser.add_argument('--count', type=int, default=20, help='Target number of companies (default: 20)')
    
    args = parser.parse_args()
    
    if args.list:
        list_companies()
    else:
        populate_companies(target_count=args.count)
