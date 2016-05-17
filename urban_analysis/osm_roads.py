####################################################################################
### Classification according to OSM wiki, adding our interests:
# https://wiki.openstreetmap.org/wiki/Key:highway

### Key: highway
_classif_roads_principal = ['motorway','trunk','primary','secondary','tertiary','unclassified','residential'] # ,'service']
_classif_roads_links = ['motorway_link','trunk_link','primary_link','secondary_link','tertiary_link']
_classif_roads_special = ['living_street','pedestrian','track','bus_guideway','raceway','road']
_classif_roads_paths = ['footway','bridleway','steps','path']

### Other keys: Sidewalk, cycleway, busway, other attributes

key = 'highway'
values = _classif_roads_principal # + _classif_roads_links
columns = []
