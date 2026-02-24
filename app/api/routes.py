from flask import Blueprint, jsonify
from app.models import db, User, Project, Task

# Create Blueprint for API routes
api_bp = Blueprint('api', __name__, url_prefix='/api')


@api_bp.route('/')
def index():
    """API information endpoint"""
    return jsonify({
        'message': 'Task Manager API',
        'version': '1.0.0',
        'endpoints': [
            '/api/health/',
            '/api/users/',
            '/api/projects/',
            '/api/tasks/'
        ]
    })


@api_bp.route('/health/')
def health():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'database': 'connected'})


@api_bp.route('/users/')
def test_users():
    """Test endpoint to list all users"""
    try:
        users = User.query.all()
        return jsonify({
            'status': 'success',
            'count': len(users),
            'users': [user.to_dict() for user in users]
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@api_bp.route('/projects/')
def test_projects():
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


@api_bp.route('/tasks/')
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
