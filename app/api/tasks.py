from flask import Blueprint, jsonify

from app.models import Task


# Create Blueprint for tasks routes
tasks_bp = Blueprint('tasks', __name__)

@tasks_bp.route('/')
def test_tasks():
    """Test endpoint to list all tasks"""
    try:
        tasks = Task.query.all()
        return jsonify({
            'status': 'success',
            'count': len(tasks),
            'tasks': [task.to_dict() for task in tasks]
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500
