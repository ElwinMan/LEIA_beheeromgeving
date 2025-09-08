from db.database import SessionLocal, engine
from models.viewer import Viewer
from models.digital_twin import DigitalTwin
from sqlalchemy.orm import Session

def seed(db: Session):
    # Map of digital twin names to their viewer configurations
    viewer_data = {
        "bodem": {
            "logo": "https://virtueel.zeeland.nl/global_assets/img/logo.svg",
            "thumbnail": "/assets/previews/preview-klimaat-bodem.png",
            "startPosition": {
                "x": 3.62121,
                "y": 51.45503,
                "z": 3096.96140,
                "heading": 360.00000,
                "pitch": -34.77193,
                "duration": 1.50
            },
            "colors": {
                "ui-background": "#ffffff",
                "interactive-01": "#214170",
                "interactive-02": "#171717",
                "interactive-03": "#0062ff",
                "interactive-04": "#0062ff",
                "ui-01": "#f3f3f3",
                "ui-02": "#ffffff",
                "ui-03": "#dcdcdc",
                "ui-04": "#8c8c8c",
                "ui-05": "#171717",
                "text-01": "#171717",
                "text-02": "#565656",
                "text-03": "#8c8c8c",
                "text-04": "#ffffff",
                "link-01": "#0062ff",
                "icon-01": "#171717",
                "icon-02": "#565656",
                "icon-03": "#ffffff",
                "field-01": "#f3f3f3",
                "field-02": "#ffffff",
                "inverse-01": "#ffffff",
                "inverse-02": "#3d3d3d",
                "support-01": "#da1e28",
                "support-02": "#24a148",
                "support-03": "#fdd13a",
                "support-04": "#054ada",
                "inverse-support-01": "#fb4b53",
                "inverse-support-02": "#3dbb61",
                "inverse-support-03": "#fdd13a",
                "inverse-support-04": "#408bfc",
                "overlay-01": "#171717CC",
                "interaction-tokens": "#0062ff",
                "hover-primary": "#376dbc",
                "hover-primary-text": "#054ada",
                "hover-secondary": "#4c4c4c",
                "hover-tertiary": "#4cabd8",
                "hover-ui": "#e5e5e5",
                "hover-selected-ui": "#cacaca",
                "hover-danger": "#ba1b23",
                "hover-row": "#e5e5e5",
                "active-primary": "#376dbc",
                "active-secondary": "#6f6f6f",
                "active-tertiary": "#0530ad",
                "active-ui": "#bebebe",
                "active-danger": "#750e13",
                "selected-ui": "#dcdcdc",
                "highlight": "#C9deff",
                "skeleton-01": "#e5e5e5",
                "skeleton-02": "#bebebe",
                "visited-link": "#'Visited links'",
                "disabled-01": "#f3f3f3",
                "disabled-02": "#bebebe",
                "disabled-03": "#8c8c8c"
            }
        },
        "fier": {
            "logo": "images/leia_logo.png",
            "thumbnail": "/assets/previews/preview-klimaat-overstroming.png",
            "startPosition": {
                "x": 5.40068,
                "y": 51.20089,
                "z": 55885.52117,
                "heading": 360.00000,
                "pitch": -34.77194,
                "duration": 1.50
            },
            "colors": {
                "ui-background": "#ffffff",
                "interactive-01": "#214170",
                "interactive-02": "#171717",
                "interactive-03": "#0062ff",
                "interactive-04": "#0062ff",
                "ui-01": "#f3f3f3",
                "ui-02": "#ffffff",
                "ui-03": "#dcdcdc",
                "ui-04": "#8c8c8c",
                "ui-05": "#171717",
                "text-01": "#171717",
                "text-02": "#565656",
                "text-03": "#8c8c8c",
                "text-04": "#ffffff",
                "link-01": "#0062ff",
                "icon-01": "#171717",
                "icon-02": "#565656",
                "icon-03": "#ffffff",
                "field-01": "#f3f3f3",
                "field-02": "#ffffff",
                "inverse-01": "#ffffff",
                "inverse-02": "#3d3d3d",
                "support-01": "#da1e28",
                "support-02": "#24a148",
                "support-03": "#fdd13a",
                "support-04": "#054ada",
                "inverse-support-01": "#fb4b53",
                "inverse-support-02": "#3dbb61",
                "inverse-support-03": "#fdd13a",
                "inverse-support-04": "#408bfc",
                "overlay-01": "#171717CC",
                "interaction-tokens": "#0062ff",
                "hover-primary": "#376dbc",
                "hover-primary-text": "#054ada",
                "hover-secondary": "#4c4c4c",
                "hover-tertiary": "#4cabd8",
                "hover-ui": "#e5e5e5",
                "hover-selected-ui": "#cacaca",
                "hover-danger": "#ba1b23",
                "hover-row": "#e5e5e5",
                "active-primary": "#376dbc",
                "active-secondary": "#6f6f6f",
                "active-tertiary": "#0530ad",
                "active-ui": "#bebebe",
                "active-danger": "#750e13",
                "selected-ui": "#dcdcdc",
                "highlight": "#C9deff",
                "skeleton-01": "#e5e5e5",
                "skeleton-02": "#bebebe",
                "visited-link": "#'Visited links'",
                "disabled-01": "#f3f3f3",
                "disabled-02": "#bebebe",
                "disabled-03": "#8c8c8c"
            }
        }
    }

    for twin_name, content in viewer_data.items():
        digital_twin = db.query(DigitalTwin).filter_by(name=twin_name).first()
        if not digital_twin:
            print(f"Digital twin '{twin_name}' not found!")
            continue

        # Check if viewer already exists
        existing = db.query(Viewer).filter_by(digital_twin_id=digital_twin.id).first()
        if not existing:
            viewer = Viewer(
                digital_twin_id=digital_twin.id,
                content=content
            )
            db.add(viewer)
    db.commit()

def run():
    db = SessionLocal()
    try:
        seed(db)
        print("Viewer Seeding completed!")
    finally:
        db.close()

if __name__ == "__main__":
    run()
