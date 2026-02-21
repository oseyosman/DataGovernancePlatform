"""
Alert Model - System notifications and alerts
Author: Osman Yildiz
"""
from datetime import datetime
from backend1.app import db


class Alert(db.Model):
    """Alert model for storing system notifications"""
    __tablename__ = 'alerts'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)  # Null for system-wide alerts
    
    alert_type = db.Column(db.String(50), nullable=False)  # "compliance", "access", "system"
    severity = db.Column(db.String(20), nullable=False, default='medium')  # "low", "medium", "high", "critical"
    message = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    read_at = db.Column(db.DateTime, nullable=True)
    
    # Relationships
    user = db.relationship('User', backref=db.backref('alerts', lazy=True))
    
    def __repr__(self):
        return f'<Alert {self.alert_type}: {self.severity}>'
    
    def to_dict(self):
        """Convert alert object to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'alert_type': self.alert_type,
            'severity': self.severity,
            'message': self.message,
            'is_read': self.is_read,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'read_at': self.read_at.isoformat() if self.read_at else None
        }
