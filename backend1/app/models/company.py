"""
Company Model - Stores scraped company data from AnnualReports.com
Author: Osman Yildiz
"""
from datetime import datetime
from backend1.app import db


class Company(db.Model):
    """Company model for storing data scraped from AnnualReports.com"""
    __tablename__ = 'companies'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    ticker = db.Column(db.String(10), nullable=True, unique=True)
    exchange = db.Column(db.String(50), nullable=True)
    industry = db.Column(db.String(100), nullable=True)
    sector = db.Column(db.String(100), nullable=True)
    description = db.Column(db.Text, nullable=True)
    employee_count = db.Column(db.Integer, nullable=True)
    website = db.Column(db.String(255), nullable=True)
    source_url = db.Column(db.String(255), nullable=False)  # URL on AnnualReports.com
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_scraped_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    annual_reports = db.relationship('AnnualReport', back_populates='company', cascade='all, delete-orphan')
    compliance_reports = db.relationship('Report', back_populates='company')
    
    def __repr__(self):
        return f'<Company {self.name} ({self.ticker})>'
    
    def to_dict(self, include_reports=False):
        """Convert company object to dictionary"""
        data = {
            'id': self.id,
            'name': self.name,
            'ticker': self.ticker,
            'exchange': self.exchange,
            'industry': self.industry,
            'sector': self.sector,
            'description': self.description,
            'employee_count': self.employee_count,
            'website': self.website,
            'source_url': self.source_url,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'last_scraped_at': self.last_scraped_at.isoformat() if self.last_scraped_at else None,
        }
        
        if include_reports:
            data['annual_reports'] = [report.to_dict() for report in self.annual_reports]
        
        return data
