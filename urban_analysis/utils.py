import numpy as np


def grid_from_bbox(bbox, grid_step):
    return np.meshgrid(np.arange(bbox[1], bbox[3], grid_step), np.arange(bbox[0], bbox[2], grid_step))
