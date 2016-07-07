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
import population
import mapzen

def delete_downloaded_shapefile(folder, city_ref):
	import os
	if (folder[-1] != "/"): folder = folder + "/"
	files = os.listdir(folder)
	for f in files:
		if ((city_ref in f) and (os.path.isfile(folder+f))):
			os.remove(folder+f)

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

def performExtraction(point_shapefile, polygon_shapefile, population_count_file = None):
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
	### Process: Perform population down-scaling and distribute to each residential point
	population.population_downscaling(population_count_file, parameters.fn_residential_final)
	gc.collect()
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
def process(point_shapefile = None, polygon_shapefile = None, population_count_file = None):
	""" Process the point and polygon shapefile for the uses extraction from osm2pgsql file
	1) Clips the file for an easier processing (lower memory usage, more efficient code performance)
	2) Extract the point uses
	3) Extract polygon uses, and convert to points (centroid)
	4) Infer polygon uses (when there is not enough information), and convert to points (centroid)
	5) Perform a population downscaling for residential points
	"""
	################################################################
	'''
	parameters.polygon_shapefile and parameters.point_shapefile must be set
	If parameters.population_count_file is set, perform the population downscaling
	'''
	if (point_shapefile == None) :
		point_shapefile = parameters.point_shapefile
	if (polygon_shapefile == None) :
		polygon_shapefile = parameters.polygon_shapefile
	if (population_count_file == None):
		population_count_file = parameters.population_count_file
	################################################################
	# Check if folder exists. In this case, assume it is already processed
	if (os.path.isdir(parameters.fn_prefix) and os.path.isfile(parameters.fn_joinResiActiv+'.shp')):
		if (not(parameters.processOverwrite)):
			print('Folder already exists. Assumption: Already processed. Only mapping categories and exiting.',parameters.fn_prefix)
		else:
			print('Folder already exists. Processing and over-writing')
	################################################################
	if (parameters.USE_verbose):
		start_time = time.time()
	################################################################
	################################################################

	# Extract residential/activity uses. Alternatively, estimate the population count for residential points
	performExtraction(point_shapefile, polygon_shapefile, population_count_file)

	################################################################
	################################################################
	if (parameters.USE_verbose):
		print("Complete processing: --- %s minutes ---" % ( (time.time() - start_time)/60.)  )
	################################################################
################################################################

def process_city(city_ref):# city_ref must contain the format city_country
	# Create folder
	import os
	if (not (os.path.exists(parameters.citiesFolder))):
		os.makedirs(parameters.citiesFolder)

	# Download shapefile associated to the city
	mapzen.getCityShapefile(parameters.citiesFolder, [city_ref])

	# Set parameters
	parameters.setInputFiles(city_ref, popu_count_file = None, numberOfCuts = 16)
	# Process
	process()

	# Delete downloaded shapefiles
	delete_downloaded_shapefile(parameters.citiesFolder, city_ref)


'''
class ExtractUses(object):
	""" Encapsulates data/methods related to the uses extraction of a city
	"""

	def __init__(self, city_ref, population_count = None):
		# basic info
		self.city_ref = city_ref
		self.bbox = None#bbox Get bounding box method
		self._pois = None
		#self._pois_shp_path = pois_shp_path

	# When asking for pois, if pois is None, compute_pois and return


	def compute_pois():
		fullUsesPath = "cities/"+city_ref+"/full_uses.shp"
		# If exists, already done...
		if (os.path.isfile(fullUsesPath)):
			print('City already processed. Loading pois')
			#Load pois and return

		else:
			print('Pois do not exist. Computing...')
			# Download shapefile associated to the city
			utils.getCityShapefile(citiesFolder, cities_countries)

			# TODO: Check how to encapsulate parameters. Population count file?
			parameters.setInputFiles(citiesFolder, city_country, popu_count_file, numberOfCuts)
			
			# PROCESS
			process()

			# TODO: Delete downloaded file
'''
