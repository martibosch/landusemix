import matplotlib.cm as cm
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import seaborn as sns


def _category_scatter(x, y, title=None, label=None, scatter_kws=None, line_kws=None, ax=None):
    """

    :param x:
    :param y:
    :param title:
    :param label:
    :param scatter_kws:
    :param line_kws:
    :param ax:
    :returns:
    :rtype:

    """
    if ax:
        ax.set_title(title)
        ax.set_aspect('equal')
    else:
        plt.title(title)
    return sns.regplot(x, y, fit_reg=False, label=label, scatter_kws=scatter_kws, line_kws=line_kws, ax=ax)


def pois_scatter(pois, overlap=False, base_figsize=8, scatter_kws=None, line_kws=None, by=['category']):
    """

    :param pois:
    :param overlap:
    :param base_figsize:
    :param scatter_kws:
    :param line_kws:
    :param by:
    :returns:
    :rtype:

    """
    category_gb = pois.groupby(by=by)
    if overlap:
        fig, ax = plt.subplots(figsize=(base_figsize, base_figsize))
        for label, df in category_gb:
            _category_scatter(df['lon'], df['lat'], title='pois', label=label,
                              scatter_kws=scatter_kws, line_kws=line_kws, ax=ax)
        ax.legend(*ax.get_legend_handles_labels())
    else:
        n_categories = len(category_gb)
        fig, axes = plt.subplots(nrows=n_categories, ncols=1, sharey=True, sharex=True, figsize=(
            base_figsize, base_figsize * n_categories))
        if n_categories == 1:  # Must be iterable
            axes = [axes]
        for (label, df), ax in zip(category_gb, axes):
            _category_scatter(df['lon'], df['lat'], label=label,
                              scatter_kws=scatter_kws, line_kws=line_kws, ax=ax)
            # return ax


def pois_scatter_kde(pois, overlap=False, base_figsize=8, xlim=None, ylim=None, scatter_kws=None, line_kws=None, by=['category'], **kwargs):
    """

    :param pois:
    :param overlap:
    :param base_figsize:
    :param xlim:
    :param ylim:
    :param scatter_kws:
    :param line_kws:
    :param by:
    :returns:
    :rtype:

    """
    category_gb = pois.groupby(by=by)
    if overlap:
        fig, axes = plt.subplots(nrows=1, ncols=2, sharey=True, sharex=True, figsize=(
            base_figsize * 2, base_figsize), squeeze=False)
        for label, df in category_gb:
            _category_scatter(pois['lon'], pois['lat'], title='pois', label=label,
                              scatter_kws=scatter_kws, line_kws=line_kws, ax=axes[0][0])
            sns.kdeplot(pois['lon'], pois['lat'], ax=axes[0][1], **kwargs)
            if xlim and ylim:
                for ax in axes[0]:
                    ax.set_xlim(xlim)
                    ax.set_ylim(ylim)
                    ax.set_xticklabels([])
                    ax.set_yticklabels([])
    else:
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


def plot_category_kde(category_kde, pois, xx, yy, category_label=None):
    """

    :param pandas.DataFrame category_kde:
    :param pandas.DataFrame pois:
    :param numpy.array xx:
    :param numpy.array yy:
    :returns:
    :rtype:

    """

    fig = plt.figure(figsize=(16, 8))
    ax1 = fig.add_subplot(1, 2, 1)
    ax2 = fig.add_subplot(1, 2, 2, projection='3d')
    ax1.scatter(pois['lon'], pois['lat'])
    if category_label:
        ax1.set_ylabel(category_label, rotation=90)
    ax2.plot_surface(xx, yy, category_kde, cmap=cm.RdYlBu)
    ax2.set_xlabel('lon', labelpad=-10)
    ax2.set_ylabel('lat', labelpad=-10)
    ax2.zaxis.set_rotate_label(False)  # workaround
    ax2.set_zlabel(r'$f$', rotation=0, labelpad=-15)
    ax2.w_xaxis.set_ticklabels([])
    ax2.w_yaxis.set_ticklabels([])
    ax2.w_zaxis.set_ticklabels([])


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

def plot_contour(xx, yy, grid, label, figsize=(12, 8)):
    """ Contour plot
    TODO: Smooth contour filling
    """
    w,h = figsize
    plt.figure(figsize=(w,h))
    cp = plt.contourf(xx[:-1,:-1], yy[:-1,:-1], grid, cmap=plt.get_cmap('Blues'))
    plt.colorbar(cp)
    plt.title(label)
    plt.xlabel('Lon')
    plt.ylabel('Lat')
    plt.show()
        
def plot_(xx, yy, grid, label, figsize = (12, 8)):
    """ Plot the input grid
    """
    w,h = figsize
    fig = plt.figure(figsize=(w,h))
    ax = fig.add_subplot(111, projection='3d')
    ax.plot_surface(xx[:-1,:-1], yy[:-1,:-1], grid, cmap=cm.RdYlBu)
    ax.set_xlabel('Lon')
    ax.set_ylabel('Lat')
    ax.set_zlabel(label)