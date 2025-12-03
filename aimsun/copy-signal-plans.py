fromToCPLookup = {
    'Base_2023_0600': 'Option_2023_0600',
    'Base_2023_0700': 'Option_2023_0700',
    'Base_2023_0800': 'Option_2023_0800',
    'Base_2023_0900': 'Option_2023_0900',
    'Base_2023_1500': 'Option_2023_1500',
    'Base_2023_1600': 'Option_2023_1600',
    'Base_2023_1700': 'Option_2023_1700',
    'Base_2023_1800': 'Option_2023_1800',
}



activeScenario = model.getActiveScenario()
fromScenario = model.getCatalog().find(89336350)


nodeType = model.getType("GKNode")


def isNodeSignalised(node, fromToCPLookup):
    # get the first control plan name from the fromToCPLookup
    fromCPName = fromToCPLookup[list(fromToCPLookup.keys())[0]]
    controlPlan = model.getCatalog().findByName(fromCPName)
    controlJunction = controlPlan.getControlJunction(node)
    if controlJunction is not None:
        return True

# signalised intersection dictionary
signalisedIntersectionDict = {}

for node in model.getCatalog().getObjectsByType(nodeType).values():
    if node.exists(fromScenario):
        if isNodeSignalised(node, fromToCPLookup):
            nodeEid = node.getExternalId()
            signalisedIntersectionDict[nodeEid] = node


for node in model.getCatalog().getObjectsByType(nodeType).values():
    if node.exists(activeScenario):
        nodeEid = node.getExternalId()
        if nodeEid in signalisedIntersectionDict:
            fromNode = signalisedIntersectionDict[nodeEid]
            # get the signals
            signalLookup = {}
            fromSignals = fromNode.getSignals()
            for signal in fromSignals:
                signalLookup[signal.getName()] = signal
            for fromControlPlan, toControlPlan in fromToCPLookup.items():
                fromCP = model.getCatalog().findByName(fromControlPlan)
                toCP = model.getCatalog().findByName(toControlPlan)
                fromControlJunction = fromCP.getControlJunction(fromNode)
                toControlJunction = toCP.createControlJunction(node)
                toControlJunction.removePhases()
                toControlJunction.setControlJunctionType(fromControlJunction.getControlJunctionType())
                toControlJunction.setCycle(fromControlJunction.getCycle())
                toControlJunction.setOffset(fromControlJunction.getOffset())
                toControlJunction.setYellowTime(fromControlJunction.getYellowTime())

                # do phases
                for fromPhase in fromControlJunction.sortPhases():
                    toPhase = toControlJunction.createPhase()
                    toPhase.setFrom(fromPhase.getFrom())
                    toPhase.setDuration(fromPhase.getDuration())
                    toPhase.setMinDuration(fromPhase.getMinDuration())
                    toPhase.setMaxDuration(fromPhase.getMaxDuration())
                    toPhase.setInterphase(fromPhase.getInterphase())
                    toPhase.setRecall(fromPhase.getRecall())
                    for signal in fromPhase.getSignals():
                        fromSignal = signal.getSignal()
                        signalName = fromSignal.getName()
                        toPhase.addSignal(signalLookup[signalName])
                    for detector in fromPhase.getControlDetectors():
                        controlDetector = toPhase.createControlDetector(detector)
                        toPhase.addControlDetector(controlDetector)
                
print("Signalised intersections copied successfully.")