"""
Dashboard routes

Author: Osman Yildiz
"""
from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.user import User

bp = Blueprint('dashboard', __name__, url_prefix='/api/dashboard')

@bp.route('/overview', methods=['GET'])
@jwt_required()
def get_overview():
    """Get dashboard overview statistics"""
    
    # Get current user
    user_id = get_jwt_identity()
    current_user = User.query.get(user_id)
    
    # Get statistics
    total_users = User.query.count()
    active_users = User.query.filter_by(is_active=True).count()
    
    # Count by role
    admins = User.query.filter_by(role='admin').count()
    compliance_officers = User.query.filter_by(role='compliance_officer').count()
    data_stewards = User.query.filter_by(role='data_steward').count()
    viewers = User.query.filter_by(role='viewer').count()
    
    return jsonify({
        'message': 'Dashboard overview loaded successfully',
        'current_user': current_user.to_dict(),
        'statistics': {
            'total_users': total_users,
            'active_users': active_users,
            'inactive_users': total_users - active_users,
            'users_by_role': {
                'admin': admins,
                'compliance_officer': compliance_officers,
                'data_steward': data_stewards,
                'viewer': viewers
            }
        },
        'placeholder_metrics': {
            'total_datasets': 0,
            'avg_data_quality_score': 0,
            'compliance_controls': 0,
            'active_alerts': 0
        }
    }), 200


@bp.route('/stats', methods=['GET'])
@jwt_required()
def get_stats():
    """Get detailed statistics"""
    
    return jsonify({
        'message': 'Detailed statistics endpoint',
        'note': 'This will be implemented in later phases'
    }), 200