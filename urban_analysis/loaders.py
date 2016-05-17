from os.path import dirname, isfile, join
from six import string_types

import pandas as pd

from geo_graph import GeoGraph
import kde
import osm_loader


# CUSTOM EXCEPTION

class NotStoredLocallyException(Exception):
    pass

# LOCAL STORAGE UTILS

def _generate_file_path(city_ref, file_extension='h5'):
    """ Generate a file path for local storage data

    :param city_ref: str with the name used to locally refer to the file
    :param file_extension: str with the extension used for local storage
    :returns: path to the file location
    :rtype: str

    """
    return join(dirname(__file__), 'hdfs_store/', city_ref + '.' + file_extension)

def _get_local_data(store, hdfs_keys):
    """ Get the data if it is stored locally. Raise NotStoredLocallyException otherwise

    :param store: pandas.HDFStore
    :param hdfs_keys: str or list of str with the key(s) used for storage at `store`
    :returns: data corresponding to `city_ref` and `hdfs_keys` if stored locally
    :rtype: pandas.DataFrame or tuple of pandas.DataFrame

    """
    try:
        if isinstance(hdfs_keys, (list, tuple)) and len(hdfs_keys) == 1:
            hdfs_keys = hdfs_keys[0]
        if isinstance(hdfs_keys, string_types):
            return store[hdfs_keys]

        if not isinstance(hdfs_keys, (list, tuple)):
            raise TypeError("keys must be a str or list/tuple")

        # there are several keys
        return tuple(store[hdfs_key] for hdfs_key in hdfs_keys)
                
    except (IOError, KeyError, TypeError), e:
        raise NotStoredLocallyException(e.message + "The keys `{hdfs_keys}` are not stored locally at `{store}`.".format(hdfs_keys=hdfs_keys, store=store))

    
# QUERY UTILS

def _get_data(store, hdfs_keys, extra_method=None, extra_args=None):
    """ Get the data, either from the `local` store or remotely through `extra_method`

    :param store: pandas.HDFStore
    :param hdfs_keys: str or list of str with the key(s) used for storage at `store`
    :param extra_method: 
    :param extra_args: 
    :returns: data at `store` for `hdfs_keys`
    :rtype: pandas.DataFrame or tuple of pandas.DataFrame

    """
    try:
        return _get_local_data(store, hdfs_keys)
    except NotStoredLocallyException, e:
        assert (extra_method != None and extra_args != None), e.message + "A method and its arguments to obtain the data must then be provided"
        return extra_method(*extra_args)

def _load_data(city_ref, hdfs_keys, extra_method, extra_args):
    """ Loads the data for `city_ref` and `hdfs_keys` if it is stored locally, or obtains the data and stores it locally.

    :param city_ref: str with the name used to locally refer to the file
    :param hdfs_keys: str or list of str with the key used to store the data frame of `city_ref`
    :param extra_method: method to obtain the data in case that it is not stored locally. It must return a component for each key in `hdfs_keys`
    :param extra_args: list of arguments that `extra_method` takes
    :returns: data corresponding to each key of `hdfs_keys` for `city_ref`
    :rtype: pandas.DataFrame or tuple of pandas.DataFrame

    """
    with pd.HDFStore(_generate_file_path(city_ref), 'w') as store:
        result = _get_data(city_ref, hdfs_keys, extra_method, extra_args)
        if isinstance(result, pd.DataFrame): # if _get_data returns pd.DataFrame we know that hdfs_keys[0] is string_types
            store.put(hdfs_keys[0], result, format='table')
        elif isinstance(result, tuple):
            assert len(result) == len(hdfs_keys), "The `extra_arg_method` must return a component for each key in hdfs_keys"
            for result_df, hdfs_key in zip(result, hdfs_keys):
                store.put(hdfs_key, result_df, format='table')
    return result



### PUBLIC METHODS

def load_graph(city_ref, bbox=None, tags=None):
    """ Loads the graph for `city_ref` if it is stored locally, or queries OSM for the region inside `bbox` and stores the result locally.

    :param city_ref: str with the name used to locally refer to the file
    :param bbox: list of floats the form [lat_min, lon_min, lat_max, lon_max]
    :param tags: list or str with a tag request according to the Overpass QL (see http://wiki.openstreetmap.org/wiki/Overpass_API/Language_Guide)
    :returns: urban graph of `city_ref`
    :rtype: GeoGraph

    """
    nodes_df, edges_df = _load_data(city_ref, ['nodes', 'edges'], osm_loader.graph_from_bbox, [bbox, tags])
    return GeoGraph(nodes_df, edges_df)


def load_pois(city_ref, bbox=None):
    """ Loads the points of interest for `city_ref` if they are stored locally, or queries OSM for the region inside `bbox` and stores the result locally.

    :param city_ref: str with the name used to locally reference the file
    :param bbox: list of floats the form [lat_min, lon_min, lat_max, lon_max]
    :returns: pois with the columns 'key', 'value', 'lon' (longitude), 'lat' (latitude)
    :rtype: pandas.DataFrame

    """
    return _load_data(city_ref, ['pois'], osm_loader.pois_from_bbox, [bbox])


def load_centrality(city_ref, geo_graph=None):
    """ Loads the centrality indices for `city_ref` if they are stored locally, or determines them

    :param city_ref: str with the name used to locally reference the file
    :param geo_graph: GeoGraph corresponding to `city_ref`
    :returns: 'betweeness', 'closeness' and 'degree' centralities for each node of `geo_graph`
    :rtype: pandas.DataFrame

    """
    return _load_data(city_ref, ['centrality'], geo_graph.get_centrality_df, [])

def load_kde(city_ref, geo_graph, pois):
    """ Loads the categorized `pois` density at the urban nodes of `geo_graph` for `city_ref` if they are stored locally, or determines them

    :param city_ref: str with the name used to locally reference the file
    :param geo_graph: GeoGraph corresponding to `city_ref`
    :returns: pois with the columns 'key', 'value', 'lon' (longitude), 'lat' (latitude)
    :returns: logarithm of the density at each node of `geo_graph`
    :rtype: pandas.DataFrame

    """
    return _load_data(city_ref, ['kde'], kde.get_kde_df, [geo_graph, pois])
