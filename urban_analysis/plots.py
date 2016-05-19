import matplotlib.pyplot as plt
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

def pois_scatter(pois_df, by=['key'], base_figsize=8, scatter_kws=None, line_kws=None):
    """ Creates a scatter plot for each group indicated with `by`

    :param pandas.DataFrame pois_df: pois with the columns 'key', 'value', 'lon' (longitude), 'lat' (latitude)
    :param by: mapping function / list of functions, dict, Series, or tuple /list of column names. (see http://pandas.pydata.org/pandas-docs/stable/generated/pandas.DataFrame.groupby.html)
    :type by: method, dict, pandas.Series, tuple, list
    :param dict scatter_kws: additional keyword arguments to pass to plt.scatter
    :param dict line_kws: additional keyword arguments to pass to plt.plot

    """
    category_gb = pois_df.groupby(by=by)
    n_categories = len(category_gb)
    fig, axes = plt.subplots(nrows=n_categories, ncols=1, sharey=True, sharex=True, figsize=(base_figsize, base_figsize*n_categories))
    for (label, df), ax in zip(category_gb, axes):
        _category_scatter(df['lon'], df['lat'], label=label, scatter_kws=scatter_kws, line_kws=line_kws, ax=ax)
    # return ax

def pois_scatter_kde(pois_df, kde_df, by=['key'], base_figsize=8, scatter_kws=None, line_kws=None, **kwargs):
    """FIXME! briefly describe function

    :param pois_df: 
    :param kde_df: 
    :param by: 
    :param base_figsize: 
    :param scatter_kws: 
    :param line_kws: 

    """
    category_gb = pois_df.groupby(by=by)
    n_categories = len(category_gb)
    fig, axes = plt.subplots(nrows=n_categories, ncols=2, sharey=True, sharex=True, figsize=(base_figsize*2, base_figsize*n_categories))
    for (label, df), ax_row in zip(category_gb, axes):
        _category_scatter(df['lon'], df['lat'], label=label, scatter_kws=scatter_kws, line_kws=line_kws, ax=ax_row[0])
        ax_kde = ax_row[1]
        ax_kde.set_title(label)     # TODO: put a title for the row
        sns.kdeplot(df['lon'], df['lat'], ax=ax_kde, **kwargs)
    # return ax




def graph_centrality_kde(graph, centrality_df):
    cmap = plt.get_cmap('jet')
    for centrality_label in centrality_df:
        for category_label, category_ser in category_gb:
            fig, ax = plt.subplots(figsize=(10,10))
            ax.set_title(centrality_label + ' vs ' + category_label)
            sns.kdeplot(category_ser['lon'], category_ser['lat'], ax=ax, legend=True, shade=True)
            geo_graph.plot(ax, node_color = [centrality_df[centrality_label][node.id] for node in geo_graph], node_size=50, cmap=cmap)

