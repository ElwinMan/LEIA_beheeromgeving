from db.database import SessionLocal
from models.digital_twin import DigitalTwin
from models.layer import Layer
from models.group import Group
from models.associations import DigitalTwinLayerAssociation
from sqlalchemy.orm import Session

def seed(db: Session):
    # Map of digital twin names to the layer titles and group they should be linked to
    connections = {
        "bodem": [
            ["BRT Achtergrondkaart (WMTS)", None], 
            ["Luchtfoto Actueel HR (WMTS)", None],
            ["3D BAG", None],
            ["Bestuurlijke grens Middelburg", None],
            ["AHN", None],
            ["Bodemhoogte", None],
            ["1850", None],
            ["Riolering", None],
            ["BHR", None],
            ["Bodemvlakken (BRO)", 1],
            ["Vlakken van bodemkundig belang (BRO)", 1],
            ["Dieptemetingen (BRO)", 2],
            ["GHG - gemiddeld kleinste diepte (BRO)", 2],
            ["GLG - gemiddeld grootste diepte (BRO)", 2],
            ["GVG - gemiddelde diepte voorjaar (BRO)", 2],
            ["GT - Grondwatertrappen (BRO)", 2],
            ["GeoTOP", 3],
            ["FRESHEM", 4],
            ["Luchtfoto 2024 Ortho 8cm RGB", 5],
            ["Luchtfoto 2023 Ortho 8cm RGB", 5]
        ],
        "fier": [
            ["Luchtfoto Actueel HR (WMTS)", None]
        ]
    }

    for twin_name, layer_titles in connections.items():
        digital_twin = db.query(DigitalTwin).filter_by(name=twin_name).first()
        if not digital_twin:
            print(f"Digital twin '{twin_name}' not found!")
            continue

        for sort_order, (layer_title, group_id) in enumerate(layer_titles):
            layer = db.query(Layer).filter_by(title=layer_title).first()
            if not layer:
                print(f"Layer '{layer_title}' not found!")
                continue

            if group_id is not None:
                group = db.query(Group).filter_by(id=group_id).first()
                if not group:
                    print(f"Group with id {group_id} not found!")
                    continue
                group_id_to_use = group.id
            else:
                group_id_to_use = None

            assoc = DigitalTwinLayerAssociation(
                digital_twin_id=digital_twin.id,
                layer_id=layer.id,
                group_id=group_id_to_use,
                sort_order=sort_order
            )
            db.merge(assoc)

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
