import math
import numpy as np


def pitagoras_aprox_dist(lat1, lon1, lat2, lon2):
    return ((lat1 - lat2)**2 + (lon1 - lon2)**2)**.5


def great_circle_dist(lat1, lon1, lat2, lon2):
    """ Get the distance (in meters) between two lat/lon points via the Haversine formula.

    :param lat1: float in degrees
    :param lon1: float in degrees
    :param lat2: float in degrees
    :param lon2: float in degrees
    :returns: distance in meters
    :rtype: float

    """
    radius = 6372795  # meters

    lat1 = math.radians(lat1)
    lon1 = math.radians(lon1)
    lat2 = math.radians(lat2)
    lon2 = math.radians(lon2)

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    # formula from:
    # http://en.wikipedia.org/wiki/Haversine_formula#The_haversine_formula
    a = math.pow(math.sin(dlat / 2), 2)
    b = math.cos(lat1) * math.cos(lat2) * math.pow(math.sin(dlon / 2), 2)
    d = 2 * radius * math.asin(math.sqrt(a + b))

    return d


def _create_grid_axis(_min, _max, step, dtype=np.float32):
    return np.arange(_min, _max, step, dtype=dtype)


def grid_from_bbox(bbox, grid_step):
    return np.meshgrid(_create_grid_axis(bbox[1], bbox[3], grid_step), _create_grid_axis(bbox[0], bbox[2], grid_step))
