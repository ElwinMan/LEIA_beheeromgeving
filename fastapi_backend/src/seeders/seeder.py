import os
from dotenv import load_dotenv

from .digital_twin_layer_association_seeder import seed as seed_digital_twin_layer_association
from .digital_twin_seeder import seed as seed_digital_twin
from .layer_seeder import seed as seed_layer
from .user_seeder import seed as seed_user
from db.database import get_db  # Adjust if path differs

# Load environment variables
load_dotenv()

def main():
    print("Starting database seeding...")

    db_gen = get_db()
    db = next(db_gen)

    try:
        seed_user(db)
        print("Seeded users.")

        seed_layer(db)
        print("Seeded layers.")

        seed_digital_twin(db)
        print("Seeded digital twins.")

        seed_digital_twin_layer_association(db)
        print("Seeded digital twin-layer associations.")

        print("Database seeding completed!")

    finally:
        db_gen.close()

if __name__ == "__main__":
    main()
