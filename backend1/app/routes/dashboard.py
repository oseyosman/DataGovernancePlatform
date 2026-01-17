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
        # Mock data matching the new design
        overview_data = {
            'metrics': {
                'compliance': {'value': 87, 'change': 3, 'trend': 'up'},
                'data_quality': {'value': 92, 'change': 2, 'trend': 'up'},
                'active_alerts': {'value': 15, 'change': -5, 'trend': 'down', 'breakdown': {'high': 3, 'medium': 7, 'low': 5}},
                'pending_reviews': {'value': 8, 'action_required': True}
            },
            'charts': {
                'compliance_trend': {
                    'labels': ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
                    'score': [82, 85, 84, 89, 87, 88],
                    'alerts': [25, 20, 22, 18, 15, 12]
                },
                'iso_controls': {
                    'implemented': 56,
                    'in_progress': 31,
                    'not_started': 13
                }
            },
            'compliance_details': {
                'iso_27001': [
                    {'name': 'Access Control', 'score': 92, 'status': 'good'},
                    {'name': 'Information Security', 'score': 88, 'status': 'good'},
                    {'name': 'Operations Security', 'score': 75, 'status': 'warning'}
                ],
                'iso_27017': [
                    {'name': 'Cloud Access Control', 'score': 90, 'status': 'good'},
                    {'name': 'Virtual Network Security', 'score': 85, 'status': 'good'},
                    {'name': 'Cloud Asset Management', 'score': 70, 'status': 'warning'}
                ],
                'policies': [
                    {'name': 'Privacy Policy', 'completion': 95},
                    {'name': 'Security Policy', 'completion': 88},
                    {'name': 'Data Handling Policy', 'completion': 82}
                ]
            },
            'recent_activity': [
                {
                    'id': 1,
                    'type': 'Access request approved',
                    'timestamp': '5 hours ago',
                    'status': 'success',
                    'priority': 'low'
                },
                {
                    'id': 2,
                    'type': 'Compliance report generated',
                    'timestamp': '6 hours ago',
                    'status': 'success',
                    'priority': 'low'
                },
                {
                    'id': 3,
                    'type': 'Unauthorized access attempt blocked',
                    'timestamp': '8 hours ago',
                    'status': 'danger',
                    'priority': 'high'
                },
                {
                    'id': 4,
                    'type': 'Policy violation detected',
                    'timestamp': '2 hours ago',
                    'status': 'danger',
                    'priority': 'high'
                },
                 {
                    'id': 5,
                    'type': 'Data quality scan completed',
                    'timestamp': '3 hours ago',
                    'status': 'success',
                    'priority': 'low'
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