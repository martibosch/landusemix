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

def bounding_box_centroid(bbox):
    """ Returns the centroid of the bounding box
    """
    return ( (bbox[0]+bbox[2])/2 , (bbox[1]+bbox[3])/2 )

def lat_lon_shift(bbox, desired_meters):
    """ Returns the latitude and longitude values which computes a distance of desired_meters from the centroid of input bounding box
    """    
    latCentroid, lonCentroid = bounding_box_centroid(bbox)
    # Starting values
    lat_ = latCentroid
    lon_ = lonCentroid
    # Increasing step
    delta = 0.000001
    
    while ( great_circle_dist(latCentroid,lonCentroid,lat_,lonCentroid) < desired_meters ):
        lat_ = lat_ + delta
    while ( great_circle_dist(latCentroid,lonCentroid,latCentroid,lon_) < desired_meters ):
        lon_ = lon_ + delta
     
    # Distance in meters:
    #print(  great_circle_dist(latCentroid,lonCentroid,lat_,lonCentroid) )
    #print(  great_circle_dist(latCentroid,lonCentroid,latCentroid,lon_) )
    
    return (abs(lat_-latCentroid), abs(lon_-lonCentroid))

def _create_grid_axis(_min, _max, step, dtype=np.float32):
    return np.arange(_min, _max, step, dtype=dtype)


def grid_from_bbox(bbox, grid_step):
    # Grid step defines the step in meters: Simplify using latitude longitude projection using great circle dist
    lat_lon_step = lat_lon_shift(bbox, grid_step)
    return np.meshgrid(_create_grid_axis(bbox[1], bbox[3], lat_lon_step[0]), _create_grid_axis(bbox[0], bbox[2], lat_lon_step[1]))

def outside_bbox(pois,bbox):
    print(pois)
    # Boolean defining whether the point of interest lies within the bounding box
    lat1, lon1, lat2, lon2 = bbox
    if ( pois.lat < lat1 or pois.lat > lat2 or pois.lon < lon1 or pois.lon > lon2):
        return True
    else:
        return False



