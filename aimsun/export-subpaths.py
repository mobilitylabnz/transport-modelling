import csv
import os

route_list = [['route', 'object_id', 'length', 'object_type']]
externalIds = {"P2G_Toll": '2033_p2g_untoll'}

for externalId, filename in externalIds.items():
    for subpath in model.getCatalog().getObjectsByType(model.getType('GKSubPath')).values():
        if subpath.getExternalId() == externalId:
            firstSection = True
            subpathName = subpath.getName()
            route = subpath.getRoute()
            for section in route:
                if firstSection:
                    firstSection = False
                    route_list.append([subpathName, section.getId(), section.length2D(), 'section'])
                else:
                    for turn in section.getOrigTurnings():
                        if (turn.getDestination() in route) and (turn.getOrigin() in route):
                            route_list.append([subpathName, turn.getId(), turn.length2D(), 'turn'])
                            route_list.append([subpathName, section.getId(), section.length2D(), 'section'])

    # export to CSV
    modelPath = os.path.dirname(GKSystem.getSystem().getActiveModel().getDocumentFileName())
    output_path = os.path.join(modelPath, "Resources", "Panels", f"subpaths_{filename}.csv")

    with open(output_path, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerows(route_list)

print("Finished Exporting Subpaths")
