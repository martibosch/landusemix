import pandas as pd
from shapefile import Reader, ShapefileException


class PoisShpDoesNotExist(Exception):
    pass


def read_shp_dbf(file_shape):
    """ Read a shapefile, returning separately shapes and attributes
    """
    try:
        reader_shp = Reader(file_shape)
    except ShapefileException:
        raise PoisShpDoesNotExist

    shapes = reader_shp.shapes()
    # Columns correspond to all the elements excepts for the first one: A deletion flag
    columns = [list[0]
               for list in reader_shp.fields[1:len(reader_shp.fields)]]
    # Conver to data frame and decode
    return shapes, pd.DataFrame(reader_shp.records(), columns=columns)


def get_extracted_osm_points(shp_file_path):
    """ Loads the extracted points of interest

    :param str shp_file_path: 
    :returns: pois with the columns 'lon' (longitude), 'lat' (latitude), 'category', 'key', 'value', [, 'population' (population count)]
    :rtype: pandas.DataFrame

    """
    # TODO: assert that shp_file exists
    shapes, df = read_shp_dbf(shp_file_path)

    # Get longitude and latitude
    lon = [i.points[0][0] for i in shapes]
    lat = [i.points[0][1] for i in shapes]

    return pd.DataFrame({'lon': lon, 'lat': lat, 'category': df.category.values,
                         'key': df.key.values, 'value': df.value.values}, index=df.osm_id.rename('id'))
