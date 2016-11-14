import shutil
import os
import parameters
import gc
import time
import os.path

import extract_point_uses
import extract_poly_uses
import infer_poly_uses
import poly_to_pts

import classif_uses

import cut_shapefile
import mapzen


def clipFiles(point_shapefile, polygon_shapefile):
	""" Clip input point and polygon shapefiles
	"""
	################################################################
	# Copy projection file for the extracted shapefiles
	if not os.path.exists(parameters.fn_prefix):
		os.makedirs(parameters.fn_prefix)
	shutil.copy(parameters.prj_shapefile, parameters.fn_prefix+'sample.prj')

	# Note that "_qnI" will be added to distinguish them
	cut_shapefile.clip_PolygonFile(polygon_shapefile,parameters.fn_subregions+parameters.fn_poly)
	gc.collect()

	cut_shapefile.clip_PointFile(point_shapefile,parameters.fn_subregions+parameters.fn_pts)
	gc.collect()	
	################################################################

def performExtraction(point_shapefile, polygon_shapefile):
	""" Given OSM extracted shapefiles osm2pgsql (point,polygon) -> Extract residential/activities points
	For each sub-shapefile: Extract point uses, polygon uses, infer polygon uses, convert all polygons to points
	"""	

	if (  (os.path.isfile(parameters.fn_joinResiActiv+'.shp')) or (os.path.isfile(parameters.fn_activities_final+".shp")) ): # If results exist, process?	
		if (not(parameters.processOverwrite)): # Avoid over-writing: Just perform the key category mapping
			# Map to final activity categories to corresponding file
			if (os.path.isfile(parameters.fn_joinResiActiv+'.shp')):
				classif_uses.performKeyCategoryMapping(parameters.fn_joinResiActiv, parameters.USE_multiActivitiesClassification)
			else:
				classif_uses.performKeyCategoryMapping(parameters.fn_activities_final, parameters.USE_multiActivitiesClassification)
			return # Exit

	# Clip files in parts (reduced memory needs if map is too big, faster polygon infer)
	clipFiles(point_shapefile, polygon_shapefile)
	
	for i in range(0,parameters.numCuts):
		if (parameters.USE_verbose):
			print("Processing cut number:",i)

		### Get name files
		in_shp_pts = parameters.fn_subregions+parameters.fn_pts + "_q"+str(i)
		in_shp_polys = parameters.fn_subregions+parameters.fn_poly + "_q"+str(i)
		in_shp_polys_sq = parameters.fn_subregions+parameters.fn_poly + "_sq" # Several quadrants polygons
		out_suffix = "_q"+str(i)

		### Process points
		extract_point_uses.main(in_shp_pts,out_suffix)
		gc.collect()

		### Process polygons
		extract_poly_uses.main(in_shp_polys,out_suffix)
		gc.collect()

		### Infer polygons
		infer_poly_uses.main(in_shp_polys,in_shp_polys_sq,out_suffix)
		gc.collect()

		### Convert polygons to points for further processing
		PolyToPoint_needed = extract_poly_uses.getNameSavedFiles(out_suffix) + infer_poly_uses.getNameSavedFiles(out_suffix)
		poly_to_pts.convert(PolyToPoint_needed)
		gc.collect()

	# Merge the different cuts into one file -> q0,q1,... to unique file
	cut_shapefile.mergeDifferentCuts(parameters.fn_prefix,parameters.numCuts,parameters.deleteParts)

	###
	
	### Merge the categories: Use only points
	if (parameters.USE_Merge_categories):
		cut_shapefile.mergeFinalCategories(parameters.fn_prefix,parameters.numCuts,parameters.deleteMergedParts)
	########
	if (parameters.USE_uniquePointsFile):
		# Merge final activities and residential shapefile into one
		removeSeparatedActivitiesResidential = True
		cut_shapefile.mergeFile(removeSeparatedActivitiesResidential, [parameters.fn_activities_final+".shp", parameters.fn_residential_final+".shp"], parameters.fn_joinResiActiv+".shp")

	###
	# Remove temp folder/files
	if (os.path.isdir(parameters.fn_subregions)):
		shutil.rmtree(parameters.fn_subregions)
	if (os.path.isfile(parameters.fn_prefix+'sample.prj') ):
		os.remove(parameters.fn_prefix+'sample.prj')

	###

	# Map to final activity categories
	classif_uses.performKeyCategoryMapping(parameters.fn_joinResiActiv, parameters.USE_multiActivitiesClassification)
	################################################################
	################################################################

################################################################	
def process(point_shapefile = None, polygon_shapefile = None):
	""" Process the point and polygon shapefile for the uses extraction from osm2pgsql file
	1) Clips the file for an easier processing (lower memory usage, more efficient code performance)
	2) Extract the point uses
	3) Extract polygon uses, and convert to points (centroid)
	4) Infer polygon uses (when there is not enough information), and convert to points (centroid)
	"""
	################################################################
	'''
	parameters.polygon_shapefile and parameters.point_shapefile must be set
	'''
	if (point_shapefile == None) :
		point_shapefile = parameters.point_shapefile
	if (polygon_shapefile == None) :
		polygon_shapefile = parameters.polygon_shapefile
	################################################################
	# Check if folder exists. In this case, assume it is already processed
	if (os.path.isdir(parameters.fn_prefix) and os.path.isfile(parameters.fn_joinResiActiv+'.shp')):
		if (not(parameters.processOverwrite)):
			print('POIs uses exist. Mapping categories and exiting.',parameters.fn_prefix)
		else:
			print('POIs uses exist. They will be over-written')
	################################################################
	if (parameters.USE_verbose or parameters.USE_mini_verbose):
		start_time = time.time()
	################################################################
	################################################################

	# Extract residential/activity uses.
	performExtraction(point_shapefile, polygon_shapefile)

	################################################################
	################################################################
	if (parameters.USE_verbose or parameters.USE_mini_verbose):
		print("Uses extraction time: --- %s minutes ---" % ( (time.time() - start_time)/60.)  )
	################################################################
################################################################

def process_city(city_ref):# city_ref must contain the format city_country
	# Create folder
	import os
	if (not (os.path.exists(parameters.citiesFolder))):
		os.makedirs(parameters.citiesFolder)
        
	if (parameters.USE_verbose or parameters.USE_mini_verbose):
		print('City:',city_ref)

	try :
		# Download shapefile associated to the city
		mapzen.getCityShapefile(parameters.citiesFolder, [city_ref])
	except (IOError) as e: # Not possible to download
		print('Error: Could not download shapefiles. Try downloading manually in https://mapzen.com/data/metro-extracts/')
		return
    
    
	# Set parameters
	parameters.setInputFiles(city_ref, popu_count_file = None, numberOfCuts = 16)
	# Process
	process()

	# Delete downloaded shapefiles
	mapzen.remove_mapzen_files(parameters.citiesFolder, city_ref)

