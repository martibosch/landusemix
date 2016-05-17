'''
OSM query
'''
####################################################################################
### Classification according to OSM wiki, adding our interests:

### Key: amenity -> Related to activities (filtered)
_amenity_sustenance = ['bar','pub','restaurant','biergarten','cafe','fast_food','food_court','ice_cream','pub','restaurant']
_amenity_education = ['college','kindergarten','library','public_bookcase','school','music_school','driving_school','language_school','university']
_amenity_transportation = ['fuel','bicycle_rental','bus_station','car_rental','taxi','car_wash','ferry_terminal']
_amenity_financial = ['atm','bank','bureau_de_change']
_amenity_healthcare = ['baby_hatch','clinic','dentist','doctors','hospital','nursing_home','pharmacy','social_facility','veterinary']
_amenity_entertainment = ['arts_centre','brothel','casino','cinema','community_centre','fountain','gambling','nightclub','planetarium','social_centre','stripclub','studio','swingerclub','theatre']
_amenity_others = ['animal_boarding','animal_shelter','courthouse','coworking_space','crematorium','dive_centre','dojo','embassy','fire_station','gym','internet_cafe','marketplace','police','post_office','townhall']

_amenity_activities = _amenity_sustenance + _amenity_education + _amenity_transportation + _amenity_financial + _amenity_healthcare + _amenity_entertainment + _amenity_others


### Key: shop -> all those which are non-null: commercial purposes
_shop_activities = ['alcohol', 'bakery', 'beverages', 'brewing_supplies', 'butcher', 'cheese', 'chocolate', 'coffee', 'confectionery', 'convenience', 'deli', 'dairy', 'farm', 'greengrocer', 'organic', 'pasta', 'pastry', 'seafood', 'tea', 'wine', 'department_store', 'general', 'kiosk', 'mall', 'supermarket', 'baby_goods', 'bag', 'boutique', 'clothes', 'fabric', 'fashion', 'jewelry', 'leather', 'shoes', 'tailor', 'watches', 'charity', 'second_hand', 'variety_store', 'beauty', 'chemist', 'cosmetics', 'drugstore', 'erotic', 'hairdresser', 'hearing_aids', 'herbalist', 'massage', 'medical_supply', 'nutrition_supplements', 'optician', 'perfumery', 'tattoo', 'bathroom_furnishing', 'doityourself', 'electrical', 'energy', 'fireplace', 'florist', 'garden_centre', 'garden_furniture', 'gas', 'glaziery', 'hardware', 'houseware', 'locksmith', 'paint', 'trade', 'antiques', 'bed', 'candles', 'carpet', 'curtain', 'furniture', 'interior_decoration', 'kitchen', 'lamps', 'window_blind', 'computer', 'electronics', 'hifi', 'mobile_phone', 'radiotechnics', 'vacuum_cleaner', 'bicycle', 'car', 'car_repair', 'car_parts', 'fishing', 'free_flying', 'hunting', 'motorcycle', 'outdoor', 'scuba_diving', 'sports', 'tyres', 'swimming_pool', 'art', 'craft', 'frame', 'games', 'model', 'music', 'musical_instrument', 'photo', 'trophy', 'video', 'video_games', 'anime', 'books', 'gift', 'lottery', 'newsagent', 'stationery', 'ticket', 'copyshop', 'dry_cleaning', 'e-cigarette', 'funeral_directors', 'laundry', 'money_lender', 'pawnbroker', 'pet', 'pyrotechnics', 'religion', 'tobacco', 'toys', 'travel_agency', 'vacant', 'weapons']

### Key: building
_building_commercial = ['commercial','office','industrial','retail','warehouse']
_building_civic_amenity = ['cathedral','chapel','church','mosque','temple','synagogue','shrine','civic','hospital','school','stadium','train_station','transportation','university','public']

_building_activities = _building_commercial + _building_civic_amenity + ['kiosk']


### Key: landuse (For polygons)
_landuse_activities = ['commercial','industrial','retail','port'] + ['quarry','salt_pond','construction','military','garages']

### Key: leisure
#Not tagged as activity: dog_park, bird_hide, bandstand, firepit, fishing, garden, golf_course, marina, miniature_golf, nature_reserve, park, playground, slipway, track, wildlife_hide
# _leisure_activies = ['adult_gaming_centre','amusement_arcade','beach_resort','dance','hackerspace','ice_rink','pitch','sports_centre','stadium','summer_camp','swimming_area','swimming_pool','water_park']
_leisure_activies = ['adult_gaming_centre','amusement_arcade','beach_resort','dance','hackerspace','ice_rink','pitch','sports_centre','stadium','summer_camp','swimming_area','water_park']

####################################################################################

### We are only interested in certain columns
# the order of the columns is VERY IMPORTANT
_amenity_columns = ['amenity', 'lon', 'lat']
_shop_columns = ['shop', 'lon', 'lat']
_building_columns = ['building', 'lon', 'lat']
_landuse_columns = ['landuse', 'lon', 'lat']
_leisure_columns = ['leisure', 'lon', 'lat']

keys = ['amenity','shop','building','landuse','leisure']
values = [_amenity_activities, _shop_activities, _building_activities, _landuse_activities, _leisure_activies]
columns = [_amenity_columns, _shop_columns, _building_columns, _landuse_columns, _leisure_columns]

# tag_iterator = (generate_tag(key, value) for key, value in zip(keys, values))

# amenity:columns: access addr:city addr:country addr:housename addr:housenumber addr:place addr:pobox addr:postcode addr:street address alt_name amenity arts_centre atm automatic beverage bic books brand brewery building cafe capacity change_machine clothes compressed_air contact:facebook contact:fax contact:housenumber contact:phone contact:postcode contact:street contact:website copy_facility country craft cuisine deaf:description:fr delivery description description:en diet:halal diet:vegetarian dispensing doctors drinking_water drive_in drive_through ele email emergency entrance fast_food fax fee fixme fuel:diesel fuel:e10 fuel:lpg fuel:octane_95 fuel:octane_98 gay halal hallal hammam health_specialty:yoga healthcare heritage heritage:operator hgv:lanes historic int_name internet_access internet_access:fee is_in kindergarten:FR lat layer leisure level license_classes lon mhs:inscription_date name name:botanical natural network note note:fr old_name old_old_name opening_hours operator operator:type organic outdoor_seating payment:cash payment:credit_cards payment:cryptocurrencies payment:debit_cards payment:electronic_purses phases phone post_office:type ref ref:FR:FINESS ref:FR:LaPoste ref:UAI ref:mhs school:FR shelter shop short_name smoking social_facility:for source_1 sport stamping_machine surface takeaway theatre:genre tobacco tobbaco toilets url vending vending_machine website wheelchair wheelchair:description wheelchair_toilet wifi wikipedia

# shop:columns: 3d_printing access activity addr:city addr:country addr:housename addr:housenumber addr:postcode addr:street addr:street_1 alcohol alt_name amenity books brand butcher cafe camera:type capacity car_service clothes compressed_air contact:email contact:facebook contact:fax contact:google_plus contact:housenumber contact:instagram contact:phone contact:street contact:twitter contact:website craft cuisine culture description dispensing disused drink:wine drive_through electronics_repair email fax female floor fuel:diesel fuel:e10 fuel:octane_98 furniture gambling hgv:lanes houseware information internet_access lat layer level linen lon male man_made massage name note old_name old_old_name opening_hours operator organic origin pastry pastry_shop payment:cash payment:coins payment:credit_cards payment:debit_cards payment:ep_moneo payment:notes payment:visa phone produce ref:FR:FINESS rental second_hand self_service service service:bicycle:diy service:bicycle:rental service:bicycle:repair service:bicycle:retail service:bicycle:second_hand service:copy service:fax service:phone shop short_name ski:repair sport surveillance tactile_paving tobacco tobbaco toilets tourism trade vending vending_machine website wheelchair wikipedia

# building:columns: addr:city addr:housenumber addr:postcode addr:street amenity building building:levels contact:website denomination lat lon name religion short_name website

# landuse:columns: landuse lat lon

# leisure:columns:
