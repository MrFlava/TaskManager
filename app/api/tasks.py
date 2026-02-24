from flask import Blueprint, jsonify, request

from app.models import Project, Task, User


# Create Blueprint for tasks routes
tasks_bp = Blueprint('tasks', __name__)


@tasks_bp.route('/project/<int:project_id>/')
def tasks_by_project(project_id: int):
    """List tasks for a given project if user (by email) is assigned to it, with pagination."""
    try:
        email = request.args.get('email')
        if not email:
            return jsonify({'status': 'error', 'message': 'Missing required query param: email'}), 400

        user = User.query.filter_by(email=email).first()
        if not user:
            return jsonify({'status': 'error', 'message': 'User not found'}), 404

        project = Project.query.get_or_404(project_id)
        if user not in project.users:
            return jsonify({'status': 'error', 'message': 'Forbidden'}), 403

        try:
            page = int(request.args.get('page', 1))
            per_page = int(request.args.get('per_page', 10))
        except ValueError:
            return jsonify({'status': 'error', 'message': 'page and per_page must be integers'}), 400

        if page < 1:
            return jsonify({'status': 'error', 'message': 'page must be >= 1'}), 400

        if per_page < 1:
            return jsonify({'status': 'error', 'message': 'per_page must be >= 1'}), 400

        per_page = min(per_page, 100)

        query = Task.query.filter_by(project_id=project_id).order_by(Task.order.asc(), Task.id.asc())
        total = query.count()
        items = query.offset((page - 1) * per_page).limit(per_page).all()
        pages = (total + per_page - 1) // per_page if per_page else 0

        return jsonify({
            'status': 'success',
            'project_id': project_id,
            'user_email': email,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': total,
                'pages': pages,
            },
            'tasks': [task.to_dict() for task in items],
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500
