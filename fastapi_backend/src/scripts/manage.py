import sys
from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker
from db.database import Base, get_db, DATABASE_URL
from seeders.seeder import main as run_seeders
import subprocess
import os

def drop_all_tables():
    engine = create_engine(DATABASE_URL)
    meta = MetaData()
    meta.reflect(bind=engine)
    meta.drop_all(bind=engine)
    print("Dropped all tables.")


def create_all_tables():
    engine = create_engine(DATABASE_URL)
    Base.metadata.create_all(engine)
    print("Created all tables.")

def migrate():
    print("Running Alembic migrations...")
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    subprocess.run(["alembic", "upgrade", "head"], cwd=project_root, check=True)

def seed():
    print("Running seeders...")
    run_seeders()

def fresh():
    drop_all_tables()
    migrate()
    seed()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python manage.py [drop|create|migrate|seed|fresh]")
        sys.exit(1)
    
    command = sys.argv[1]

    if command == "drop":
        drop_all_tables()
    elif command == "create":
        create_all_tables()
    elif command == "migrate":
        migrate()
    elif command == "seed":
        seed()
    elif command == "fresh":
        fresh()
    else:
        print(f"Unknown command {command}")