import parameters
import pandas as pd
import numpy as np
import os
import shapefile
import shutil
import shapely
from shapely.geometry import Point

import classif_uses

########################################################################
""" OSM default fields for points and polygons (osm2pgsql)
"""
Pointfields = [['osm_id', 'N', 19, 0], ['access', 'C', 11, 0], ['aerialway', 'C', 7, 0], ['aeroway', 'C', 7, 0], ['amenity', 'C', 18, 0], ['area', 'C', 2, 0], ['barrier', 'C', 24, 0], ['bicycle', 'C', 10, 0], ['brand', 'C', 17, 0], ['bridge', 'C', 32, 0], ['boundary', 'C', 32, 0], ['building', 'C', 11, 0], ['capital', 'C', 1, 0], ['covered', 'C', 3, 0], ['culvert', 'C', 32, 0], ['cutting', 'C', 32, 0], ['disused', 'C', 3, 0], ['ele', 'C', 8, 0], ['embankment', 'C', 32, 0], ['foot', 'C', 10, 0], ['harbour', 'C', 32, 0], ['highway', 'C', 26, 0], ['historic', 'C', 19, 0], ['horse', 'C', 3, 0], ['junction', 'C', 3, 0], ['landuse', 'C', 17, 0], ['layer', 'C', 10, 0], ['leisure', 'C', 16, 0], ['lock', 'C', 32, 0], ['man_made', 'C', 18, 0], ['military', 'C', 18, 0], ['motorcar', 'C', 7, 0], ['name', 'C', 99, 0], ['natural', 'C', 13, 0], ['oneway', 'C', 32, 0], ['operator', 'C', 47, 0], ['poi', 'C', 32, 0], ['population', 'C', 6, 0], ['power', 'C', 26, 0], ['place', 'C', 17, 0], ['railway', 'C', 14, 0], ['ref', 'C', 35, 0], ['religion', 'C', 9, 0], ['route', 'C', 32, 0], ['service', 'C', 13, 0], ['shop', 'C', 21, 0], ['sport', 'C', 21, 0], ['surface', 'C', 8, 0], ['toll', 'C', 32, 0], ['tourism', 'C', 11, 0], ['tower:type', 'C', 13, 0], ['tunnel', 'C', 32, 0], ['water', 'C', 32, 0], ['waterway', 'C', 9, 0], ['wetland', 'C', 32, 0], ['width', 'C', 32, 0], ['wood', 'C', 32, 0], ['z_order', 'N', 11, 0], ['tags', 'C', 254, 0]]
Polyfields = [['osm_id', 'N', 19, 0], ['access', 'C', 11, 0], ['aerialway', 'C', 7, 0], ['aeroway', 'C', 9, 0], ['amenity', 'C', 18, 0], ['area', 'C', 3, 0], ['barrier', 'C', 10, 0], ['bicycle', 'C', 10, 0], ['brand', 'C', 21, 0], ['bridge', 'C', 3, 0], ['boundary', 'C', 14, 0], ['building', 'C', 17, 0], ['covered', 'C', 3, 0], ['culvert', 'C', 32, 0], ['cutting', 'C', 32, 0], ['disused', 'C', 3, 0], ['embankment', 'C', 32, 0], ['foot', 'C', 10, 0], ['harbour', 'C', 32, 0], ['highway', 'C', 13, 0], ['historic', 'C', 14, 0], ['horse', 'C', 2, 0], ['junction', 'C', 32, 0], ['landuse', 'C', 23, 0], ['layer', 'C', 2, 0], ['leisure', 'C', 17, 0], ['lock', 'C', 32, 0], ['man_made', 'C', 17, 0], ['military', 'C', 8, 0], ['motorcar', 'C', 32, 0], ['name', 'C', 128, 0], ['natural', 'C', 9, 0], ['oneway', 'C', 32, 0], ['operator', 'C', 85, 0], ['population', 'C', 6, 0], ['power', 'C', 26, 0], ['place', 'C', 13, 0], ['railway', 'C', 8, 0], ['ref', 'C', 12, 0], ['religion', 'C', 10, 0], ['route', 'C', 32, 0], ['service', 'C', 36, 0], ['shop', 'C', 19, 0], ['sport', 'C', 83, 0], ['surface', 'C', 15, 0], ['toll', 'C', 32, 0], ['tourism', 'C', 12, 0], ['tower:type', 'C', 13, 0], ['tracktype', 'C', 32, 0], ['tunnel', 'C', 32, 0], ['water', 'C', 5, 0], ['waterway', 'C', 9, 0], ['wetland', 'C', 5, 0], ['width', 'C', 32, 0], ['wood', 'C', 10, 0], ['z_order', 'N', 11, 0], ['way_area', 'N', 32, 10], ['tags', 'C', 254, 0]]

""" Reduced fields: osm_id, value, key 
"""
reducedFields = [['osm_id', 'N', 19, 0], ['value', 'C', 32, 0], ['key', 'C', 32, 0] ]
def filterColumns(workingKey, sub_selection):
	""" Filter the columns and return the rows with the reduced fields format
	Use as input the working key, which determines the contained value
	"""
	filteredColumns_Selection = sub_selection[['osm_id',workingKey]]
	filteredColumns_Selection = filteredColumns_Selection.rename(columns={workingKey:'value'})
	filteredColumns_Selection['key'] = np.repeat(workingKey,len(filteredColumns_Selection))
	return filteredColumns_Selection

def performKeyCategoryMapping(fn_result):
	""" Given the file containing all point activities: Map {key,value} to the final key category classification
	"""
	### Read data-set
	shapes , df_attrs = read_shp_dbf(fn_result)
	# Perform the mapping to categories
	df_attrs = classif_uses.keyCategoryMapping(df_attrs, parameters.USE_multiActivitiesClassification)
	# Add the category field
	reducedFields_category = reducedFields + [['category','C',32,0]]
	# Save
	toFile(fn_result, shapes, df_attrs, shapefile.POINT, reducedFields_category)

########################################################################
### Compatibility with encoding/decoding
def UnicodeToStr(x, thresholdLength = None):
	""" To use only in Python2: encode the unicode input to utf-8, and strip if it is too long
	"""
	if (thresholdLength != None):
		if (thresholdLength < 25):
			print('Be careful, threshold length smaller than 25!')
			quit()
	if isinstance(x, unicode):
		# Decode to UTF8, then strip to remove white blank spaces at begining/end
		try:
			if (thresholdLength == None):
				return x.encode('UTF-8')
			else:
				return x[0:thresholdLength].encode('UTF-8')
		# If UnicodeDecodeError because of bytes length, shrink to avoid error
		except UnicodeDecodeError: # Recursive shrinking the length of the object
			if (thresholdLength == None):
				return UnicodeToStr(x, len(x)-1 )
			else:
				return UnicodeToStr(x, thresholdLength - 1 )
	else:
		return x

def ByteToStr(x, thresholdLength = None):
	""" To use only in Python2: decode the bytes to utf-8, and strip if it is too long
	"""
	if (thresholdLength != None):
		if (thresholdLength < 25):
			print('Be careful, threshold length smaller than 25!')
			quit()
	if isinstance(x, bytes):
		# Decode to UTF8, then strip to remove white blank spaces at begining/end
		try:
			if (thresholdLength == None):
				return x.decode('UTF-8').strip()
			else:
				return x[0:thresholdLength].decode('UTF-8').strip()
		# If UnicodeDecodeError because of bytes length, shrink to avoid error
		except UnicodeDecodeError: # Recursive shrinking the length of the object
			if (thresholdLength == None):
				return ByteToStr(x, len(x)-1 )
			else:
				return ByteToStr(x, thresholdLength - 1 )
	else:
		return x

########################################################################
### File I/O related to shapefile

def toFile(fileName, shapes, shape_attrs, shapefileType, fields = None):
	""" Store the shapes with its attributes to a .shp file
	shapefileType indicates whether points or polygons are going to be stored
	fields denote the columns which are going to be stored
	"""
	if (shape_attrs.empty):
		if (parameters.USE_verbose):
			print('Empty shape for file:',fileName)
		return

	# shapefileType : shapefile.POINT or shapefile.POLYGON
	w = shapefile.Writer(shapefileType)
	w.autoBalance = 1
	# Indicate the fields to be filled
	if (fields == None):
		if (shapefileType == shapefile.POINT):
			w.fields = Pointfields
		elif (shapefileType == shapefile.POLYGON):
			w.fields = Polyfields
		else:
			print('Error with field type')
			return
	else:
		w.fields = fields

	if (shapefileType == shapefile.POINT): # Input can be in form of shapely Point or shapefile Geometry
		# Check the nature of the input
		if (shapely.geometry.point.Point == type(shapes[0])):
			is_shapely_point = True
		else:
			is_shapely_point = False


	for index, row in shape_attrs.iterrows():
		RowLEncoded = map(UnicodeToStr,row.tolist())

		if (shapefileType == shapefile.POINT):
			if (is_shapely_point):
				Pt = [shapes[index].x,shapes[index].y]
			else:
				Pt = shapes[index].points[0]			
			w.point(Pt[0],Pt[1])
		else:
			Poly = shapes[index].points
			w.poly([Poly])
		w.record(*(RowLEncoded))

	w.save(fileName)
	import os.path
	if (not(os.path.isfile(fileName+'.prj'))):
		try:
			shutil.copy(parameters.fn_prefix+'sample.prj',fileName+'.prj')
		except ValueError, IOError:
			pass
#####################

################################################
### Read data-set

# Read dataset: Shapes and attributes
def read_shp_dbf(file_shape):
	""" Read a shapefile, returning separately shapes and attributes
	"""
	reader_shp = shapefile.Reader(file_shape)
	shapes = reader_shp.shapes()
	# Columns correspond to all the elements excepts for the first one: A deletion flag
	columns = [list[0] for list in reader_shp.fields[1:len(reader_shp.fields)]]
	# Conver to data frame and decode
	pd_dataframe = pd.DataFrame(reader_shp.records(), columns = columns).applymap(ByteToStr)
	return shapes, pd_dataframe
# Read dataset: Only shapes
def read_shp(file_shape):
	""" Read a shapefile, returning only the shapes
	"""
	reader_shp = shapefile.Reader(file_shape)
	shapes = reader_shp.shapes()
	return shapes
################################################

def download_unzip(citiesFolder, city_download):
	import urllib
	import zipfile
	import os
	# Get filename: temporary
	fname = citiesFolder+city_download+".zip"
	# Download zip file corresponding to city
	testfile = urllib.URLopener()
	testfile.retrieve(city_download, fname)
	# Unzip file
	zip_ref = zipfile.ZipFile(fname, 'r')
	zip_ref.extractall(citiesFolder)
	zip_ref.close()
	# Remove zip file
	os.remove(fname)
	print('Downloaded and unzipped:',city_download)
def getCityShapefile(citiesFolder, cities_countries):
	""" Download from Mapzen data metro-extracts the shapefile for the required city
	Download file and unzip into the required folder
	"""
	import os
	# Suffix and prefix for downloading a city from mapzen metro extracts
	Dl_prefix = 'https://s3.amazonaws.com/metro-extracts.mapzen.com/'
	Dl_suffix = '.osm2pgsql-shapefiles.zip'
	# Check if folder exists
	if (not(os.path.exists(citiesFolder))):
		# Create folder
		os.makedirs(citiesFolder)
	# For each city_country to download:
	for city_country in cities_countries:
		city_download = Dl_prefix + city_country + Dl_suffix
		if ( os.path.isfile(citiesFolder+city_country+"_osm_polygon.shp") ):
			print('Existing shapefile for',city_country)
		else:
			download_unzip(citiesFolder, city_download)


def getBoundingBox(point_shapefile, polygon_shapefile = None , line_shapefile = None):
	""" Compute bounding box for the input given files
	return: bbox -> latitude1 , longitude1 , latitude2, longitude2
	"""
	# Get the bounding box for the given shapefiles
	if ((point_shapefile is None) or (not(os.path.isfile(point_shapefile)))):
		#print('Warning: Null shapefile or file does not exist')
		return None

	bbox_pts = shapefile.Reader(point_shapefile).bbox
	if (polygon_shapefile != None):
		bbox_poly = shapefile.Reader(polygon_shapefile).bbox
	else:
		bbox_poly = bbox_pts
	if (line_shapefile != None):
		bbox_line = shapefile.Reader(line_shapefile).bbox
	else:
		bbox_line = bbox_pts
    
	# Format: latitude1 , longitude1 , latitude2, longitude2
	bbox = [ min(bbox_poly[1],bbox_pts[1],bbox_line[1]) , min(bbox_poly[0],bbox_pts[0],bbox_line[0]) , max(bbox_poly[3],bbox_pts[3],bbox_line[3]), max(bbox_poly[2],bbox_pts[2],bbox_line[2]) ]

	if (parameters.USE_verbose):
		print('Bounding box:',bbox)
	return bbox

################################################
