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
        ),
        Layer(
            type='3dtiles',
            title='3D BAG',
            isBackground=False,
            defaultOn=False,
            url='https://api.pdok.nl/kadaster/3d-basisvoorziening/ogc/v1_0/collections/gebouwen/3dtiles',
            featureName=None,
            content={
                'legendUrl': '',
                'imageUrl': '',
                'defaultAddToManager': True,
                'attribution': '',
                'description': ''
            }
        ),
        Layer(
            type='geojson',
            title='Bestuurlijke grens Middelburg',
            isBackground=False,
            defaultOn=False,
            url='https://virtueel.zeeland.nl/tiles_other/middelburg_bestuurlijkegrens_line_4326.geojson',
            featureName=None,
            content={
                'theme': 'woonplaatsnaam',
                'legendUrl': '',
                'imageUrl': '',
                'defaultAddToManager': True,
                'attribution': '',
                'description': ''
            }
        ),
        Layer(
            type='wms',
            title='AHN',
            isBackground=False,
            defaultOn=False,
            url='https://zldlufow3.zeeland.nl/geoserver/AHN4/wms?transparent=true&format=image%2Fpng&styles=&service=WMS&version=1.1.1',
            featureName='AHN4_DTM_0.5mtr',
            content={
                'contenttype': 'image/png',
                'legendUrl': '',
                'imageUrl': '',
                'defaultAddToManager': True,
                'attribution': 'AHN4_DTM_0.5mtr',
                'description': 'Het Actueel Hoogtebestand Nederland is een digitaal hoogtemodel voor het Europese deel van Nederland. De eigenaar van de dataset is Rijkswaterstaat. Het AHN is als open data publiek toegankelijk, zowel door het downloaden van de data als door middel van verschillende viewers.'
            }
        ),
        Layer(
            type='wms',
            title='Bodemhoogte',
            isBackground=False,
            defaultOn=False,
            url='https://projectgeodata.zeeland.nl/geoserver/digitaltwin/wms?transparent=true&format=image%2Fpng&styles=&service=WMS&version=1.1.1&request=GetMap&layers=digitaltwin%3Azeeland_1m',
            featureName=None,
            content={
                'contenttype': 'image/png',
                'legendUrl': '',
                'imageUrl': '',
                'defaultAddToManager': True,
                'attribution': 'digitaltwin%3Azeeland_1m',
                'description': 'Voor de Provincie Zeeland is adequaat digitaal inzicht in de hoogte van het terrein en in de wateren van groot belang. Bestaande beschikbare geodata is hiervoor bijgewerkt tot 1 dekkende bodemhoogte kaart. De bodemhoogte kaart is te gebruiken door ketenpartners waar de Provincie Zeeland mee samenwerkt in het kader van de Digital Twin. CC - SPOTinfo.'
            }
        ),
        Layer(
            type='wmts',
            title='1850',
            isBackground=False,
            defaultOn=False,
            url='https://s.map5.nl/map/prze.zu1952/service?service=WMTS&request=GetCapabilities&version=1.0.0',
            featureName='tmk_1850',
            content={
                'contentType': 'image/png',
                'matrixids': ["00", "01", "02", "03", "04", "05", "06", "07", "08", "09", "10", "11", "12", "13", "14", "15", "16", "17", "18", "19"],
                'tileMatrixSetID': 'webmerc_grid',
                'legendUrl': '',
                'imageUrl': '',
                'defaultAddToManager': True,
                'attribution': 'tmk_1850',
                'description': ''
            }
        ),
        Layer(
            type='wms',
            title='Riolering',
            isBackground=False,
            defaultOn=False,
            url='https://opengeodata.zeeland.nl/geoserver/gemeenten/wms?transparent=true&format=image%2Fpng&styles=&service=WMS&version=1.1.1&request=GetMap&layers=gemeente%3Ariolering_middelburg',
            featureName=None,
            content={
                'contenttype': 'image/png',
                'legendUrl': '',
                'imageUrl': '',
                'defaultAddToManager': True,
                'attribution': 'gemeente%3Ariolering_middelburg',
                'description': ''
            }
        ),
        Layer(
            type='3dtiles',
            title='BHR',
            isBackground=False,
            defaultOn=False,
            url='https://virtueel.zeeland.nl/tiles_other/BHR_Cesium_Tileset_Zeeland/tileset.json',
            featureName=None,
            content={
                'shadows': False,
                'legendUrl': '',
                'imageUrl': '',
                'defaultAddToManager': True,
                'attribution': '',
                'description': ''
            }
        ),
        Layer(
            type='wms',
            title='Bodemvlakken (BRO)',
            isBackground=False,
            defaultOn=False,
            url='https://service.pdok.nl/bzk/bro-bodemkaart/wms/v1_0?transparent=true&format=image%2Fpng&styles=&service=WMS&version=1.1.1',
            featureName='soilarea',
            content={
                'contenttype': 'image/png',
                'attribution': 'soilarea',
                'description': '',
                'imageUrl': '',
                'legendUrl': '',
                'defaultAddToManager': True
            }
        ),
        Layer(
            type='wms',
            title='Vlakken van bodemkundig belang (BRO)',
            isBackground=False,
            defaultOn=False,
            url='https://service.pdok.nl/bzk/bro-bodemkaart/wms/v1_0?transparent=true&format=image%2Fpng&styles=&service=WMS&version=1.1.1',
            featureName='areaofpedologicalinterest',
            content={
                'contenttype': 'image/png',
                'attribution': 'areaofpedologicalinterest',
                'description': '',
                'imageUrl': '',
                'legendUrl': '',
                'defaultAddToManager': True
            }
        ),
        Layer(
            type='wms',
            title='Dieptemetingen (BRO)',
            isBackground=False,
            defaultOn=False,
            url='https://service.pdok.nl/bzk/bro-grondwaterspiegeldiepte/wms/v1_0?service=WMS&version=1.1.1',
            featureName='bro-grondwaterspiegeldieptemetingen',
            content={
                'contenttype': 'image/png',
                'attribution': 'bro-grondwaterspiegeldieptemetingen',
                'description': '',
                'imageUrl': '',
                'legendUrl': '',
                'defaultAddToManager': True
            }
        ),
        Layer(
            type='wms',
            title='GHG - gemiddeld kleinste diepte (BRO)',
            isBackground=False,
            defaultOn=False,
            url='https://service.pdok.nl/bzk/bro-grondwaterspiegeldiepte/wms/v1_0?service=WMS&version=1.1.1',
            featureName='bro-grondwaterspiegeldieptemetingen-GHG',
            content={
                'contenttype': 'image/png',
                'attribution': 'bro-grondwaterspiegeldieptemetingen-GHG',
                'description': '',
                'imageUrl': '',
                'legendUrl': '',
                'defaultAddToManager': True
            }
        ),
        Layer(
            type='wms',
            title='GLG - gemiddeld grootste diepte (BRO)',
            isBackground=False,
            defaultOn=False,
            url='https://service.pdok.nl/bzk/bro-grondwaterspiegeldiepte/wms/v1_0?service=WMS&version=1.1.1',
            featureName='bro-grondwaterspiegeldieptemetingen-GLG',
            content={
                'contenttype': 'image/png',
                'attribution': 'bro-grondwaterspiegeldieptemetingen-GLG',
                'description': '',
                'imageUrl': '',
                'legendUrl': '',
                'defaultAddToManager': True
            }
        ),
        Layer(
            type='wms',
            title='GVG - gemiddelde diepte voorjaar (BRO)',
            isBackground=False,
            defaultOn=False,
            url='https://service.pdok.nl/bzk/bro-grondwaterspiegeldiepte/wms/v1_0?service=WMS&version=1.1.1',
            featureName='bro-grondwaterspiegeldieptemetingen-GVG',
            content={
                'contenttype': 'image/png',
                'attribution': 'bro-grondwaterspiegeldieptemetingen-GVG',
                'description': '',
                'imageUrl': '',
                'legendUrl': '',
                'defaultAddToManager': True
            }
        ),
        Layer(
            type='wms',
            title='GT - Grondwatertrappen (BRO)',
            isBackground=False,
            defaultOn=False,
            url='https://service.pdok.nl/bzk/bro-grondwaterspiegeldiepte/wms/v1_0?service=WMS&version=1.1.1',
            featureName='bro-grondwaterspiegeldieptemetingen-GT',
            content={
                'contenttype': 'image/png',
                'attribution': 'bro-grondwaterspiegeldieptemetingen-GT',
                'description': '',
                'imageUrl': '',
                'legendUrl': '',
                'defaultAddToManager': True
            }
        ),
        Layer(
            type='3dtiles',
            title='GeoTOP',
            isBackground=False,
            defaultOn=False,
            url='https://virtueel.zeeland.nl/tiles_other/geotop_middelburg/tileset.json',
            featureName=None,
            content={
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
                },
                'attribution': 'BRO',
                'description': '',
                'imageUrl': '',
                'legendUrl': 'https://virtueel.zeeland.nl/tiles_other/legendas/geotop_legenda.png',
                'defaultAddToManager': True
            }
        ),
        Layer(
            type='3dtiles',
            title='FRESHEM',
            isBackground=False,
            defaultOn=False,
            url='https://virtueel.zeeland.nl/tiles_other/freshem_middelburg/tileset.json',
            featureName=None,
            content={
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
                },
                'attribution': '',
                'description': '',
                'imageUrl': '',
                'legendUrl': '',
                'defaultAddToManager': True
            }
        ),
        Layer(
            type='wms',
            title='Luchtfoto 2024 Ortho 8cm RGB',
            isBackground=False,
            defaultOn=False,
            url='https://service.pdok.nl/hwh/luchtfotorgb/wmts/v1_0',
            featureName='2024_orthoHR',
            content={
                'contenttype': 'image/png',
                'attribution': 'PDOK',
                'description': '',
                'imageUrl': '',
                'legendUrl': '',
                'defaultAddToManager': True
            }
        ),
        Layer(
            type='wms',
            title='Luchtfoto 2023 Ortho 8cm RGB',
            isBackground=False,
            defaultOn=False,
            url='https://service.pdok.nl/hwh/luchtfotorgb/wmts/v1_0',
            featureName='2023_orthoHR',
            content={
                'contenttype': 'image/png',
                'attribution': 'PDOK',
                'description': '',
                'imageUrl': '',
                'legendUrl': '',
                'defaultAddToManager': True
            }
        ),
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
