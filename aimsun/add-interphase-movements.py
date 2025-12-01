controlPlan = model.getCatalog().find(88955768)

node = model.getCatalog().find(10261415)

controlJunction = controlPlan.getControlJunction(node)


phases = controlJunction.getPhases()

for index, phase in enumerate(phases):
    interphase = phase.getInterphase()
    if interphase:
        print(f"Setting signals for interphase {index+1}")
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


print("Finished")