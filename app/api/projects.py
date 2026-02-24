from flask import Blueprint, jsonify, request
from pydantic import ValidationError

from app.models import Project, User, db
from app.api.schemas import (
    ProjectAddUserIn,
    ProjectOut,
    ProjectsListOut,
    ProjectUserChangedOut,
    validation_error_payload,
)

# Create Blueprint for projects routes
projects_bp = Blueprint('projects', __name__)


@projects_bp.route('/')
def get_projects():
    """Test endpoint to list all projects"""
    try:
        projects = Project.query.all()
        payload = ProjectsListOut(
            count=len(projects),
            projects=[ProjectOut(**project.to_dict()) for project in projects],
        ).model_dump()
        return jsonify(payload)
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@projects_bp.route('/<int:project_id>/users/', methods=['POST'])
def add_user_to_project(project_id: int):
    try:
        data = request.get_json(silent=True) or {}
        try:
            payload_in = ProjectAddUserIn.model_validate(data)
        except ValidationError as ve:
            return jsonify(validation_error_payload(ve)), 422

        project = Project.query.get_or_404(project_id)
        user = User.query.filter_by(email=str(payload_in.email)).first()
        if not user:
            return jsonify({'status': 'error', 'message': 'User not found'}), 404

        if user in project.users:
            payload = ProjectUserChangedOut(
                message='User already in project',
                project=ProjectOut(**project.to_dict()),
            ).model_dump()
            return jsonify(payload), 200

        try:
            project.add_user(user)
        except ValueError as e:
            return jsonify({'status': 'error', 'message': str(e)}), 400

        db.session.commit()
        payload = ProjectUserChangedOut(
            message='User added to project',
            project=ProjectOut(**project.to_dict()),
        ).model_dump()
        return jsonify(payload), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 500
