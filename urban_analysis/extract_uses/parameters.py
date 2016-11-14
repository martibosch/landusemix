####################################################################################
""" Parameters
This file contains several parameters used for all the scripts
"""
####################################################################################
# Fully verbose
USE_verbose = True
# Minimal verbose
USE_mini_verbose = True

# Default values
city_name = ""
point_shapefile = ''
polygon_shapefile = ''
prj_shapefile = ''

####################################################################################
############# Name of files
### Folders:
# Prefix for outputting results (if any)
fn_prefix = city_name+'/'
# If dividing in sub-regions for easier processing, temporary folder:
fn_subregions = 'quadrants/'
fn_final_clasif = "full_"

### Intermmediate:
# Classification
fn_residential = "residential"
fn_activities = "activities"
fn_uncertain = "uncertain"

# For infer_poly_uses
fn_inferred = "_inferred"

### Type of object:
fn_pts_from_poly = "_pts_from_poly"
fn_poly = "_poly"
fn_pts = "_pts"

fn_residential_final = fn_prefix+fn_final_clasif+fn_residential
fn_activities_final = fn_prefix+fn_final_clasif+fn_activities
# Final file containing both activities and residential points
fn_joinResiActiv = fn_prefix+fn_final_clasif+"uses"

citiesFolder = 'cities/'

# Set input files
def setInputFiles(city_country, popu_count_file = None, numberOfCuts = 4):
	global fn_prefix, city_name, fn_residential_final, fn_activities_final, point_shapefile, polygon_shapefile, prj_shapefile, numCuts, fn_final_clasif, fn_residential, fn_activities, fn_joinResiActiv
	import os
	if ((popu_count_file != None) and (not(os.path.isfile(popu_count_file)))):
		popu_count_file = None

	city_name = city_country
	fn_prefix = citiesFolder+city_country+'/'
	fn_residential_final = fn_prefix+fn_final_clasif+fn_residential
	fn_activities_final = fn_prefix+fn_final_clasif+fn_activities
	fn_joinResiActiv = fn_prefix+fn_final_clasif+"uses"
	point_shapefile = citiesFolder+city_country+'_osm_point.shp'
	polygon_shapefile = citiesFolder+city_country+'_osm_polygon.shp'
	prj_shapefile = citiesFolder+city_country+'_osm_point.prj'
	numCuts = numberOfCuts
####################################################################################
####################################################################################
####################################################################################
####################################################################################
####################################################################################

'''
Inferring
'''
# building=yes and no other tag compute as Residential
USE_infer_polyBuildings = True
# If False: When performing assumption on buildings, ignore items which contain tag Non-Null, or { !='' }
USE_ignoreRowsWithTaggingInformation = True
# Those inferred polygons which remain uncertain: Classify as residential?
USE_Assume_Residential_under_uncertainty = True
# Remove duplicates which are in more than one category (e.g. a shop and an amenity using the same osm_id)
# Note: Sometimes a point represents more than one valid category: e.g. A big shop containing amenities inside
USE_dropDuplicates = False
# Merge files representing the different categories into one
USE_Merge_categories = True

##########
# Filter buildings smaller than X squared meters
USE_filterSmallResidentialBuildings = True
USE_filterSmallActivitiesBuildings = False
squaredMeterThreshold = 12
### Parallelization during polygon classification infer
USE_parallel = True
num_processes = 8
sizeChunk = 100
##########################################

# If the cities' folder to process already exists, over-write and process anyway? If false, skip...
processOverwrite = False
# When merging files, delete the different cut parts? -> q0,q1,q2,q3 ...
deleteParts = True
# When converting polygons to points, delete polygon file?
deletePolyToPts = True
# When merging to final classification, delete the files?
deleteMergedParts = True
# Conserve in separated files activities/residential points, or use unique points shapefile?
USE_uniquePointsFile = True
# Since using quadrants, it is cut in 4 different files. Possibilities = [1,2,4,9,16,25,...]
numCuts = 4

###
# When defining mapping the categories, use multi activities classification (e.g. shop, comercial/industrial, leisure/amenity) ? Otherwise: 'activity'
USE_multiActivitiesClassification = False
####################################################################################