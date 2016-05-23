import parameters
from subprocess import call
import shapefile
import utils
import os
import glob

from shapely.geometry import Polygon
import shapely.geometry


#########################################################################################################
'''
- Cut an input shapefile into various files
- Merge several shapefiles into one file
Meant to be used when the shapefile is too big, and hence help to process it in parts

Points: Distributed
Polygons: Each poly distributed to one unique file. As well, an additional file containing all polygons which relie in more than one "cut" box is provided
'''
#########################################################################################################

def removeFiles(i):
	""" Receive .shp file, and remove all files related to it
	"""
	if (os.path.isfile(i) ):
		os.remove(i)
	if (os.path.isfile(i.replace(".shp",".shx")) ):
		os.remove(i.replace(".shp",".shx"))
	if (os.path.isfile(i.replace(".shp",".dbf")) ):
		os.remove(i.replace(".shp",".dbf"))
	if (os.path.isfile(i.replace(".shp",".prj")) ):
		os.remove(i.replace(".shp",".prj"))
	if (os.path.isfile(i.replace(".shp",".cpj")) ):
		os.remove(i.replace(".shp",".cpj"))
	if (os.path.isfile(i.replace(".shp",".cpg")) ):
		os.remove(i.replace(".shp",".cpg"))

def callOgr(arguments):
	""" Perform a call to ogr2ogr tool. Use the received arguments
	"""
	if ( not ( call(arguments) == 0) ):
		print('Problem calling ogr2ogr')

###

def mergeFile(removeParts, to_merge_in_shp, out_shp_merged):
	""" Merge all files into an output shapefile. 
	Alternatively, remove the different parts
	"""
	if (parameters.USE_verbose):
		print("Merge file",to_merge_in_shp)

	callOgr(['ogr2ogr',"-f","ESRI Shapefile",out_shp_merged,to_merge_in_shp[0],"-lco","ENCODING=UTF-8","-overwrite"])
	for i in range(1,len(to_merge_in_shp)):
		callOgr(['ogr2ogr','-update','-append',out_shp_merged,to_merge_in_shp[i],"-lco","ENCODING=UTF-8"])
	
	# Remove part-files ?
	if (removeParts):
		# For each file
		for i in to_merge_in_shp:
			removeFiles(i)

def mergeFinalCategories(folder,numCuts,removeParts):
	""" Merge the different categories into one final "full" part
	"""
	if (parameters.USE_verbose):
		print('Merge folder',folder)

	# Remove slash
	dirF = folder
	if ( folder[len(folder)-1] == "/"):
		dirF = folder[:-1]

	# Merge by activities and residential categories. Keep only points ?
	# Assumes files with points are named "pts" and has the respective category name
	toMergeActivities = []
	toMergeResidential = []
	for file in os.listdir(dirF):
		# Only points
		if (parameters.fn_pts in file):
			if (("activities" in file) and (file.endswith(".shp")) and (parameters.fn_final_clasif not in file)):
				toMergeActivities.append(folder+file)
			if (parameters.USE_Assume_Residential_under_uncertainty):
				if (("uncertain" in file) and (file.endswith(".shp")) and (parameters.fn_final_clasif not in file)):
					toMergeResidential.append(folder+file)
			if (("residential" in file) and (file.endswith(".shp")) and (parameters.fn_final_clasif not in file)):
				toMergeResidential.append(folder+file)

	mergeFile(removeParts, toMergeActivities, parameters.fn_activities_final+".shp")
	mergeFile(removeParts, toMergeResidential, parameters.fn_residential_final+".shp")

def mergeDifferentCuts(folder,numCuts,removeParts):
	""" Merge the different cuts represented by q0,q1, ... into one file
	For the input files, it is assumed that the different cuts start with q0
	Alternatively, remove the different cuts
	"""
	dirF = folder
	if ( folder[len(folder)-1] == "/"): # If the folder finishes with a slash, remove it
		dirF = folder[:-1]

	for file in os.listdir(dirF): # For all files within the folder to process
		if file.endswith("q0.shp"):
			toMerge = [ folder+file.replace("q0","q"+str(i)) for i in range(0,numCuts) ]
			mergeFile(removeParts, toMerge, folder+file.replace("q0",""))

#########################################################################################################
##########################################################################################

def getTouchingQuadrants(PolygonQuadrants, Polygon):
	""" Get the different zones where a polygon touches/is contained
	"""
	intersectsQuadrants = [ i for i,quad in zip(range(0,len(PolygonQuadrants)),PolygonQuadrants) if quad.intersects(Polygon) ]
	return intersectsQuadrants
'''
# First quadrant which matches
def getFirstQuadrant(PolygonQuadrants, Polygon):
	for i in PolygonQuadrants:
		if (i.intersects(Polygon)):
			return [i]
'''

def getCoordsArrQuadrants(bbox, numCuts):
	import math
	# Compute the grid size (j which computes j*j=numCuts)
	gridSize = math.sqrt(numCuts)

	if (not(gridSize.is_integer())):
		print('Number of cuts should be compatible with format [j*j] with j integer; Possibilities: 1,2,4,9,16,25,...')
		quit()

	x1,y1,x2,y2 = bbox

	# Generate an Xs and Ys array containing the delimitation values
	Xs = [x1]
	Ys = [y1]
	for i in range(1,int(gridSize)): # First element already added
		Xi = x1 + i*(x2-x1)/gridSize
		Yi = y1 + i*(y2-y1)/gridSize
		Xs.append(Xi)
		Ys.append(Yi)
	Xs.append(x2)
	Ys.append(y2)
	return Xs,Ys

def getPolygonQuadrants(bbox, numCuts):
	""" Compute the bounding box coordinates of the different cuts
	Returns a polygon shape
	"""
	Xs,Ys = getCoordsArrQuadrants(bbox,numCuts)

	PolygonQuadrants = []
	# Generate the polygon quadrants
	for y_i in range(0,len(Ys) -1 ): # For all Y's values except the last one
		for x_i in range(0,len(Xs) -1 ): # For all X's values except the last one
			# Create the box containing X'i,Y'i and X'i+1,Y'i+1
			box = shapely.geometry.box(Xs[x_i],Ys[y_i],Xs[x_i+1],Ys[y_i+1])
			PolygonQuadrants.append(box)
	return PolygonQuadrants

def getBboxArr_Quadrants(bbox, numCuts):
	""" Compute the bounding box coordinates of the different cuts
	Returns a bounding box array
	"""
	Xs,Ys = getCoordsArrQuadrants(bbox,numCuts)
	Xs = [ str(x) for x in Xs ]
	Ys = [ str(y) for y in Ys ]

	BboxArr_Quadrants = []
	# Generate the polygon quadrants
	for y_i in range(0,len(Ys) -1 ): # For all Y's values except the last one
		for x_i in range(0,len(Xs) -1 ): # For all X's values except the last one
			# Create the box containing X'i,Y'i and X'i+1,Y'i+1
			boxArr = [ Xs[x_i],Ys[y_i],Xs[x_i+1],Ys[y_i+1] ]
			BboxArr_Quadrants.append(boxArr)
	return BboxArr_Quadrants

####################################

def clip_PointFile(in_shp, out_shp):
	""" Clip a given point file to divide it in several files (easier to process)
	Divide in four quadrants, using the centre of the bounding box
	"""
	# Clip an input point shapefile in different cuts
	if (parameters.USE_verbose):
		print("Clip point file")

	# Create a reader instance for our shapefile
	r = shapefile.Reader(in_shp)

	# Output files
	f1 = [out_shp+"_q"+str(i)+".shp" for i in range(0,parameters.numCuts)]

	####################################################################
	PolygonQuadrants = getBboxArr_Quadrants(r.bbox,parameters.numCuts)
	
	for f,quad in zip(f1,PolygonQuadrants): # Output shapefile, bounding box quadrant
		callOgr(["ogr2ogr","-overwrite","-f","ESRI Shapefile",f,in_shp,"-clipsrc",quad[0],quad[1],quad[2],quad[3]])

####################################

def clip_PolygonFile(in_shp, out_shp):
	""" Clip a given polygon file to divide it in several files (easier to process)
	Divide in four quadrants, using the centre of the bounding box
	An additional several quadrants file is created, for those polygons which are contained/touch more than one quadrant
	"""
	# Clip an input polygon shapefile in different cuts
	if (parameters.USE_verbose):
		print("Clip polygon file")

	# Create a reader instance for our shapefile
	r = shapefile.Reader(in_shp)

	# Create a writer instance copying the reader's shapefile type. 
	# Respectively, considering all quadrants and only first appearing quadrant
	w_several_quadrants = shapefile.Writer(r.shapeType)
	w_fq = [shapefile.Writer(r.shapeType) for i in range(0,parameters.numCuts)]

	# Copy the database fields to the writer
	w_several_quadrants.fields = r.fields
	for i in w_fq:
		i.fields = r.fields

	####################################################################
	PolygonQuadrants = getPolygonQuadrants(r.bbox,parameters.numCuts)

	# Iterate through the shapes and attributes at the same time
	for poly in r.iterShapeRecords():
	    # Shape geometry
	    geom = poly.shape
	    # Database attributes 
	    rec = poly.record
	    
	    # Get the quadrants which intersect the polygon
	    quadrant = getTouchingQuadrants(PolygonQuadrants, Polygon(geom.points))

	    # If polygon lies within several quadrants, add it as a special polygon:
	    if (len(quadrant) > 1):
	    	w_several_quadrants._shapes.append(geom)
	    	w_several_quadrants.records.append(rec)

	    # For each polygon, add it to one quadrant. It will be further processed to be inferred
	    w_fq[quadrant[0]]._shapes.append(geom)
	    w_fq[quadrant[0]].records.append(rec)
	    
	# Save the new shapefile! (.shp, .shx, .dbf) with its respective quadrant
	for i in range(0,parameters.numCuts):
		w_fq[i].save(out_shp+"_q"+str(i))
	# Save polygons which lie within at least two quadrants
	w_several_quadrants.save(out_shp+"_sq")
