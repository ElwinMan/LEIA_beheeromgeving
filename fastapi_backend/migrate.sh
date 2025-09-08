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
    echo "Running full seeding..."
    cd /app
    python -m scripts.manage seed
    echo "Full seeding completed!"
else
    echo "Unknown seed type: $SEED_TYPE. Use 'none', 'minimal', or 'full'"
    exit 1
fi

echo "Migration/seeding completed successfully!"