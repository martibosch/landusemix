import pandas as pd
import numpy as np
import shapefile


################################################
#import utils
##############
def ByteToStr(x):
	""" To use only in Python2: decode the bytes to utf-8, and strip if it is too long
	"""
	if isinstance(x, bytes):
		# Decode to UTF8, then strip to remove white blank spaces at begining/end
		try:
			return x.decode('UTF-8').strip()
		# If UnicodeDecodeError because of bytes length, shrink to avoid error
		except UnicodeDecodeError:
			return x[0:200].decode('UTF-8').strip()
	else:
		return x

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

def getBoundingBox(point_shapefile, polygon_shapefile = None , line_shapefile = None):
	""" Compute bounding box for the input given files
	"""
	# Get the bounding box for the given shapefiles
	bbox_pts = shapefile.Reader(point_shapefile).bbox
	if (polygon_shapefile != None):
		bbox_poly = shapefile.Reader(polygon_shapefile).bbox
	else:
		bbox_poly = bbox_pts
	if (line_shapefile != None):
		bbox_line = shapefile.Reader(line_shapefile).bbox
	else:
		bbox_line = bbox_pts

	# Get the bounding box for all shapefile: Min of xmin,ymin and Max of xmax,ymax
	#bbox = [ min(bbox_poly[0],bbox_pts[0],bbox_line[0]) , min(bbox_poly[1],bbox_pts[1],bbox_line[1]) , max(bbox_poly[2],bbox_pts[2],bbox_line[2]) , max(bbox_poly[3],bbox_pts[3],bbox_line[3]) ]
	# lat or lonigutde first?
	bbox = [ min(bbox_poly[1],bbox_pts[1],bbox_line[1]) , min(bbox_poly[0],bbox_pts[0],bbox_line[0]) , max(bbox_poly[3],bbox_pts[3],bbox_line[3]), max(bbox_poly[2],bbox_pts[2],bbox_line[2]) ]
	return bbox
################################################

def load_extracted_osm_pois(shp):
	""" Load into a data frame the extracted points of interest (activities/residential)
	"""
	# Load residential/activities points
	shapes,pd_df = read_shp_dbf(shp)

	# Get longitude and latitude
	lon = [ i.points[0][0] for i in shapes]
	lat = [ i.points[0][1] for i in shapes]
	
	if ('population' in pd_df.columns): # Check if population exists
		# Convert to pandas DF {value,lon,lat,key,population} with indices=osm_id
		loader_df = pd.DataFrame({'key':pd_df.key.values , 'lat':lat , 'lon':lon , 'value':pd_df.value.values, 'population':pd_df.population.values}, index=pd_df.osm_id.rename("id"))
	else: 
		# Convert to pandas DF {value,lon,lat,key} with indices=osm_id
		loader_df = pd.DataFrame({'key':pd_df.key.values , 'lat':lat , 'lon':lon , 'value':pd_df.value.values}, index=pd_df.osm_id.rename("id"))	
	return loader_df


graph_sqlite = "grenoble.sqlite"
def load_extracted_graph(graph_sqlite):
	''' Load the graph outputted by spatialite tool
	:param graph_sqlite: Name of the sqlite file containing the graph
	PROBLEM: Interprete geometry in binary format
	'''
	print('Hola')

	import sqlite3
	conn = sqlite3.connect(graph_sqlite)

	# Roads
	c = conn.cursor()
	sq_roads = c.execute('SELECT * FROM roads')
	roads_columns = [ i[0] for i in sq_roads.description]
	roads = pd.DataFrame(sq_roads.fetchall(),columns=roads_columns)

	# Nodes
	c = conn.cursor()
	sq_roads_nodes = c.execute('SELECT * FROM roads_nodes')
	roads_nodes_columns = [ i[0] for i in sq_roads_nodes.description]
	roads_nodes = pd.DataFrame(sq_roads_nodes.fetchall(),columns=roads_nodes_columns)


	"""
	from sqlalchemy import create_engine
	engine = create_engine('sqlite:///'+graph_sqlite)

	pd.read_sql_table("roads", conn)
	#pd.read_sql_table("roads", engine)
	"""

	#nodes_df, edges_df = [], []#...
	#return GeoGraph(nodes_df, edges_df)
