import parameters
import pandas as pd
import numpy as np
import shapefile
import shutil
import shapely
from shapely.geometry import Point

import classif_uses

########################################################################
""" OSM default fields for points and polygons (osm2pgsql)
"""
point_fields = [['osm_id', 'N', 19, 0], ['access', 'C', 11, 0], ['aerialway', 'C', 7, 0], ['aeroway', 'C', 7, 0], ['amenity', 'C', 18, 0], ['area', 'C', 2, 0], ['barrier', 'C', 24, 0], ['bicycle', 'C', 10, 0], ['brand', 'C', 17, 0], ['bridge', 'C', 32, 0], ['boundary', 'C', 32, 0], ['building', 'C', 11, 0], ['capital', 'C', 1, 0], ['covered', 'C', 3, 0], ['culvert', 'C', 32, 0], ['cutting', 'C', 32, 0], ['disused', 'C', 3, 0], ['ele', 'C', 8, 0], ['embankment', 'C', 32, 0], ['foot', 'C', 10, 0], ['harbour', 'C', 32, 0], ['highway', 'C', 26, 0], ['historic', 'C', 19, 0], ['horse', 'C', 3, 0], ['junction', 'C', 3, 0], ['landuse', 'C', 17, 0], ['layer', 'C', 10, 0], ['leisure', 'C', 16, 0], ['lock', 'C', 32, 0], [
    'man_made', 'C', 18, 0], ['military', 'C', 18, 0], ['motorcar', 'C', 7, 0], ['name', 'C', 99, 0], ['natural', 'C', 13, 0], ['oneway', 'C', 32, 0], ['operator', 'C', 47, 0], ['poi', 'C', 32, 0], ['population', 'C', 6, 0], ['power', 'C', 26, 0], ['place', 'C', 17, 0], ['railway', 'C', 14, 0], ['ref', 'C', 35, 0], ['religion', 'C', 9, 0], ['route', 'C', 32, 0], ['service', 'C', 13, 0], ['shop', 'C', 21, 0], ['sport', 'C', 21, 0], ['surface', 'C', 8, 0], ['toll', 'C', 32, 0], ['tourism', 'C', 11, 0], ['tower:type', 'C', 13, 0], ['tunnel', 'C', 32, 0], ['water', 'C', 32, 0], ['waterway', 'C', 9, 0], ['wetland', 'C', 32, 0], ['width', 'C', 32, 0], ['wood', 'C', 32, 0], ['z_order', 'N', 11, 0], ['tags', 'C', 254, 0]]

poly_fields = [['osm_id', 'N', 19, 0], ['access', 'C', 11, 0], ['aerialway', 'C', 7, 0], ['aeroway', 'C', 9, 0], ['amenity', 'C', 18, 0], ['area', 'C', 3, 0], ['barrier', 'C', 10, 0], ['bicycle', 'C', 10, 0], ['brand', 'C', 21, 0], ['bridge', 'C', 3, 0], ['boundary', 'C', 14, 0], ['building', 'C', 17, 0], ['covered', 'C', 3, 0], ['culvert', 'C', 32, 0], ['cutting', 'C', 32, 0], ['disused', 'C', 3, 0], ['embankment', 'C', 32, 0], ['foot', 'C', 10, 0], ['harbour', 'C', 32, 0], ['highway', 'C', 13, 0], ['historic', 'C', 14, 0], ['horse', 'C', 2, 0], ['junction', 'C', 32, 0], ['landuse', 'C', 23, 0], ['layer', 'C', 2, 0], ['leisure', 'C', 17, 0], ['lock', 'C', 32, 0], ['man_made', 'C', 17, 0], ['military', 'C', 8, 0], [
    'motorcar', 'C', 32, 0], ['name', 'C', 128, 0], ['natural', 'C', 9, 0], ['oneway', 'C', 32, 0], ['operator', 'C', 85, 0], ['population', 'C', 6, 0], ['power', 'C', 26, 0], ['place', 'C', 13, 0], ['railway', 'C', 8, 0], ['ref', 'C', 12, 0], ['religion', 'C', 10, 0], ['route', 'C', 32, 0], ['service', 'C', 36, 0], ['shop', 'C', 19, 0], ['sport', 'C', 83, 0], ['surface', 'C', 15, 0], ['toll', 'C', 32, 0], ['tourism', 'C', 12, 0], ['tower:type', 'C', 13, 0], ['tracktype', 'C', 32, 0], ['tunnel', 'C', 32, 0], ['water', 'C', 5, 0], ['waterway', 'C', 9, 0], ['wetland', 'C', 5, 0], ['width', 'C', 32, 0], ['wood', 'C', 10, 0], ['z_order', 'N', 11, 0], ['way_area', 'N', 32, 10], ['tags', 'C', 254, 0]]

""" Reduced fields: osm_id, value, key 
"""
reduced_fiels = [['osm_id', 'N', 19, 0], [
    'value', 'C', 32, 0], ['key', 'C', 32, 0]]


def filter_columns(working_key, sub_selection):
    """ Filter the columns and return the rows with the reduced fields format
    Use as input the working key, which determines the contained value
    """
    filtered_columns_selection = sub_selection[['osm_id', working_key]]
    filtered_columns_selection = filtered_columns_selection.rename(
        columns={working_key: 'value'})
    filtered_columns_selection['key'] = np.repeat(
        working_key, len(filtered_columns_selection))
    return filtered_columns_selection

########################################################################
# Compatibility with encoding/decoding


def unicode_to_str(x):
    """ To use only in Python2: encode the unicode input to utf-8, and strip if it is too long
    """
    if isinstance(x, unicode):
        # Decode to UTF8, then strip to remove white blank spaces at
        # begining/end
        try:
            return x.encode('UTF-8')
        # If UnicodeDecodeError because of bytes length, shrink to avoid error
        except UnicodeDecodeError:
            return x[0:253].encode('UTF-8')
    else:
        return x


def byte_to_str(x):
    """ To use only in Python2: decode the bytes to utf-8, and strip if it is too long
    """
    if isinstance(x, bytes):
        # Decode to UTF8, then strip to remove white blank spaces at
        # begining/end
        try:
            return x.decode('UTF-8').strip()
        # If UnicodeDecodeError because of bytes length, shrink to avoid error
        except UnicodeDecodeError:
            return x[0:200].decode('UTF-8').strip()
    else:
        return x

########################################################################
# File I/O related to shapefile


def to_file(file_name, shapes, shape_attrs, shapefile_type, fields=None):
    """ Store the shapes with its attributes to a .shp file
    shapefile_type indicates whether points or polygons are going to be stored
    fields denote the columns which are going to be stored
    """
    if (shape_attrs.empty):
        if (parameters.USE_verbose):
            print('Empty shape for file:', file_name)
        return

    # shapefile_type : shapefile.POINT or shapefile.POLYGON
    w = shapefile.Writer(shapefile_type)
    w.autoBalance = 1
    # Indicate the fields to be filled
    if (fields == None):
        if (shapefile_type == shapefile.POINT):
            w.fields = point_fields
        elif (shapefile_type == shapefile.POLYGON):
            w.fields = poly_fields
        else:
            print('Error with field type')
            return
    else:
        w.fields = fields

    # Input can be in form of shapely Point or shapefile Geometry
    if (shapefile_type == shapefile.POINT):
        # Check the nature of the input
        if (shapely.geometry.point.Point == type(shapes[0])):
            is_shapely_point = True
        else:
            is_shapely_point = False

    for index, row in shape_attrs.iterrows():
        RowLEncoded = map(UnicodeToStr, row.tolist())

        if (shapefile_type == shapefile.POINT):
            if (is_shapely_point):
                Pt = [shapes[index].x, shapes[index].y]
            else:
                Pt = shapes[index].points[0]
            w.point(Pt[0], Pt[1])
        else:
            Poly = shapes[index].points
            w.poly([Poly])
        w.record(*(RowLEncoded))

    w.save(file_name)
    import os.path
    if (not(os.path.isfile(file_name + '.prj'))):
        try:
            shutil.copy(parameters.fn_prefix +
                        'sample.prj', file_name + '.prj')
        except ValueError:
            pass
#####################

################################################
# Read data-set

# Read dataset: Shapes and attributes


def read_shp_dbf(file_shape):
    """ Read a shapefile, returning separately shapes and attributes
    """
    reader_shp = shapefile.Reader(file_shape)
    shapes = reader_shp.shapes()
    # Columns correspond to all the elements excepts for the first one: A
    # deletion flag
    columns = [list[0] for list in reader_shp.fields[1:len(reader_shp.fields)]]
    # Conver to data frame and decode
    df = pd.DataFrame(reader_shp.records(),
                      columns=columns).applymap(ByteToStr)
    return shapes, df

# Read dataset: Only shapes


def read_shp(file_shape):
    """ Read a shapefile, returning only the shapes
    """
    reader_shp = shapefile.Reader(file_shape)
    shapes = reader_shp.shapes()
    return shapes
################################################


def get_bounding_box(point_shapefile, polygon_shapefile=None, line_shapefile=None):
    """ Compute bounding box for the input given files
    return: bbox -> latitude1 , longitude1 , latitude2, longitude2
    """
    # Get the bounding box for the given shapefiles
    bbox_pts = shapefile.Reader(point_shapefile).bbox
    if (polygon_shapefile != None):
        bbox_poly = shapefile.Reader(polygon_shapefile).bbox
    else:
        bbox_poly = bbox_pts
    if (line_shapefile != None):
        bbox_line = shapefile.Reader(line_shapefile).bbox
    else:
        bbox_line = bbox_pts

    # Get the bounding box for all shapefile: Min of xmin,ymin and Max of xmax,ymax
    #bbox = [ min(bbox_poly[0],bbox_pts[0],bbox_line[0]) , min(bbox_poly[1],bbox_pts[1],bbox_line[1]) , max(bbox_poly[2],bbox_pts[2],bbox_line[2]) , max(bbox_poly[3],bbox_pts[3],bbox_line[3]) ]
    # Format: latitude1 , longitude1 , latitude2, longitude2
    bbox = [min(bbox_poly[1], bbox_pts[1], bbox_line[1]), min(bbox_poly[0], bbox_pts[0], bbox_line[
        0]), max(bbox_poly[3], bbox_pts[3], bbox_line[3]), max(bbox_poly[2], bbox_pts[2], bbox_line[2])]

    if (parameters.USE_verbose):
        print('Bounding box:', bbox)
    return bbox


def perform_key_category_mapping(fn_activities):
    """ Given the file containing all point activities: Map {key,value} to the final key category classification
    """
    # Read data-set
    shapes, df_attrs = read_shp_dbf(fn_activities)
    df_attrs = classif_uses.key_category_mapping(df_attrs)
    to_file(fn_activities, shapes, df_attrs, shapefile.POINT, reduced_fiels)


def get_extracted_osm_points(shp_file_dict):
    """ Loads the extracted points of interest

    :param shp_file: 
    :returns: pois with the columns 'lon' (longitude), 'lat' (latitude), 'category', 'key', 'value', [, 'population' (population count)]
    :rtype: pandas.DataFrame

    """
    df_list = []
    for category, shp_file in shp_file_dict.items():
        # TODO: assert that shp_file exists
        shapes, df = read_shp_dbf(shp_file)

        # Get longitude and latitude
        lon = [i.points[0][0] for i in shapes]
        lat = [i.points[0][1] for i in shapes]

        # Convert to pandas DF {value,lon,lat,key} with indices=osm_id
        df_list = pd.DataFrame({'lon': lon, 'lat': lat, 'category': category,
                                'key': df.key.values, 'value': df.value.values}, index=df.osm_id.rename('id'))
    return pd.concat(df_list)

################################################
