import numpy as np
import pandas as pd
from sklearn.neighbors.kde import KernelDensity

def get_kde_df(geo_graph, pois):
    """ Determine density of categorized `pois` for each node of `geo_graph`

    :param geo_graph: geo_graph.GeoGraph of the region
    :param pois: pandas.DataFrame with the pois of the region
    :returns: logarithm of the density at each node of `geo_graph`
    :rtype: pandas.DataFrame

    """
    nodes_array = np.array([node.pos for node in geo_graph])
    kde_df = pd.DataFrame(index=[node.id for node in geo_graph])
    
    for category, items in pois.groupby(by=['key']):
        kde = KernelDensity()
        kde.fit(items[['lon','lat']].values)
        kde_df[category] = kde.score_samples(nodes_array)

    return kde_df
