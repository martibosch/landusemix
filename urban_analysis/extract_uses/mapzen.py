import parameters

# Module to download shapefile from mapzen

def download_unzip(citiesFolder, city_download):
	import urllib
	import zipfile
	import os
	# Get filename: temporary
	fname = citiesFolder+"temp.zip"
	# Download zip file corresponding to city
	testfile = urllib.URLopener()
	testfile.retrieve(city_download, fname)
	# Unzip file
	zip_ref = zipfile.ZipFile(fname, 'r')
	zip_ref.extractall(citiesFolder)
	zip_ref.close()
	# Remove zip file
	os.remove(fname)
	if (parameters.USE_verbose):
		print('Downloaded and unzipped:',city_download)

def getCityShapefile(citiesFolder, cities_countries):
	""" Download from Mapzen data metro-extracts the shapefile for the required city
	Download file and unzip into the required folder
	"""
	import os
	# Suffix and prefix for downloading a city from mapzen metro extracts
	Dl_prefix = 'https://s3.amazonaws.com/metro-extracts.mapzen.com/'
	Dl_suffix = '.osm2pgsql-shapefiles.zip'
	# Check if folder exists
	if (not(os.path.exists(citiesFolder))): os.makedirs(citiesFolder)
	# For each city_country to download:
	for city_country in cities_countries:
		city_download = Dl_prefix + city_country + Dl_suffix
		if ( os.path.isfile(citiesFolder+city_country+"_osm_polygon.shp") ):
			if (parameters.USE_verbose):
				print('Existing shapefile for:',city_country)
		else:
			download_unzip(citiesFolder, city_download)

def getCityOsmPbf(citiesFolder, cities_countries):
    """ Download from Mapzen data metro-extracts the osm pbf for the required city
    """
    import os
    import urllib
    # Suffix and prefix for downloading a city from mapzen metro extracts
    Dl_prefix = 'https://s3.amazonaws.com/metro-extracts.mapzen.com/'
    Dl_suffix = '.osm.pbf'
    # Check if folder exists
    if (not(os.path.exists(citiesFolder))): os.makedirs(citiesFolder)
    # For each city_country to download:
    for city_country in cities_countries:
        city_download = Dl_prefix + city_country + Dl_suffix
        if ( os.path.isfile(citiesFolder+city_country+".osm.pbf") ):
            if (parameters.USE_verbose):
                print('Existing osm pbf for',city_country)
        else:
            testfile = urllib.URLopener()
            testfile.retrieve(city_download, citiesFolder + city_country + ".osm.pbf")
            if (parameters.USE_verbose):
                print('Downloaded osm pbf:',city_download)

def remove_mapzen_files(folder, city_ref):
	""" Remove the downloaded mapzen files. (i.e. Any file containing the city_ref name. Remember that results are stored in a folder called the same way as the city)
	"""
	import os
	if (folder[-1] != "/"): folder = folder + "/"
	files = os.listdir(folder)
	for f in files:
		if ((city_ref in f) and (os.path.isfile(folder+f))):
			os.remove(folder+f)