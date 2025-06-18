# LEIA beheeromgeving Web App - Svelte + FastAPI + PostgreSQL

Gebruikt om de JSON configuratie files van LEIA digital twins te beheren.

## Clone
```sh
git clone https://github.com/ElwinMan/LEIA_beheeromgeving.git
cd LEIA_beheeromgeving
```
## Build

### With docker

```sh
docker compose up --build
```

Svelte frontend: http://localhost:8080/

FastAPI backend: http://localhost:8000/
API docs: http://localhost:8000/docs

PostgreSQL: http://localhost:5432/

## Backend manage tool
This manage.py script provides a simple command-line interface to manage your database. It supports dropping tables, creating tables, running migrations, seeding data, and running a full reset (fresh) combining all steps.

### Usage
Run the script with Python and pass one of the following commands: 
```sh
python -m scripts.manage [command]
```
### Commands
- drop  
Drops all tables in the database. Use with caution as this deletes all data.

- create  
Creates all tables based on your SQLAlchemy models (without migrations).

- migrate  
Runs Alembic migrations to update the database schema to the latest version.

- seed  
Runs the seeding scripts to populate the database with initial or sample data.

- fresh  
Drops all tables, runs migrations, and seeds the database. Use this for a full reset of the database.

## Alembic

### Creating Migrations
When you add or modify tables, columns, or relationships in your SQLAlchemy models, generate a new Alembic migration by running the following from the root of your FastAPI project (e.g.```./fastapi_backend/```):
```sh
alembic revision --autogenerate -m "Add sort_order to group table"
```

#### Applying Migrations
To apply all unapplied migrations and update your database schema:
```sh
alembic upgrade head
```