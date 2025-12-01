scenario_from = model.getCatalog().find(34355785)
experiment_from = model.getCatalog().find(34355787)

scenarios_to = [34431446]
experiments_to = [34431448]


# set the Geometry Configuration for the input scenario based on the input list
def setGeoConfig(scenario,geoconfig_lst):
    geo_lst = []
    for configid in geoconfig_lst:
        geo_lst.append(configid)
    scenario.setGeometryConfigurations(geo_lst)

# set the Strategies and Conditions for the input scenario based on the input list
def setStratCond(scenario,strat_lst):
    scenario.removeAllStrategiesAndConditions()
    for strat in strat_lst:
        strat_obj = strat
        scenario.addStrategy(strat_obj)

# set the Attribute Overrides for the input experiment based on the input list
def setAttOver(experiment, attover_lst):
    experiment.clearNetworkAttributesOverrides()
    for attribute in attover_lst:
        att_obj = attribute
        experiment.addNetworkAttributesOverride(att_obj)

# set the Policies for the input experiment based on the input list
def setPolicy(experiment, policy_lst):
    experiment.removePolicies()
    for policy in policy_lst:
        policy_obj = policy
        experiment.addPolicy(policy_obj)




geoConfigs = scenario_from.getGeometryConfigurations()
for scenario_id in scenarios_to:
	scenario = model.getCatalog().find(scenario_id)
	setGeoConfig(scenario, geoConfigs)

attOvers = experiment_from.getNetworkAttributesOverrides()
for experiment_id in experiments_to:
	experiment = model.getCatalog().find(experiment_id)
	setAttOver(experiment, attOvers)

print("Finished Setting GeoConfigs and Attribute Overrides")
