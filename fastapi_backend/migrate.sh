#!/bin/bash
set -e

echo "Migration container starting..."

# Parse command line arguments
SEED_TYPE=${1:-none}  # none, minimal, full
echo "Seed type: $SEED_TYPE"

# Wait for database
echo "Waiting for database..."
until python -c "
import psycopg2
import sys
import os
try:
    conn = psycopg2.connect(
        host=os.getenv('POSTGRES_HOST', 'db'),
        database=os.getenv('POSTGRES_DB', 'mydb'),
        user=os.getenv('POSTGRES_USER', 'postgres'),
        password=os.getenv('POSTGRES_PASSWORD', 'mysecretpassword'),
        port=os.getenv('POSTGRES_PORT', '5432')
    )
    conn.close()
    print('Database is ready!')
except psycopg2.OperationalError as e:
    print(f'Database not ready: {e}')
    sys.exit(1)
"; do
    echo "Database is unavailable - sleeping"
    sleep 2
done

echo "Database is ready! Running migrations..."
cd /
alembic upgrade head

# Handle seeding based on argument
if [ "$SEED_TYPE" = "none" ]; then
    echo "Skipping seeding (SEED_TYPE=none)"
elif [ "$SEED_TYPE" = "minimal" ]; then
    echo "Running minimal seeding..."
    cd /app
    python -m scripts.manage seed-minimal
    echo "Minimal seeding completed!"
elif [ "$SEED_TYPE" = "full" ]; then
    echo "Checking if database needs full seeding..."
    cd /app

    # Check if database is empty before seeding
    if python -c "
from db.database import get_db
from models.digital_twin import DigitalTwin
import sys

db_gen = get_db()
db = next(db_gen)

try:
    count = db.query(DigitalTwin).count()
    print(f'DigitalTwin count: {count}')
    
    if count == 0:
        print('Database is empty, should run seeders.')
        sys.exit(0)  # Success - should run seeders
    else:
        print(f'Database has {count} digital twins, skipping seeders.')
        sys.exit(1)  # Skip seeders
        
except Exception as e:
    print(f'Error checking database: {e}')
    print('Running seeders due to error.')
    sys.exit(0)  # Run seeders on error
finally:
    db.close()
"; then
        echo "Running full seeders..."
        python -m scripts.manage seed
        echo "Full seeders completed!"
    else
        echo "Skipping full seeders - database already has data."
    fi
else
    echo "Unknown seed type: $SEED_TYPE. Use 'none', 'minimal', or 'full'"
    exit 1
fi

echo "Migration/seeding completed successfully!"