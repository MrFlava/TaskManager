from flask import Blueprint, jsonify, request
from pydantic import ValidationError

from app.models import Project, Task, User
from app.api.schemas import (
    Pagination,
    TaskOut,
    TasksByProjectOut,
    TasksByProjectQuery,
    validation_error_payload,
)


# Create Blueprint for tasks routes
tasks_bp = Blueprint('tasks', __name__)


@tasks_bp.route('/project/<int:project_id>/')
def tasks_by_project(project_id: int):
    """List tasks for a given project if user (by email) is assigned to it, with pagination."""
    try:
        try:
            query_in = TasksByProjectQuery.model_validate(dict(request.args))
        except ValidationError as ve:
            return jsonify(validation_error_payload(ve)), 422

        user = User.query.filter_by(email=str(query_in.email)).first()
        if not user:
            return jsonify({'status': 'error', 'message': 'User not found'}), 404

        project = Project.query.get_or_404(project_id)
        if user not in project.users:
            return jsonify({'status': 'error', 'message': 'Forbidden'}), 403

        query = Task.query.filter_by(project_id=project_id).order_by(Task.order.asc(), Task.id.asc())
        total = query.count()
        items = query.offset((query_in.page - 1) * query_in.per_page).limit(query_in.per_page).all()
        pages = (total + query_in.per_page - 1) // query_in.per_page if query_in.per_page else 0

        payload = TasksByProjectOut(
            project_id=project_id,
            user_email=query_in.email,
            pagination=Pagination(
                page=query_in.page,
                per_page=query_in.per_page,
                total=total,
                pages=pages,
            ),
            tasks=[TaskOut(**task.to_dict()) for task in items],
        ).model_dump()
        return jsonify(payload)
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500
