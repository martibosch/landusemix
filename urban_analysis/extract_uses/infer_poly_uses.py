import pandas as pd
import numpy as np
from shapely.geometry import Polygon
import shapefile

import parameters
import classif_uses
import utils
import time


def getNameSavedFiles(suffix_out_shp):
	""" Get the list of all generated files
	"""
	f1 = parameters.fn_prefix+parameters.fn_uncertain+parameters.fn_inferred+parameters.fn_poly+suffix_out_shp
	f2 = parameters.fn_prefix+parameters.fn_activities+parameters.fn_inferred+parameters.fn_poly+suffix_out_shp
	f3 = parameters.fn_prefix+parameters.fn_residential+parameters.fn_inferred+parameters.fn_poly+suffix_out_shp
	return [f1,f2,f3]

def firstMatchingContainedPolygon(df_Polygons_LU_Region, infer_poly):
	""" Useful functions: Get the first polygon which contains the smallest polygon to test/infer
	"""
	return next( (x for x in df_Polygons_LU_Region.iterrows() if x[1]['Polygon'].contains(infer_poly)), None)
def MatchingContainedPoly_List(df_Polygons_LU_Region, polys_to_infer):
	""" For each polygon to infer, get the first (smallest) matching contained polygon
	"""
	return [ firstMatchingContainedPolygon(df_Polygons_LU_Region, i) for i in polys_to_infer ]

def perform(df_Polygons_LU_Region, chunks_toPolygons_ToInfer_poly):
	""" Send to process in parallel the calculation of the containing polygons
	"""
	# Initialize parallel 
	from multiprocessing import Pool
	from functools import partial
	import multiprocessing

	pool = multiprocessing.Pool(processes=parameters.num_processes)
	func = partial(MatchingContainedPoly_List, df_Polygons_LU_Region)
	result = pool.map(func, chunks_toPolygons_ToInfer_poly)
	pool.close()
	pool.join()
	return result


def getPolygons_LU_Region(df_polygon, polygon_shapes, df_polygon_sq, polygon_shapes_sq):
	"""Get all polygons which contain a Landuse region, classified accordingly to {Activity,Residential,Other}
	Convert to Polygon object [Polygon, Index, Classification]
	"""
	toPolygons_nonResiAct_LU_region = [ ( Polygon(polygon_shapes[i].points) , "other" ) for i in df_polygon.loc[ ( df_polygon['landuse'].isin(classif_uses.landuse_notResidentialActivity) ) & (df_polygon['building'].isin(['']) )].index  ]
	toPolygons_activities_LU_region = [ ( Polygon(polygon_shapes[i].points) , df_polygon.loc[i,'landuse'] ) for i in df_polygon.loc[ ( df_polygon['landuse'].isin(classif_uses.landuse_activities) ) & (df_polygon['building'].isin(['']) )].index  ]
	toPolygons_residential_LU_region = [ ( Polygon(polygon_shapes[i].points) , "residential" ) for i in df_polygon.loc[ ( df_polygon['landuse'].isin(classif_uses.landuse_residential) ) & (df_polygon['building'].isin(['']) )].index  ]
	
	sq_toPolygons_nonResiAct_LU_region = [ ( Polygon(polygon_shapes_sq[i].points) , "other" ) for i in df_polygon_sq.loc[ ( df_polygon_sq['landuse'].isin(classif_uses.landuse_notResidentialActivity) ) & (df_polygon_sq['building'].isin(['']) )].index ]
	sq_toPolygons_residential_LU_region = [ ( Polygon(polygon_shapes_sq[i].points) , "residential" ) for i in df_polygon_sq.loc[ ( df_polygon_sq['landuse'].isin(classif_uses.landuse_residential) ) & (df_polygon_sq['building'].isin(['']) )].index ]

	sq_toPolygons_activities_LU_region = [ ( Polygon(polygon_shapes_sq[i].points) , df_polygon_sq.loc[i,'landuse'] ) for i in df_polygon_sq.loc[ ( df_polygon_sq['landuse'].isin(classif_uses.landuse_activities) ) & (df_polygon_sq['building'].isin(['']) )].index ]
	#sq_toPolygons_activities_LU_region = [ ( Polygon(polygon_shapes_sq[i].points) , "activity" ) for i in df_polygon_sq.loc[ ( df_polygon_sq['landuse'].isin(classif_uses.landuse_activities) ) & (df_polygon_sq['building'].isin(['']) )].index ]

	several_quadrants_LU_region = sq_toPolygons_nonResiAct_LU_region + sq_toPolygons_activities_LU_region + sq_toPolygons_residential_LU_region

	################
	# Concatenate lists
	np_Polygons_LU_Region = toPolygons_nonResiAct_LU_region + toPolygons_activities_LU_region + toPolygons_residential_LU_region + several_quadrants_LU_region
	return np_Polygons_LU_Region


def calculateContainingPolygons(df_Polygons_LU_Region, toPolygons_ToInfer_poly):
	""" For each polygon which needs to be inferred, calculate the first containing polygon (smallest) with a defined landuse
	Eventually, a parallelized version is given: It creates different chunks and sends to process
	"""
	# Parallelize?
	if (not(parameters.USE_parallel)):
		if (parameters.USE_verbose):
			print('Not using parallelization')

		full_containingPolygons = [ firstMatchingContainedPolygon(df_Polygons_LU_Region, i) for i in toPolygons_ToInfer_poly ]
	else:
		'''
		TODO: Shared memory
		#ArrShared_df_Polygons_LU_Region = Array(df_Polygons_LU_Region, lock=False)
		'''
		# Divide the data to process in chunks
		chunks_toPolygons_ToInfer_poly = np.asarray( [toPolygons_ToInfer_poly[x:x+parameters.sizeChunk] for x in xrange(0, len(toPolygons_ToInfer_poly), parameters.sizeChunk)] )

		if (parameters.USE_verbose):
			start_time = time.time()
		
		# Perform in parallel the smallest polygon which contains the polygons to be inferred
		containingPolygons = perform(df_Polygons_LU_Region, chunks_toPolygons_ToInfer_poly)

		if (parameters.USE_verbose):
			print("--- %s seconds ---" % (time.time() - start_time))

		full_containingPolygons = [item for sublist in containingPolygons for item in sublist]
	return full_containingPolygons

def inferUseGivenContainingPolygons(ToInfer_poly, full_containingPolygons):
	""" Given the smallest containing polygon for those which need to be inferred: Set the category
	Categories: Residential, Activity, Uncertain
	"""
	inferred_poly_residential = []
	inferred_poly_activity = []
	inferred_poly_uncertain = []

	### For each polygon to infer: Get the smallest containing polygon, and pick its landuse
	for idx, containingPoly in zip(ToInfer_poly.index, full_containingPolygons):
		if (containingPoly != None):
			# New classification: Residential/Other/{Related to activity}
			if (containingPoly[1]['Classification'] == 'residential'):
				inferred_poly_residential.append(idx)
			elif (containingPoly[1]['Classification'] != 'other'): # Any activity tag
				inferred_poly_activity.append([idx, containingPoly[1]['Classification'] ])
		else:
			# If none, it remains uncertain
			inferred_poly_uncertain.append(idx)

	return inferred_poly_activity , inferred_poly_residential , inferred_poly_uncertain
	
def polygonsToInfer(df_polygon):
	""" Given all polygons, select those which need to be inferred
	Get the polygons which need to be inferred: building=yes, afterwards Null values
	Filter points which have building=yes	
	"""
	columns_polygons = [list[0] for list in utils.Polyfields]
	if (parameters.USE_ignoreRowsWithTaggingInformation):
		selectedCols = [col for col in columns_polygons if col not in ['osm_id', 'way_area', 'z_order', 'building', 'name', 'tags']]
	else:
		selectedCols = [col for col in columns_polygons if col not in ['osm_id', 'way_area', 'z_order', 'building', 'name']]
	# Blank spaces
	emptyRow = np.repeat('',len(selectedCols))
	################
	# Get the polygons which need to be inferred: building=yes, afterwards Null values
	ToInfer_poly = df_polygon.ix[(df_polygon['building']=='yes') & (df_polygon[selectedCols] == emptyRow).all(axis=1)]
	return ToInfer_poly
	################

def reprojectSinusoidal( points ):
	""" Perform the reprojection from latitude,longitude point to sinusoidal projection	
	Input: Array of points [ p1, p2, p3 ] in latitude,longitude
	Returns the x & y coordinates in meters using a sinusoidal projection
	More info: http://stackoverflow.com/questions/4681737/how-to-calculate-the-area-of-a-polygon-on-the-earths-surface-using-python
	"""
	from math import pi, cos, radians
	earth_radius = 6371009 # in meters
	lat_dist = pi * earth_radius / 180.0

	Pts = []
	for p in points: # (latitude,longitude) pairs
		latitude = p[0]
		longitude = p[1]
		Pts.append( [ longitude * lat_dist * cos(radians(latitude)) , latitude * lat_dist ] )
	return Pts

def filterSmallBuildings(polygons_idx, polygon_shapes, squaredMeterThreshold):
	""" Filter polygons which compute an area smaller than the threshold
	Use the sinusoidal projection to calculate the area
	"""
	filteredPolys_idx = [ poly for poly in polygons_idx if Polygon( reprojectSinusoidal ( polygon_shapes[poly].points ) ).area >= squaredMeterThreshold ]
	if (parameters.USE_verbose):
		print('Small buildings filtered:',len(polygons_idx) - len(filteredPolys_idx))
	return filteredPolys_idx

def filterInferredColumns(sub_selection):
	""" Filter the inferred columns in the reduced format
	[osm_id, key:inferred, value:""]
	"""
	filteredColumns_Selection = sub_selection[['osm_id']].copy()
	filteredColumns_Selection['value'] = np.repeat('',len(filteredColumns_Selection))
	filteredColumns_Selection['key'] = np.repeat('inferred',len(filteredColumns_Selection))
	return filteredColumns_Selection

def filterInferredActivityColumns(df_polygon, inferred_poly_activity):
	""" Filter the inferred activity columns in the reduced format
	df_polygon: dataframe attributes of the polygons
	inferred_poly_activity: array of [index, activityFromContainingPolygon]
	return: [osm_id, key:inferred, value:correspondingActivity]
	"""
	# Get the array for the indices and the activity value
	inferred_poly_act_indices = [ i[0] for i in inferred_poly_activity]
	inferred_poly_act_values = np.asarray( [ i[1] for i in inferred_poly_activity] )

	filteredColumns_Selection = df_polygon.iloc[inferred_poly_act_indices][['osm_id']]
	filteredColumns_Selection['value'] = inferred_poly_act_values
	filteredColumns_Selection['key'] = np.repeat('inferred',len(filteredColumns_Selection))
	return filteredColumns_Selection

##############################
################################################################################################

def main(polygon_shapefile, poly_shp_several_quadrants, suffix_out_shp):
	"""Given the polygon shapefile, it infers the residential/activity category they belong to
	If not enough information exists: Check the landuse non-null of the polygon where it is contained that is smallest in size
		-> Infer it accordingly
	Uses the reduced fields: osm_id, key, value
	"""
	if (not (parameters.USE_infer_polyBuildings) ):
		print('Not inferring polygons')
		return

	################################################
	### Read data-set
	# Polygon shapefile
	polygon_shapes , df_polygon = utils.read_shp_dbf(polygon_shapefile)
	### Polygons appearing in several quadrants
	polygon_shapes_sq , df_polygon_sq = utils.read_shp_dbf(poly_shp_several_quadrants)
	################################################

	# Get the polygons which need to be inferred: building=yes, afterwards Null values
	ToInfer_poly = polygonsToInfer(df_polygon)

	################

	# Concatenate lists and sort by its size
	np_Polygons_LU_Region = getPolygons_LU_Region(df_polygon, polygon_shapes, df_polygon_sq, polygon_shapes_sq)
	
	def getKey(item):
		return item[0].area
	np_Polygons_LU_Region = sorted(np_Polygons_LU_Region, key=getKey)
	# Convert to DataFrame to iterate rows
	df_Polygons_LU_Region = pd.DataFrame(np_Polygons_LU_Region, columns=['Polygon', 'Classification'])

	################
	
	if (parameters.USE_verbose):
		print("infer_poly_uses. Polygons with Landuse Region:", len(df_Polygons_LU_Region), "Polygons to infer", len(ToInfer_poly))

	################ 

	# Calculate for each polygon to infer, the smallest containing polygon which has a defined landuse
	toPolygons_ToInfer_poly = [ Polygon(polygon_shapes[i].points) for i in ToInfer_poly.index ]
	full_containingPolygons = calculateContainingPolygons(df_Polygons_LU_Region, toPolygons_ToInfer_poly)

	# Get the inferred uses
	inferred_poly_activity, inferred_poly_residential , inferred_poly_uncertain = inferUseGivenContainingPolygons(ToInfer_poly, full_containingPolygons)

	# Filter buildings small enough?
	if (parameters.USE_filterSmallResidentialBuildings):
		# Filter residential and uncertain polygons smaller than X m2
		inferred_poly_residential = filterSmallBuildings(inferred_poly_residential, polygon_shapes, parameters.squaredMeterThreshold)
		inferred_poly_uncertain = filterSmallBuildings(inferred_poly_uncertain, polygon_shapes, parameters.squaredMeterThreshold)
	if (parameters.USE_filterSmallActivitiesBuildings):
		# Filter activities polygons smaller than X m2
		inferred_poly_activity = filterSmallBuildings(inferred_poly_activity, polygon_shapes, parameters.squaredMeterThreshold)

	################################################################
	if (parameters.USE_verbose):
		print('Inferred Activities polygons',len(inferred_poly_activity))
		print('Inferred Residential polygons',len(inferred_poly_residential))
		print('Inferred Uncertain polygons',len(inferred_poly_uncertain))

	#########################
	
	# Filter the important columns for uncertain/residential purposes: [osm_id, key="inferred", value=""]
	fc_inferred_poly_uncertain = filterInferredColumns(df_polygon.iloc[inferred_poly_uncertain])
	fc_inferred_poly_residential = filterInferredColumns(df_polygon.iloc[inferred_poly_residential])
	# Filter the important columns for activity purposes: [osm_id, key="inferred", value=Activity from the containing polygon]
	fc_inferred_poly_activity = filterInferredActivityColumns(df_polygon, inferred_poly_activity)


	### Write to file
	utils.toFile(parameters.fn_prefix+parameters.fn_uncertain+parameters.fn_inferred+parameters.fn_poly+suffix_out_shp, polygon_shapes, fc_inferred_poly_uncertain, shapefile.POLYGON, utils.reducedFields )
	utils.toFile(parameters.fn_prefix+parameters.fn_activities+parameters.fn_inferred+parameters.fn_poly+suffix_out_shp, polygon_shapes, fc_inferred_poly_activity, shapefile.POLYGON, utils.reducedFields )
	utils.toFile(parameters.fn_prefix+parameters.fn_residential+parameters.fn_inferred+parameters.fn_poly+suffix_out_shp, polygon_shapes, fc_inferred_poly_residential, shapefile.POLYGON, utils.reducedFields )

	########################################################################################################################
