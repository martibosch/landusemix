"""
BASED ON https://github.com/UDST/pandana/blob/master/pandana/loaders/osm.py

Tools for creating graphs from Open Street Map.
"""
from __future__ import division
from itertools import islice, izip

import pandas as pd
import requests

import osm_pois
import utils

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


# DATA PROCESSING

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
