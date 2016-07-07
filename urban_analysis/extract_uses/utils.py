import pandas as pd
import numpy as np

########################################################################

def filterColumns(workingKey, sub_selection):
	""" Filter the columns and return the rows with the reduced fields format
	Use as input the working key, which determines the contained value
	"""
	filteredColumns_Selection = sub_selection[['osm_id',workingKey]]
	filteredColumns_Selection = filteredColumns_Selection.rename(columns={workingKey:'value'})
	filteredColumns_Selection['key'] = np.repeat(workingKey,len(filteredColumns_Selection))
	return filteredColumns_Selection

########################################################################
