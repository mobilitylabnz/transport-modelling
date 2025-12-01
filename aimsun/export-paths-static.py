import os

class PathReader(ForestCalculator):
    def __init__(self, forest, model, name):
        super(PathReader, self).__init__(forest, model, ForestCalculator.eOnlyAvailablePaths)
        self.forest = forest
        self.model = model
        self.name = name
        self.geo = forest.getGeometry()
        self.nbLines = 1
        self.file = None

    def init(self):
        output_folder = os.path.join(os.path.dirname(str(self.model.getDocumentFileName())), 'Outputs')
        try:
            os.mkdir(output_folder)
        except OSError:
            # This will also catch other errors, so optionally check if folder already exists
            if not os.path.exists(output_folder):
                raise
            print "Outputs folder already exists."

        filename = os.path.join(output_folder, "{}_paths.csv".format(self.name))
        self.file = open(filename, 'w')
        if self.file:
            headers = (
                "origin, destination,vehicle,path,"
                "veh generated\n"
            )
            self.file.write(headers)
            self.file.flush()
        else:
            print "Could not open file {}".format(filename)

    def doPath(self, pathKey, treeData, connections, aux):
        if not self.file:
            return
        origin_id = self.geo.getOriginCentroid(pathKey.mOriginIndex)
        dest_id = self.geo.getDestinationCentroid(pathKey.mDestinationIndex)



        
        # typelist = ['None', 'RC', 'PAR', 'ODR', 'TRJ', 'P2P']

        # path_type = typelist[treeData.pathType()]
        path = treeData.getPath(self.forest)
        section_ids = self.forest.getPathSections(
            self.geo.getSection(treeData.entrancePosition),
            path,
            pathKey.mVehicleIndex
        )
        section_str = '-'.join(map(str, section_ids))

        comp = treeData.getComponents()
        veh_generated = comp[0]


        self.file.write("{},{},{},{},{}\n".format(
            origin_id, dest_id, pathKey.mVehicleIndex, section_str, veh_generated
        ))

        # row = "{},{},{},{},{},{},{:.6f},{:.6f},{:.6f},{:.6f},{:.6f},{:.6f},{:.6f}\n".format(
        #     pathKey.mInterval,
        #     pathKey.mVehicleIndex,
        #     origin_id,
        #     dest_id,
        #     path_type,
        #     section_str
        # )
        # self.file.write(row)

        # self.nbLines += 1
        # if self.nbLines % 1000 == 0:
        #     self.file.flush()

    def finishPaths(self):
        if self.file:
            self.file.close()


def export_paths_for_experiment(experiment_id):
    experiment = model.getCatalog().find(experiment_id)
    if experiment is None:
        print "No object found with ID {}".format(experiment_id)
        return

    valid_types = {
        'MacroExperiment'
    }

    type_name = experiment.getTypeName()
    if type_name not in valid_types:
        print "Object {} is not a valid experiment type ({})".format(experiment_id, type_name)
        return

    GKSystem.getSystem().executeAction("retrieve_paths", experiment, [], "")

    forest = experiment.getForest()

    filter_ = AnalysisFilter()
    filter_.setIntervals([0])  # Adjust if needed
    filter_.setUserClass(0)          # Default user class
    filter_.setOriginCentroids([])   # Add specific IDs if needed
    filter_.setDestinationCentroids([])

    rep_name = str(experiment.getId())
    reader = PathReader(forest, model, rep_name)
    reader.init()
    reader.calculate(filter_)
    # reader.finishPaths()

    print "Path data exported to Outputs/{}_paths.csv".format(rep_name)
    print "Script finished."

export_paths_for_experiment(34360093)