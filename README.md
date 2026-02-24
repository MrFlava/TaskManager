# Task Manager API

A Flask-based task management system with PostgreSQL database, Docker deployment, and database migrations.

## Features

- **User Management**: Create and manage users
- **Project Management**: Projects with max 3 users per project
- **Task Management**: Tasks belonging to projects
- **Database Migrations**: Flask-Migrate for schema changes
- **Docker Support**: Complete containerized setup
- **REST API**: JSON endpoints for all operations

## Quick Start

### Using Docker (Recommended)

1. **Manually:**
   ```bash
   # Create .env file
   cp .env.example .env
   
   # Build and start containers
   docker-compose build
   docker-compose up -d
   
   # Initialize database
   docker-compose exec web flask db init
   docker-compose exec web flask db migrate -m "Initial migration"
   docker-compose exec web flask db upgrade
   ```

2. **Test the API:**
   ```bash
   curl http://localhost:8001/
   curl http://localhost:8001/api/
   curl http://localhost:8001/api/health/
   ```

### Manual Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up PostgreSQL database** and update `.env` file

3. **Initialize migrations:**
   ```bash
   flask db init
   flask db migrate -m "Initial migration"
   flask db upgrade
   ```

4. **Run the app:**
   ```bash
   flask run --host=0.0.0.0 --port=8001
   ```

## API Endpoints

### API Endpoints

#### Base Endpoints
- `GET /` - API information and available endpoints
- `GET /api/` - API information and available endpoints
- `GET /api/health` - Health check

#### User Endpoints
- `GET /api/users/` - List all users
- `POST /api/users/` - Create a new user
- `GET /api/users/<user_id>/` - Get user by ID
- `PATCH /api/users/<user_id>/` - Update user (partial update allowed)
- `DELETE /api/users/<user_id>/` - Delete user (requires password)

#### Test Endpoints
- `GET /api/projects/` - List all projects
- `GET /api/tasks/` - List all tasks

### Task Operations

#### List tasks in a project (requires user email + pagination)
```bash
curl "http://localhost:8001/api/tasks/project/1/?email=john@example.com&page=1&per_page=10"
```

### Project Operations

#### Add existing user to a project (by email)
```bash
curl -X POST http://localhost:8001/api/projects/1/users/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john@example.com"
  }'
```

## API Usage Examples

### User Operations

#### Create User
```bash
curl -X POST http://localhost:8001/api/users/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe",
    "email": "john@example.com",
    "password": "password123"
  }'
```

#### List Users
```bash
curl http://localhost:8001/api/users/
```

#### Get User by ID
```bash
curl http://localhost:8001/api/users/1/
```

#### Update User (Partial)
```bash
curl -X PATCH http://localhost:8001/api/users/1/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Updated"
  }'
```

#### Validation errors
If the request body (or query params) is invalid, the API returns **422** with Pydantic error details.

#### Delete User
```bash
curl -X DELETE http://localhost:8001/api/users/1/ \
  -H "Content-Type: application/json" \
  -d '{
    "password": "password123"
  }'
```

## Database Schema

### Users
- `id` (Primary Key)
- `name` (String, 100 chars)
- `email` (String, 120 chars, unique)
- `password` (String, 255 chars)
- `created_at` (DateTime)

### Projects
- `id` (Primary Key)
- `title` (String, 200 chars)
- `description` (Text)
- `order` (Integer)
- `created_at` (DateTime)
- `updated_at` (DateTime)

### Tasks
- `id` (Primary Key)
- `title` (String, 200 chars)
- `description` (Text)
- `order` (Integer)
- `project_id` (Foreign Key to Projects)
- `created_at` (DateTime)
- `updated_at` (DateTime)

### Relationships
- **Project ↔ User**: Many-to-many (max 3 users per project)
- **Project → Task**: One-to-many

## Database Migrations

### Create new migration
```bash
docker-compose exec web flask db migrate -m "Description of changes"
```

### Apply migrations
```bash
docker-compose exec web flask db upgrade
```

### Rollback migration
```bash
docker-compose exec web flask db downgrade
```

## Docker Commands

### Start services
```bash
docker-compose up -d
```

### Stop services
```bash
docker-compose down
```

### View logs
```bash
docker-compose logs -f web
docker-compose logs -f db
```

### Execute commands in container
```bash
docker-compose exec web bash
docker-compose exec db psql -U taskuser -d taskmanager
```

## Environment Variables

Using a `.env` file is **optional**.

- When you run via **docker-compose**, variables are already provided in `docker-compose.yml`.
- When you run locally via the **Flask CLI** (`flask run`, `flask db ...`), a `.env` file is a convenient way to provide configuration without exporting variables in your shell.

### Recommended variables

Create a `.env` file with:

```env
FLASK_APP=main.py
FLASK_ENV=development
FLASK_DEBUG=1
DATABASE_URL=postgresql://taskuser:taskpass@localhost:5432/taskmanager
SECRET_KEY=change-me
```

Notes:

- **`DATABASE_URL`** is the most important variable (switch DBs without changing code).
- **`SECRET_KEY`** becomes important once you use sessions/auth/CSRF.

## Pydantic Schemas

Request validation and response formatting use **Pydantic** schemas located in `app/api/schemas.py`.

- **[validation]** Invalid request bodies / query parameters return **422** with Pydantic error details.
- **[responses]** Successful responses are serialized via response schema models (for consistent shapes).

## Development

### Adding new models
1. Update `app/models.py`
2. Create migration: `flask db migrate -m "Add new model"`
3. Apply migration: `flask db upgrade`

### Adding new endpoints
1. Add/update Blueprints in `app/api/` (for example `users.py`, `projects.py`, `tasks.py`)
2. Restart the container: `docker-compose restart web`

## Tests

API tests are written with **pytest** under `tests/` and use **mocks** (no real database required).

Run locally:

```bash
pytest -q
```

Notes:

- **[app context]** `tests/conftest.py` creates the Flask app via `main.create_app()` and pushes an application context.
- **[mocking]** Tests monkeypatch `Model.query` and `db.session` to control behavior and assert commits/deletes.

## Database Access

### Connection details
- **Host**: localhost
- **Port**: 5432
- **Database**: taskmanager
- **Username**: taskuser
- **Password**: taskpass

### Connect with psql
```bash
docker-compose exec db psql -U taskuser -d taskmanager
```

## Troubleshooting

### Database connection issues
1. Check if PostgreSQL is running: `docker-compose ps`
2. Check database logs: `docker-compose logs db`
3. Verify environment variables in `.env`

### Migration issues
1. Check migration status: `docker-compose exec web flask db current`
2. View migration history: `docker-compose exec web flask db history`
3. Reset database (caution): `docker-compose exec web flask db downgrade base`
