import csv
import os

modelPath = os.path.dirname(GKSystem.getSystem().getActiveModel().getDocumentFileName())

timing_data_path = f"{modelPath}/Resources/SCATS/scats_timing_scaled.csv"
signal_group_lookup_path = f"{modelPath}/Resources/SCATS/signal_group_lookup.csv"

# create a map of detectors
detectorLookup = {}
detectorType = model.getType("GKDetector")
for detector in model.getCatalog().getObjectsByType( detectorType ).values():
	section = detector.getSection()
	fromLane = detector.getFromLane()
	toLane = detector.getToLane()
	pos = detector.getPositionFromEnd()
	if pos <  5:
		if section not in detectorLookup:
			detectorLookup[section] = []
		detectorLookup[section].append({'detector': detector, 'fromLane': fromLane, 'toLane': toLane})



# read in signal_group_lookup.csv to create a mapping of phases to signal groups
signal_group_map = {}
with open(signal_group_lookup_path, 'r', newline='', encoding='utf-8') as lookup_file:
    reader = csv.DictReader(lookup_file)
    for row in reader:
        site = row['Site']
        phase = row['Phase']
        signal_id = int(row['MovementId'])
        if site not in signal_group_map:
            signal_group_map[site] = {}
        if phase not in signal_group_map[site]:
            signal_group_map[site][phase] = []
        signal_group_map[site][phase].append(signal_id)


# get nodes from the model
node_lookup = {}
for node in model.getCatalog().getObjectsByType(model.getType('GKNode')).values():
    external_id = node.getExternalId()
    if external_id not in node_lookup:
        node_lookup[external_id] = {'node': None, 'signals': {}}
        node_lookup[external_id]['node'] = node
    signals = node.getSignals()
    for signal in signals:
        signal_name = signal.getName()
        signal_id = signal.getId()
        if signal_id not in node_lookup[external_id]['signals']:
            node_lookup[external_id]['signals'][signal_id] = signal

def get_control_junction(time_group, node):
    control_plans = {}
    for plan in model.getCatalog().getObjectsByType(model.getType('GKControlPlan')).values():
        plan_name = plan.getName()
        control_plans[plan_name] = plan

    # strip out seconds and : from time_group string
    time_group_stripped = time_group[:-3].replace(":", "")
    control_plan_name = f"Base_2023_{time_group_stripped}"
    control_plan = control_plans.get(control_plan_name, None)
    control_junction = control_plan.getControlJunction(node)
    


    return control_junction

signal_phase_map = {}
with open(timing_data_path, 'r', newline='', encoding='utf-8') as timing_file:
    reader = csv.DictReader(timing_file)
    for row in reader:

        site = row['Site']
        if site not in signal_phase_map:
            signal_phase_map[site] = {}

        time_group = row['Time Group']
        if time_group not in signal_phase_map[site]:
            signal_phase_map[site][time_group] = {}

        phase = row['Phase']
        cycle_time = row['Avg Cycle Time (s)']
        duration = row['Scaled Duration (s)']

        signal_phase_map[site][time_group]['cycle_time'] = cycle_time
        if 'phases' not in signal_phase_map[site][time_group]:
            signal_phase_map[site][time_group]['phases'] = []
        signal_phase_map[site][time_group]['phases'].append({'phase': phase, 'duration': duration})





# loop through the signal_phase_map to update the model
for site in signal_phase_map:
    for time_group in signal_phase_map[site]:
        print(f"Setting signal plan for site {site} time group {time_group}")
        cycle_time = signal_phase_map[site][time_group]['cycle_time']
        phases = signal_phase_map[site][time_group]['phases']

        control_junction = get_control_junction(time_group, node_lookup[site]['node'])
        # set as actuated control type
        control_junction.setControlJunctionType(4)
        # remove phases from control junction
        control_junction.removePhases()
        # set the cycle time
        control_junction.setCycle(float(cycle_time))
        from_time = 0
        for phase_info in phases:
            phase = phase_info['phase']
            phase_duration = phase_info['duration']
            # create a new phase
            new_phase = control_junction.createPhase()
            # set the phase from time and duration
            new_phase.setFrom(float(from_time))
            new_phase.setDuration(float(phase_duration) - 5)
            # add the signals to the phase
            # if phase exists in signal_group_map
            if phase in signal_group_map[site]:
                for signal_group in signal_group_map[site][phase]:
                    if signal_group in node_lookup[site]['signals']:
                        signal = node_lookup[site]['signals'][signal_group]
                        new_phase.addSignal(signal)

            # setting standard actuation parameters
            new_phase.setMinDuration(float(phase_duration) - 5)
            new_phase.setMaxDuration(float(phase_duration) - 5)
            new_phase.setRecall(1)

            if float(phase_duration)-5 <= 5.0:
                # setting recall to 0 (No recall)
                new_phase.setRecall(0)
                signals = new_phase.getSignals()
                for signal in signals:
                    actual_signal = signal.getSignal()
                    turns = actual_signal.getTurnings()
                    for turn in turns:
                        origin_section = turn.getOrigin()
                        fromLane = turn.getOriginFromLane()
                        toLane = turn.getOriginToLane()
                        # find the detectors on the origin section
                        if origin_section in detectorLookup:
                            for detector_info in detectorLookup[origin_section]:
                                detector = detector_info['detector']
                                det_fromLane = detector_info['fromLane']
                                det_toLane = detector_info['toLane']
                                # if the detector fromLane is within the signal turning fromLane and toLane
                                if (det_fromLane >= fromLane) and (det_fromLane <= toLane):
                                    control_detector = new_phase.createControlDetector(detector)
                                    new_phase.addControlDetector(control_detector)
            # add the phase to the control junction
            #control_junction.addPhase(new_phase)
            # add the interphase time of 5 seconds
            inter_phase = control_junction.createPhase()
            inter_phase.setFrom(float(from_time) + float(phase_duration) - 5)
            inter_phase.setDuration(5)
            inter_phase.setInterphase(True)
            #control_junction.addPhase(inter_phase)
            # increment the from_time
            from_time += float(phase_duration)



# loop through the signal_phase_map to add in interphase movements
for site in signal_phase_map:
    for time_group in signal_phase_map[site]:


        control_junction = get_control_junction(time_group, node_lookup[site]['node'])

        phases = control_junction.getPhases()

        for index, phase in enumerate(phases):
            interphase = phase.getInterphase()
            if interphase:
                # get the signals from the previous phase
                previous_phase = phases[index - 1]
                signals = previous_phase.getSignals()
                # get the signals of the next phase
                next_phase = phases[(index + 1) % len(phases)]
                next_signals = next_phase.getSignals()
                # check if there are common signals between the two phases
                common_signals = []
                for signal in signals:
                    for next_signal in next_signals:
                        if signal.getSignal() == next_signal.getSignal():
                            common_signals.append(signal.getSignal())
                # add signals to interphase
                for signal in common_signals:
                    phase.addSignal(signal)

print("Finished Setting Signal Plans")