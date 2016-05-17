import glob

import pandas as pd

import settings

# DICTIONARY KEYS
CITY_KEY = "city"
SOURCE_KEY = "source"
YEARS_KEY = "years"

# FLAGS
GPCI_FLAG = "gpci"
NUMBEO_FLAG = "numbeo"

# KINDS
CITIES_IN_ALL_YEARS = "and"
ALL_CITIES = "or"


def _get_path(source, file_name, extension=None):
    if source == GPCI_FLAG:
        data_directory = settings.GPCI_DATA_DIRECTORY
        if not extension:
            extension = settings.GPCI_DATA_FILE_EXTENSION
    elif source == NUMBEO_FLAG:
        data_directory = settings.NUMBEO_DATA_DIRECTORY
        if not extension:
            extension = settings.NUMBEO_DATA_FILE_EXTENSION
    return data_directory + '/' + file_name + '.' + extension


def get_file_list(source):
    return glob.glob(_get_path(source, '*'))


def save_data_frame(source, kind, df):
    df.to_pickle(_get_path(source, settings.DATAFRAME_FILE_NAME + '_' + kind,
                           settings.PICKLE_FILE_EXTENSION))


def load_data_frame(source, kind):
    return pd.read_pickle(_get_path(source, settings.DATAFRAME_FILE_NAME + '_' + kind, settings.PICKLE_FILE_EXTENSION))


def get_city_list():
    gpci_df = load_data_frame(GPCI_FLAG)
    return list(map(gpci_df.label.__getitem__, gpci_df.index))


# import json

# def _get_city_file_name(city):
#     return city.lower().replace(' ', '_') + '.' + DATA_FILE_EXTENSION

# def _get_city_file_path(city, source):
#     if source == GPCI_VALUE:
#         data_directory_path = GPCI_DATA_DIRECTORY
#     else:
#         data_directory_path = NUMBEO_DATA_DIRECTORY
#     return data_directory_path + "/" + _get_city_file_name(city)

# def load_city_dict(city, source):
#     infile_path = _get_city_file_path(city, source)
#     try:
#         infile = open(infile_path, 'r')
#         city_dict = json.load(infile)
#         inflie.close()
#         return city_dict
#     except (OSError, IOError, ValueError) as error:
#         if isinstance(error, ValueError):
#             print("Problem parsing the data. Make sure that " + infile_path + " is a well-formed " + DATA_FILE_EXTENSION + " file.")
#         else:
#             print("The file " + infile_path + " does not exist")


# def save_city_file(city_dict):
#     outfile = open(_get_city_file_path(city_dict[CITY_KEY], city_dict[SOURCE_KEY]), 'w')
#     json.dump(city_dict, outfile)
#     outfile.close()

# def save_city_list_file(city_list):
#     city_list_file = open(numbeo.CITY_LIST_FILE_PATH, 'w')
#     json.dump(city_list, city_list_file)
#     city_list_file.close()
