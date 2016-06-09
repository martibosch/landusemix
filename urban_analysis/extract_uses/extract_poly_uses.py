#%matplotlib inline
# import pysal as ps  # 1.5 or higher
import numpy as np  # 1.7 or higher
import pandas as pd  # 0.10 or higher
from matplotlib.pyplot import *
from time import sleep
from shapely.geometry import Polygon
import shapefile

import utils
import classif_uses
import parameters


def get_name_saved_files(suffix_out_shp):
    """ Get the list of all generated files
    """
    return [parameters.fn_prefix + parameters.fn_residential + parameters.fn_poly + suffix_out_shp, parameters.fn_prefix + parameters.fn_activities + parameters.fn_poly + suffix_out_shp]


def main(polygon_shapefile, suffix_out_shp):
    """Given the polygon shapefile, it extracts the residential/activity category they belong to
    Generates an activity point file, and a residential point file
    Uses the reduced fields: osm_id, key, value
    """
    ##########################################################################
    # Read data-set
    # Polygon shapefile
    polygon_shapes, df_polygon = utils.read_shp_dbf(polygon_shapefile)
    ##########################################################################

    if (parameters.USE_verbose):
        print('extract_poly_uses. Loaded Points:', len(df_polygon))

    ##########################################################################

    # Activities: Polygon
    sub_activities_shops = df_polygon.loc[~df_polygon['shop'].isin([''])]
    sub_activities_amenities = df_polygon.loc[df_polygon[
        'amenity'].isin(classif_uses.amenities_activities)]
    sub_activities_leisure = df_polygon.loc[df_polygon[
        'leisure'].isin(classif_uses.leisure_activies)]
    sub_activities_buildings = df_polygon.loc[df_polygon[
        'building'].isin(classif_uses.building_activities)]
    # Filtering: If landuse=residential/activity, check that building!=NULL
    sub_activities_landuse_building = df_polygon.loc[(df_polygon['landuse'].isin(
        classif_uses.landuse_activities)) & (~df_polygon['building'].isin(['']))]

    # Residential: Polygon
    sub_residential_buildings = df_polygon.loc[df_polygon[
        'building'].isin(classif_uses.building_residential)]
    # Filtering: If landuse=residential/activity, check that building!=NULL
    sub_residential_landuse_building = df_polygon.loc[(df_polygon['landuse'].isin(
        classif_uses.landuse_residential)) & (~df_polygon['building'].isin(['']))]

    # Filter important columns: osm_id, key, value
    poly_activities_shops = utils.filter_columns('shop', sub_activities_shops)
    poly_activities_amenities = utils.filter_columns(
        'amenity', sub_activities_amenities)
    poly_activities_leisure = utils.filter_columns(
        'leisure', sub_activities_leisure)
    poly_activities_buildings = utils.filter_columns(
        'building', sub_activities_buildings)
    poly_activities_landuse_building = utils.filter_columns(
        'landuse', sub_activities_landuse_building)
    poly_residential_buildings = utils.filter_columns(
        'building', sub_residential_buildings)
    poly_residential_landuse_building = utils.filter_columns(
        'landuse', sub_residential_landuse_building)

    ##########################################################################
    # Concatenate keeping indices
    activities_poly = pd.concat([poly_activities_shops, poly_activities_amenities,
                                 poly_activities_leisure, poly_activities_buildings, poly_activities_landuse_building])
    residential_poly = pd.concat(
        [poly_residential_buildings, poly_residential_landuse_building])

    if (parameters.USE_dropDuplicates):
        # Remove duplicates and order by index
        activities_poly = activities_poly.groupby(
            activities_poly.index).first()
        residential_poly = residential_poly.groupby(
            residential_poly.index).first()
    ##########################################################################
    # Save to file
    utils.to_file(parameters.fn_prefix + parameters.fn_residential + parameters.fn_poly +
                  suffix_out_shp, polygon_shapes, residential_poly, shapefile.POLYGON, utils.reduced_ields)
    utils.to_file(parameters.fn_prefix + parameters.fn_activities + parameters.fn_poly +
                  suffix_out_shp, polygon_shapes, activities_poly, shapefile.POLYGON, utils.reduced_fields)
    ##########################################################################

    if (parameters.USE_verbose):
        print('Activites polygons', len(activities_poly))
        print('Residential polygons', len(residential_poly))
