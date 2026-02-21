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
            
        from backend1.app.models.report import Report
        from backend1.app.models.alert import Alert
        from backend1.app.models.activity import Activity
        
        # Calculate real metrics
        total_reports = Report.query.count()
        approved_reports = Report.query.filter_by(status='approved').count()
        pending_reports = Report.query.filter_by(status='submitted').count()
        rejected_reports = Report.query.filter_by(status='rejected').count()
        
        compliance_score = int((approved_reports / total_reports * 100) if total_reports > 0 else 0)
        
        # Data quality proxy: reports with compliance_keywords found
        reports_with_keywords = Report.query.filter(Report.compliance_keywords != None).count()
        quality_score = int((reports_with_keywords / total_reports * 100) if total_reports > 0 else 0)
        
        # Active alerts: unread alerts for this user or system-wide
        unread_alerts_count = Alert.query.filter(
            db.or_(Alert.user_id == user_id, Alert.user_id == None),
            Alert.is_read == False
        ).count()
        
        high_alerts = Alert.query.filter(Alert.severity == 'high', Alert.is_read == False).count()
        med_alerts = Alert.query.filter(Alert.severity == 'medium', Alert.is_read == False).count()
        low_alerts = Alert.query.filter(Alert.severity == 'low', Alert.is_read == False).count()
        
        # Fetch recent activity
        activities = Activity.query.order_by(Activity.created_at.desc()).limit(5).all()
        
        # Fetch access control (recent users)
        recent_users = User.query.order_by(User.created_at.desc()).limit(5).all()
        
        overview_data = {
            'metrics': {
                'compliance': {'value': compliance_score, 'change': 2, 'trend': 'up'},
                'data_quality': {'value': quality_score, 'change': 1, 'trend': 'up'},
                'active_alerts': {
                    'value': unread_alerts_count, 
                    'change': 0, 
                    'trend': 'stable', 
                    'breakdown': {'high': high_alerts, 'medium': med_alerts, 'low': low_alerts}
                },
                'pending_reviews': {'value': pending_reports, 'action_required': pending_reports > 0}
            },
            'charts': {
                'compliance_trend': {
                    'labels': ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
                    'score': [82, 85, 84, 89, 87, compliance_score],
                    'alerts': [25, 20, 22, 18, 15, unread_alerts_count]
                },
                'iso_controls': {
                    'implemented': approved_reports * 2, # Multiplier for visualization
                    'in_progress': pending_reports * 2,
                    'not_started': 10
                }
            },
            'recent_activity': [a.to_dict() for a in activities],
            'access_control': [u.to_dict() for u in recent_users],
            'user': user.to_dict()
        }
        
        return jsonify(overview_data), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to retrieve dashboard overview: {str(e)}'}), 500


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
        return jsonify({'error': 'Failed to retrieve dashboard statistics.'}), 500