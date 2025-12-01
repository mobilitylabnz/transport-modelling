import os
import json

directory = os.path.dirname(GKSystem.getSystem().getActiveModel().getDocumentFileName())
filePath_signalgroups = os.path.join(directory, "Resources", "SCATS", "movements.geojson")
# create the folder if it doesn't exist
os.makedirs(os.path.dirname(filePath_signalgroups), exist_ok=True)

scenario = model.getActiveScenario()

geoModel = model.getGeoModel()

translator = geoModel.getCoordinateTranslator()

nodeType = model.getType("GKNode")

# Initialise a list to hold GeoJSON features
features = []


for node in model.getCatalog().getObjectsByType(nodeType).values():
    # get node signal groups and turns
    signal_turns = {}
    for group in node.getSignals():
        geometry = {}
        geometry['type'] = 'MultiLineString'
        if geometry.get('coordinates') is None:
            geometry['coordinates'] = []
        turns = group.getTurnings()
        # for each turn get the geometry
        for turn in turns:
            if turn.exists(scenario):
                points = turn.calculatePolyline(20, False, [])
                geometry['coordinates'].append([[translator.toDegrees(p).x, translator.toDegrees(p).y] for p in points])
			
        properties = {
            'id': group.getId(),
            'signal_group_name': group.getName(),
            'node_id': node.getId(),
        }
        feature = {
            'type': 'Feature',
            'geometry': geometry,
            'properties': properties
        }
        features.append(feature)

# create feature collection
feature_collection = {
    "type": "FeatureCollection",
    "features": features
}

with open(filePath_signalgroups, 'w') as f:
    json.dump(feature_collection, f, indent=4)

print(f'File written to {filePath_signalgroups}')