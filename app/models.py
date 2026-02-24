from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Table
from sqlalchemy.orm import relationship
from datetime import datetime
from app import db

# Association table for many-to-many relationship between Project and User
# Only 3 users can be on a single project (enforced at application level)
project_users = Table(
    'project_users',
    db.metadata,
    Column('project_id', Integer, ForeignKey('projects.id'), primary_key=True),
    Column('user_id', Integer, ForeignKey('users.id'), primary_key=True),
    Column('assigned_at', DateTime, default=datetime.utcnow)
)


class User(db.Model):
    """User model representing system users"""
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    email = Column(String(120), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Many-to-many relationship with projects
    projects = relationship(
        "Project",
        secondary=project_users,
        back_populates="users"
    )

    def __repr__(self):
        return f"<User(id={self.id}, name='{self.name}', email='{self.email}')>"

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class Project(db.Model):
    """Project model representing work projects"""
    __tablename__ = 'projects'

    id = Column(Integer, primary_key=True)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    order = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # One-to-many relationship with tasks
    tasks = relationship("Task", back_populates="project", cascade="all, delete-orphan")

    # Many-to-many relationship with users
    users = relationship(
        "User",
        secondary=project_users,
        back_populates="projects"
    )

    def __repr__(self):
        return f"<Project(id={self.id}, title='{self.title}')>"

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'order': self.order,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'user_count': len(self.users) if self.users else 0
        }

    def add_user(self, user):
        """Add user to project with validation (max 3 users)"""
        if len(self.users) >= 3:
            raise ValueError(f"Project {self.title} already has maximum 3 users")
        if user not in self.users:
            self.users.append(user)

    def can_add_user(self):
        """Check if project can accept more users"""
        return len(self.users) < 3


class Task(db.Model):
    """Task model representing individual tasks within projects"""
    __tablename__ = 'tasks'

    id = Column(Integer, primary_key=True)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    order = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Foreign key to Project (many-to-one relationship)
    project_id = Column(Integer, ForeignKey('projects.id'), nullable=False)

    # Relationship back to Project
    project = relationship("Project", back_populates="tasks")

    def __repr__(self):
        return f"<Task(id={self.id}, title='{self.title}', project_id={self.project_id})>"

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'order': self.order,
            'project_id': self.project_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


# Database utility functions
def create_tables(engine):
    """Create all database tables"""
    db.metadata.create_all(engine)


def drop_tables(engine):
    """Drop all database tables"""
    db.metadata.drop_all(engine)


# Model validation utilities
class ModelValidator:
    """Utility class for model validation"""

    @staticmethod
    def validate_project_user_count(project, user_to_add=None):
        """Validate that project doesn't exceed 3 users"""
        current_users = len(project.users) if project.users else 0

        if user_to_add and user_to_add in project.users:
            return True  # User already assigned, no change

        if current_users >= 3:
            raise ValueError(f"Project '{project.title}' already has maximum 3 users")

        return True

    @staticmethod
    def validate_task_project(task):
        """Validate that task has a valid project"""
        if not task.project:
            raise ValueError("Task must be assigned to a project")
        return True
