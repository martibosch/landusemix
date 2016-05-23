from osgeo import gdal
from gdalconst import * 
import numpy as np
import math
import pandas as pd
from shapely.geometry import Point
import shapely.geometry.geo as geo
import shapefile
import time

import parameters
import utils


############################################################################
############################################################################
############################################################################
from osgeo import gdal
from osgeo import osr
# The following method translates given latitude/longitude pairs into pixel locations on a given GEOTIF
# INPUTS: geotifAddr - The file location of the GEOTIF
#      latLonPairs - The decimal lat/lon pairings to be translated in the form [[lat1,lon1],[lat2,lon2]]
# OUTPUT: The pixel translation of the lat/lon pairings in the form [[x1,y1],[x2,y2]]
# NOTE:   This method does not take into account pixel size and assumes a high enough 
#	  image resolution for pixel size to be insignificant
def latLonToPixel(geotifAddr, latLonPairs):
	# Load the image dataset
	ds = gdal.Open(geotifAddr)
	# Get a geo-transform of the dataset
	gt = ds.GetGeoTransform()
	# Create a spatial reference object for the dataset
	srs = osr.SpatialReference()
	srs.ImportFromWkt(ds.GetProjection())
	# Set up the coordinate transformation object
	srsLatLong = srs.CloneGeogCS()
	ct = osr.CoordinateTransformation(srsLatLong,srs)
	# Go through all the point pairs and translate them to latitude/longitude pairings
	pixelPairs = []
	for point in latLonPairs:
		# Change the point locations into the GeoTransform space
		(point[1],point[0],holder) = ct.TransformPoint(point[1],point[0])
		# Translate the x and y coordinates into pixel values
		x = (point[1]-gt[0])/gt[1]
		y = (point[0]-gt[3])/gt[5]
		# Add the point to our return array
		pixelPairs.append([int(x),int(y)])
	return pixelPairs
# The following method translates given pixel locations into latitude/longitude locations on a given GEOTIF
# INPUTS: geotifAddr - The file location of the GEOTIF
#      pixelPairs - The pixel pairings to be translated in the form [[x1,y1],[x2,y2]]
# OUTPUT: The lat/lon translation of the pixel pairings in the form [[lat1,lon1],[lat2,lon2]]
# NOTE:   This method does not take into account pixel size and assumes a high enough 
#	  image resolution for pixel size to be insignificant
def pixelToLatLon(geotifAddr,pixelPairs):
	# Load the image dataset
	ds = gdal.Open(geotifAddr)
	# Get a geo-transform of the dataset
	gt = ds.GetGeoTransform()
	# Create a spatial reference object for the dataset
	srs = osr.SpatialReference()
	srs.ImportFromWkt(ds.GetProjection())
	# Set up the coordinate transformation object
	srsLatLong = srs.CloneGeogCS()
	ct = osr.CoordinateTransformation(srs,srsLatLong)
	# Go through all the point pairs and translate them to pixel pairings
	latLonPairs = []
	for point in pixelPairs:
		# Translate the pixel pairs into untranslated points
		ulon = point[0]*gt[1]+gt[0]
		ulat = point[1]*gt[5]+gt[3]
		# Transform the points to the space
		(lon,lat,holder) = ct.TransformPoint(ulon,ulat)
		# Add the point to our return array
		latLonPairs.append([lat,lon])

	return latLonPairs
############################################################################

def pixel2coord(GeoTransform, x, y):
    """ Returns global coordinates from pixel x, y coords
    """
    xoff, a, b, yoff, d, e = GeoTransform
    xp = a * x + b * y + xoff
    yp = d * x + e * y + yoff
    return(xp, yp)

def coord2pixel(GeoTransform, lon, lat):
	""" Uses a gdal geomatrix (gdal.GetGeoTransform()) to calculate	the pixel location of a geospatial coordinate
	Input: GeoTransformation, longitude, latitude
	"""
	xoff, a, b, yoff, d, e = GeoTransform
	ulX, ulY = xoff, yoff
	xDist, yDist = a, e
	rtnX, rtnY = b, d
	pixel = ((lat - ulX) / xDist)
	line = ((ulY - lon) / xDist)
	return (pixel, line)

############################################################################
def getSubArray(dataset, x1, y1, x2, y2):
	""" Returns the matrix containing the region of interest (given coordinates) of input data-set
	"""
	data = dataset.ReadAsArray().astype(np.float)
	# Extract selected rows
	Rows = [ data[row] for row in range(y1,y2+1)]
	# Extracted, from the selected rows, the selected columns
	ColsOfRows = [ row[x1:x2+1] for row in Rows]
	return np.matrix(ColsOfRows)

def getContaining_LatitudeLongitude(GeoTransform, x0, y0):
	""" Computes the latitude/longitude bounding box for the given pixel and geo-transform
	Returns latitude1,longitude1,latitude2,longitude2
	"""
	# Top left and bottom right in terms of world coordinates (latitude,longitude)
	topLeft = pixel2coord(GeoTransform, x0, y0)
	bottomRight = pixel2coord(GeoTransform, x0+1, y0+1)
	# World coordinates in y-axis go the other sense, i.e. it gets lower when it gets down:
	# lat1, long1, lat2, long2
	return topLeft[0] , bottomRight[1] , bottomRight[0], topLeft[1]


############################################################################

def getROI(GeoTransform, point_shapefile, polygon_shapefile = None, line_shapefile = None):
	""" Get the region of interest (pixels) using the Geotransform, given the input shapefile. 
	"""
	# Get Region of interest (x,y coordinates) given the Geotransformation, and the shapefile which contain the points
	##########################
	# bbox Format: latitude1 , longitude1 , latitude2, longitude2
	bbox = utils.getBoundingBox(point_shapefile, polygon_shapefile, line_shapefile)

	# Get the pixel values (floating precision) of the extremes given longitude/latitude
	Pix1 = coord2pixel(GeoTransform, bbox[0] , bbox[1])
	Pix2 = coord2pixel(GeoTransform, bbox[2] , bbox[3])

	### Get min and max values, since ReadAsAray will interprete as an image: (0,0) at top left
	x1 = int( math.floor( min( Pix1[0] , Pix2[0] ) ) )# Round DOWN the minimum value pixel X
	x2 = int( math.ceil( max( Pix1[0] , Pix2[0] ) ) )# Round UP the maximum value pixel X
	y1 = int( math.floor( min( Pix1[1] , Pix2[1] ) ) )# Round DOWN the minimum value pixel Y
	y2 = int( math.ceil( max( Pix1[1] , Pix2[1] ) ) )# Round UP the maximum value pixel Y
	return x1, y1, x2, y2
############################################################################




def population_downscaling(population_count_file, residential_point_shapefile):
	"""
	Given the population count grid and the residential points, estimate/distribute the population count for each residential point
	"""
	####################################################################################
	if (parameters.USE_verbose):
		print('Population down-scaling')
	####################################################################################
	# Open tif file
	dataset = gdal.Open(population_count_file, GA_ReadOnly)
	# GDAL affine transform parameters, According to gdal documentation xoff/yoff are image left corner, a/e are pixel width/height and b/d is rotation and is zero if image is north up. 
	GeoTransform = dataset.GetGeoTransform()

	# Get the desired region of interest
	x1, y1, x2, y2 = getROI(GeoTransform, residential_point_shapefile)

	# Get the ROI of the population count matrix
	population_np = getSubArray(dataset, x1,y1,x2,y2)

	# Read shapefile and attributes
	shape_residential_pts, df_residential_pts = utils.read_shp_dbf(residential_point_shapefile)
	# Replace with population format: Key=residential, value=population count
	df_residential_pts['value'] = 0
	df_residential_pts['key'] = "residential"
	# Create the points structure
	s_residential_pts = pd.Series( [Point(shape.points[0]) for shape in shape_residential_pts] )
	##########################

	if (parameters.USE_verbose):
		start_time = time.time()

	# For the given raster, assign to the corresponding residential points its population count
	for row in range(0,population_np.shape[0]):
		for col in range(0,population_np.shape[1]):
			# Population count
			pop_count = population_np[row,col]

			# Get real coordinates respect to file 
			#x, y = int(cols[0])+x1 , int(rows[0])+y1
			x, y = int(col+x1) , int(row+y1)
			
			# Get the latitude,longitude bounding box to identify points contained within the box
			lat1,long1,lat2,long2 = getContaining_LatitudeLongitude(GeoTransform, x, y)
			# Create a geometry box for the containing coordinates
			Bbox = geo.box(lat1,long1,lat2,long2)

			# For all residential points, pick those which are contained in the bounding box
			within_residential_pts = s_residential_pts[ s_residential_pts.apply(lambda s: Bbox.contains(s)) ]

			# Assign pop_count distributed in an homogeneous way across the residential points
			homogeneousPopCountDistribution = pop_count / len(within_residential_pts)

			# Set the value
			df_residential_pts.loc[ within_residential_pts.index ,'value'] = homogeneousPopCountDistribution

	if (parameters.USE_verbose):
		print("--- %s seconds ---" % (time.time() - start_time))

	# Save file
	utils.toFile(parameters.fn_prefix+parameters.fn_final_clasif+parameters.fn_residential, shape_residential_pts, df_residential_pts, shapefile.POINT, utils.reducedFields)
	####################################################################################
