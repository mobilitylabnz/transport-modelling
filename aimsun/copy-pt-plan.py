'''
This script duplicates specified PT Plans along with their PT Lines and Timetables.
If the duplicated PT Lines are not correct in the active scenario, it attempts to fix their routes
by finding the shortest paths between sections.

The corrected PT Lines are corrected to the current active scenario.

WARNING: This script does not handle adding bus stops back into the corrected PT Lines.

Caleb
caleb@mobilitylab.co.nz
'''


ptLineType = model.getType("GKPublicLine")

activeScenario = model.getActiveScenario()
activeExperiment = model.getActiveExperiment()


ptLine_dict = {}

spManager = GKSPManager()
spManager.setCostType(0)
spManager.build(model, activeExperiment)


def duplicateObject(object):
    cmd = GKObjectDuplicateCmd()
    cmd.init( object )
    model.getCommander().addCommand(cmd)

    return cmd.createdObject()


def duplicatePTPlan(ptPlans, optionName):
    for ptPlanId in ptPlans:
        ptPlan = model.getCatalog().find(ptPlanId)
        print(f"Duplicating PT Plan: {ptPlan.getName()} for option name: {optionName}")
        newPTPlan = duplicateObject(ptPlan)
        newPTPlan.setExternalId(optionName)
        newPTPlan.setName(f"{ptPlan.getName()}_{optionName}")

        # for each ptline in the ptplan timetable - remove it from newPTPlan, duplicate it, and add the duplicate to newPTPlan
        for timeTable in ptPlan.getTimeTables():
            # create the pt line / timetable lookup
            ptLine = timeTable.getPublicLine()
            if ptLine not in ptLine_dict:
                ptLine_dict[ptLine] = [timeTable]
            else:
                ptLine_dict[ptLine].append(timeTable)

        for ptLine, timeTables in ptLine_dict.items():
            for timeTable in timeTables:
                newPTPlan.removeTimeTable(timeTable)



            newPTLine = duplicateObject(ptLine)
            newPTLine.setExternalId(optionName)
            newPTLine.setName(ptLine.getName())

            if not newPTLine.isCorrect(activeScenario)[0]:
                # print(f"Warning: duplicated PT Line {newPTLine.getName()} is not correct in the active scenario.")
                existingSections = []
                for section in newPTLine.getRoute():
                    if section.exists(activeScenario):
                        existingSections.append(section)

                correctRoute = []
                for index, section in enumerate(existingSections):
                    if index+1 < len(existingSections):
                        nextSection = existingSections[index+1]
                        # get the shortest path
                        path = spManager.getPath(section, nextSection)
                        # print(f"Fixing route between section {section.getId()} and {nextSection.getId()}")
                        pathIds = [sec.getId() for sec in path]
                        # print(f"Shortest path sections: {pathIds}")
                        # remove the section that already exists
                        path.remove(section)
                        path.remove(nextSection)
                        correctRoute.append(section)
                        correctRoute.extend(path)
                    else:
                        correctRoute.append(section)
                newPTLine.setRoute(correctRoute)




            for newTimeTable in newPTLine.getTimeTables():
                newPTPlan.addTimeTable(newTimeTable)

print("Finished duplicating PT Plans")



ptPlans = [89335929, 89336136]
optionName = "Option"

duplicatePTPlan(ptPlans, optionName)