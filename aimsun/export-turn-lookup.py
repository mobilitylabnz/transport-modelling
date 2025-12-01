import csv
import os

turn_list = []
turn_list.append(['turn','origin','destination'])

turnType = model.getType("GKTurning")

for turn in model.getCatalog().getObjectsByType( turnType ).values():
	origin = turn.getOrigin()
	destination = turn.getDestination()
	turn_list.append([turn.getId(), origin.getId(), destination.getId()])

# export to csv
modelPath = os.path.dirname(GKSystem.getSystem().getActiveModel().getDocumentFileName())
output_path = os.path.join(modelPath, "Resources", "turn_lookup.csv")
	
with open(output_path, mode='w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerows(turn_list)

print("Finished Exporting Turn Lookup")