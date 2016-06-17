import numpy as np
import pandas as pd
from seaborn.distributions import _statsmodels_bivariate_kde
from six import string_types
from sklearn.neighbors.kde import KernelDensity
import statsmodels.nonparametric.api as smnp

import utils


def _kde(x, y, grid):
    """Compute a bivariate kde using statsmodels. Based on https://github.com/mwaskom/seaborn/blob/master/seaborn/distributions.py

    :param numpy.ndarray x: 
    :param numpy.ndarray y: 
    :param list grid: 
    :returns: 
    :rtype: numpy.ndarray

    """

    bw_func = smnp.bandwidths.bw_scott  # scott
    # bw_func = smnp.bandwidths.bw_silverman #silverman
    print('Bw func X', bw_func(x))
    print('Bw func Y', bw_func(y))
    # Test bw = 0.2 ?

    # TODO: Check other option; normal_reference: normal reference rule of
    # thumb (default), cv_ml: cross validation maximum likelihood, cv_ls:
    # cross validation least squares
    kde = smnp.KDEMultivariate([x, y], "cc", [bw_func(x), bw_func(y)])
    #kde = smnp.KDEMultivariate([x, y], "cc", 'cv_ml')
    #kde = smnp.KDEMultivariate([x, y], "cc", 'cv_ls')

    return kde.pdf([grid[0].ravel(), grid[1].ravel()]).reshape(grid[0].shape)


def get_nodes_kde(graph, pois):
    """ Determine density of categorized pois for each node of `graph`

    :param graph: graph.GeoGraph of the region
    :param pois: pandas.DataFrame with the pois of the region
    :returns: logarithm of the density at each node of `graph`
    :rtype: pandas.DataFrame

    """
    nodes_array = np.array([node.pos for node in graph])
    kde_df = pd.DataFrame(index=[node.id for node in graph])

    for category, items in pois.groupby(by=['category']):
        kde = KernelDensity()
        kde.fit(items[['lon', 'lat']].values)
        kde_df[category] = kde.score_samples(nodes_array)

    return kde_df


def _get_grid_kde(pois, grid):
    """FIXME! briefly describe function

    :param pois: 
    :param grid: 
    :returns: 
    :rtype: numpy.ndarray

    """
    return _kde(pois['lon'].values, pois['lat'].values, grid)


def get_grid_category_kde(pois, bbox, grid_step=0.0015):
    """ 

    :param pandas.DataFrame pois: 
    :param list bbox: 
    :param float grid_step: 
    :returns: 
    :rtype: pandas.DataFrame

    """
    return pd.DataFrame(_kde(pois['lon'].values, pois['lat'].values, utils.grid_from_bbox(bbox, grid_step)))


def get_grid_all_kde(pois, bbox, grid_step=0.0015):
    """

    :param pandas.DataFrame pois: 
    :param list bbox: 
    :param float grid_step: 
    :returns: 
    :rtype: dict

    """
    kde_dict = {}
    grid = utils.grid_from_bbox(bbox, grid_step)

    for category, items in pois.groupby(by=['category']):
        kde_dict[category] = pd.DataFrame(_get_grid_kde(items, grid))

    # kde_dict['total'] = pd.DataFrame(_get_grid_kde(pois, grid))

    return kde_dict
