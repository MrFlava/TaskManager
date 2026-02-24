import csv
from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Any, Optional

from main import create_app
from app.models import db, User as DBUser, Project as DBProject, Task as DBTask


@dataclass
class BaseEntity:
    """Base entity for all CSV records"""
    id: int
    title: str
    order: int


@dataclass
class User(BaseEntity):
    """User entity with email and password"""
    email: str
    password: str
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'User':
        return cls(
            id=int(data['id']),
            title=data['name'],
            order=0,
            email=data['email'],
            password=data['password']
        )


@dataclass
class Project(BaseEntity):
    """Project entity with description"""
    description: str
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Project':
        return cls(
            id=int(data['id']),
            title=data['title'],
            description=data['description'],
            order=int(data['order'])
        )


@dataclass
class Task(BaseEntity):
    """Task entity with description and creation date"""
    description: str
    created_at: str
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Task':
        return cls(
            id=int(data['id']),
            title=data['title'],
            description=data['description'],
            created_at=data['created_at'],
            order=int(data['order'])
        )


class CSVParserInterface(ABC):
    """Abstract interface for CSV parsers"""
    
    @abstractmethod
    def parse(self, file_path: Path) -> List[Any]:
        """Parse CSV file and return list of entities"""
        pass


class BaseCSVParser(CSVParserInterface):
    """Base CSV parser with common functionality"""
    
    def __init__(self, entity_class: type):
        self.entity_class = entity_class
    
    def parse(self, file_path: Path) -> List[Any]:
        """Parse CSV file and return list of entities"""
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        try:
            with file_path.open('r', newline='', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                return [self.entity_class.from_dict(row) for row in reader]
        except Exception as e:
            raise RuntimeError(f"Error parsing {file_path}: {e}")


class UserCSVParser(BaseCSVParser):
    """Parser for user CSV files"""
    def __init__(self):
        super().__init__(User)


class ProjectCSVParser(BaseCSVParser):
    """Parser for project CSV files"""
    def __init__(self):
        super().__init__(Project)


class TaskCSVParser(BaseCSVParser):
    """Parser for task CSV files"""
    def __init__(self):
        super().__init__(Task)


class CSVDataStore:
    """Data store for parsed CSV data"""
    
    def __init__(self):
        self._users: List[User] = []
        self._projects: List[Project] = []
        self._tasks: List[Task] = []
    
    @property
    def users(self) -> List[User]:
        return self._users
    
    @property
    def projects(self) -> List[Project]:
        return self._projects
    
    @property
    def tasks(self) -> List[Task]:
        return self._tasks
    
    def add_users(self, users: List[User]) -> None:
        self._users.extend(users)
    
    def add_projects(self, projects: List[Project]) -> None:
        self._projects.extend(projects)
    
    def add_tasks(self, tasks: List[Task]) -> None:
        self._tasks.extend(tasks)
    
    def get_summary(self) -> Dict[str, int]:
        """Get summary of parsed data"""
        return {
            'users': len(self._users),
            'projects': len(self._projects),
            'tasks': len(self._tasks)
        }


class CSVParsingService:
    """Service for orchestrating CSV parsing operations"""
    
    def __init__(self, data_store: CSVDataStore):
        self.data_store = data_store
        self.parsers = {
            'users': UserCSVParser(),
            'projects': ProjectCSVParser(),
            'tasks': TaskCSVParser()
        }
    
    def parse_file(self, file_type: str, file_path: Path) -> bool:
        """Parse a single CSV file"""
        if file_type not in self.parsers:
            raise ValueError(f"Unknown file type: {file_type}")
        
        try:
            entities = self.parsers[file_type].parse(file_path)
            
            if file_type == 'users':
                self.data_store.add_users(entities)
            elif file_type == 'projects':
                self.data_store.add_projects(entities)
            elif file_type == 'tasks':
                self.data_store.add_tasks(entities)
            
            return True
        except Exception as e:
            print(f"Error parsing {file_type}: {e}")
            return False
    
    def parse_all_files(self, file_paths: Dict[str, Path]) -> bool:
        """Parse all CSV files"""
        success = True
        
        for file_type, path in file_paths.items():
            if self.parse_file(file_type, path):
                print(f"Successfully parsed {len(getattr(self.data_store, file_type))} {file_type}")
            else:
                success = False
        
        return success


class ConsoleReporter:
    """Reporter for console output"""
    
    @staticmethod
    def print_header(message: str) -> None:
        """Print formatted header"""
        print(message)
        print("-" * 40)
    
    @staticmethod
    def print_separator() -> None:
        """Print separator line"""
        print("-" * 40)
    
    @staticmethod
    def print_summary(data_store: CSVDataStore) -> None:
        """Print parsing summary"""
        summary = data_store.get_summary()
        print("\n PARSING SUMMARY")
        print("=" * 50)
        for entity_type, count in summary.items():
            print(f"{entity_type.capitalize()}: {count}")
        
        if data_store.users:
            user = data_store.users[0]
            print(f"\nFirst user: {user.title} ({user.email})")
        if data_store.projects:
            project = data_store.projects[0]
            print(f"First project: {project.title}")
        if data_store.tasks:
            task = data_store.tasks[0]
            print(f"First task: {task.title}")


class DatabaseSaver:
    """Class to handle saving parsed CSV data to database"""
    
    def __init__(self):
        self.app = create_app()
    
    def save_users(self, users: List[User]) -> int:
        """Save users to database"""
        with self.app.app_context():
            saved_count = 0
            for user in users:
                # Check if user already exists
                existing_user = DBUser.query.filter_by(email=user.email).first()
                if existing_user:
                    print(f"User {user.email} already exists, skipping...")
                    continue
                
                # Create new database user
                db_user = DBUser(
                    name=user.title,
                    email=user.email,
                    password=user.password
                )
                db.session.add(db_user)
                saved_count += 1
            
            try:
                db.session.commit()
                print(f"Successfully saved {saved_count} users to database")
                return saved_count
            except Exception as e:
                db.session.rollback()
                print(f"Error saving users: {e}")
                return 0
    
    def save_projects(self, projects: List[Project]) -> int:
        """Save projects to database"""
        with self.app.app_context():
            saved_count = 0
            for project in projects:
                # Check if project already exists
                existing_project = DBProject.query.filter_by(title=project.title).first()
                if existing_project:
                    print(f"Project {project.title} already exists, skipping...")
                    continue
                
                # Create new database project
                db_project = DBProject(
                    title=project.title,
                    description=project.description,
                    order=project.order
                )
                db.session.add(db_project)
                saved_count += 1
            
            try:
                db.session.commit()
                print(f"Successfully saved {saved_count} projects to database")
                return saved_count
            except Exception as e:
                db.session.rollback()
                print(f"Error saving projects: {e}")
                return 0
    
    def save_tasks(self, tasks: List[Task]) -> int:
        """Save tasks to database"""
        with self.app.app_context():
            saved_count = 0
            for task in tasks:
                # Check if task already exists
                existing_task = DBTask.query.filter_by(title=task.title).first()
                if existing_task:
                    print(f"Task {task.title} already exists, skipping...")
                    continue
                
                # Find project by title (assuming CSV task has project info)
                # For now, we'll assign to first project or create a default one
                project = DBProject.query.first()
                if not project:
                    print("No projects found in database, skipping tasks...")
                    return 0
                
                # Create new database task
                db_task = DBTask(
                    title=task.title,
                    description=task.description,
                    order=task.order,
                    project_id=project.id
                )
                db.session.add(db_task)
                saved_count += 1
            
            try:
                db.session.commit()
                print(f"Successfully saved {saved_count} tasks to database")
                return saved_count
            except Exception as e:
                db.session.rollback()
                print(f"Error saving tasks: {e}")
                return 0
    
    def save_all_data(self, users: List[User], projects: List[Project], tasks: List[Task]) -> Dict[str, int]:
        """Save all parsed data to database"""
        print("\n Saving data to database...")
        print("-" * 40)
        
        results = {
            'users': self.save_users(users),
            'projects': self.save_projects(projects),
            'tasks': self.save_tasks(tasks)
        }
        
        print("-" * 40)
        total_saved = sum(results.values())
        print(f"Total records saved: {total_saved}")
        
        return results


class CSVParserApp:
    """Main application class"""
    
    def __init__(self, base_path: Optional[Path] = None):
        self.base_path = base_path or Path(__file__).parent
        self.data_store = CSVDataStore()
        self.parsing_service = CSVParsingService(self.data_store)
        self.reporter = ConsoleReporter()
        self.db_saver = DatabaseSaver()
    
    def get_file_paths(self) -> Dict[str, Path]:
        """Get file paths for all CSV files"""
        return {
            'users': self.base_path / "Task Manager - Users_Projects_Tasks - Users.csv",
            'projects': self.base_path / "Task Manager - Users_Projects_Tasks - Projects.csv",
            'tasks': self.base_path / "Task Manager - Users_Projects_Tasks - Tasks.csv"
        }
    
    def run(self, save_to_db: bool = False) -> bool:
        """Run the CSV parsing application"""
        self.reporter.print_header("Starting CSV parsing...")
        
        file_paths = self.get_file_paths()
        success = self.parsing_service.parse_all_files(file_paths)
        
        self.reporter.print_separator()
        
        if success:
            print("All files parsed successfully!")
            self.reporter.print_summary(self.data_store)
            
            # Save to database if requested
            if save_to_db:
                self.db_saver.save_all_data(
                    self.data_store.users,
                    self.data_store.projects,
                    self.data_store.tasks
                )
        else:
            print("Some files failed to parse")
        
        return success
    
    def get_data(self) -> Dict[str, List[Any]]:
        """Get all parsed data"""
        return {
            'users': self.data_store.users,
            'projects': self.data_store.projects,
            'tasks': self.data_store.tasks
        }


def main() -> None:
    """Main entry point"""
    import sys
    
    # Check command line arguments
    save_to_db = '--save-to-db' in sys.argv or '-db' in sys.argv
    
    app = CSVParserApp()
    
    if save_to_db:
        print("Database saving mode enabled")
    
    app.run(save_to_db=save_to_db)


if __name__ == "__main__":
    main()
