from flask import Blueprint, jsonify


from app.api.users import users_bp
from app.api.tasks import tasks_bp
from app.api.projects import projects_bp

# Create Blueprint for API routes
api_bp = Blueprint('api', __name__, url_prefix='/api')

# Register nested blueprints
api_bp.register_blueprint(users_bp, url_prefix='/users')
api_bp.register_blueprint(projects_bp, url_prefix='/projects')
api_bp.register_blueprint(tasks_bp, url_prefix='/tasks')


@api_bp.route('/')
def index():
    """API information endpoint"""
    return jsonify({
        'message': 'Task Manager API',
        'version': '1.0.0',
        'endpoints': [
            '/api/health/',
            '/api/users/',
            '/api/users/<int:user_id>/',
            '/api/projects/',
            '/api/tasks/'
        ]
    })


@api_bp.route('/health/')
def health():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'database': 'connected'})
