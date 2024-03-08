'''
This scripts exports section and turn time series data to GeoJSON format.
output columns should be defined based on the name used in the attribute data. This can be found in the type data in the Aimsun GUI.

08/03/2024
Caleb Deverell
caleb@mobilitylab.co.nz
'''
import os
from datetime import datetime, timedelta
import json


replication_ids = [9999]


geoModel = model.getGeoModel()

translator = geoModel.getCoordinateTranslator()

for replication_id in replication_ids:

    filePath_section = os.path.join(os.path.dirname(str(model.getDocumentFileName())), 'output', f'{replication_id}_sections.geojson')
    filePath_turn = os.path.join(os.path.dirname(str(model.getDocumentFileName())), 'output', f'{replication_id}_turns.csv')

    # time series output columns
    output_columns = ['delayTime', 'count', 'speed', 'travelTime']

    # initial setup

    # get the replication object
    replication = model.getCatalog().find(replication_id)
    # get the experiment and scenario objects
    experiment = replication.getExperiment()
    scenario = experiment.getScenario()
    # get the date of the scenario
    date = scenario.getDate().toString("yyyy-MM-dd")
    # get the statistical interval of the scenario outputs
    interval = scenario.getInputData().getStatisticalInterval().toMinutes()
    # get the scenario start time
    start_time = scenario.getDemand().initialTime().toString()
    # get the scenario duration
    duration = scenario.getDemand().duration().toMinutes()

    # create the datetime objects for each interval
    start_time = datetime.strptime(f'{date} {start_time}','%Y-%m-%d %H:%M:%S')
    number_of_intervals = int(duration / interval)
    datetime_objects = [start_time + timedelta(minutes=interval * i) for i in range(number_of_intervals)]

    # get the list of vehicles - start with 0 to get all vehicle statistics
    veh_dict = {'all':0}

    for veh in scenario.getDemand().getUsedVehicles():
        name = veh.getName()
        id = veh.getId()
        if name not in veh_dict:
            veh_dict[name] = id


    ptplan = scenario.getPublicLinePlan()
    ptvehs = ptplan.getUsedVehicles()
    for ptveh in ptvehs:
        name = veh.getName()
        id = veh.getId()
        if name not in veh_dict:
            veh_dict[name] = id


    # Initialize a list to hold GeoJSON features
    features = []

    for section in model.getCatalog().getObjectsByType(model.getType("GKSection")).values():
        if section.exists(scenario):
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

            # write out the linestring for conversion to a shapefile
            # get the points along the polyline
            points = section.getPoints()

            geometry = {
                "type": "LineString",
                "coordinates": [[translator.toDegrees(p).x, translator.toDegrees(p).y] for p in points]
            }

            # loop through the time periods
            for i in range(number_of_intervals):
                # get the time period
                time_period = datetime_objects[i]
                # get the time period string
                time_period_str = time_period.strftime('%Y-%m-%d %H:%M:%S')  

                properties = {
                    "id": id,
                    "name": name,
                    "nb_lanes": nb_lanes,
                    "speed": speed,
                    "capacity": capacity,
                    "rd_type": rd_type,
                    "datetime": time_period_str,
                }
                    
                # get the time series data
                for column in output_columns:
                    for veh_name, veh in veh_dict.items():
                        # get the column object
                        col = model.getType("GKSection").getColumn(f'DYNAMIC::GKSection_{column}_{replication_id}_{veh}',0)
                        # get the time series data
                        time_series = section.getDataValueTS(col)
                        # get the value
                        value = time_series.getValue(i)[0]
                        properties[f'{column}_{replication_id}_{veh_name}'] = value
                        
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
        if turn.exists(scenario):
            # id
            id = turn.getId()
            # name
            name = turn.getName()
            # write out the linestring for conversion to a shapefile
            # get the points along the polyline
            points = turn.getPoints()

            geometry = {
                "type": "LineString",
                "coordinates": [[translator.toDegrees(p).x, translator.toDegrees(p).y] for p in points]
            }

            # loop through the time periods
            for i in range(number_of_intervals):
                # get the time period
                time_period = datetime_objects[i]
                # get the time period string
                time_period_str = time_period.strftime('%Y-%m-%d %H:%M:%S')  

                properties = {
                    "id": id,
                    "name": name,
                    "datetime": time_period_str,
                }
                    
                # get the time series data
                for column in output_columns:
                    for veh_name, veh in veh_dict.items():
                        # get the column object
                        col = model.getType("GKTurning").getColumn(f'DYNAMIC::GKTurning_{column}_{replication_id}_{veh}',0)
                        # get the time series data
                        time_series = turn.getDataValueTS(col)
                        # get the value
                        value = time_series.getValue(i)[0]
                        properties[f'{column}_{replication_id}_{veh_name}'] = value
                        
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