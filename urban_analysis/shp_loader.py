import pandas as pd
from shapefile import Reader, ShapefileException


class PoisShpDoesNotExist(Exception):
    pass


def byte_to_str(x, threshold_length=None):
    """ To use only in Python2: decode the bytes to utf-8, and strip if it is too long
    """
    if (threshold_length != None):
        if (threshold_length < 25):
            print('Be careful, threshold length smaller than 50!')
            quit()
    if isinstance(x, bytes):
        # Decode to UTF8, then strip to remove white blank spaces at
        # begining/end
        try:
            if (threshold_length == None):
                return x.decode('UTF-8').strip()
            else:
                return x[0:threshold_length].decode('UTF-8').strip()
            # If UnicodeDecodeError because of bytes length, shrink to avoid
            # error
        except UnicodeDecodeError:  # Recursive shrinking the length of the object
            if (threshold_length == None):
                return byte_to_str(x, len(x) - 1)
            else:
                return byte_to_str(x, threshold_length - 1)
    else:
        return x


def read_shp_dbf(file_shape):
    """ Read a shapefile, returning separately shapes and attributes
    """
    try:
        reader_shp = Reader(file_shape)
    except ShapefileException:
        raise PoisShpDoesNotExist

    shapes = reader_shp.shapes()
    # Columns correspond to all the elements excepts for the first one: A
    # deletion flag
    columns = [list[0]
               for list in reader_shp.fields[1:len(reader_shp.fields)]]
    # Conver to data frame and decode
    return shapes, pd.DataFrame(
        reader_shp.records(), columns=columns).applymap(byte_to_str)


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
