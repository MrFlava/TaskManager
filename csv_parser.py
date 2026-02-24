import csv
import os
from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Any, Optional


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
            print(f"✗ Error parsing {file_type}: {e}")
            return False
    
    def parse_all_files(self, file_paths: Dict[str, Path]) -> bool:
        """Parse all CSV files"""
        success = True
        
        for file_type, path in file_paths.items():
            if self.parse_file(file_type, path):
                print(f"✓ Successfully parsed {len(getattr(self.data_store, file_type))} {file_type}")
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


class CSVParserApp:
    """Main application class"""
    
    def __init__(self, base_path: Optional[Path] = None):
        self.base_path = base_path or Path(__file__).parent
        self.data_store = CSVDataStore()
        self.parsing_service = CSVParsingService(self.data_store)
        self.reporter = ConsoleReporter()
    
    def get_file_paths(self) -> Dict[str, Path]:
        """Get file paths for all CSV files"""
        return {
            'users': self.base_path / "Task Manager - Users_Projects_Tasks - Users.csv",
            'projects': self.base_path / "Task Manager - Users_Projects_Tasks - Projects.csv",
            'tasks': self.base_path / "Task Manager - Users_Projects_Tasks - Tasks.csv"
        }
    
    def run(self) -> bool:
        """Run the CSV parsing application"""
        self.reporter.print_header("Starting CSV parsing...")
        
        file_paths = self.get_file_paths()
        success = self.parsing_service.parse_all_files(file_paths)
        
        self.reporter.print_separator()
        
        if success:
            print("All files parsed successfully!")
            self.reporter.print_summary(self.data_store)
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
    app = CSVParserApp()
    app.run()


if __name__ == "__main__":
    main()
