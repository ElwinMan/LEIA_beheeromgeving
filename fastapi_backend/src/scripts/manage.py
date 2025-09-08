import sys
from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker
from db.database import Base, get_db, DATABASE_URL
from seeders.seeder import main as run_seeders    
from seeders.content_type_seeder import seed as seed_content_type
from seeders.tool_seeder import seed as seed_tool
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
    print("Running full seeders...")
    run_seeders()

def seed_minimal():
    print("Running minimal seeders (content types and tools only)...")
    
    db_gen = get_db()
    db = next(db_gen)
    try:
        seed_content_type(db)
        seed_tool(db)
        print("Minimal seeding completed!")
    except Exception as e:
        print(f"Error during minimal seeding: {e}")
        raise
    finally:
        db.close()

def fresh():
    drop_all_tables()
    migrate()
    seed()

def fresh_minimal():
    drop_all_tables()
    migrate()
    seed_minimal()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python manage.py [drop|create|migrate|seed|seed-minimal|fresh|fresh-minimal]")
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
    elif command == "seed-minimal":
        seed_minimal()
    elif command == "fresh":
        fresh()
    elif command == "fresh-minimal":
        fresh_minimal()
    else:
        print(f"Unknown command {command}")