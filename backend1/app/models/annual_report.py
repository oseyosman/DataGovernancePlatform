"""
Annual Report Model - Stores annual report metadata from AnnualReports.com
Author: Osman Yildiz
"""
from datetime import datetime
from backend1.app import db


class AnnualReport(db.Model):
    """Annual report model for storing report metadata"""
    __tablename__ = 'annual_reports'
    
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    
    # Report details
    year = db.Column(db.Integer, nullable=False)
    title = db.Column(db.String(200), nullable=False)
    report_type = db.Column(db.String(50), nullable=True)  # "Annual Report", "10-K", etc.
    
    # Download links
    pdf_url = db.Column(db.String(500), nullable=True)
    html_url = db.Column(db.String(500), nullable=True)
    view_url = db.Column(db.String(500), nullable=True)
    
    # Metadata
    filing_date = db.Column(db.Date, nullable=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    company = db.relationship('Company', back_populates='annual_reports')
    
    def __repr__(self):
        return f'<AnnualReport {self.title} ({self.year})>'
    
    def to_dict(self, include_company=False):
        """Convert annual report object to dictionary"""
        data = {
            'id': self.id,
            'company_id': self.company_id,
            'year': self.year,
            'title': self.title,
            'report_type': self.report_type,
            'pdf_url': self.pdf_url,
            'html_url': self.html_url,
            'view_url': self.view_url,
            'filing_date': self.filing_date.isoformat() if self.filing_date else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
        
        if include_company and self.company:
            data['company'] = self.company.to_dict()
        
        return data
