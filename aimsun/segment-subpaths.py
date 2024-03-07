'''
This scripts splits subpaths into segments of a defined length (note that the length of the segments may not match the input length exactly due to the individual length of sections)
An external id list is used to define which subpaths get segmented
The script also exports a list of connecting turns between segments and a list of segment lengths

02/03/2024
Caleb Deverell
caleb@mobilitylab.co.nz
'''

import os
import csv

# use the external id to define which subpaths get segmented

subpath_eid_lst = ['example_eid_1','example_eid_2']

# segment approximate length
segLength = 500


# get the subpath type
subpathType = model.getType("GKSubPath")

def createSubpath(segID, section_list, subpathName, externalID):

	# create the subpath name and external id
	segName = subpathName + '_seg' + str(segID)
	segEID = externalID + "_segments"

	

	# check if the segment already exists
	segPath = model.getCatalog().findByName(segName, subpathType)
	if segPath:
		# clear the existing sections
		segPath.clear()
		# add the new sections in 
		for section in section_list:
			segPath.add(section)

		tempLength = segPath.length3D()

		print(segName + ' has been updated')

	else:
		segPath = GKSystem.getSystem().newObject("GKSubPath", model)
		segPath.setName(segName)
		for section in section_list:
			segPath.add(section)

		segPath.setExternalId(segEID)
		# Get the root folder
		rootFolder = model.getCreateRootFolder()

		# Internal name of the Subpaths folder
		subPathsFolderName = "GKModel::subPaths"

		# Try to find the Subpaths folder
		subPathsFolder = rootFolder.findFolder(subPathsFolderName)
		subPathsFolder.append(segPath)

		

		print(segName + ' has been created')

	tempLength = segPath.length3D()

	segmentLengths.append([segPath.getId(), segName, tempLength])

# list to store turns between subpath segments
connectingTurns = []

# list to store segment subpath lengths
segmentLengths = []

for subpath in model.getCatalog().getObjectsByType( subpathType ).values():
	subpathName = subpath.getName()
	# get the external id and check if in selected list
	externalID = subpath.getExternalId()
	if externalID in subpath_eid_lst:
		# get the sections in the subpath
		sections = subpath.getRoute()
		sectionNum = len(sections)
		segID = 0
		pathLength = 0
		section_list = []
		end_section = None
		for section in sections:
			if pathLength == 0 and end_section:
				# get the destination node of the previous end section
				destNode = end_section.getDestination()
				turn = destNode.getTurning(end_section, section)
				connectingTurns.append([subpathName + '_seg' + str(segID-1), turn.getId(), turn.length3D()])
			# get the length of the section
			secLength = section.length3D()
			pathLength += secLength
			#print(pathLength, secLength)
			section_list.append(section)
			if pathLength >= segLength:
				# create the new subpath
				createSubpath(segID, section_list, subpathName, externalID)
				# update parameters
				segID += 1
				pathLength = 0
				section_list = []
				end_section = section
			elif sections.index(section) == sectionNum - 1:
				# create the new subpath
				createSubpath(segID, section_list, subpathName, externalID)
				# update parameters
				segID += 1
				pathLength = 0
				section_list = []


# export the list of connecting turns
file_path = os.path.join(os.path.dirname(str(model.getDocumentFileName())), 'segment_connecting_turns.csv')


with open(file_path, 'w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    # Write each list (row) to the CSV
    for row in connectingTurns:
        writer.writerow([s if isinstance(s, str) else str(s) for s in row])

# export the list of segment lengths
file_path = os.path.join(os.path.dirname(str(model.getDocumentFileName())), 'segment_lengths.csv')


with open(file_path, 'w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    # Write each list (row) to the CSV
    for row in segmentLengths:
        writer.writerow([s if isinstance(s, str) else str(s) for s in row])


print("Finished Creating Subpath Segments")