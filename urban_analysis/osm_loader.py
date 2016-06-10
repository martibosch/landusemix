"""
BASED ON https://github.com/UDST/pandana/blob/master/pandana/loaders/osm.py

Tools for creating graphs from Open Street Map.
"""
from __future__ import division
from itertools import islice, izip
import math

import pandas as pd
import requests

import osm_pois
import osm_roads

uninteresting_tags = {
    'source',
    'source_ref',
    'source:ref',
    'history',
    'attribution',
    'created_by',
    'tiger:tlid',
    'tiger:upload_uuid',
}

# UTILS


def _pitagoras_aprox_dist(lat1, lon1, lat2, lon2):
    return ((lat1 - lat2)**2 + (lon1 - lon2)**2)**.5


def _great_circle_dist(lat1, lon1, lat2, lon2):
    """ Get the distance (in meters) between two lat/lon points via the Haversine formula.

    :param lat1: float in degrees
    :param lon1: float in degrees
    :param lat2: float in degrees
    :param lon2: float in degrees
    :returns: distance in meters
    :rtype: float

    """
    radius = 6372795  # meters

    lat1 = math.radians(lat1)
    lon1 = math.radians(lon1)
    lat2 = math.radians(lat2)
    lon2 = math.radians(lon2)

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    # formula from:
    # http://en.wikipedia.org/wiki/Haversine_formula#The_haversine_formula
    a = math.pow(math.sin(dlat / 2), 2)
    b = math.cos(lat1) * math.cos(lat2) * math.pow(math.sin(dlon / 2), 2)
    d = 2 * radius * math.asin(math.sqrt(a + b))

    return d


# QUERY REQUEST

def _generate_osm_tag(key, values):
    """ Generates the query tag allowing all the values in 'values' for the key 'key'

    :param key: str with the key name
    :param values: list with the acceptable values
    :returns: with the generated tag
    :rtype: str
    """
    return '"' + key + '"~"' + '|'.join(values) + '"'


def _build_query(bbox, query_type, tags=None):
    """ Build the string for a node-based OSM query.

    :param bbox: list of float of the form [lat_min, lon_min, lat_max, lon_max]
    :param query_type: 'node' or 'way'
    :param tags: list or str with a tag request according to the Overpass QL (see http://wiki.openstreetmap.org/wiki/Overpass_API/Language_Guide)
    :returns: query
    :rtype: str

    """
    if tags is not None:
        if isinstance(tags, str):
            tags = [tags]
        tags = ''.join('[{}]'.format(t) for t in tags)
    else:
        tags = ''

    query_fmt = (
        '[out:json];'
        '('
        '  {query_type}'
        '  {tags}'
        '  ({lat_min},{lon_min},{lat_max},{lon_max});'
        '  >;'  # the '>' makes it recurse so we get ways and way nodes
        ');'
        'out;')

    return query_fmt.format(
        query_type=query_type,
        tags=tags,
        lat_min=bbox[0], lon_min=bbox[1], lat_max=bbox[2], lon_max=bbox[3],
    )


def _make_osm_query(query):
    """ Make a request to OSM and return the parsed JSON.

    :param query: str in the Overpass QL format
    :returns: data of the query response
    :rtype: dict

    """
    osm_url = 'http://www.overpass-api.de/api/interpreter'
    req = requests.get(osm_url, params={'data': query})
    req.raise_for_status()

    return req.json()


# QUERY RESPONSE
# ROAD GRAPH
def _process_node(e):
    """ Process a node element entry into a dict suitable for going into a Pandas DataFrame.

    :param e: dict
    :returns: node
    :rtype: dict

    """
    node = {
        'id': e['id'],
        'lat': e['lat'],
        'lon': e['lon']
    }

    if 'tags' in e:
        for t, v in e['tags'].items():
            if t not in uninteresting_tags:
                node[t] = v

    return node


def _process_way(e):
    """ Process a way element entry into a list of dicts suitable for going into a Pandas DataFrame.

    :param e: dict
    :returns: way, list waynodes : dict
    :rtype: tuple

    """
    way = {
        'id': e['id']
    }

    if 'tags' in e:
        for t, v in e['tags'].items():
            if t not in uninteresting_tags:
                way[t] = v

    waynodes = []

    for n in e['nodes']:
        waynodes.append({'way_id': e['id'], 'node_id': n})

    return way, waynodes


def _parse_graph_osm_query(data):
    """ Convert OSM query data to DataFrames of ways and way-nodes.

    :param data: dict response of an OSM query
    :returns: nodes, ways, waynodes : pandas.DataFrame
    :rtype: tuple

    """
    if len(data['elements']) == 0:
        raise RuntimeError('OSM query results contain no data.')

    nodes = []
    ways = []
    waynodes = []

    for e in data['elements']:
        if e['type'] == 'node':
            nodes.append(_process_node(e))
        elif e['type'] == 'way':
            w, wn = _process_way(e)
            ways.append(w)
            waynodes.extend(wn)

    return (
        pd.DataFrame.from_records(nodes, index='id'),
        pd.DataFrame.from_records(ways, index='id'),
        pd.DataFrame.from_records(waynodes, index='way_id'))


# DATA PROCESSING
# ROAD GRAPH
def _intersection_nodes(waynodes):
    """ Get a set of all the nodes that appear in 2 or more ways.

    :param waynodes: pandas.DataFrame mapping of way IDs to node IDs as returned by `ways_in_bbox`
    :returns: intersections; node IDs that appear in 2 or more ways
    :rtype: set

    """
    counts = waynodes.node_id.value_counts()
    return set(counts[counts > 1].index.values)


def _node_pairs(nodes, ways, waynodes, two_way=True, distance_type='pitagoras', weight_distance=True):
    """ Create a table of node pairs with the distances between them.

    :param nodes: pandas.DataFrame with 'lat' and 'lon' columns
    :param ways: pandas.DataFrame of way metadata
    :param waynodes: pandas.DataFrame linking way IDs to node IDs. Way IDs should be in the index, with a column called 'node_ids'.
    :param two_way: bool, whether the routes are two-way. If True, node pairs will only occur once. 
    :param distance_type: str 'pitagoras' or 'haversine'
    :param weight_distance: 
    :returns: pairs; with columns of 'from_id', 'to_id', and 'distance'. The index will be a MultiIndex of (from id, to id). The distance metric is in meters.
    :rtype: pandas.DataFrame

    """
    def pairwise(l):
        return izip(islice(l, 0, len(l)), islice(l, 1, None))
    intersections = _intersection_nodes(waynodes)
    waymap = waynodes.groupby(level=0, sort=False)
    pairs = []

    for id, row in ways.iterrows():
        nodes_in_way = waymap.get_group(id).node_id.values
        nodes_in_way = filter(lambda x: x in intersections, nodes_in_way)

        # row.highway contains the highway type which connects the potential
        # nodes (from_node, to_node)
        highway_weight = osm_roads.get_highway_weight(row.highway)

        if len(nodes_in_way) < 2:
            # no nodes to connect in this way
            continue

        for from_node, to_node in pairwise(nodes_in_way):
            fn = nodes.loc[from_node]
            tn = nodes.loc[to_node]

            if distance_type == 'pitagoras':
                distance = _pitagoras_aprox_dist(
                    fn.lat, fn.lon, tn.lat, tn.lon)
            else:
                distance = _great_circle_dist(fn.lat, fn.lon, tn.lat, tn.lon)
            if weight_distance:
                distance = distance * highway_weight

            pairs.append({
                'from_id': from_node,
                'to_id': to_node,
                'distance': distance
                #'cost': distance_weighted
            })

            if not two_way:
                pairs.append({
                    'from_id': to_node,
                    'to_id': from_node,
                    'distance': distance
                    #'cost': distance_weighted
                })

    pairs = pd.DataFrame.from_records(pairs)
    pairs.index = pd.MultiIndex.from_arrays(
        [pairs['from_id'].values, pairs['to_id'].values])

    return pairs


# POIS NODES

def _nodes_from_bbox(bbox, tags=None):
    """ Queries for OSM nodes within a bounding box that match given tags.
    :param bbox: list of float of the form [lat_min, lon_min, lat_max, lon_max]
    :param tags: list or str with a tag request according to the Overpass QL (see http://wiki.openstreetmap.org/wiki/Overpass_API/Language_Guide)
    :returns: nodes : pandas.DataFrame
    :rtype: tuple

    """
    node_data = _make_osm_query(_build_query(bbox, 'node', tags=tags))

    if len(node_data['elements']) == 0:
        raise RuntimeError('OSM query results contain no data.')

    nodes = [_process_node(n) for n in node_data['elements']]
    return pd.DataFrame.from_records(nodes, index='id')


def _process_pois_df_columns(df, key, columns):
    """ Formats the dataframe with the columns ['key','value','lon','lat']

    :param df: pandas.DataFrame
    :param key: str
    :param columns: list
    :returns: df with the corresponding format
    :rtype: pandas.DataFrame

    """
    df = df[columns].rename(columns={columns[0]: 'value'})
    df['value'] = df['value'].astype(str)
    df['key'] = key
    df['category'] = 'activities'
    return df


# ROAD GRAPH
def graph_from_bbox(bbox, tags=None, two_way=True):
    """ Get road nodes and edges from a bounding lat/lon box.
    :param bbox: list of float of the form [lat_min, lon_min, lat_max, lon_max]
    :param tags: list or str with a tag request according to the Overpass QL (see http://wiki.openstreetmap.org/wiki/Overpass_API/Language_Guide)
    :param two_way: bool whether the routes are two-way. If True, node pairs will only occur once.
    :returns: nodes_df, edges_df : pandas.DataFrame
    :rtype: dict
    """
    if not tags:
        tags = _generate_osm_tag(osm_roads.key, osm_roads.values)

    nodes, ways, waynodes = _parse_graph_osm_query(_make_osm_query(
        _build_query(bbox, 'way', tags=tags)))  # ways_in_bbox(bbox, tags)
    pairs = _node_pairs(nodes, ways, waynodes, two_way=two_way)

    # make the unique set of nodes that ended up in pairs
    node_ids = sorted(
        set(pairs['from_id'].unique()).union(set(pairs['to_id'].unique())))
    nodes = nodes.loc[node_ids]

    return {'nodes': pd.DataFrame({'lon': nodes['lon'], 'lat': nodes['lat']}),
            'edges': pd.DataFrame({'from': pairs['from_id'], 'to': pairs['to_id']}).join(pairs[['distance']])}


# POIS NODES

def pois_from_bbox(bbox):
    """ Queries OSM for points of interest inside a `bbox` according to the OSM keys and values

    :param bbox: list of float of the form [lat_min, lon_min, lat_max, lon_max]
    :returns: pois inside bbox as pandas.DataFrame
    :rtype: pandas.DataFrame

    """
    pois = pd.DataFrame()  # columns=['key','value','lon','lat'])
    for key, values, columns in zip(osm_pois.keys, osm_pois.values, osm_pois.columns):
        try:
            df = _process_pois_df_columns(_nodes_from_bbox(
                bbox, tags=_generate_osm_tag(key, values)), key, columns)
            if len(df) > 1:
                pois = pd.concat([pois, df])
        except RuntimeError:  # the query result is empty
            pass
    return pois
