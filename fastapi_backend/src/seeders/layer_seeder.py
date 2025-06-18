from db.database import SessionLocal
from models.layer import Layer
from sqlalchemy.orm import Session

def seed(db: Session):
    layers = [
        Layer(
            type="wmts",
            title="BRT Achtergrondkaart (WMTS)",
            url="https://service.pdok.nl/brt/achtergrondkaart/wmts/v2_0?",
            featureName="standaard",
            isBackground=True,
            defaultOn=True,
            content={
                "imageURL": "",
                "legendURL": "",
                "defaultAddToManager": True,
                "attribution": "PDOK",
                "contentType": "image/png"
            }
        ),
        Layer(
            type="wmts",
            title="Luchtfoto Actueel HR (WMTS)",
            url="https://service.pdok.nl/hwh/luchtfotorgb/wmts/v1_0",
            featureName="Actueel_orthoHR",
            isBackground=True,
            defaultOn=True,
            content={
                "imageURL": "",
                "legendURL": "",
                "defaultAddToManager": True,
                "contentType": "image/jpeg",
                "matrixids": ["00", "01", "02", "03", "04", "05", "06", "07", "08", "09", "10", "11", "12", "13", "14", "15", "16", "17", "18", "19"],
                "matrixset": "EPSG:3857"
            }
        )
    ]

    db.add_all(layers)
    db.commit()

def run():
    db = SessionLocal()
    try:
        seed(db)
        print("Layer seeding completed!")
    finally:
        db.close()

if __name__ == "__main__":
    run()