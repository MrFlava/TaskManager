from flask import Blueprint, jsonify, request

from app.models import Project, User, db

# Create Blueprint for projects routes
projects_bp = Blueprint('projects', __name__)


@projects_bp.route('/')
def get_projects():
    """Test endpoint to list all projects"""
    try:
        projects = Project.query.all()
        return jsonify({
            'status': 'success',
            'count': len(projects),
            'projects': [project.to_dict() for project in projects]
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@projects_bp.route('/<int:project_id>/users/', methods=['POST'])
def add_user_to_project(project_id: int):
    try:
        data = request.get_json(silent=True) or {}
        email = data.get('email')
        if not email:
            return jsonify({'status': 'error', 'message': 'Missing required field: email'}), 400

        project = Project.query.get_or_404(project_id)
        user = User.query.filter_by(email=email).first()
        if not user:
            return jsonify({'status': 'error', 'message': 'User not found'}), 404

        if user in project.users:
            return jsonify({'status': 'success', 'message': 'User already in project', 'project': project.to_dict()}), 200

        try:
            project.add_user(user)
        except ValueError as e:
            return jsonify({'status': 'error', 'message': str(e)}), 400

        db.session.commit()
        return jsonify({'status': 'success', 'message': 'User added to project', 'project': project.to_dict()}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 500
