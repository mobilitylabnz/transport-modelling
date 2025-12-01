import os
import csv

scenarios = {'2033 DM': 34431440, '2033 DF1 with Signalised Ruahine': 34421285, '2033 DF1 with LILO Ruahine': 34465072, '2033 Early Works': 34514402}
for scenario_name, replication_id in scenarios.items():
    scenario = model.getCatalog().find(replication_id).getExperiment().getScenario()

    lane_list = []
    lane_list.append(['id','length','lanes', 'type'])

    for section in model.getCatalog().getObjectsByType( model.getType('GKSection') ).values():
        if section.exists(scenario):
            id = section.getId()
            lanes = section.getExitLanes()[1] +1
            length = section.length2D()
            lane_list.append([id, length, lanes, 'section'])

    for turn in model.getCatalog().getObjectsByType(model.getType("GKTurning")).values():
        if turn.exists(scenario):
            id = turn.getId()
            originFromLane = turn.getOriginFromLane()
            originToLane = turn.getOriginToLane()
            lanes = abs(originToLane - originFromLane) + 1
            length = turn.length2D()
            lane_list.append([id, length, lanes, 'turn'])	


    # export to csv
    modelPath = os.path.dirname(GKSystem.getSystem().getActiveModel().getDocumentFileName())
    output_path = os.path.join(modelPath, "Resources", f"section_lanes_{scenario_name}.csv")

    with open(output_path, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerows(lane_list)
    print(f"Finished Exporting Section Lanes for scenario: {scenario_name}")

print("Finished Exporting Section Lanes")