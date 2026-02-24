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

    @app.route('/health')
    def health():
        return jsonify({'status': 'healthy', 'database': 'connected'})

    @app.route('/test/users')
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

    @app.route('/test/projects')
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

    @app.route('/test/tasks')
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

    @app.route('/test/create-sample-data')
    def create_sample_data():
        try:
            # Create sample users
            user1 = User(name='John Doe', email='john@example.com', password='password123')
            user2 = User(name='Jane Smith', email='jane@example.com', password='password456')
            user3 = User(name='Mike Johnson', email='mike@example.com', password='password789')

            db.session.add_all([user1, user2, user3])
            db.session.commit()

            # Create sample project
            project = Project(title='Sample Project', description='A test project', order=1)
            project.add_user(user1)
            project.add_user(user2)

            db.session.add(project)
            db.session.commit()

            # Create sample tasks
            task1 = Task(title='Setup Database', description='Initialize the database', order=1, project_id=project.id)
            task2 = Task(title='Create API', description='Build REST API endpoints', order=2, project_id=project.id)

            db.session.add_all([task1, task2])
            db.session.commit()

            return jsonify({
                'status': 'success',
                'message': 'Sample data created successfully',
                'users': len([user1, user2, user3]),
                'projects': 1,
                'tasks': 2
            })
        except Exception as e:
            db.session.rollback()
            return jsonify({'status': 'error', 'message': str(e)}), 500

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
