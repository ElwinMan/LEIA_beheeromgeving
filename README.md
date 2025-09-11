# LEIA beheeromgeving Web App - Svelte + FastAPI + PostgreSQL

The application is used to manage JSON config files for LEIA digital twins.

## Clone
```sh
git clone https://github.com/ElwinMan/LEIA_beheeromgeving.git
cd LEIA_beheeromgeving
```
## Build

### With docker
Copy the .env.example as .env in svelte_frontend and .env.docker.example in fastAPI_backend as .env.docker

Fill in the required database connection if you are using a external database.
Else keep the localhost database connection and edit the RUN_MIGRATIONS and SEED_MODE dependent on how you want to run the build.

| RUN_MIGRATIONS | Description |
|----------------|-------------|
| `true` | Run Alembic migrations (required for initial build and schema updates) |
| `false` | Skip migrations (safer for production to prevent accidental schema changes) |

| SEED_MODE | Description |
|-----------|-------------|
| `none` | No seeding - just migrations and start server |
| `minimal` | Clean version with only the required data of tools and tool_content_types |
| `full` | Seeding of everything (only use this if you added external seeders to fastAPI_backend/src/seeders e.g. internal Provincie Zeeland seeders for digital twins and layers. May not be up-to-date to existing digital twins because it depends on the hardcoded seeders.) |

**Production Safety Note**: For production environments, it's recommended to set `RUN_MIGRATIONS=false` after the initial setup to prevent accidental database schema changes during container restarts. Migrations should be run manually or through a controlled deployment process in production.

Open docker desktop and use one of the following command line. (If you don't have administrative permissions on your work device, the solution might be switching to the guest wifi and disable the VPN connection)

Use the following command line to migrate and seed the database schema on the initial build (Make sure to turn the RUN_MIGRATIONS to "false" and SEED_MODE back to "none" after initial setup to prevent unnecessary migrations and seeding on subsequent builds).
```sh
docker compose up --build
```

Links to the containers:

Svelte frontend: http://localhost:3000/

FastAPI backend: http://localhost:8000/
API docs: http://localhost:8000/docs

PostgreSQL: http://localhost:5432/

### Run local
Copy the .env.example as .env in svelte_frontend and .env.example in fastAPI_backend as .env

```sh
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
cd src
python -m src.scripts.manage fresh
uvicorn main:app --reload
```

Run the frontend svelte with the following command line and open the application on http://localhost:5173/ (It can take a minute for the app to work properly)
```sh
cd frontend_svelte
npm install
npm run dev
```

## Backend local manage tool
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

- seed-full
Runs the seeding scripts to populate the database with initial or sample data.

- seed-minimal
Runs the seeding script to populate the database with the minimal data (tool and tool content_type data).

- fresh-full
Drops all tables, runs migrations, and seeds the database. Use this for a full reset of the database.

- fresh-minimal
Drops all tables, runs migrations, and seeds the database with minimal data. Use this for a full reset of the database with minimal data.

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