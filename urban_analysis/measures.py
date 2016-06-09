import numpy as np

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


def _row_avg_decomposition(xx, yy, f):
    return np.hstack(xx), np.hstack(yy), np.hstack(f), f.mean()


def moran_index(f, xx, yy):
    x_row, y_row, f_row, f_avg = _row_avg_decomposition(xx, yy, f)
    phi = [0, 0, 0]
    for i, (x_i, y_i) in enumerate(zip(x_row, y_row)):
        f_i = f_row[i]
        for j, (x_j, y_j) in enumerate(zip(x_row[i + 1:-1], y_row[i + 1:-1]), start=i + 1):
            # print('(%d,%d) against (%d,%d):' % (x_i, y_i, x_j, y_j))
            w = 1.0 / np.sqrt((x_i - x_j)**2 + (y_i - y_j)**2)
            # print('weight for (%d, %d) : %f' % (i, j, w))
            phi[0] += w
            phi[1] += w * (f_i - f_avg) * (f_row[j] - f_avg)
        phi[2] += (f_i - f_avg) ** 2
        # print('completed row ' + str(i) + ' of ' + str(len(x_row)))
    return (float(len(x_row)) / phi[0]) * (phi[1] / phi[2])


def geary_index(f, xx, yy):
    x_row, y_row, f_row, f_avg = _row_avg_decomposition(xx, yy, f)
    phi = [0, 0, 0]
    for i, (x_i, y_i) in enumerate(zip(x_row, y_row)):
        f_i = f_row[i]
        for j, (x_j, y_j) in enumerate(zip(x_row[i + 1:-1], y_row[i + 1:-1]), start=i + 1):
            # print('(%d,%d) against (%d,%d):' % (x_i, y_i, x_j, y_j))
            w = 1.0 / np.sqrt((x_i - x_j)**2 + (y_i - y_j)**2)
            # print('weight for (%d, %d) : %f' % (i, j, w))
            phi[0] += w
            phi[1] += w * (f_i - f_row[j]) ** 2
        phi[2] += (f_i - f_avg) ** 2
        # print('completed row ' + str(i) + ' of ' + str(len(x_row)))
    return (.5 * (len(x_row) - 1) / phi[0]) * (phi[1] / phi[2])


def shannon_entropy(f):
    f_row = np.hstack(f)
    F = f.sum()
    total = 0
    for f_i in f_row:
        total -= (f_i / F) * np.log(f_i / F)
    return total


def relative_entropy(f):
    return shannon_entropy(f) / np.log(f.shape[0] * f.shape[1])
