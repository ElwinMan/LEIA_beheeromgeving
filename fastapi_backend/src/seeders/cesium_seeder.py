from db.database import SessionLocal
from models.tool_associations import TerrainProvidersSnippets
from sqlalchemy.orm import Session

def seed(db: Session):
    try:
        cesium_snippets = [
            {
                "url": "https://api.pdok.nl/kadaster/3d-basisvoorziening/ogc/v1_0/collections/digitaalterreinmodel/quantized-mesh",
                "vertexNormals": True,
                "content": {
                    "fxaa": True,
                    "shadows": False,
                    "animate": False,
                    "resolutionScale": 1,
                    "maximumScreenSpaceError": 16,
                    "groundAtmosphere": True,
                    "lighting": True,
                    "skyAtmosphere": True,
                    "fog": True,
                    "highDynamicRange": False,
                    "pointCloudAttenuationMaximum": 2,
                    "terrainProviders": [
                        {
                            "title": "PDOK Terrain",
                            "url": "https://api.pdok.nl/kadaster/3d-basisvoorziening/ogc/v1_0/collections/digitaalterreinmodel/quantized-mesh",
                            "vertexNormals": True
                        },
                        {
                            "title": "Uit"
                        }
                    ]
                }
            }
        ]
        for c in cesium_snippets:
            if not db.query(TerrainProvidersSnippets).filter_by(url=c["url"]).first():
                db.add(TerrainProvidersSnippets(**c))
        db.commit()
        print("Cesium snippets seeded.")
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