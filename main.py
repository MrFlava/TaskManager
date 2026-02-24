from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from app.models import db, User, Project, Task
import os


def create_app():
    app = Flask(__name__)

    # Configuration
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///app.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Initialize extensions
    db.init_app(app)
    migrate = Migrate(app, db)

    # Routes
    @app.route('/')
    def index():
        return jsonify({
            'message': 'Task Manager API',
            'version': '1.0.0',
            'endpoints': [
                '/health',
                '/test/users',
                '/test/projects',
                '/test/tasks'
            ]
        })

    @app.route('/health/')
    def health():
        return jsonify({'status': 'healthy', 'database': 'connected'})

    @app.route('/test/users/')
    def test_users():
        try:
            users = User.query.all()
            return jsonify({
                'status': 'success',
                'count': len(users),
                'users': [user.to_dict() for user in users]
            })
        except Exception as e:
            return jsonify({'status': 'error', 'message': str(e)}), 500

    @app.route('/test/projects/')
    def test_projects():
        try:
            projects = Project.query.all()
            return jsonify({
                'status': 'success',
                'count': len(projects),
                'projects': [project.to_dict() for project in projects]
            })
        except Exception as e:
            return jsonify({'status': 'error', 'message': str(e)}), 500

    @app.route('/test/tasks/')
    def test_tasks():
        try:
            tasks = Task.query.all()
            return jsonify({
                'status': 'success',
                'count': len(tasks),
                'tasks': [task.to_dict() for task in tasks]
            })
        except Exception as e:
            return jsonify({'status': 'error', 'message': str(e)}), 500

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
