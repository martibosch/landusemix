import numpy as np  # 1.7 or higher
import pandas as pd # 0.10 or higher
from matplotlib.pyplot import *
from shapely.geometry import Polygon
from shapely.geometry import Point
import shapefile
import os.path

import cut_shapefile
import parameters
import utils


def getNameSavedFiles(PolyToPoint_needed):
	""" Get the list of all generated files
	"""
	f = []
	for i in PolyToPoint_needed:
		# If exists file: Conversion exists
		if ( os.path.isfile( i +".shp") ):
			f.append ( i.replace(parameters.fn_poly, parameters.fn_pts_from_poly) )
	return f

####################################################################################
### Those polygons which contain building=yes and were inferred as a certain activity/residential use
### Convert to points according to their centroid
def convertPolysToPoints(in_shp_poly_file, out_shp_pts_file):
	""" Convert polygon input file to point format
	"""
	if (not ( os.path.isfile(in_shp_poly_file+".shp") )):
		if (parameters.USE_verbose):
			print("Empty file:",in_shp_poly_file)
		return

	####################################################################################
	### Read data-set
	# Point shapefile
	polygon_shapes , df_polygon = utils.read_shp_dbf(in_shp_poly_file)
	####################################################################################

	Points_atr = [ i[1] for i in df_polygon.iterrows() ]
	Points_xy = [ Point(Polygon(shp.points).centroid) for shp in polygon_shapes ]

	if (parameters.USE_verbose):
		print('poly_to_pts. Dataset; Number of points',out_shp_pts_file,len(Points_atr))

	utils.toFile(out_shp_pts_file, Points_xy, df_polygon, shapefile.POINT, utils.reducedFields)

	if (parameters.deletePolyToPts):
		cut_shapefile.removeFiles(in_shp_poly_file+".shp")

####################################################################################

def convert(PolyToPoint_needed):
	""" Convert from polygons to points (computing centroid) for all input files
	"""
	# For each file which needs to be converted to points: Process
	for i in PolyToPoint_needed:
		convertPolysToPoints(i, i.replace(parameters.fn_poly, parameters.fn_pts_from_poly))
	####################################################################################