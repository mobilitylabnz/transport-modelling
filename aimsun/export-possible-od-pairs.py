activeScenario = model.getActiveScenario()
activeExperiment = model.getActiveExperiment()


spManager = GKSPManager()
spManager.setCostType(0)
spManager.build(model, activeExperiment)

def findShortestPath(origin, destination):
    path = spManager.getPath(origin, destination)
    if len(path) > 0:
        return True
    else:
        return False
    

centoidConfig = model.getCatalog().find(89335710)

# loop through origin and destination centroids
od_pairs = []
for origin in centoidConfig.getOriginCentroids():
    for destination in centoidConfig.getDestinationCentroids():
        origin_id = origin.getId()
        destination_id = destination.getId()
        if origin_id != destination_id:
            if findShortestPath(origin, destination):
                od_pairs.append((origin_id, destination_id))
            else:
                print(f"No path from {origin_id} to {destination_id}")

# export to CSV
import csv
import os

directory = os.path.dirname(GKSystem.getSystem().getActiveModel().getDocumentFileName())
filePath_odpairs = os.path.join(directory, "Resources", "Demand", "possible_od_pairs.csv")
# create the folder if it doesn't exist
os.makedirs(os.path.dirname(filePath_odpairs), exist_ok=True)

with open(filePath_odpairs, 'w', newline='') as csvfile:
    fieldnames = ['origin_id', 'destination_id']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

    writer.writeheader()
    for od_pair in od_pairs:
        writer.writerow({'origin_id': od_pair[0], 'destination_id': od_pair[1]})

print(f'File written to {filePath_odpairs}')