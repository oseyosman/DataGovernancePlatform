"""
Activity Model - User activity tracking
Author: Osman Yildiz
"""
from datetime import datetime
from backend1.app import db


class Activity(db.Model):
    """Activity model for tracking user actions"""
    __tablename__ = 'activities'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    action = db.Column(db.String(100), nullable=False)  # "login", "create_user", "approve_report", etc.
    table_name = db.Column(db.String(50), nullable=True)
    record_id = db.Column(db.Integer, nullable=True)
    
    description = db.Column(db.Text, nullable=True)
    ip_address = db.Column(db.String(45), nullable=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref=db.backref('activities', lazy=True))
    
    def __repr__(self):
        return f'<Activity {self.user_id}: {self.action}>'
    
    def to_dict(self):
        """Convert activity object to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'username': self.user.username if self.user else 'Unknown',
            'action': self.action,
            'table_name': self.table_name,
            'record_id': self.record_id,
            'description': self.description,
            'ip_address': self.ip_address,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
