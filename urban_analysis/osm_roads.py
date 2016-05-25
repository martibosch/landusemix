####################################################################################
### Classification according to OSM wiki, adding our interests:
# https://wiki.openstreetmap.org/wiki/Key:highway

### Key: highway
_classif_roads_principal = ['motorway','trunk','primary','secondary','tertiary','unclassified','residential']
_classif_roads_links = ['motorway_link','trunk_link','primary_link','secondary_link','tertiary_link']
_classif_roads_special = ['living_street','pedestrian','track','bus_guideway','raceway','road']
_classif_roads_paths = ['footway','bridleway','steps','path']
# Other keys: Sidewalk, cycleway, busway, other attributes


key = 'highway'
values = _classif_roads_principal # + _classif_roads_links
columns = []


### Speed associated to type of highway. Relative to the default value. Weights the cost of performing a certain distance, given the speed within which it can be circulated
'''
SpeedClass::30.0 # default value
SpeedClass:motorway:110.0
SpeedClass:trunk:110.0
SpeedClass:primary:90.0
SpeedClass:secondary:70.0
SpeedClass:tertiary:50.0
'''
speedHighway = {'motorway': 30./110., 'trunk': 30./110., 'primary': 30./90., 'secondary': 30./70., 'tertiary': 30./50., 'unclassified': 30./30., 'residential': 30./30.}

def getHighwayWeight(highway_type):
    if (highway_type in speedHighway): # Found instance in dictionary
        return speedHighway[highway_type]
    else: # Return default value
        return 1 