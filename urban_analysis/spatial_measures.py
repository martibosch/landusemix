import numpy as np

# import utils

# def land_use_mix(categories_kde_dict):
#     phi = 0
#     categories_list = categories_kde_dict.items()
#     # let: n be the total number of categories; l be the total number of grid (lattice) points
#     n = len(categories_list[0][0])
#     l = len(categories_list[0][1]) # TODO: more `correct` GRIDSIZE handling
#     # [[phi += np.sum(vi - vj) for j, (kj, vj) in enumerate(categories_list[i:])] for i, (ki, vi) in enumerate(categories_list)]

#     for i, (ki, vi) in enumerate(categories_list):
#         for j, (kj, vj) in enumerate(categories_list[i:]):
# phi += np.sum(vi.values - vj.values) # here i would divide it by l, but
# computationally i can do that at the end

#     return phi / (l * l) # (l * l * n * (n-1) * .5)

# PRE-PROCESSING METHODS

# def _row_avg_decomposition(xx, yy, f):
#     return np.hstack(xx), np.hstack(yy), np.hstack(f), f.mean()


def grid_cell_kde_average(f):
    """ Determines for each cell the trapezoid-based average out of the kde values of the cell's vertices

    :param numpy.ndarray f: 2-dimensional
    :returns: flat array
    :rtype: numpy.ndarray 

    """
    ff = []
    for i in range(len(f) - 1):
        f_row1 = f[i]
        f_row2 = f[i + 1]
        for j in range(len(f[0]) - 1):
            ff.append((f_row1[j] + f_row1[j + 1] +
                       f_row2[j] + f_row2[j + 1]) / 4)
    return np.array(ff)


def grid_cell_pois_count(pois, xx, yy):
    """ Determines for each cell the number of pois

    :param pandas.DataFrame pois: 
    :param numpy.ndarray xx: 2-dimensional array first componenent of a numpy.meshgrid() call
    :param numpy.ndarray yy: 2-dimensional array second componenent of a numpy.meshgrid() call
    :returns: flat array
    :rtype: numpy.ndarray

    """
    ff = []
    n_rows, n_cols = xx.shape
    for i in range(n_rows - 1):
        xi = xx[i]
        yil = yy[i]
        yih = yy[i + 1]
        for j in range(n_cols - 1):
            ff.append(len(pois[(pois['lon'] > xi[j]) & (pois['lon'] <= xi[j + 1]) & (
                pois['lat'] > yil[j]) & (pois['lat'] <= yih[j])]))
    return np.array(ff)


# INDICATOR CALCULATION

def moran_index(f, xx, yy):
    """ 

    :param numpy.ndarray f: flat array
    :param numpy.ndarray xx: flat array
    :param numpy.ndarray yy: flat array
    :returns: 
    :rtype: float

    """
    # x_row, y_row, f_row, f_avg = _row_avg_decomposition(xx, yy, f)
    f_avg = f.mean()
    phi = [0, 0, 0]
    for i, (x_i, y_i) in enumerate(zip(xx, yy)):
        f_i = f[i]
        for j, (x_j, y_j) in enumerate(zip(xx[i + 1:-1], yy[i + 1:-1]), start=i + 1):
            # print('(%d,%d) against (%d,%d):' % (x_i, y_i, x_j, y_j))
            w = 1.0 / np.sqrt((x_i - x_j)**2 + (y_i - y_j)**2)
            # print('weight for (%d, %d) : %f' % (i, j, w))
            phi[0] += w
            phi[1] += w * (f_i - f_avg) * (f[j] - f_avg)
        phi[2] += (f_i - f_avg) ** 2
        # print('completed row ' + str(i) + ' of ' + str(len(x_row)))
    return (float(len(xx)) / phi[0]) * (phi[1] / phi[2])


def geary_index(f, xx, yy):
    """ 

    :param numpy.ndarray f: flat array
    :param numpy.ndarray xx: flat array 
    :param numpy.ndarray yy: flat array
    :returns: 
    :rtype: float

    """
    # x_row, y_row, f_row, f_avg = _row_avg_decomposition(xx, yy, f)
    f_avg = f.mean()
    phi = [0, 0, 0]
    for i, (x_i, y_i) in enumerate(zip(xx, yy)):
        f_i = f[i]
        for j, (x_j, y_j) in enumerate(zip(xx[i + 1:-1], yy[i + 1:-1]), start=i + 1):
            # print('(%d,%d) against (%d,%d):' % (x_i, y_i, x_j, y_j))
            w = 1.0 / np.sqrt((x_i - x_j)**2 + (y_i - y_j)**2)
            # print('weight for (%d, %d) : %f' % (i, j, w))
            phi[0] += w
            phi[1] += w * (f_i - f[j]) ** 2
        phi[2] += (f_i - f_avg) ** 2
        # print('completed row ' + str(i) + ' of ' + str(len(x_row)))
    return (.5 * (len(xx) - 1) / phi[0]) * (phi[1] / phi[2])


def shannon_entropy(f):
    """

    :param numpy.ndarray f: flat array
    :returns: 
    :rtype: float

    """
    F = f.sum()
    total = 0
    for f_i in f:
        total -= (f_i / F) * np.log(f_i / F)
    return total


def relative_entropy(f):
    """

    :param numpy.ndarray f: flat array
    :returns: 
    :rtype: float

    """
    return shannon_entropy(f) / np.log(len(f))


# def calculate_measure(measure_key, measure_pre, **kwargs):

#     try:
#         if measure_pre == 'kde':
#             ff = grid_cell_kde_average(kwargs['f'])
#         if measure_pre == 'count':
#             ff = grid_cell_pois_count(
#                 kwargs['pois'], kwargs['xx'], kwargs['yy'])
#     except KeyError:
#         raise Exception, 'Wrong arguments'

#     MEASURE_METHOD_MAPPING = {
#         'geary': geary_index,
#         'moran': moran_index,
#         'entropy': relative_entropy
#     }

#     return MEASURE_METHOD_MAPPING[measure_key](ff)

    # def pois_grid_cell_count(pois, xx, yy, step=None):
    #     # assume regular squared grid
    #     if not step:
    #         step = xx[0][1] - xx[0][0]
    #     ff = []
    #     n_rows, n_cols = xx.shape
    #     for i in range(n_rows - 1):
    #         xij = xx[0][0]
    #         yij = yy[i][0]
    #         for j in range(n_cols - 1):
    #             xl = xij
    #             xij += step
    #             xh = xij
    #             yl = yij
    #             yij += step
    #             yh = yij
    #             ff.append(len(pois[(pois['lon'] > xl) & (pois['lon'] <= xh) & (
    #                 pois['lat'] > yl) & (pois['lat'] <= yh)]))
    #     print(xij, yij)
    #     return np.array(ff)
