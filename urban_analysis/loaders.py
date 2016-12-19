from os.path import dirname, join, exists
from six import string_types

import pandas as pd

import kde
import osm_loader
import shp_loader

# CONSTANTS FOR THE STORAGE-RELATED DEFINITIONS
BASE_DIR = join(dirname(__file__), 'hdfs_store')

GRAPH_KEYS = ['nodes', 'edges']
GRAPH_CENTRALITY_KEYS = ['graph_centrality']
OSM_POIS_KEYS = ['osm_pois']
# OSM_EXTRACTED_POIS_KEYS = ['activities', 'residential']
POIS_KEYS = ['pois']
GRAPH_KDE_KEYS = ['graph_kde']
GRID_KDE_KEYS = ['activity', 'residential' , 'total']


# CUSTOM EXCEPTION

class NotStoredLocallyException(Exception):
    pass

class HDF5ExtError(Exception):
    pass

# LOCAL STORAGE UTILS


def _generate_file_path(city_ref, file_extension='h5'):
    """ Generate a file path for local storage data
    :param city_ref: str with the name used to locally refer to the file
    :param file_extension: str with the extension used for local storage
    :returns: path to the file location
    :rtype: str
    """
    return join(BASE_DIR, city_ref + '.' + file_extension)


def _get_local_data(store, hdfs_keys):
    """ Get the data if it is stored locally. Raise NotStoredLocallyException otherwise

    :param store: pandas.HDFStore
    :param hdfs_keys: str or list of str with the key(s) used for storage at `store`
    :returns: data corresponding to `city_ref` and `hdfs_keys` if stored locally
    :rtype: pandas.DataFrame or dict of pandas.DataFrame

    """
    try:
        if isinstance(hdfs_keys, (list, tuple)) and len(hdfs_keys) == 1:
            hdfs_keys = hdfs_keys[0]
        if isinstance(hdfs_keys, string_types):
            return store[hdfs_keys]

        # if not isinstance(hdfs_keys, (list, tuple)):
        #     raise TypeError("hdfs_keys must be a str or list/tuple")

        # there are several keys
        # return tuple(store[hdfs_key] for hdfs_key in hdfs_keys)
        return {hdfs_key: store[hdfs_key] for hdfs_key in hdfs_keys}

    except (IOError, KeyError), e:
        raise NotStoredLocallyException(
            e.message + "The keys `{hdfs_keys}` are not stored locally at `{store}`.".format(hdfs_keys=hdfs_keys, store=store))


def _update_local_data(store, df_dict, format='table'):
    """

    :param store: pandas.HDFStore
    :param df_dict: dict indexed by hdfs keys and with pandas.DataFrame as values
    """
    try :
        [store.put(hdfs_key, df, format=format) for hdfs_key, df in df_dict.items()]
    except:# (HDF5ExtError) as err:
        print('HDF5 Error. Local data not updated')
# QUERY UTILS


def _load_data(city_ref, hdfs_keys, extra_method=None, extra_args=None):
    """ Get the data, either from the local `store` or remotely through `extra_method` and store it locally.

    :param city_ref: str with the name used to locally refer to the file
    :param hdfs_keys: str or list of str with the key(s) used for storage at `store`
    :param extra_method:
    :param extra_args:
    :returns: data at `store` for `hdfs_keys`
    :rtype: pandas.DataFrame or dict of pandas.DataFrame

    """
    try:
        print("Querying locally for `%s`" % str(hdfs_keys))
        with pd.HDFStore(_generate_file_path(city_ref), 'r') as store:
            result = _get_local_data(store, hdfs_keys)
            print("Found %s stored locally" % str(hdfs_keys))
    except (NotStoredLocallyException, IOError) as e:
        assert (extra_method != None), e.message + \
            "A method and its arguments to obtain the data must then be provided"
        print("`%s` is/are not stored locally. Determining it/them through `%s` method" %
              (str(hdfs_keys), extra_method.__name__))
        result = extra_method(*extra_args)
        with pd.HDFStore(_generate_file_path(city_ref), 'a') as store:
            print("Saving data for `%s` at `%s`" % (str(hdfs_keys), str(store._path)))
            # if _get_data returns pd.DataFrame we know that hdfs_keys[0] is string_types
            if isinstance(result, pd.DataFrame):
                _update_local_data(store, {hdfs_keys[0]: result})
            elif isinstance(result, dict):
                # assert len(result) == len(hdfs_keys), "The `extra_arg_method` must return a component for each key in hdfs_keys"
                _update_local_data(store, result)
            print("The data has been stored locally with success")
    return result


# PUBLIC METHODS

# LOADERS
def load_graph(city_ref, bbox=None, tags=None):
    """ Loads the graph for `city_ref` if it is stored locally, or queries OSM for the region inside `bbox` and stores the result locally.

    :param city_ref: str with the name used to locally refer to the file
    :param bbox: list of floats the form [lat_min, lon_min, lat_max, lon_max]
    :param tags: list or str with a tag request according to the Overpass QL (see http://wiki.openstreetmap.org/wiki/Overpass_API/Language_Guide)
    :returns: urban graph of `city_ref`
    :rtype: GeoGraph

    """
    result = _load_data(city_ref, GRAPH_KEYS,
                        osm_loader.graph_from_bbox, [bbox, tags])
    return GeoGraph(result[GRAPH_KEYS[0]], result[GRAPH_KEYS[1]])


def load_graph_centrality(city_ref, graph=None):
    """ Loads the centrality indices for `city_ref` if they are stored locally, or determines them

    :param city_ref: str with the name used to locally reference the file
    :param graph: GeoGraph corresponding to `city_ref`
    :returns: 'betweeness', 'closeness' and 'degree' centralities for each node of `graph`
    :rtype: pandas.DataFrame

    """
    return _load_data(city_ref, GRAPH_CENTRALITY_KEYS, graph.get_centrality_df, [])


def load_osm_pois(city_ref, bbox=None):
    """ Loads the points of interest for `city_ref` if they are stored locally, or queries OSM for the region inside `bbox` and stores the result locally.

    :param city_ref: str with the name used to locally reference the file
    :param bbox: list of floats the form [lat_min, lon_min, lat_max, lon_max]
    :returns: pois with the columns 'key', 'value', 'lon' (longitude), 'lat' (latitude)
    :rtype: pandas.DataFrame

    """
    return _load_data(city_ref, OSM_POIS_KEYS, osm_loader.pois_from_bbox, [bbox])


def load_pois(city_ref, pois_shp_path=None):
    """ Loads the points of interest assuming that the activities and residential shapefiles are present.

    :param city_ref: str with the name used to locally reference the file
    :param pois_shp_path:
    :returns: pois with the columns 'key', 'value', 'lon' (longitude), 'lat' (latitude) and 'cat'
    :rtype: pandas.DataFrame

    """
    try:
        return _load_data(city_ref, POIS_KEYS, shp_loader.get_extracted_osm_points, [pois_shp_path, city_ref])
    except shp_loader.PoisShpDoesNotExist:
        print('%s does not exist. You might try to load OSM pois instead through `load_osm_pois`.' % pois_shp_path)


def load_graph_kde(city_ref, graph=None, pois=None):
    """ Loads the categorized pois density at the urban nodes of `graph` for `city_ref` if they are stored locally, or determines them

    :param city_ref: str with the name used to locally reference the file
    :param graph: GeoGraph corresponding to `city_ref`
    :param pois:
    :returns: logarithm of the density at each node of `graph`
    :rtype: pandas.DataFrame

    """
    return _load_data(city_ref, GRAPH_KDE_KEYS, kde.get_nodes_kde, [graph, pois])


def load_grid_kde(city_ref, meters_kde_distance, pois=None, bbox=None, grid_step=100):
    """ Loads the categorized pois density at the urban nodes of `geo_graph` for `city_ref` if they are stored locally, or determines them

    :param city_ref: str with the name used to locally reference the file
    :param pois: 
    :param bbox: 
    :param grid_step: 
    :returns: for each 'category' key, pandas.DataFrame with density at each point of the grid
    :rtype: dict

    """
    # Kde_category + _grid_step
    kde_dict = _load_data(city_ref,  list(map(lambda s: s + '_' + str(grid_step), GRID_KDE_KEYS)), kde.get_grid_all_kde, [pois, bbox, meters_kde_distance, grid_step])
    # Pop _...
    [kde_dict.__setitem__(key[:key.find('_')], kde_dict.pop(key)) for key in kde_dict.keys() if '_' in key]
    return kde_dict
