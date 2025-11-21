# Mini CRM (FastAPI)

A lightweight CRM backend built with **FastAPI**, designed for managing clients, deals, and tasks.  
Implements a clean architecture with layers: **API → Services → Repository → Database**.  
Includes authentication (JWT), role-based access control, logging, migrations, Docker setup, and comprehensive tests.

## 🔧 Features

- JWT-based authentication with user roles (`admin`, `manager`, `user`)  
- CRUD for users, clients, deals, and tasks  
- Filtering, searching, sorting for clients, deals & tasks
- Role-based access control  
- Alembic migrations for database schema management  
- Structured logging (info + error)  
- Docker support  
- Test coverage (78+ tests)  
- Pydantic schemas for request/response validation

## 📦 Technology Stack

- Python 3.x
- FastAPI  
- SQLAlchemy  
- PostgreSQL  
- Alembic  
- PyJWT  
- Pydantic  
- Docker  
- pytest / httpx  
- Logging via `logging.config`

## 🏗 Architecture
src/
  api/ # FastAPI controllers / routers
  services/ # Business logic
  repositories/ # Database access (SQLAlchemy)
  schemas/ # Pydantic models
  core/ # Config, logging, security
  database.py # DB setup
  models.py # ORM models
  enums.py
  main.py # Application entry point
  migrations/ # Alembic migrations
tests/ # Pytest test suite


## 🚀 Getting Started

1. **Clone the repository**  
   ```bash
   git clone https://github.com/Dafoe17/mini-crm-fastapi.git
   cd mini-crm-fastapi
   ```

2. Create a .env file
Use .env.example as a template

3. Run with Docker
   ```bash
   docker build -t image .
   docker run --name=server -p 9090:8000 --env-file .env image
   ```

4. Or run locally
  ```bash
  pip install -r requirements.txt
  alembic upgrade head
  uvicorn src.main:app --reload
  ```

5. Swagger / API Docs
Visit: http://localhost:8000/docs for API documentation

for Running Tests:
  ```bash
  pip install -r requirements-dev.txt
  pytest -vv
  ```

for Database Migrations:
  ```bash
  alembic revision --autogenerate -m "describe change"
  alembic upgrade head
  ```
