import os
from datetime import datetime, timedelta


replication_id = 14676

filePath_section = os.path.join(os.path.dirname(str(model.getDocumentFileName())), 'output', f'{replication_id}_sections.csv')
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


# get section data
with open(filePath_section, 'w') as file:
    # write the header
    header = ['id', 'name', 'nb_lanes', 'speed', 'capacity', 'rd_type', 'line_wkt', 'time']
    header.extend([f'{column}_{replication_id}_{veh}' for column in output_columns for veh in veh_dict.keys()])
    file.write(','.join(header) + '\n')
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
            line_wkt = f'"LINESTRING ({", ".join([f"{p.x} {p.y}" for p in points])})"'

            # loop through the time periods
            for i in range(number_of_intervals):
                # get the time period
                time_period = datetime_objects[i]
                # get the time period string
                time_period_str = time_period.strftime('%Y-%m-%d %H:%M:%S')
                

                ts_data_list = []
                # get the time series data
                for column in output_columns:
                    for veh in veh_dict.values():
                        # get the column object
                        col = model.getType("GKSection").getColumn(f'DYNAMIC::GKSection_{column}_{replication_id}_{veh}',0)
                        # get the time series data
                        time_series = section.getDataValueTS(col)
                        # get the value
                        value = time_series.getValue(i)[0]
                        # add value to ts_data_list
                        ts_data_list.append(value)

                # write the data to the file
                data_row = [str(id), name, str(nb_lanes), str(speed), str(capacity), str(rd_type), line_wkt, time_period_str]
                data_row.extend([str(value) for value in ts_data_list])
                data_line = ','.join(data_row)
                file.write(data_line + '\n')

print(f'File written to {filePath_section}')

with open(filePath_turn, 'w') as file:
    # write the header
    header = ['id', 'name', 'line_wkt', 'time']
    header.extend([f'{column}_{replication_id}_{veh}' for column in output_columns for veh in veh_dict.keys()])
    file.write(','.join(header) + '\n')
    for turn in model.getCatalog().getObjectsByType(model.getType("GKTurning")).values():
        if turn.exists(scenario):
            # id
            id = turn.getId()
            # name
            name = turn.getName()
            # write out the linestring for conversion to a shapefile
            # get the points along the polyline
            points = turn.getPoints()
            line_wkt = f'"LINESTRING ({", ".join([f"{p.x} {p.y}" for p in points])})"'

            # loop through the time periods
            for i in range(number_of_intervals):
                # get the time period
                time_period = datetime_objects[i]
                # get the time period string
                time_period_str = time_period.strftime('%Y-%m-%d %H:%M:%S')
                

                ts_data_list = []
                # get the time series data
                for column in output_columns:
                    for veh in veh_dict.values():
                        # get the column object
                        col = model.getType("GKTurning").getColumn(f'DYNAMIC::GKTurning_{column}_{replication_id}_{veh}',0)
                        # get the time series data
                        time_series = turn.getDataValueTS(col)
                        # get the value
                        value = time_series.getValue(i)[0]
                        # add value to ts_data_list
                        ts_data_list.append(value)

                # write the data to the file
                data_row = [str(id), name, line_wkt, time_period_str]
                data_row.extend([str(value) for value in ts_data_list])
                data_line = ','.join(data_row)
                file.write(data_line + '\n')

print(f'File written to {filePath_turn}')