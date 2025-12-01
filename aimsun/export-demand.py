import csv
import os

modelPath = os.path.dirname(GKSystem.getSystem().getActiveModel().getDocumentFileName())

centroidConfig = model.getCatalog().find(34359197)

#demand_dict = {'cordon_am': 34359482, 'cordon_pm': 34359614, 'adjusted_am': 34403751, 'adjusted_pm': 34387053}
demand_dict = {'ec_am': 34360283, 'ec_pm': 34387052}

# Centroid lookup
centroidDict = {c.getId(): c for c in centroidConfig.getCentroids()}

for peak, demand_id in demand_dict.items():
    demand = model.getCatalog().find(demand_id)
    schedule = demand.getSchedule()

    demandOutput = [['origin', 'destination', 'time', 'vehicle', 'trips']]

    for scheduleItem in schedule:
        startTime = scheduleItem.getFrom()
        # Try to format as ISO if it's a Qt time/datetime; otherwise fallback to str()
        try:
            time_str = startTime.toString(Qt.ISODate)  # type: ignore
        except Exception:
            time_str = str(startTime)

        trafficDemand = scheduleItem.getTrafficDemandItem()
        userClass = trafficDemand.getUserClass().getName()

        for origin_id, originC in centroidDict.items():
            for dest_id, destinationC in centroidDict.items():
                trips = trafficDemand.getTrips(originC, destinationC)
                demandOutput.append([origin_id, dest_id, time_str, userClass, trips])

    outputPath = os.path.join(modelPath, 'Resources', 'Demand', f'{peak}_cordon_demand.csv')

    # In Python 3, write text with newline='' to avoid extra blank lines on Windows
    with open(outputPath, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerows(demandOutput)

print("Finished Exporting Demand to CSV")