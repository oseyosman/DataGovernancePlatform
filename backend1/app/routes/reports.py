"""
Reports Routes - Report Management
Author: Osman Yildiz
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from backend1.app import db
from backend1.app.models.user import User
from backend1.app.models.report import Report

bp = Blueprint('reports', __name__, url_prefix='/api/reports')


@bp.route('/', methods=['GET'])
@jwt_required()
def get_reports():
    """Get all reports (filtered by user role)"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Admins see all reports, users see only their own
        if user.role == 'admin':
            reports = Report.query.order_by(Report.created_at.desc()).all()
        else:
            reports = Report.query.filter_by(created_by=user_id).order_by(Report.created_at.desc()).all()
        
        return jsonify({
            'reports': [report.to_dict() for report in reports],
            'total': len(reports)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/<int:report_id>', methods=['GET'])
@jwt_required()
def get_report(report_id):
    """Get specific report by ID"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        report = Report.query.get(report_id)
        if not report:
            return jsonify({'error': 'Report not found'}), 404
        
        # Check permissions
        if user.role != 'admin' and report.created_by != user_id:
            return jsonify({'error': 'Access denied'}), 403
        
        # Get creator and reviewer info
        creator = User.query.get(report.created_by)
        reviewer = User.query.get(report.reviewed_by) if report.reviewed_by else None
        
        report_data = report.to_dict()
        report_data['creator'] = creator.to_dict() if creator else None
        report_data['reviewer'] = reviewer.to_dict() if reviewer else None
        
        return jsonify(report_data), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/', methods=['POST'])
@jwt_required()
def create_report():
    """Create a new report"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['title', 'report_type']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Create new report
        report = Report(
            title=data['title'],
            description=data.get('description', ''),
            report_type=data['report_type'],
            status=data.get('status', 'draft'),
            priority=data.get('priority', 'medium'),
            created_by=user_id
        )
        
        db.session.add(report)
        db.session.commit()
        
        return jsonify({
            'message': 'Report created successfully',
            'report': report.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@bp.route('/<int:report_id>', methods=['PUT'])
@jwt_required()
def update_report(report_id):
    """Update a report"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        report = Report.query.get(report_id)
        if not report:
            return jsonify({'error': 'Report not found'}), 404
        
        # Check permissions
        if user.role != 'admin' and report.created_by != user_id:
            return jsonify({'error': 'Access denied'}), 403
        
        data = request.get_json()
        
        # Update fields if provided
        if 'title' in data:
            report.title = data['title']
        if 'description' in data:
            report.description = data['description']
        if 'report_type' in data:
            report.report_type = data['report_type']
        if 'status' in data:
            report.status = data['status']
        if 'priority' in data:
            report.priority = data['priority']
        
        db.session.commit()
        
        return jsonify({
            'message': 'Report updated successfully',
            'report': report.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@bp.route('/<int:report_id>/review', methods=['POST'])
@jwt_required()
def review_report(report_id):
    """Review a report (admin only)"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if user.role != 'admin':
            return jsonify({'error': 'Admin access required'}), 403
        
        report = Report.query.get(report_id)
        if not report:
            return jsonify({'error': 'Report not found'}), 404
        
        data = request.get_json()
        
        # Update review fields
        report.reviewed_by = user_id
        report.reviewed_at = datetime.utcnow()
        report.review_notes = data.get('review_notes', '')
        report.compliance_score = data.get('compliance_score')
        report.status = data.get('status', 'reviewed')
        
        db.session.commit()
        
        return jsonify({
            'message': 'Report reviewed successfully',
            'report': report.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@bp.route('/<int:report_id>', methods=['DELETE'])
@jwt_required()
def delete_report(report_id):
    """Delete a report"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        report = Report.query.get(report_id)
        if not report:
            return jsonify({'error': 'Report not found'}), 404
        
        # Check permissions
        if user.role != 'admin' and report.created_by != user_id:
            return jsonify({'error': 'Access denied'}), 403
        
        db.session.delete(report)
        db.session.commit()
        
        return jsonify({'message': 'Report deleted successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@bp.route('/stats', methods=['GET'])
@jwt_required()
def get_report_stats():
    """Get report statistics"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        # Get base query
        if user.role == 'admin':
            base_query = Report.query
        else:
            base_query = Report.query.filter_by(created_by=user_id)
        
        # Calculate statistics
        total = base_query.count()
        draft = base_query.filter_by(status='draft').count()
        submitted = base_query.filter_by(status='submitted').count()
        reviewed = base_query.filter_by(status='reviewed').count()
        approved = base_query.filter_by(status='approved').count()
        
        high_priority = base_query.filter_by(priority='high').count()
        critical_priority = base_query.filter_by(priority='critical').count()
        
        return jsonify({
            'total_reports': total,
            'by_status': {
                'draft': draft,
                'submitted': submitted,
                'reviewed': reviewed,
                'approved': approved
            },
            'high_priority': high_priority,
            'critical_priority': critical_priority
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500