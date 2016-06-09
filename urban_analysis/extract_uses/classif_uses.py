'''
Classiy uses according to OpenStreetMap wiki
'''
####################################################################################
### Classification according to OSM wiki, adding our interests:

### Key: amenity -> Related to activities (filtered)
amenities_sustenance = ['bar','pub','restaurant','biergarten','cafe','fast_food','food_court','ice_cream','pub','restaurant']
amenities_education = ['college','kindergarten','library','public_bookcase','school','music_school','driving_school','language_school','university']
amenities_transportation = ['fuel','bicycle_rental','bus_station','car_rental','taxi','car_wash','ferry_terminal']
amenities_financial = ['atm','bank','bureau_de_change']
amenities_healthcare = ['baby_hatch','clinic','dentist','doctors','hospital','nursing_home','pharmacy','social_facility','veterinary']
amenities_entertainment = ['arts_centre','brothel','casino','cinema','community_centre','fountain','gambling','nightclub','planetarium','social_centre','stripclub','studio','swingerclub','theatre']
amenities_others = ['animal_boarding','animal_shelter','courthouse','coworking_space','crematorium','dive_centre','dojo','embassy','fire_station','gym','internet_cafe','marketplace','police','post_office','townhall']

amenities_activities = amenities_sustenance + amenities_education + amenities_transportation + amenities_financial + amenities_healthcare + amenities_entertainment + amenities_others

'''
### Key: shop -> all those which are non-null: commercial purposes
'''

### Key: building
building_other = ['barn','bridge','bunker','cabin','construction','cowshed','digester','farm_auxiliary','garage','garages','greenhouse','hangar','hut','roof','shed','stable','sty','transformer_tower','service','ruins','yes','kiosk']

building_commercial = ['commercial','office','industrial','retail','warehouse']
building_civic_amenity = ['cathedral','chapel','church','mosque','temple','synagogue','shrine','civic','hospital','school','stadium','train_station','transportation','university','public']

building_activities = building_commercial + building_civic_amenity + ['kiosk', 'garage', 'garages', 'hangar', 'stable', 'cowshed', 'digester'] # From building_other related to activities
building_residential = ['hotel','farm','apartment','apartments','dormitory','house','residential','retirement_home','terrace','houseboat','bungalow','static_caravan','detached']

### Key: landuse (For polygons)
landuse_other = ['cemetery', 'landfill', 'railway']
landuse_water = ['water', 'reservoir', 'basin']
landuse_green = ['allotments','conservation', 'farmland', 'farmyard','forest','grass', 'greenfield', 'greenhouse_horticulture','meadow','orchard','pasture','peat_cutting','plant_nursery','recreation_ground','village_green','vineyard']
landuse_construction = ['brownfield']

landuse_activities = ['commercial','industrial','retail','port'] + ['quarry','salt_pond','construction','military','garages']
landuse_residential = ['residential']

# Construction tag not used, since might be old
landuse_notResidentialActivity = landuse_other + landuse_water + landuse_green

### Key: leisure
#Not tagged as activity: dog_park, bird_hide, bandstand, firepit, fishing, garden, golf_course, marina, miniature_golf, nature_reserve, park, playground, slipway, track, wildlife_hide, swimming_pool
leisure_activies = ['adult_gaming_centre','amusement_arcade','beach_resort','dance','hackerspace','ice_rink','pitch','sports_centre','stadium','summer_camp','swimming_area','water_park']
####################################################################################
'''
# Activity categories:
	'shop'
	'leisure/amenity'
	'commercial/industrial'
	-> Pick those values for the keys ['building','landuse','inferred'] and join it to the respective categories

######
	http://wiki.openstreetmap.org/wiki/Key:amenity
	-> 'amenity' = Education ?
	-> 'amenity' = Healthcare ? (civic)

	http://wiki.openstreetmap.org/wiki/Key:building
	-> 'building' = Commercial ?
	-> 'building' = Civic/Amenity ?
'''

def key_category_mapping(pois_df):
	####################
	### Process landuse key
	# landuse => commercial/industrial
	pois_df.loc[ (pois_df.key.isin(["landuse"]) )& (pois_df.value.isin(landuse_activities) ) , 'key'] = 'commercial/industrial'
	# landuse => leisure/amenity
	pois_df.loc[ (pois_df.key.isin(["landuse"]) )& (pois_df.value.isin(amenities_activities) ),'key'] = 'leisure/amenity'
	# landuse => shop
	pois_df.loc[ (pois_df.key.isin(["landuse"]) )& (pois_df.value.isin(['shop']) ),'key'] = 'shop'

	### Merge leisure and amenity
	# leisure => leisure/amenity
	pois_df.loc[ pois_df.key.isin(["leisure"]) , 'key'] = 'leisure/amenity'
	# amenity => leisure/amenity
	pois_df.loc[ pois_df.key.isin(["amenity"]) , 'key'] = 'leisure/amenity'

	### Process building key
	# building => leisure/amenity
	pois_df.loc[ (pois_df.key.isin(["building"]) )& (pois_df.value.isin(amenities_activities) ) ,'key'] = 'leisure/amenity'
	# building => commercial/industrial
	pois_df.loc[ (pois_df.key.isin(["building"]) )& (pois_df.value.isin(building_activities) ) ,'key'] = 'commercial/industrial'
	# building => shop
	pois_df.loc[ (pois_df.key.isin(["building"]) )& (pois_df.value.isin(['shop']) ),'key'] = 'commercial/industrial'

	### Process inferred
	# inferred => leisure/amenity
	pois_df.loc[ (pois_df.key.isin(["inferred"]) )& (pois_df.value.isin(amenities_activities) ),'key'] = 'leisure/amenity'
	# inferred => commercial/industrial
	pois_df.loc[ (pois_df.key.isin(["inferred"]) )& (pois_df.value.isin(building_activities) ) ,'key'] = 'commercial/industrial'
	pois_df.loc[ (pois_df.key.isin(["inferred"]) )& (pois_df.value.isin(landuse_activities) ) ,'key'] = 'commercial/industrial'
	# inferred => shop
	pois_df.loc[ (pois_df.key.isin(["inferred"]) )& (pois_df.value.isin(['shop']) ) ,'key'] = 'shop'
	####################
	return pois_df

####################################################################################
### Roads:
highway_important =  ["motor_way" , "trunk" , "primary" , "secondary", "tertiary", "residential", "unclassified", "service"]


