from flask import Flask
from flask_migrate import Migrate

from app.models import db
from app.api.routes import api_bp
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

    # Register API Blueprint
    app.register_blueprint(api_bp)

    # Root route redirects to API
    @app.route('/')
    def index():
        return {
            'message': 'Task Manager API',
            'version': '1.0.0',
            'api_base_url': '/api',
            'endpoints': [
                '/api/',
                '/api/health',
                '/api/test/users',
                '/api/test/projects',
                '/api/test/tasks'
            ]
        }

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
