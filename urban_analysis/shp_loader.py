import pandas as pd

class PoisShpDoesNotExist(Exception):
    pass

def get_extracted_osm_points(shp_file_path, city_ref = None):
    """ Loads the extracted points of interest

    :param str shp_file_path: 
    :returns: pois with the columns 'lon' (longitude), 'lat' (latitude), 'category', 'key', 'value', [, 'population' (population count)]
    :rtype: pandas.DataFrame

    """
    import extract_uses.extract_uses as extract_uses
    from extract_uses import shp_utils
    import os
    # Check if file exists: full_uses.shp
    if (not(os.path.isfile(shp_file_path))):
        extract_uses.process_city(city_ref)
    # Get shapes and attributes
    shapes, df = shp_utils.read_shp_dbf(shp_file_path, decode_bytes = False)

    if (len(shapes) <= 0):
        raise PoisShpDoesNotExist

    # Get longitude and latitude
    lon = [i.points[0][0] for i in shapes]
    lat = [i.points[0][1] for i in shapes]

    return pd.DataFrame({'lon': lon, 'lat': lat, 'category': df.category.values,
                         'key': df.key.values, 'value': df.value.values}, index=df.osm_id.rename('id'))
