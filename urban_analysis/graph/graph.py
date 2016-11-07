from subprocess import call
import os
import matplotlib.pyplot as plt
import networkx as nx
import pandas as pd
import shapefile
import time
from extract_uses import mapzen
from extract_uses import shp_utils


def spatialite_network(city_country, folder = 'cities/'):
	""" Computes the spatialite network for the input city_country 
	"""
	if os.path.isfile(folder+city_country+"/roads.shp"):
		print('Road network exists')
		return

	# Download .osm.pbf given bounding box from Mapzen
	mapzen.getCityOsmPbf(folder,[city_country])
	pbf_file = folder+city_country+'.osm.pbf'

	# Call spatialite
	sqlite_file = folder+city_country+'.sqlite'
	if (not(os.path.isfile(sqlite_file))):
		start_time = time.time() # TIME
		call_spatialite = 'spatialite_osm_net -o '+pbf_file+' -d '+sqlite_file+' -T roads -m -tf ../graph/spatialite_configuration'
		if (call(call_spatialite.split(' ')) == 0):
			print("Spatialite OSM processed in: --- %s minutes ---" % ( (time.time() - start_time)/60.)  )
		else:
			print('Error calling spatialite: Maybe file already exists:',call_spatialite)
	else:
		print('File already exists:',sqlite_file)

	if (os.path.isfile(pbf_file)): os.remove(pbf_file)

	# Convert to shapefile
	print(folder+city_country,sqlite_file)
	call_ogr = ['ogr2ogr','-f',"ESRI Shapefile",folder+city_country,sqlite_file,'-dsco','SPATIALITE=yes']

	if (call(call_ogr) == 0):
		print('ogr2ogr: SQLite to Shapefile done')
	else:
		print('Error calling ogr2ogr:',call_ogr)
		print('Possible problem: SQLite format not supported in virtual environment. Check the allowed formats: ogr2ogr --formats')
		#http://gis.stackexchange.com/questions/67371/gdal-1-10-ogr2ogr-osm-unable-to-open-datasource

	# Remove the created temp file
	os.remove(sqlite_file)


def load_graph(city_country, folder = 'cities/'):
	""" Create the networkx graph given the routing network folder input
	Assumes that 'roads_nodes' and 'roads' files exist in the city_folder
	"""	
	nodes_f = folder + city_country + "/roads_nodes"
	roads_f = folder + city_country + "/roads"
	# Load shapefile
	nodes_shapes, nodes_attr = shp_utils.read_shp_dbf(nodes_f, decode_bytes = False) # Columns: Cardinality, [osm_id]. Name + 1 to set as Id
	roads_shapes, roads_attr = shp_utils.read_shp_dbf(roads_f, decode_bytes = False) # Columns: node_from, node_to, length, cost, oneway_fro, oneway_tof, [class, name, osm_id]

	# Initialize
	g = nx.Graph()
	# Add nodes, with latitude longitude
	for node_shape, node_attr in zip(nodes_shapes,nodes_attr.iterrows()):
		idx = node_attr[0] + 1 # Node from, and Node to stored in roads: Equals (Feature_id+1) in node
		g.add_node(idx, pos = tuple(node_shape.points[0]), cardinality = node_attr[1].cardinalit) # Longitude,Latitude format [long,lat]
	# Add edges: Cost is measured in seconds. Length in meters
	for road_shape, road_attr in zip(roads_shapes,roads_attr.iterrows()):
		attrs = road_attr[1]
		# Potentially: To attrs.cost, sum the overhead proportional to the cardinality of the origin node ('from')
		if (attrs.oneway_fro):
			g.add_edge(attrs.node_from, attrs.node_to, cost = attrs.cost, length = attrs.length, type = attrs['class'])
		if (attrs.oneway_tof):
			g.add_edge(attrs.node_to, attrs.node_from, cost = attrs.cost, length = attrs.length, type = attrs['class'])
	return g

def haversine(lon_lat1, lon_lat2):
    """
    Calculate the great circle distance between two points 
    on the earth (specified in decimal degrees)
    """
    from math import radians, cos, sin, asin, sqrt
    # convert decimal degrees to radians 
    lon1, lat1, lon2, lat2 = map(radians, [lon_lat1[0], lon_lat1[1], lon_lat2[0], lon_lat2[1]])
    # haversine formula 
    dlon = lon2 - lon1 
    dlat = lat2 - lat1 
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a)) 
    km = 6367 * c
    return km

def get_closest_node(nodeOfInterest, graph):
	closestNode = graph.nodes(data=True)[0] # Initial start
	distanceToNode = haversine(nodeOfInterest,closestNode[1]['pos'])
	for node in graph.nodes_iter(data=True):
	    #node[0] # Node id
	    #node[1]['pos'] # Node longitude, latitude
	    if (distanceToNode > haversine(nodeOfInterest,node[1]['pos']) ):
	    	distanceToNode = haversine(nodeOfInterest,node[1]['pos'])
	    	closestNode = node
	print("Distance to closest node in Km: ",distanceToNode)
	return closestNode
	