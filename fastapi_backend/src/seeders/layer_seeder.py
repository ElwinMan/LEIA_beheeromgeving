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
            content={
                "imageUrl": "",
                "legendUrl": "",
                "defaultAddToManager": True,
                "attribution": "PDOK",
                "wmts": {
                    "contentType": "image/png",
                }
            }
        ),
        Layer(
            type="wmts",
            title="Luchtfoto Actueel HR (WMTS)",
            url="https://service.pdok.nl/hwh/luchtfotorgb/wmts/v1_0",
            featureName="Actueel_orthoHR",
            isBackground=True,
            content={
                "imageUrl": "",
                "legendUrl": "",
                "defaultAddToManager": True,
                "wmts": {
                    "contentType": "image/jpeg",
                    "matrixids": ["00", "01", "02", "03", "04", "05", "06", "07", "08", "09", "10", "11", "12", "13", "14", "15", "16", "17", "18", "19"],
                    "tileMatrixSetID": "EPSG:3857"
                }
            }
        ),
        Layer(
            type="wmts",
            title="Topo Simple",
            url="https://s.map5.nl/map/prze.zu1952/service?service=WMTS&request=GetCapabilities&version=1.0.0",
            featureName="map5topo_simple",
            isBackground=True,
            content={
                "imageUrl": "",
                "legendUrl": "",
                "defaultAddToManager": True,
                "wmts": {
                    "contentType": "image/jpeg",
                    "matrixids": ["00", "01", "02", "03", "04", "05", "06", "07", "08", "09", "10", "11", "12", "13", "14", "15", "16", "17", "18", "19"],
                    "tileMatrixSetID": "webmerc_grid"
                }
            }
        ),
        Layer(
            type='3dtiles',
            title='3D BAG',
            isBackground=False,
            url='https://api.pdok.nl/kadaster/3d-basisvoorziening/ogc/v1_0/collections/gebouwen/3dtiles',
            featureName=None,
            content={
                'imageUrl': '',
                'legendUrl': '',
                'defaultAddToManager': True,
                'tiles3d': {}
            }
        ),
        Layer(
            type='geojson',
            title='Bestuurlijke grens Middelburg',
            isBackground=False,
            url='https://virtueel.zeeland.nl/tiles_other/middelburg_bestuurlijkegrens_line_4326.geojson',
            featureName=None,
            content={
                'imageUrl': '',
                'legendUrl': '',
                'defaultAddToManager': True,
                'settings': {
                    'theme': 'woonplaatsnaam'
                }
            }
        ),
        Layer(
            type='wms',
            title='AHN',
            isBackground=False,
            url='https://zldlufow3.zeeland.nl/geoserver/AHN4/wms?transparent=true&format=image%2Fpng&styles=&service=WMS&version=1.1.1',
            featureName='AHN4_DTM_0.5mtr',
            content={
                'imageUrl': '',
                'legendUrl': '',
                'defaultAddToManager': True,
                'attribution': 'AHN4_DTM_0.5mtr',
                'wms': {
                    'contentType': 'image/png'
                }
            }
        ),
        Layer(
            type='wms',
            title='Bodemhoogte',
            isBackground=False,
            url='https://projectgeodata.zeeland.nl/geoserver/digitaltwin/wms?transparent=true&format=image%2Fpng&styles=&service=WMS&version=1.1.1&request=GetMap&layers=digitaltwin%3Azeeland_1m',
            featureName=None,
            content={
                'imageUrl': '',
                'legendUrl': '',
                'defaultAddToManager': True,
                'attribution': 'digitaltwin%3Azeeland_1m',
                'wms': {
                    'contentType': 'image/png'
                }
            }
        ),
        Layer(
            type='wmts',
            title='1850',
            isBackground=False,
            url='https://s.map5.nl/map/prze.zu1952/service?service=WMTS&request=GetCapabilities&version=1.0.0',
            featureName='tmk_1850',
            content={
                'imageUrl': '',
                'legendUrl': '',
                'defaultAddToManager': True,
                'attribution': 'tmk_1850',
                'wmts': {
                    'contentType': 'image/png',
                    'matrixids': ["00", "01", "02", "03", "04", "05", "06", "07", "08", "09", "10", "11", "12", "13", "14", "15", "16", "17", "18", "19"],
                    'tileMatrixSetID': 'webmerc_grid'
                }
            }
        ),
        Layer(
            type='wms',
            title='Riolering',
            isBackground=False,
            url='https://opengeodata.zeeland.nl/geoserver/gemeenten/wms?transparent=true&format=image%2Fpng&styles=&service=WMS&version=1.1.1&request=GetMap&layers=gemeente%3Ariolering_middelburg',
            featureName=None,
            content={
                'imageUrl': '',
                'legendUrl': '',
                'defaultAddToManager': True,
                'attribution': 'gemeente%3Ariolering_middelburg',
                'wms': {
                    'contentType': 'image/png'
                }
            }
        ),
        Layer(
            type='3dtiles',
            title='BHR',
            isBackground=False,
            url='https://virtueel.zeeland.nl/tiles_other/BHR_Cesium_Tileset_Zeeland/tileset.json',
            featureName=None,
            content={
                'imageUrl': '',
                'legendUrl': '',
                'defaultAddToManager': True,
                'tiles3d': {
                    'shadows': False
                }
            }
        ),
        Layer(
            type='wms',
            title='Bodemvlakken (BRO)',
            isBackground=False,
            url='https://service.pdok.nl/bzk/bro-bodemkaart/wms/v1_0?transparent=true&format=image%2Fpng&styles=&service=WMS&version=1.1.1',
            featureName='soilarea',
            content={
                'imageUrl': '',
                'legendUrl': '',
                'defaultAddToManager': True,
                'attribution': 'soilarea',
                'wms': {
                    'contentType': 'image/png'
                }
            }
        ),
        Layer(
            type='wms',
            title='Vlakken van bodemkundig belang (BRO)',
            isBackground=False,
            url='https://service.pdok.nl/bzk/bro-bodemkaart/wms/v1_0?transparent=true&format=image%2Fpng&styles=&service=WMS&version=1.1.1',
            featureName='areaofpedologicalinterest',
            content={
                'imageUrl': '',
                'legendUrl': '',
                'defaultAddToManager': True,
                'attribution': 'areaofpedologicalinterest',
                'wms': {
                    'contentType': 'image/png'
                }
            }
        ),
        Layer(
            type='wms',
            title='Dieptemetingen (BRO)',
            isBackground=False,
            url='https://service.pdok.nl/bzk/bro-grondwaterspiegeldiepte/wms/v1_0?service=WMS&version=1.1.1',
            featureName='bro-grondwaterspiegeldieptemetingen',
            content={
                'imageUrl': '',
                'legendUrl': '',
                'defaultAddToManager': True,
                'attribution': 'bro-grondwaterspiegeldieptemetingen',
                'wms': {
                    'contentType': 'image/png'
                }
            }
        ),
        Layer(
            type='wms',
            title='GHG - gemiddeld kleinste diepte (BRO)',
            isBackground=False,
            url='https://service.pdok.nl/bzk/bro-grondwaterspiegeldiepte/wms/v1_0?service=WMS&version=1.1.1',
            featureName='bro-grondwaterspiegeldieptemetingen-GHG',
            content={
                'imageUrl': '',
                'legendUrl': '',
                'defaultAddToManager': True,
                'attribution': 'bro-grondwaterspiegeldieptemetingen-GHG',
                'wms': {
                    'contentType': 'image/png'
                }
            }
        ),
        Layer(
            type='wms',
            title='GLG - gemiddeld grootste diepte (BRO)',
            isBackground=False,
            url='https://service.pdok.nl/bzk/bro-grondwaterspiegeldiepte/wms/v1_0?service=WMS&version=1.1.1',
            featureName='bro-grondwaterspiegeldieptemetingen-GLG',
            content={
                'imageUrl': '',
                'legendUrl': '',
                'defaultAddToManager': True,
                'attribution': 'bro-grondwaterspiegeldieptemetingen-GLG',
                'wms': {
                    'contentType': 'image/png'
                }
            }
        ),
        Layer(
            type='wms',
            title='GVG - gemiddelde diepte voorjaar (BRO)',
            isBackground=False,
            url='https://service.pdok.nl/bzk/bro-grondwaterspiegeldiepte/wms/v1_0?service=WMS&version=1.1.1',
            featureName='bro-grondwaterspiegeldieptemetingen-GVG',
            content={
                'imageUrl': '',
                'legendUrl': '',
                'defaultAddToManager': True,
                'attribution': 'bro-grondwaterspiegeldieptemetingen-GVG',
                'wms': {
                    'contentType': 'image/png'
                }
            }
        ),
        Layer(
            type='wms',
            title='GT - Grondwatertrappen (BRO)',
            isBackground=False,
            url='https://service.pdok.nl/bzk/bro-grondwaterspiegeldiepte/wms/v1_0?service=WMS&version=1.1.1',
            featureName='bro-grondwaterspiegeldieptemetingen-GT',
            content={
                'imageUrl': '',
                'legendUrl': '',
                'defaultAddToManager': True,
                'attribution': 'bro-grondwaterspiegeldieptemetingen-GT',
                'wms': {
                    'contentType': 'image/png'
                }
            }
        ),
        Layer(
            type='3dtiles',
            title='GeoTOP',
            isBackground=False,
            url='https://virtueel.zeeland.nl/tiles_other/geotop_middelburg/tileset.json',
            featureName=None,
            content={
                'imageUrl': '',
                'legendUrl': 'https://virtueel.zeeland.nl/tiles_other/legendas/geotop_legenda.png',
                'defaultAddToManager': True,
                'attribution': 'BRO',
                'tiles3d': {
                    'shadows': False,
                    'style': {
                        'pointSize': '15'
                    },
                    'filter': {
                        'filterAttribute': 'Classification',
                        'classMapping': {
                            '0': 'Antropogeen',
                            '1': 'Organisch materiaal (veen)',
                            '2': 'Klei',
                            '3': 'Kleiig zand, zanderige klei en leem',
                            '5': 'Fijn zand',
                            '6': 'Midden zand',
                            '7': 'Grof zand',
                            '8': 'Grind',
                            '9': 'Schelpen'
                        }
                    }
                }
            }
        ),
        Layer(
            type='3dtiles',
            title='FRESHEM',
            isBackground=False,
            url='https://virtueel.zeeland.nl/tiles_other/freshem_middelburg/tileset.json',
            featureName=None,
            content={
                'imageUrl': '',
                'legendUrl': '',
                'defaultAddToManager': True,
                'tiles3d': {
                    'shadows': False,
                    'style': {
                        'pointSize': '15'
                    },
                    'filter': {
                        'filterAttribute': 'Classification',
                        'classMapping': {
                            '100': '0',
                            '101': '150',
                            '102': '300',
                            '103': '500',
                            '104': '750',
                            '105': '1000',
                            '106': '1250',
                            '107': '1500',
                            '108': '2000',
                            '109': '3000',
                            '110': '5000',
                            '111': '7500',
                            '112': '10000',
                            '113': '15000'
                        }
                    }
                }
            }
        ),
        Layer(
            type='wms',
            title='Luchtfoto 2024 Ortho 8cm RGB',
            isBackground=False,
            url='https://service.pdok.nl/hwh/luchtfotorgb/wmts/v1_0',
            featureName='2024_orthoHR',
            content={
                'imageUrl': '',
                'legendUrl': '',
                'defaultAddToManager': True,
                'attribution': 'PDOK',
                'wms': {
                    'contentType': 'image/png'
                }
            }
        ),
        Layer(
            type='wms',
            title='Luchtfoto 2023 Ortho 8cm RGB',
            isBackground=False,
            url='https://service.pdok.nl/hwh/luchtfotorgb/wmts/v1_0',
            featureName='2023_orthoHR',
            content={
                'imageUrl': '',
                'legendUrl': '',
                'defaultAddToManager': True,
                'attribution': 'PDOK',
                'wms': {
                    'contentType': 'image/png'
                }
            }
        ),
    ]

    for layer in layers:
        # Check if layer already exists
        existing = db.query(Layer).filter_by(title=layer.title).first()
        if not existing:
            db.add(layer)
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
