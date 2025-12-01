import csv
import os

path = r'C:\Users\caleb\Documents\Projects\1022_WellingtonRoNS_Phase2\20250804 - Submodels Created\Resources\Demand'
option = 'Option'
year = 2033

peaks = ['am', 'pm']

def createMatrix(matrixName, vehicleName, centroidConfig, time_str, year, option, peak):
    """
    Create a matrix with the given name and vehicle type.
    """
    matrix = GKSystem.getSystem().newObject("GKODMatrix", model)
    matrix.setName(matrixName)
    centroidConfig.addODMatrix(matrix)
    vehicle = model.getCatalog().findByName(vehicleName, model.getType("GKVehicle"))
    matrix.setVehicle(vehicle)
    print(time_str)
    matrix.setFrom(QTime.fromString(time_str, Qt.ISODate))
    matrix.setDuration(GKTimeDuration.fromString("00:15:00"))
    matrix.setExternalId(f"{year} {option} {peak}")
    return matrix

# create a centroid lookup
centroidConfig = model.getCatalog().find(34359197)
centDict = {}
for centroid in centroidConfig.getCentroids():
    if centroid.getId() not in centDict:
        centDict[centroid.getId()] = centroid

# create a demand lookup
matrices = centroidConfig.getODMatrices()
matrixDict = {}
for matrix in matrices:
    if matrix.getName() not in matrixDict:
        matrixDict[matrix.getName()] = matrix

for peak in peaks:
    filename = f"ec_{option}_{peak}_forecast_demand_v3.csv"
    filepath = os.path.join(path, filename)

    # Read the CSV file (text mode for Python 3; newline='' prevents extra blank lines on Windows)
    with open(filepath, 'r', newline='', encoding='utf-8-sig') as csvfile:
        reader = csv.reader(csvfile)
        header = next(reader)
        data = [row for row in reader]

    timestamps = header[3:]
    print(timestamps)

    for i, time_str in enumerate(timestamps):
        for row in data:
            originId = row[0]
            destinationId = row[1]
            vehicle = row[2]

            matrixName = f"{year} {option} {peak} {vehicle} {time_str}"
            if matrixName not in matrixDict:
                print(f"Matrix {matrixName} not found in matrixDict")
                # create the matrix if it does not exist
                matrix = createMatrix(matrixName, vehicle, centroidConfig, time_str, year, option, peak)
                matrixDict[matrixName] = matrix
            else:
                matrix = matrixDict[matrixName]

            # Get the origin and destination centroids
            originCentroid = centDict.get(int(originId)) if originId else None
            destinationCentroid = centDict.get(int(destinationId)) if destinationId else None
            if not originCentroid or not destinationCentroid:
                print(f"Origin or destination centroid not found for {originId} to {destinationId}")
                continue

            # get the trips for the current time
            trips = row[3 + i] if len(row) > 3 + i else ''
            if not trips:
                print(f"No trips found for {originId} to {destinationId} at {time_str}")
                continue

            try:
                trips_val = float(trips)
            except ValueError:
                print(f"Invalid trips value '{trips}' for {originId} to {destinationId} at {time_str}")
                continue

            # Set the trips in the matrix
            matrix.setTrips(originCentroid, destinationCentroid, trips_val)

print("Finished importing matrices")
