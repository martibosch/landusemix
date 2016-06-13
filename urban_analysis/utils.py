import numpy as np

def _create_grid_axis(_min, _max, step, dtype=np.float32):
    return np.arange(_min, _max, step, dtype=dtype)

def grid_from_bbox(bbox, grid_step):
    return np.meshgrid(_create_grid_axis(bbox[1], bbox[3], grid_step), _create_grid_axis(bbox[0], bbox[2], grid_step))
