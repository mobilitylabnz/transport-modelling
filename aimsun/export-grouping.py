import os
import csv

profileSystem = model.getCatalog().find(89335871)

exportSystem = []
exportSystem.append(['group','centroid'])

for groupId in profileSystem.getGroups():
	group = model.getCatalog().find(groupId) 
	for centroid in group.getObjects():
		exportSystem.append([group.getName(), centroid.getId()])

# export to CSV
directory = os.path.dirname(GKSystem.getSystem().getActiveModel().getDocumentFileName())
output_path = os.path.join(directory, "Resources", "group_centroid_mapping.csv")
with open(output_path, 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerows(exportSystem)
print(f"Exported groups to {output_path}")