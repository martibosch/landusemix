import abc
import functools
import glob

import numpy as np
import pandas as pd

import utils

# CONSTANTS
KEYWORDS_TO_REMOVE = ["of", "for", "per", "at", "and", "with", "on", "in"]
INDICATOR_IGNORED_KEYS = set([11, 46, 49, 54, 62])

INDICATOR_MAPPING = {}
INDICATOR_MAPPING[
    'easiness securing human resource'] = 'ease securing human resources'
INDICATOR_MAPPING['density metro stations'] = 'density railway stations'
INDICATOR_MAPPING['healthy life expectancy rate'] = 'life expectancy age 60'
INDICATOR_MAPPING[
    'level satisfaction dining'] = 'attractiveness dining options'
INDICATOR_MAPPING[
    'level satisfaction shopping'] = 'attractiveness shopping options'
INDICATOR_MAPPING[
    'number cities international direct flights'] = 'number cities direct international flights'
INDICATOR_MAPPING['number employees'] = 'total employees'
INDICATOR_MAPPING['number foreign population'] = 'number foreign residents'
INDICATOR_MAPPING[
    'number guest rooms luxury hotels'] = 'number luxury hotel guest rooms'
INDICATOR_MAPPING[
    'number holdings international conventions'] = 'number international conferences held'
INDICATOR_MAPPING[
    'number holdings world-class largest cultural events'] = 'number large world-class cultural events held'
INDICATOR_MAPPING['number murders resident'] = 'number murders population'
INDICATOR_MAPPING[
    'number passengers international flights'] = 'number arriving/departing passengers international flights'
INDICATOR_MAPPING[
    'number travelers international flights'] = 'number arriving/departing passengers international flights'
INDICATOR_MAPPING[
    'number world heritage (within 100km area)'] = 'number world heritage sites (within 100km area)'
INDICATOR_MAPPING[
    'opportunities interactive activities between researchers'] = 'interaction opportunities between researchers'
INDICATOR_MAPPING[
    'percentage renewable energy'] = 'percentage renewable energy used'
INDICATOR_MAPPING['unemployment rate'] = 'total unemployment rate'


# CLASSES
class SetItem(metaclass=abc.ABCMeta):

    def __init__(self, label, year, key):
        self.label = label
        self.keys = {}
        self.keys[year] = key

    def __hash__(self):
        return hash(self.label)

    @abc.abstractmethod
    def on_intersection(self, other):
        """actions to exectue when 'merging' two items from a set"""

    def __repr__(self):
        return str(self.label)


class Indicator(SetItem):

    def __init__(self, label, year, key, values):
        super().__init__(self.preprocess_indicator(label), year, key)
        self.values = {}
        # np.fromiter((float(value) if is_float(value) else np.nan for value in
        # values), np.float)
        self.values[year] = values

    @staticmethod
    def preprocess_indicator(indicator_label):
        """Given the indicator label read from the file:
        1. lowercase and remove certain frequent keywords and unwanted chars
        2. homogenize it
        :param string indicator_label: label as read from the file
        :returns: clean label after (1) and (2)
        :rtype: string

        """
        clean_label = indicator_label.lower().replace("  ", '')
        for keyword in KEYWORDS_TO_REMOVE:
            clean_label = clean_label.replace(' ' + keyword + ' ', ' ')
        clean_label = clean_label.strip()
        if clean_label in INDICATOR_MAPPING:
            return INDICATOR_MAPPING[clean_label]
        else:
            return clean_label

    def on_intersection(self, other):
        self.values.update(other.values)
        self.keys.update(other.keys)


class City(SetItem):

    def __init__(self, label, year, key):
        super().__init__(label.lower(), year, key)

    def on_intersection(self, other):
        self.keys.update(other.keys)

# UTILS


def _float_from_string(s):
    """Extracts float number from the given string

    :param string s: input string
    :returns: float with the value of s or np.nan if s does not represent a float
    :rtype: float

    """
    try:
        value = float(s)
        return value
    except ValueError:
        return np.nan


def _extract_year(file_path):
    """
    Given a path such as "origin/step_1/.../step_k/gpci_XXXX.csv, return the str of the year XXXX
    """
    return functools.reduce(lambda s0, s1: s0 + s1, (char for char in file_path.split('/')[-1].split('.')[0] if char.isdigit()))


def _set_intersection(single_set, accumulative_set):
    result = {}
    for item in accumulative_set.values():
        label = item.label
        if label in single_set:
            item.on_intersection(single_set[label])
            result[label] = item

    return result


def _set_union(single_set, accumulative_set):
    result = _set_intersection(single_set, accumulative_set)

    for item in accumulative_set.values():
        label = item.label
        if label not in result:
            result[label] = item

    for item in single_set.values():
        label = item.label
        if label not in result:
            result[label] = item

    return result

# LOAD CONTENT


def _load_content_all_files(file_list):
    C_or = []
    D_or = []
    for file_path in file_list:
        year = _extract_year(file_path)
        f_t = open(file_path, 'r')

        cities_t = {}  # USE DICT FOR O(1) ACCESS
        f_t_city_list = f_t.readline().strip().replace('"', '').split(',')
        for i, label in enumerate(f_t_city_list):
            city = City(label, year, i)
            cities_t[city.label] = city
        C_or.append(cities_t)

        indicators_t = {}  # USE DICT FOR O(1) ACCESS
        for f_t_line in f_t:
            f_t_line_list = f_t_line.strip().split(',')
            key = int(f_t_line_list[0])
            if key not in INDICATOR_IGNORED_KEYS:
                indicator = Indicator(
                    f_t_line_list[1], year, key, f_t_line_list[2:])
                indicators_t[indicator.label] = indicator
        D_or.append(indicators_t)

        f_t.close()

    return C_or, D_or


def _data_dict_from_sets(C, D):
    data = {}
    for indicator_label, indicator in D.items():
        data[indicator_label] = {}
        for city_label, city in C.items():
            city_years = city.keys.keys()
            data[indicator_label][city_label] = pd.Series(list(
                _float_from_string(
                    indicator.values[year][city.keys[year]])
                for year in city_years),
                index=city_years)

    return data


# MAIN
if __name__ == "__main__":
    file_list = utils.get_file_list(utils.GPCI_FLAG)
    T = list(map(_extract_year, file_list))

    C_all, D_all = _load_content_all_files(file_list)

    C_and = C_all[0]
    C_or = dict(C_all[0])  # dict to avoid alias
    for C_t in C_all[1:]:
        C_and = _set_intersection(C_t, C_and)
        C_or = _set_union(C_t, C_or)

    D_and = D_all[0]
    for D_t in D_all[1:]:
        D_and = _set_intersection(D_t, D_and)

    years = list(pd.Period(year) for year in T)

    data_and = _data_dict_from_sets(C_and, D_and)
    data_or = _data_dict_from_sets(C_or, D_and)

    utils.save_data_frame(
        utils.GPCI_FLAG, utils.CITIES_IN_ALL_YEARS, pd.DataFrame(data_and))
    utils.save_data_frame(
        utils.GPCI_FLAG, utils.ALL_CITIES, pd.DataFrame(data_or))
