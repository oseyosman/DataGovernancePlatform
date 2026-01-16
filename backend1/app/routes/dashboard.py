"""
Dashboard Routes
Author: Osman Yildiz
"""
from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from backend1.app import db
from backend1.app.models.user import User

bp = Blueprint('dashboard', __name__, url_prefix='/api/dashboard')


@bp.route('/overview', methods=['GET'])
@jwt_required()
def get_overview():
    """Get dashboard overview data"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Mock data for now - will be replaced with real data
        overview_data = {
            'total_assets': 1234,
            'compliant_assets': 1100,
            'non_compliant_assets': 134,
            'compliance_score': 89.1,
            'recent_activities': [
                {
                    'id': 1,
                    'type': 'Data Classification',
                    'description': 'Customer data classified as PII',
                    'timestamp': '2024-01-15T10:30:00Z'
                },
                {
                    'id': 2,
                    'type': 'Access Review',
                    'description': 'Quarterly access review completed',
                    'timestamp': '2024-01-14T15:45:00Z'
                }
            ],
            'user': user.to_dict()
        }
        
        return jsonify(overview_data), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/stats', methods=['GET'])
@jwt_required()
def get_stats():
    """Get dashboard statistics"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Mock statistics data
        stats = {
            'data_assets': {
                'total': 1234,
                'databases': 45,
                'files': 890,
                'apis': 299
            },
            'compliance': {
                'gdpr': 92.5,
                'hipaa': 87.3,
                'sox': 95.1
            },
            'risks': {
                'high': 12,
                'medium': 45,
                'low': 123
            }
        }
        
        return jsonify(stats), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500