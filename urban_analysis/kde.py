import numpy as np
import pandas as pd
from seaborn.distributions import _statsmodels_bivariate_kde
from six import string_types
from sklearn.neighbors.kde import KernelDensity
import statsmodels.nonparametric.api as smnp

import utils

USE_normalise_kde = True
normalisation_max = False

def normalise_kde(np_kde):
	""" Input: Numpy matrix of the KDE
	Depending on normalisation_max parameter:
	1) Normalise the gridded KDE; Sum(elements) = 1
	2) Divide by its maximum value. All values are within [0,1]
	"""
	### Normalise to [0,1] all cells of KDE; sum(elements) = 1
	def applyDiv(x,total):
	    return x/total
	applyNormalisation = np.vectorize(applyDiv)
	if (normalisation_max):
		norm_kde = applyNormalisation(np_kde, np_kde.max())
	else:
		norm_kde = applyNormalisation(np_kde, np_kde.sum())
	return norm_kde

def _kde(x, y, grid, bandwidth_x_y):
    """Compute a bivariate kde using statsmodels. Based on https://github.com/mwaskom/seaborn/blob/master/seaborn/distributions.py
    Bandwidth in x,y dimensions are determined according to the walkability distance: Usually around 400m

    :param numpy.ndarray x: 
    :param numpy.ndarray y: 
    :param list grid: 
    :returns: 
    :rtype: numpy.ndarray

    """
    # https://jakevdp.github.io/blog/2013/12/01/kernel-density-estimation/
    # https://pypi.python.org/pypi/fastkde/1.0.9
    # Issue with other implementations: Bandwidth.
    if (False): # Scipy
        # PROBLEM: Cannot set a bandwidth relative to latitude and longitude
        # Should reproject latitude/longitude to another projection space, to avoid distortion and use a unique bandwidth
        from scipy import stats
        values = np.vstack([x, y])
        kernel = stats.gaussian_kde(values)#, bw_method=[ bandwidth_x_y[0], bandwidth_x_y[1] ])
        kde_ = kernel.pdf([grid[0].ravel(), grid[1].ravel()]).reshape(grid[0].shape)
    else: # Statsmodel KDE
        """
        #normal_reference: normal reference rule of thumb (default), cv_ml: cross validation maximum likelihood, cv_ls: cross validation least squares
        bw_func = smnp.bandwidths.bw_scott 
        bw_func = smnp.bandwidths.bw_silverman 
        kde = smnp.KDEMultivariate([x, y], "cc", [bw_func(x), bw_func(y)])
        kde = smnp.KDEMultivariate([x, y], "cc", 'cv_ml')
        kde = smnp.KDEMultivariate([x, y], "cc", 'cv_ls')
        """
        kde = smnp.KDEMultivariate([x, y], "cc", [ bandwidth_x_y[0], bandwidth_x_y[1] ])
        kde_ = kde.pdf([grid[0].ravel(), grid[1].ravel()]).reshape(grid[0].shape)
    
    if (USE_normalise_kde):
        # Normalise KDE's. Otherwise: Entropy based metric may return negative values (probabilities lie between 0 and 1)
        np_kde = normalise_kde( kde_ )
    else:
        np_kde = kde_
        
    # Check
    if (USE_normalise_kde and (not(normalisation_max) ) ) : assert( np_kde.sum() < 1.00001 and np_kde.sum() > 0.99999 )        
    return np_kde


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


def _get_grid_kde(pois, grid, bbox, meters_kde_distance ):
    """FIXME! briefly describe function

    :param pois: 
    :param grid: 
    :returns: 
    :rtype: numpy.ndarray

    """
    if (bbox == None):
        return _kde(pois['lon'].values, pois['lat'].values, grid)
    else:
        return _kde(pois['lon'].values, pois['lat'].values, grid, utils.lat_lon_shift(bbox,meters_kde_distance) )


def get_grid_category_kde(pois, bbox, meters_kde_distance, grid_step=100):
    """ 

    :param pandas.DataFrame pois: 
    :param list bbox: 
    :param float grid_step: 
    :returns: 
    :rtype: pandas.DataFrame

    """
    if (bbox == None):
        print('Warning: Bounding box missing')
        return pd.DataFrame(_kde(pois['lon'].values, pois['lat'].values, utils.grid_from_bbox(bbox, grid_step) ) )
    else:
        return pd.DataFrame(_kde(pois['lon'].values, pois['lat'].values, utils.grid_from_bbox(bbox, grid_step), utils.lat_lon_shift(bbox,meters_kde_distance) ) )


def get_grid_all_kde(pois, bbox, meters_kde_distance, grid_step=100):
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
        kde_dict[category+'_'+str(grid_step)] = pd.DataFrame(_get_grid_kde(items, grid, bbox, meters_kde_distance))

    kde_dict['total_'+str(grid_step)] = pd.DataFrame(_get_grid_kde(pois, grid, bbox, meters_kde_distance))

    return kde_dict
