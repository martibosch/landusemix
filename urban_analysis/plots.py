import matplotlib.cm as cm
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import seaborn as sns


def _category_scatter(x, y, label=None, scatter_kws=None, line_kws=None, ax=None):
    """ Creates a scatter plot for each group indicated with `by`

    :param pandas.DataFrame pois_df: pois with the columns 'key', 'value', 'lon' (longitude), 'lat' (latitude)
    :param by: mapping function / list of functions, dict, Series, or tuple /list of column names. (see http://pandas.pydata.org/pandas-docs/stable/generated/pandas.DataFrame.groupby.html)
    :type by: method, dict, pandas.Series, tuple, list
    :param dict scatter_kws: additional keyword arguments to pass to plt.scatter
    :param dict line_kws: additional keyword arguments to pass to plt.plot
    :param plt.Axes ax:
    """
    if ax:
        ax.set_title(label)
        ax.set_aspect('equal')
    else:
        plt.title(label)
    return sns.regplot(x, y, fit_reg=False, scatter_kws=scatter_kws, line_kws=line_kws, ax=ax)


def pois_scatter(pois, by=['key'], base_figsize=8, scatter_kws=None, line_kws=None):
    """ Creates a scatter plot for each group indicated with `by`

    :param pandas.DataFrame pois: pois with the columns 'key', 'value', 'lon' (longitude), 'lat' (latitude)
    :param by: mapping function / list of functions, dict, Series, or tuple /list of column names. (see http://pandas.pydata.org/pandas-docs/stable/generated/pandas.DataFrame.groupby.html)
    :type by: method, dict, pandas.Series, tuple, list
    :param dict scatter_kws: additional keyword arguments to pass to plt.scatter
    :param dict line_kws: additional keyword arguments to pass to plt.plot

    """
    category_gb = pois.groupby(by=by)
    n_categories = len(category_gb)
    fig, axes = plt.subplots(nrows=n_categories, ncols=1, sharey=True, sharex=True, figsize=(
        base_figsize, base_figsize * n_categories))
    if n_categories == 1:  # Must be iterable
        axes = [axes]
    for (label, df), ax in zip(category_gb, axes):
        _category_scatter(df['lon'], df['lat'], label=label,
                          scatter_kws=scatter_kws, line_kws=line_kws, ax=ax)
    # return ax


def pois_scatter_kde(pois, by=['key'], base_figsize=8, scatter_kws=None, line_kws=None, **kwargs):
    """ 

    :param pandas.DataFrame pois: 
    :param list by: 
    :param base_figsize: 
    :param scatter_kws: 
    :param line_kws: 

    """
    category_gb = pois.groupby(by=by)
    n_categories = len(category_gb)
    fig, axes = plt.subplots(nrows=n_categories, ncols=2, sharey=True, sharex=True, figsize=(
        base_figsize * 2, base_figsize * n_categories), squeeze=False)
    for (label, df), ax_row in zip(category_gb, axes):
        _category_scatter(df['lon'], df['lat'], label=label,
                          scatter_kws=scatter_kws, line_kws=line_kws, ax=ax_row[0])
        ax_kde = ax_row[1]
        ax_kde.set_title(label)     # TODO: put a title for the row
        sns.kdeplot(df['lon'], df['lat'], ax=ax_kde, **kwargs)
    # return ax


def graph_centrality_kde(graph, centrality):
    """

    :param GeoGraph graph: 
    :param pandas.DataFrame centrality: 
    :returns: 
    :rtype: 

    """
    cmap = plt.get_cmap('jet')
    for centrality_label in centrality:
        for category_label, category_ser in category_gb:
            fig, ax = plt.subplots(figsize=(10, 10))
            ax.set_title(centrality_label + ' vs ' + category_label)
            sns.kdeplot(category_ser['lon'], category_ser[
                        'lat'], ax=ax, legend=True, shade=True)
            geo_graph.plot(ax, node_color=[centrality[centrality_label][
                           node.id] for node in geo_graph], node_size=50, cmap=cmap)


def plot_categories_kde(categories_kde, pois, xx, yy):
    """ 

    :param dict categories_kde: 
    :param pandas.DataFrame pois: 
    :param numpy.array xx: 
    :param numpy.array yy: 
    :returns: 
    :rtype: 

    """
    n_rows = len(categories_kde)
    base_figsize = 8

    fig = plt.figure(figsize=(8, 8 * n_rows))
    i = 1
    for label, f in categories_kde.items():
        if label == 'total':
            category_pois = pois
        else:
            category_pois = pois[pois['category'] == label]
        ax1 = fig.add_subplot(n_rows, 2, i)
        ax2 = fig.add_subplot(n_rows, 2, i + 1, projection='3d')
        ax1.scatter(category_pois['lon'], category_pois['lat'])
        ax1.set_ylabel(label, rotation=90)
        ax2.plot_surface(xx, yy, f, cmap=cm.RdYlBu)
        i += 2
        ax2.set_xlabel('lon', labelpad=-10)
        ax2.set_ylabel('lat', labelpad=-10)
        ax2.zaxis.set_rotate_label(False)  # workaround
        ax2.set_zlabel(r'$f_c$', rotation=0, labelpad=-15)
        ax2.w_xaxis.set_ticklabels([])
        ax2.w_yaxis.set_ticklabels([])
        ax2.w_zaxis.set_ticklabels([])
