import os
from dotenv import load_dotenv

from .user_seeder import seed as seed_user
from .digital_twin_seeder import seed as seed_digital_twin
from .viewer_seeder import seed as seed_viewer
from .layer_seeder import seed as seed_layer
from .group_seeder import seed as seed_group
from .digital_twin_layer_association_seeder import seed as seed_digital_twin_layer_association
from .tool_seeder import seed as seed_tool
from .content_type_seeder import seed as seed_content_type
from .bookmark_seeder import seed as seed_bookmark
from .terrain_provider_seeder import seed as seed_terrain_provider
from .project_seeder import seed as seed_project
from .story_seeder import seed as seed_story
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

        seed_content_type(db)
        print("Seeded tools content types.")

        seed_bookmark(db)
        print("Seeded bookmarks.")
        seed_terrain_provider(db)
        print("Seeded terrain providers.")
        seed_story(db)
        print("Seeded stories.")
        seed_project(db)
        print("Seeded projects.")

        seed_digital_twin_tool_association(db)
        print("Seeded digital twin-tool associations.")

        print("Database seeding completed!")

    except Exception as e:
        print(f"Error during seeding: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    main()
