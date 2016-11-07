import matplotlib.cm as cm
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import seaborn as sns

# Plots font size to use
font_size_ = 14

def _category_scatter(x, y, title=None, label=None, scatter_kws=None, ax=None, color = 'b', fileName = None):
    if ax:
        ax.set_title(title, fontsize=font_size_)
        ax.set_xlabel('Longitude', fontsize=font_size_)
        ax.set_ylabel('Latitude', fontsize=font_size_)
        ax.set_aspect('equal')        
    else:
        plt.title(title, fontsize=font_size_)
    x.name = 'Longitude'
    y.name = 'Latitude'
    plot = sns.regplot(x, y, fit_reg=False, scatter_kws=scatter_kws, ax=ax, color=color)
    if (not( fileName is None) ):
        plt.savefig(fileName+'.png', format='png', bbox_inches='tight', dpi=300)
    return plot
    
def pois_scatter(city,categories=['activity','residential'],alphas=[0.1,0.1],colors=['b','g'],little_margin = 0.01, figsize=(12, 8)):
    """ Scatter plot
    """
    for category, alpha, color in zip( categories, alphas, colors ):
        pois = city.pois[city.pois.category == category ]
        fig, ax = plt.subplots(nrows=1, ncols=1, figsize=figsize)
        ax.set_ylim([pois['lat'].min() - little_margin, pois['lat'].max() + little_margin])
        ax.set_xlim([pois['lon'].min() - little_margin, pois['lon'].max() + little_margin])
        fileN = str(city.city_ref)+'_Scatter_'+category
        _category_scatter(pois['lon'],pois['lat'],title=category.title(),fileName=fileN,ax=ax,color=color,scatter_kws={'alpha':alpha})
        
        
def plot_contour_local(fileN, xx,yy,grid, label, log_scale = True, figsize=(12, 8)):
    """ Contour plot
    Optional: Save into file
    """
    plt.figure(figsize=figsize)
    cmap = cm.RdYlBu # plt.get_cmap('winter')
    if (log_scale):
        cp = plt.contourf(xx[:-1,:-1], yy[:-1,:-1], grid, cmap=cmap, antialiased=False, locator=ticker.LogLocator())
    else:
        cp = plt.contourf(xx[:-1,:-1], yy[:-1,:-1], grid, cmap=cmap, antialiased=False)
    plt.colorbar(cp)
    plt.title(label, fontsize=font_size_)
    plt.xlabel('Longitude', fontsize=font_size_)
    plt.ylabel('Latitude', fontsize=font_size_)
    if not( fileN is None ):
        plt.savefig(fileN+'.png', format='png', bbox_inches='tight', dpi=300)   
        
def plot_local(fileN, xx,yy,grid_3d,zlim, label, figsize=(12, 8) ):
    """ 3D Plot
    Optional: Save into file
    """
    fig = plt.figure(figsize=figsize)
    ax = fig.add_subplot(111, projection='3d')
    ax.set_xlabel('Longitude', fontsize=font_size_)
    ax.set_ylabel('Latitude', fontsize=font_size_)
    ax.set_zlabel('')
    ax.set_title(label, fontsize=font_size_)
    if (not zlim is None):
        ax.set_zlim([0,zlim])
    ax.view_init(elev=60)
    ax.plot_surface(xx[:-1,:-1], yy[:-1,:-1], grid_3d, cmap=cm.RdYlBu)
    if not( fileN is None ):
        plt.savefig(fileN+'.png', format='png', bbox_inches='tight', dpi=300)  
                           
def plot_kdes(city, figsize = (12, 8), zlim = True, fileSave = False, log_scale = False):
    """ Plot KDE's: 3D plot + Contour plot
    KDE's: Activity, Residential, [Total]
    """
    xx, yy = city.grid    
    typesKde = [ 'KDE: Activity', 'KDE: Residential' ]
    fileN = None
    zlim_ = None
    for (typeKde,kde) in zip( typesKde , [city.f_kde_act, city.f_kde_res] ):
        if (fileSave):
            fileN = str (city.city_ref)+'_'+typeKde.replace(' ','_')
        if (zlim): zlim_ = kde.max()
        plot_local(fileN, xx,yy,kde,zlim_, typeKde, figsize=figsize )
        plot_contour_local(fileN + '_Contour', xx,yy,kde, typeKde, log_scale=log_scale, figsize=figsize)

def plot_bubble(city, fig_size = (12,8), grid_step_ = 250, MAX_B = 120):
    """ Bubble plot of LUM
    Bubble's size: Land use intensity value
    Bubble's color: Land use mixity degree
    """
    # LU mix bubble
    city.grid_step = grid_step_
    xx, yy = city.grid
    # Bubble's size related to the importance of both KDE's
    lu_mix_grid_bubble_size = city.f_kde_total.copy() #city.f_lu_mix_grid.copy()

    maxVal = lu_mix_grid_bubble_size.max()
    minOffset = 0
    rows, cols = lu_mix_grid_bubble_size.shape[0] , lu_mix_grid_bubble_size.shape[1]
    for i in range(rows): #Rows
        for j in range(cols): #Cols
            lu_mix_grid_bubble_size[i,j] = ( lu_mix_grid_bubble_size[i,j] / maxVal ) * MAX_B + minOffset


    fig, ax = plt.subplots(figsize=fig_size)
    ax.set_ylim([yy[:-1,:-1].min(), yy[:-1,:-1].max()])
    ax.set_xlim([xx[:-1,:-1].min(), xx[:-1,:-1].max()])
    ax.set_xlabel('Longitude', fontsize=font_size_)
    ax.set_ylabel('Latitude', fontsize=font_size_)
    plt.title('Land use mix', fontsize=font_size_)
    cmap_ = cm.RdYlBu # cool winter autumn
    plt.scatter(xx[:-1,:-1], yy[:-1,:-1], c=city.f_lu_mix_grid, s= lu_mix_grid_bubble_size, alpha=1, cmap=cmap_ , antialiased=True)
    fileN = str (city.city_ref)+'_LUM'
    plt.savefig(fileN+'_Bubble:'+str(MAX_B)+'.png', format='png', bbox_inches='tight', dpi=300)
        
def plot_lu_mix(city, figsize = (12, 8), zlim = True, fileSave = False, log_scale = False, grid_step_=250, MAX_B = 120):
    """ Plot Land use mixity: 3D plot + Contour plot
    """
    xx, yy = city.grid    
    fileN = None
    zlim_ = None
    if (fileSave):
        fileN = str (city.city_ref)+'_LUM'
    LUM = city.f_lu_mix_grid
    if (zlim): zlim_ = LUM.max()
    label = 'Land use mix'
    plot_local(fileN, xx,yy,LUM,zlim_, label, figsize=figsize )
    plot_contour_local(fileN + '_Contour', xx,yy,LUM, label, log_scale=log_scale, figsize=figsize)
    plot_bubble(city, figsize, grid_step_, MAX_B)
    
#TODO
#def plot_full(city, fig_size = (12,8), zlim = True, fileSave = False, log_scale = False, grid_bubble_step_ = 250, MAX_B = 120):
    
                           
#########################

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
    
    
def plot_category_kde( city, fileSave = False): # category_kde, pois, xx, yy, category_label=None):
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
    
def plot_contour_comparison(xx, yy, grid, label, lu_mix_grid_bubble_size, figsize=(12, 8)):
    """ Contour plot comparing Land use mix (grid values) with total (residential+activity) grid (lu_mix_grid_bubble_size)
    """
    w,h = figsize
    plt.figure(figsize=(w,h))
    cp = plt.contourf(xx[:-1,:-1], yy[:-1,:-1], lu_mix_grid_bubble_size, cmap=plt.get_cmap('Greys'), alpha = 1, antialiased=True)
    plt.colorbar(cp)
    plt.show()    
    plt.figure(figsize=(w,h))
    cp = plt.contourf(xx[:-1,:-1], yy[:-1,:-1], grid, cmap=plt.get_cmap('Purples'), alpha = 0.75, antialiased=True)
    plt.colorbar(cp)
    plt.show()
    #plt.title(label)
    #plt.xlabel('Lon')
    #plt.ylabel('Lat')