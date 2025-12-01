'''
This scripts exports section and turn time series data to GeoJSON format.
output columns should be defined based on the name used in the attribute data. This can be found in the type data in the Aimsun GUI.

The replication must have data either loaded in or able to be retrieved from the database.

28/01/2024
Caleb Deverell
caleb@mobilitylab.co.nz
'''
import os
from datetime import datetime, timedelta
import json

def export_gis(scenario_name, replication_id, directory):



	subNetPolygon = model.getCatalog().find(89335707)
	scenario = model.getCatalog().find(replication_id).getExperiment().getScenario()
	sectionsInside = subNetPolygon.classifyObjectsPartiallyInside(scenario)
	turnsInside = subNetPolygon.classifyObjectsInside(scenario)


	geoModel = model.getGeoModel()

	translator = geoModel.getCoordinateTranslator()

	filePath_section = os.path.join(directory, 'Resources', f'{scenario_name}_sections.geojson')
	filePath_turn = os.path.join(directory, 'Resources', f'{scenario_name}_turns.geojson')


	# initial setup

	# get the replication object
	replication = model.getCatalog().find(replication_id)


	# Initialize a list to hold GeoJSON features
	features = []

	for section in model.getCatalog().getObjectsByType(model.getType("GKSection")).values():
		if section.exists(scenario) and section in sectionsInside:
			# id
			id = section.getId()
			# name
			name = section.getName()
			# nb_lanes
			nb_lanes = len(section.getLanes())
			# speed
			speed = section.getSpeed()
			# capacity
			capacity = section.getCapacity()
			# rd_type
			rd_type = section.getRoadType().getId()
			# section length
			length = section.length2D()

			# write out the linestring for conversion to a shapefile
			# get the points along the polyline
			points = section.calculatePolyline()

			geometry = {
				"type": "LineString",
				"coordinates": [[translator.toDegrees(p).x, translator.toDegrees(p).y] for p in points]
			}

			properties = {
								"id": id,
								"name": name,
								"nb_lanes": nb_lanes,
								"speed": speed,
								"capacity": capacity,
								"rd_type": rd_type,
								"length": length
							}

			# add the feature to the list
			feature = {
				"type": "Feature",
				"geometry": geometry,
				"properties": properties
			}
			features.append(feature)

	# create feature collection
	feature_collection = {
		"type": "FeatureCollection",
		"features": features
	}

	with open(filePath_section, 'w') as f:
		json.dump(feature_collection, f, indent=4)

	print(f'File written to {filePath_section}')


	# Initialize a list to hold GeoJSON features
	features = []

	for turn in model.getCatalog().getObjectsByType(model.getType("GKTurning")).values():
		if turn.exists(scenario) and turn in turnsInside:
			# id
			id = turn.getId()
			# name
			name = turn.getName()
			# length
			length = turn.length2D()
			# write out the linestring for conversion to a shapefile
			# get the points along the polyline
			points = turn.calculatePolyline(20, False, [])

			geometry = {
				"type": "LineString",
				"coordinates": [[translator.toDegrees(p).x, translator.toDegrees(p).y] for p in points]
			}

			properties = {
								"id": id,
								"name": name,
								"length": length
							}
					
			# add the feature to the list
			feature = {
				"type": "Feature",
				"geometry": geometry,
				"properties": properties
			}
			features.append(feature)

	# create feature collection
	feature_collection = {
		"type": "FeatureCollection",
		"features": features
	}

	with open(filePath_turn, 'w') as f:
		json.dump(feature_collection, f, indent=4)

	print(f'File written to {filePath_turn}')

export_data = {'2025 Base': 89336353}


directory = os.path.dirname(GKSystem.getSystem().getActiveModel().getDocumentFileName())

for scenario, replication_id in export_data.items():
	print(scenario, replication_id)
	export_gis(scenario, replication_id, directory)