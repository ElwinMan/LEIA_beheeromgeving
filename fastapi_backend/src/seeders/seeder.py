import os
from dotenv import load_dotenv

from .user_seeder import seed as seed_user
from .digital_twin_seeder import seed as seed_digital_twin
from .viewer_seeder import seed as seed_viewer
from .layer_seeder import seed as seed_layer
from .group_seeder import seed as seed_group
from .digital_twin_layer_association_seeder import seed as seed_digital_twin_layer_association
from .tool_seeder import seed as seed_tool
from .digital_twin_tool_association_seeder import seed as seed_digital_twin_tool_association
from db.database import get_db

# Load environment variables
load_dotenv()

def main():
    print("Starting database seeding...")

    db_gen = get_db()
    db = next(db_gen)

    try:
        seed_user(db)
        print("Seeded users.")

        seed_digital_twin(db)
        print("Seeded digital twins.")

        seed_viewer(db)
        print("Seeded viewers.")

        seed_layer(db)
        print("Seeded layers.")

        seed_group(db)
        print("Seeded groups.")

        seed_digital_twin_layer_association(db)
        print("Seeded digital twin-layer associations.")

        seed_tool(db)
        print("Seeded tools.")

        seed_digital_twin_tool_association(db)
        print("Seeded digital twin-tool associations.")

        print("Database seeding completed!")

    finally:
        db_gen.close()

if __name__ == "__main__":
    main()
