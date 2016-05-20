import shutil
import os
import parameters
import gc

import extract_point_uses
import extract_poly_uses
import infer_poly_uses
import poly_to_pts

import cut_shapefile
import population


def clipFiles(point_shapefile, polygon_shapefile):
	################################################################
	# Copy projection file for the extracted shapefiles
	if not os.path.exists(parameters.fn_prefix):
		os.makedirs(parameters.fn_prefix)
	shutil.copy(parameters.prj_shapefile, parameters.fn_prefix+'sample.prj')

	# Note that "_qnI" will be added to distinguish them
	print('Clip polygon')
	cut_shapefile.clip_PolygonFile(polygon_shapefile,parameters.fn_subregions+parameters.fn_poly)
	gc.collect()

	print('Clip points')
	cut_shapefile.clip_PointFile(point_shapefile,parameters.fn_subregions+parameters.fn_pts)
	gc.collect()
	################################################################

def performExtraction(population_count_file = None):
	################################################################
	### Given OSM extracted shapefiles (point,polygon) -> Extract residential/activities points	
	# For each sub-shapefile: Extract point uses, polygon uses, infer polygon uses, convert all polygons to points	
	
	for i in range(0,parameters.numCuts):
		print("Iteration:",i)

		### Get name files
		in_shp_pts = parameters.fn_subregions+parameters.fn_pts + "_q"+str(i)
		in_shp_polys = parameters.fn_subregions+parameters.fn_poly + "_q"+str(i)
		in_shp_polys_sq = parameters.fn_subregions+parameters.fn_poly + "_sq" # Several quadrants polygons
		out_suffix = "_q"+str(i)

		### Process points
		extract_point_uses.main(in_shp_pts,out_suffix)
		gc.collect()

		### Process polygons
		extract_poly_uses.main(in_shp_polys,out_suffix)
		gc.collect()

		### Infer polygons
		infer_poly_uses.main(in_shp_polys,in_shp_polys_sq,out_suffix)
		gc.collect()

		### Convert polygons to points for further processing
		PolyToPoint_needed = extract_poly_uses.getNameSavedFiles(out_suffix) + infer_poly_uses.getNameSavedFiles(out_suffix)
		poly_to_pts.convert(PolyToPoint_needed)
		gc.collect()

	# Merge the different cuts into one file
	
	cut_shapefile.mergeDifferentCuts(parameters.fn_prefix,parameters.numCuts,parameters.deleteParts)

	### Merge the categories: Use only points
	if (parameters.USE_Merge_categories):
		cut_shapefile.mergeFinalCategories(parameters.fn_prefix,parameters.numCuts,parameters.deleteMergedParts)
	
	########
	if (population_count_file != None):
		### Process: Perform population down-scaling and distribute to each residential point
		population.population_downscaling(population_count_file, parameters.fn_residential_final)

	########

	# Remove temp folder/files
	if (os.path.isdir(parameters.fn_subregions)):
		shutil.rmtree(parameters.fn_subregions)
	if (os.path.isfile(parameters.fn_prefix+'sample.prj') ):
		os.remove(parameters.fn_prefix+'sample.prj')
	################################################################

################################################################	
def process(point_shapefile, polygon_shapefile, population_count_file = None):
	'''	
	parameters.population_count_file must be initialized
	'''
	################################################################
	# Clip files in parts (reduced memory needs if map is too big, faster polygon infer)
	clipFiles(point_shapefile, polygon_shapefile)
	# Extract residential/activity uses. Alternatively, estimate the population count for residential points
	performExtraction(population_count_file)
	################################################################

################################################################

def main():
	################################################################
	print('Hola: Main')
	###
	'''
	parameters.polygon_shapefile and parameters.point_shapefile must be set
	If parameters.population_count_file is set, perform the population downscaling
	'''
	process(parameters.point_shapefile, parameters.polygon_shapefile, parameters.population_count_file)

	# for i in files:
	# set parameters. files
	# 	process()
	###
	print('Chau: Main')
	################################################################

if __name__ == "__main__":
   # stuff only to run when not called via 'import' here
   main()
