from db.database import SessionLocal
from models.tool_associations import ProjectsSnippets
from sqlalchemy.orm import Session

def seed(db: Session):
    try:
        projects_snippets = [
            {
                "name": "My project name",
                "description": "Short description of my project",
                "content": {
                    "polygon": [
                        [4.9000, 52.39961],
                        [4.91807, 52.39961],
                        [4.9193, 52.38107],
                        [4.9000, 52.38575]
                    ],
                    "layers": [
                        "DTB 3D",
                        "3D BAG",
                        "Bomen 3D"
                    ],
                    "cameraPosition": {
                        "x": 4.94802,
                        "y": 52.35647,
                        "z": 2176.53646,
                        "heading": 326.85260,
                        "pitch": -24.10943,
                        "duration": 1.50
                    }
                }
            }
        ]
        for p in projects_snippets:
            if not db.query(ProjectsSnippets).filter_by(name=p["name"]).first():
                db.add(ProjectsSnippets(**p))
        db.commit()
        print("Projects snippets seeded.")
    finally:
        db.close()

def run():
    db = SessionLocal()
    try:
        seed(db)
    finally:
        db.close()

if __name__ == "__main__":
    run()