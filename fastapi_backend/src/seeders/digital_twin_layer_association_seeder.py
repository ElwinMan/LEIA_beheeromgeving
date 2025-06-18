from db.database import SessionLocal
from models.digital_twin import DigitalTwin
from models.layer import Layer
from models.associations import DigitalTwinLayerAssociation
from sqlalchemy.orm import Session

def seed(db: Session):
    # Map of digital twin names to the layer titles they should be linked to
    connections = {
        "bodem": ["BRT Achtergrondkaart (WMTS)", "Luchtfoto Actueel HR (WMTS)"],
        "fier": ["Luchtfoto Actueel HR (WMTS)"]
    }

    for twin_name, layer_titles in connections.items():
        digital_twin = db.query(DigitalTwin).filter_by(name=twin_name).first()
        if not digital_twin:
            print(f"Digital twin '{twin_name}' not found!")
            continue

        for sort_order, layer_title in enumerate(layer_titles):
            layer = db.query(Layer).filter_by(title=layer_title).first()
            if not layer:
                print(f"Layer '{layer_title}' not found!")
                continue

            assoc = DigitalTwinLayerAssociation(
                digital_twin_id=digital_twin.id,
                layer_id=layer.id,
                sort_order=sort_order
            )
            db.merge(assoc)  # Use merge to avoid duplicates

    db.commit()
    print("Digital Twin-Layer associations seeded.")

def run():
    db = SessionLocal()
    try:
        seed(db)
    finally:
        db.close()

if __name__ == "__main__":
    run()
