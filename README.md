# LEIA beheeromgeving Web App - Svelte + FastAPI + PostgreSQL

The application is used to manage JSON config files for LEIA digital twins.

## Getting Started

### Prerequisites

- Git
- Docker Desktop

local usage
- npm (Node Package Manager)
- Python 3.x

## Clone
```sh
git clone https://github.com/ElwinMan/LEIA_beheeromgeving.git
```
```sh
cd LEIA_beheeromgeving
```

## Build

### With Docker

#### Step 1: Set up Environment Files

**Frontend Configuration:**
```bash
# Copy frontend environment file
cp svelte_frontend/.env.example svelte_frontend/.env
```

**Backend Configuration:**
```bash
# Copy backend environment file
cp fastapi_backend/.env.docker.example fastapi_backend/.env.docker
```

#### Step 2: Configure Database Settings

Open `LEIA_beheeromgeving/fastapi_backend/.env.docker` and configure:

**Choose your database setup:**

**Option A: Use Docker Database (Recommended for first-time setup)**
1. Keep the default settings in `.env.docker` - no changes needed
2. For production use, change the default database password in `docker-compose.yml`:
   - Open `docker-compose.yml`
   - Change `POSTGRES_PASSWORD: mysecretpassword` to a secure password
   - Update the corresponding `POSTGRES_PASSWORD` in `.env.docker` to match

**Option B: Use External Database**
1. Update the DATABASE_URL in `.env.docker` to point to your external database
2. Remove the database service from `docker-compose.yml`:
   - Delete the entire `db:` service section
   - Remove `depends_on: - db` from the backend service
   - Remove the `pgdata:` volume from the volumes section

#### Step 3: Configure Database Setup Options

In the `.env.docker` file, set these important variables:

**Database Migrations:**
| RUN_MIGRATIONS | When to Use | Description |
|----------------|-------------|-------------|
| `true` | ✅ **First-time setup** or schema updates | Creates/updates database tables (**required for initial build**) |
| `false` | 🔒 **Production** or existing database | Skips migrations (safer for production environments) |

**Database Seeding:**
| SEED_MODE | When to Use | Description |
|-----------|-------------|-------------|
| `minimal` | ✅ **Recommended for most users** | Adds essential tools and content types only |
| `none` | 🔧 **Production** or custom setup | No sample data - just creates empty database |
| `full` | 🏢 **Custom seeders** | Includes all digital twins and layers (requires custom seeder files) |

**For Custom Seeders (`SEED_MODE=full`):**
If you want to use custom seeder data (pre-configured digital twins and layers for your organization):
1. Navigate to `fastapi_backend/src/seeders/`
2. Replace the existing seeder files with your custom seeder files
3. Ensure your custom seeders follow the same structure as the existing ones
4. Set `SEED_MODE=full` in your `.env.docker` file

#### Quick Setup for New Users:
```bash
# In .env.docker file, set:
RUN_MIGRATIONS=true
SEED_MODE=minimal
```

> 💡 **Tip**: After initial setup, change `RUN_MIGRATIONS=false` and `SEED_MODE=none` to prevent unnecessary operations on subsequent builds.

#### Step 4: Build and Run

1. **Start Docker Desktop** (if not already running)

2. **Build and start the application:**
   ```sh
   docker compose up --build
   ```

> 💡 **Network Issues?** If you encounter SSH permission errors, try switching to guest WiFi and disabling VPN connections.

#### Step 5: Access the Application

Once the containers are running, access the application at:

- **Frontend**: http://localhost:3000/
- **Backend API**: http://localhost:8000/
- **API Documentation**: http://localhost:8000/docs
- **Database**: localhost:5432

#### Step 6: Post-Setup Configuration

After successful initial setup:
1. Edit `.env.docker` and set:
   - `RUN_MIGRATIONS=false`
   - `SEED_MODE=none`

---

### Run locally (Alternative to Docker)

**Prerequisites**: Node.js, Python 3.x

#### Backend Setup:
```bash
# Copy environment file
cp fastapi_backend/.env.example fastapi_backend/.env

# Create virtual environment
python -m venv venv
venv\Scripts\activate
pip install -r fastapi_backend/requirements.txt

# Setup database
cd fastapi_backend/src
python -m src.scripts.manage fresh-minimal
uvicorn main:app --reload
```

> 💡 **Custom Seeders**: To use custom seeders, replace files in `fastapi_backend/src/seeders/` and use `fresh-full` instead of `fresh-minimal`.

#### Frontend Setup:
```bash
# Copy environment file  
cp svelte_frontend/.env.example svelte_frontend/.env

# Install and run
cd svelte_frontend
npm install
npm run dev
```

Access at: http://localhost:5173/


#### Optional Cesium Ion Map
The position selector function uses Cesium for 3D globe visualization. For high-quality satellite imagery, you can optionally provide a Cesium Ion access token, which you can obtain from https://ion.cesium.com/tokens by creating a free Cesium account.

To use Cesium Ion imagery, add your token to the `.env` file:
```
VITE_CESIUM_ION_TOKEN=your_cesium_ion_token_here
```
Located in: `LEIA_beheeromgeving/svelte_frontend/.env`

If no token is provided, the application will automatically fall back to using OpenStreetMap tiles, which work without any configuration.

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