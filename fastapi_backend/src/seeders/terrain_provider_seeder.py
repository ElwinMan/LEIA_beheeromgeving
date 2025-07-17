from db.database import SessionLocal
from models.tool_associations import TerrainProvider
from sqlalchemy.orm import Session

def seed(db: Session):
    try:
        terrainProviders = [
            {
                "title": "uit",
                "url": "uit",
                "vertexNormals": False
            },
            {
                "title": "Zeeland 1m",
                "url": "https://virtueel.zeeland.nl/tiles_other/zeeland_1m",
                "vertexNormals": True
            },
            {
                "title": "PDOK Terrain",
                "url": "https://api.pdok.nl/kadaster/3d-basisvoorziening/ogc/v1_0/collections/digitaalterreinmodel/quantized-mesh",
                "vertexNormals": True,
            }
        ]
        for t in terrainProviders:
            if not db.query(TerrainProvider).filter_by(url=t["url"]).first():
                db.add(TerrainProvider(**t))
        db.commit()
        print("terrainProvider seeded.")
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