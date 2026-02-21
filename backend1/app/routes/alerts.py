"""
Alerts Routes - System Notifications
Author: Osman Yildiz
"""
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from backend1.app import db
from backend1.app.models.alert import Alert

bp = Blueprint('alerts', __name__, url_prefix='/api/alerts')


@bp.route('/', methods=['GET'])
@jwt_required()
def get_alerts():
    """Get alerts for the current user and system-wide alerts"""
    try:
        user_id = get_jwt_identity()
        
        # Fetch user-specific and system-wide (user_id is null) alerts
        alerts = Alert.query.filter(
            db.or_(Alert.user_id == user_id, Alert.user_id == None)
        ).order_by(Alert.created_at.desc()).limit(50).all()
        
        return jsonify({
            'alerts': [alert.to_dict() for alert in alerts],
            'unread_count': len([a for a in alerts if not a.is_read])
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/<int:alert_id>/read', methods=['PUT'])
@jwt_required()
def mark_read(alert_id):
    """Mark an alert as read"""
    try:
        user_id = get_jwt_identity()
        alert = Alert.query.get(alert_id)
        
        if not alert:
            return jsonify({'error': 'Alert not found'}), 404
        
        # Ensure user has permission (can mark read their own or system-wide)
        if alert.user_id and alert.user_id != user_id:
            return jsonify({'error': 'Unauthorized'}), 403
            
        alert.is_read = True
        alert.read_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({'message': 'Alert marked as read'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@bp.route('/read-all', methods=['PUT'])
@jwt_required()
def mark_all_read():
    """Mark all alerts for current user as read"""
    try:
        user_id = get_jwt_identity()
        
        Alert.query.filter_by(user_id=user_id, is_read=False).update({
            'is_read': True,
            'read_at': datetime.utcnow()
        })
        
        db.session.commit()
        
        return jsonify({'message': 'All alerts marked as read'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
