"""
Report Model
Author: Osman Yildiz
"""
from datetime import datetime
from backend1.app import db


class Report(db.Model):
    """Report model for compliance reports"""
    __tablename__ = 'reports'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    report_type = db.Column(db.String(50), nullable=False)  # compliance, audit, risk, etc.
    status = db.Column(db.String(20), nullable=False, default='draft')  # draft, submitted, reviewed, approved
    priority = db.Column(db.String(20), nullable=False, default='medium')  # low, medium, high, critical
    file_path = db.Column(db.String(255), nullable=True)  # Path to uploaded file
    
    # Relationships
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    reviewed_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    reviewed_at = db.Column(db.DateTime, nullable=True)
    
    # Review fields
    review_notes = db.Column(db.Text, nullable=True)
    compliance_score = db.Column(db.Float, nullable=True)
    
    def __repr__(self):
        return f'<Report {self.title}>'
    
    def to_dict(self):
        """Convert report object to dictionary"""
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'report_type': self.report_type,
            'status': self.status,
            'priority': self.priority,
            'file_path': self.file_path,
            'created_by': self.created_by,
            'reviewed_by': self.reviewed_by,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'reviewed_at': self.reviewed_at.isoformat() if self.reviewed_at else None,
            'review_notes': self.review_notes,
            'compliance_score': self.compliance_score
        }