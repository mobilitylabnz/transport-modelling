import os

class PathReader(ForestCalculator):
    def __init__(self, forest, model, name):
        super(ForestCalculator, self).__init__(forest, model, ForestCalculator.eOnlyAvailablePaths)
        self.forest = forest
        self.model = model
        self.name = name
        self.geo = forest.getGeometry()
        self.nbLines = 1
        self.file = None

    def init(self):
        output_folder = os.path.join(os.path.dirname(str(model.getDocumentFileName())), 'Outputs')
        try:
            os.mkdir(output_folder)
        except OSError:
            print("Outputs folder already exists.")

        filename = os.path.join(output_folder, "{}_paths.csv".format(self.name))
        self.file = open(filename, 'w')
        if self.file:
            headers = (
                "interval,vehicle,origin,destination,type,path,probability,"
                "veh generated,veh arrived,cost,distance,travel time,speed\n"
            )
            self.file.write(headers)
            self.file.flush()
        else:
            print("Could not open file {}".format(filename))

    def doPath(self, pathKey, treeData, connections, aux):
        if not self.file:
            return

        origin_id = self.geo.getOriginCentroid(pathKey.mOriginIndex)
        dest_id = self.geo.getDestinationCentroid(pathKey.mDestinationIndex)
        typelist = ['None', 'RC', 'PAR', 'ODR', 'TRJ', 'P2P']
        path_type = typelist[treeData.pathType()]
        path = treeData.getPath(self.forest)
        section_ids = self.forest.getPathSections(
            self.geo.getSection(treeData.entrancePosition),
            path,
            pathKey.mVehicleIndex
        )
        section_str = '-'.join(map(str, section_ids))
        comp = treeData.getComponents()

        costs = self.geo.getPathCost(
            pathKey.mOriginIndex, pathKey.mDestinationIndex,
            connections, pathKey.mVehicleIndex, pathKey.mInterval
        )

        travel_time = comp[3] / comp[2] if comp[2] != 0 else 0.0
        speed = (costs.mDistance * 3.6 / travel_time) if travel_time != 0 else 0.0

        row = "{},{},{},{},{},{},{:.6f},{:.6f},{:.6f},{:.6f},{:.6f},{:.6f},{:.6f}\n".format(
            pathKey.mInterval,
            pathKey.mVehicleIndex,
            origin_id,
            dest_id,
            path_type,
            section_str,
            comp[1],
            comp[0],
            comp[2],
            costs.mCost,
            costs.mDistance,
            travel_time,
            speed
        )
        self.file.write(row)

        self.nbLines += 1
        if self.nbLines % 1000 == 0:
            self.file.flush()

    def finishPaths(self):
        if self.file:
            self.file.close()


def export_paths_for_replication(replication_id):
    replication = model.getCatalog().find(replication_id)
    if replication is None:
        print("No object found with ID {}".format(replication_id))
        return

    valid_types = {
        'GKReplication',
        'GKExperimentResult',
        'GKDynamicAdjustmentReplication',
        'GKDynamicAdjustmentExperimentResult'
    }

    type_name = replication.getTypeName()
    if type_name not in valid_types:
        print("Object {} is not a valid replication type ({})".format(replication_id, type_name))
        return

    path_assignment = replication.getOutputPathAssignment()
    if path_assignment is None:
        print("No path assignment found for replication {}".format(replication_id))
        return

    if not path_assignment.isRetrieved():
        path_assignment.retrieveForest()

    forest = path_assignment.getRetrievedForest()

    filter_ = AnalysisFilter()
    filter_.setIntervals(range(107))            # Adjust if needed
    filter_.setUserClass(0)                    # Default user class
    filter_.setOriginCentroids([])             # Add specific IDs if needed
    filter_.setDestinationCentroids([])

    rep_name = str(replication.getId())
    reader = PathReader(forest, model, rep_name)
    reader.init()
    reader.calculate(filter_)
    reader.finishPaths()

    print("Path data exported to Outputs/{}_paths.csv".format(rep_name))
    print("Script finished.")


# Run for a specific replication
export_paths_for_replication(34431441)
export_paths_for_replication(34431451)

export_paths_for_replication(34421286)
export_paths_for_replication(34421310)

export_paths_for_replication(34465073)
export_paths_for_replication(34465083)

