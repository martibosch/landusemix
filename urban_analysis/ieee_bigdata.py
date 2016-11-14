import matplotlib.pyplot as plt
import matplotlib.cm as cm
from matplotlib import ticker
import seaborn as sns

from analysis import Analysis

import plots
    
def processCompleteCity(city_ref, grid_step, alphas, bbox = None, fig_size = None, bubble_plot_step = 250):
    import lu_mix
    # Instance of analysis for particular city
    city = Analysis(city_ref, pois_shp_path = "cities/"+city_ref+"/full_uses.shp", grid_step=grid_step)

    # Visualize some points
    city.pois.head()
    
    if (not (bbox is None)):
        city.reduce_bbox(bbox)
    if (fig_size is None):
        fig_size = (12,8)

    ''' POIS
    '''
    # POIS count
    print('POIS: Activities', len ( city.pois[city.pois.category == 'activity'] ) )
    print('POIS: Residential', len ( city.pois[city.pois.category == 'residential'] ) )
    print('POIS: Total', len ( city.pois ) )
    
    # Scatter plot
    plots.pois_scatter(city,['activity','residential'],[0.1,0.1],['b','g'],0.01, fig_size)
    
    ''' KDE
    '''
    log_scale = False
    #plots.plot_kdes(city, figsize=fig_size, zlim = True, fileSave = True, log_scale = False)
    plots.plot_kdes(city, figsize=fig_size, zlim = True, fileSave = True, log_scale = False)

    ''' LU MIX
    '''
    city._phi_metric = 'phi_entropy'
    city._f_lu_mix_grid = None
    
    plots.plot_lu_mix(city, figsize = (12, 8), zlim = True, fileSave = True, log_scale = False, MAX_B = bubble_plot_step, grid_step_ = bubble_plot_step)