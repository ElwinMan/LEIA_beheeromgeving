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
            ["BRT Achtergrondkaart (WMTS)", None, True], 
            ["Luchtfoto Actueel HR (WMTS)", None, True],
            ["3D BAG", None, False],
            ["Bestuurlijke grens Middelburg", None, False],
            ["AHN", None, False],
            ["Bodemhoogte", None, False],
            ["1850", None, False],
            ["Riolering", None, False],
            ["BHR", None, False],
            ["Bodemvlakken (BRO)", 1, False],
            ["Vlakken van bodemkundig belang (BRO)", 1, False],
            ["Dieptemetingen (BRO)", 2, False],
            ["GHG - gemiddeld kleinste diepte (BRO)", 2, False],
            ["GLG - gemiddeld grootste diepte (BRO)", 2, False],
            ["GVG - gemiddelde diepte voorjaar (BRO)", 2, False],
            ["GT - Grondwatertrappen (BRO)", 2, False],
            ["GeoTOP", 3, False],
            ["FRESHEM", 4, False],
            ["Luchtfoto 2024 Ortho 8cm RGB", 5, False],
            ["Luchtfoto 2023 Ortho 8cm RGB", 5, False]
        ],
        "fier": [
            ["Luchtfoto Actueel HR (WMTS)", None, True]
        ]
    }

    for twin_name, layer_titles, in connections.items():
        digital_twin = db.query(DigitalTwin).filter_by(name=twin_name).first()
        if not digital_twin:
            print(f"Digital twin '{twin_name}' not found!")
            continue

        for sort_order, (layer_title, group_id, is_default) in enumerate(layer_titles):
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
                sort_order=sort_order,
                is_default=is_default
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
