import os
from time import sleep

import numpy as np  # 1.7 or higher
import pandas as pd  # 0.10 or higher
from matplotlib.pyplot import *
from shapely.geometry import Polygon
import shapefile

import classif_uses
import parameters
import utils


def getNameSavedFiles(suffix_out_shp):
    """ Get the list of all generated files
    """
    return [parameters.fn_prefix + parameters.fn_residential + parameters.fn_pts + suffix_out_shp, parameters.fn_prefix + parameters.fn_activities + parameters.fn_pts + suffix_out_shp]


def main(points_shapefile, suffix_out_shp):
    """Given the point shapefile, it extracts the residential/activity category they belong to
    Generates an activity point file, and a residential point file
    Uses the reduced fields: osm_id, key, value
    """
    if (not (os.path.isfile(points_shapefile))):
        if (parameters.USE_verbose):
            print('Empty file:', points_shapefile)
        return
    ##########################################################################
    # Read data-set
    # Point shapefile
    point_shapes, df_point = utils.read_shp_dbf(points_shapefile)
    ##########################################################################

    if (parameters.USE_verbose):
        print('extract_point_uses. Loaded Points:', len(df_point))

    ##########################################################################

    # Activities: Points
    sub_activities_shops = df_point.loc[~df_point['shop'].isin([''])]
    sub_activities_amenities = df_point.loc[
        df_point['amenity'].isin(classif_uses.amenities_activities)]
    sub_activities_leisure = df_point.loc[
        df_point['leisure'].isin(classif_uses.leisure_activies)]
    sub_activities_buildings = df_point.loc[
        df_point['building'].isin(classif_uses.building_activities)]
    sub_activities_landuse = df_point.loc[
        df_point['landuse'].isin(classif_uses.landuse_activities)]
    # Residential: Points
    sub_residential_buildings = df_point.loc[
        df_point['building'].isin(classif_uses.building_residential)]
    sub_residential_landuse = df_point.loc[
        df_point['landuse'].isin(classif_uses.landuse_residential)]

    # Filter important columns: osm_id, key, value
    pts_activities_shops = utils.filterColumns('shop', sub_activities_shops)
    pts_activities_amenities = utils.filterColumns(
        'amenity', sub_activities_amenities)
    pts_activities_leisure = utils.filterColumns(
        'leisure', sub_activities_leisure)
    pts_activities_buildings = utils.filterColumns(
        'building', sub_activities_buildings)
    pts_activities_landuse = utils.filterColumns(
        'landuse', sub_activities_landuse)
    pts_residential_buildings = utils.filterColumns(
        'building', sub_residential_buildings)
    pts_residential_landuse = utils.filterColumns(
        'landuse', sub_residential_landuse)

    ##########################################################################
    # Concatenate keeping indices
    activities_pts = pd.concat([pts_activities_shops, pts_activities_amenities,
                                pts_activities_leisure, pts_activities_buildings, pts_activities_landuse])
    residential_pts = pd.concat(
        [pts_residential_buildings, pts_residential_landuse])

    if (parameters.USE_dropDuplicates):
        # Remove duplicates and order by index
        activities_pts = activities_pts.groupby(activities_pts.index).first()
        residential_pts = residential_pts.groupby(
            residential_pts.index).first()
    ##########################################################################
    # Save to file
    utils.toFile(parameters.fn_prefix + parameters.fn_residential + parameters.fn_pts +
                 suffix_out_shp, point_shapes, residential_pts, shapefile.POINT, utils.reducedFields)
    utils.toFile(parameters.fn_prefix + parameters.fn_activities + parameters.fn_pts +
                 suffix_out_shp, point_shapes, activities_pts, shapefile.POINT, utils.reducedFields)
    ##########################################################################

    if (parameters.USE_verbose):
        print('Activites points', len(activities_pts))
        print('Residential points', len(residential_pts))

####################################################
