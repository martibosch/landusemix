import numpy as np

USE_normalise_lu_grid = False

def metric_phi(x,y):
    #return abs(x-y)
    return abs(x-y)**0.75
    #return abs(x-y) * max(x,y)
    #return abs(x-y) * min(1,x+y)
    #return (1 - ( abs(x-y)**0.1 ) ) * min(1,x+y)
    #return (1 - ( abs(x-y)**0.5 ) ) * max(x,y)

def metric_phi_entropy(x,y):
    """ Shannon (diversity) index
    Phi entropy metric. Based on paper "Comparing measures of urban land use mix, 2013"
    """
    import math
    if (x <= 0 or y <= 0): return 0
    #https://www.wolframalpha.com/input/?i=plot+z+%3D+-+(+(+x*ln(x)+)+%2B+(+y*ln(y)+)+)+%2F+ln(2),+x%3D0..1
    return - ( ( x*math.log(x) ) + ( y*math.log(y) ) ) / math.log(2)

def metric_phi_balance_index(x,y):
    """ Phi balance index metric. Based on paper "Comparing measures of urban land use mix, 2013"
    """
    #https://www.wolframalpha.com/input/?i=plot+z%3D+1-+(abs(x-y))%2F(x%2By)+,+x%3D0..1
    return 1 - (abs(x-y))/(x+y)

def metric_phi_true_diversity_index(x,y):
	""" True diversity index
	https://en.wikipedia.org/wiki/Diversity_index
	"""
	q = 0.5
	return (x**q + y**q )** (1/(1-q))

def metric_phi_generalized_entropy_alpha(x,y):
	""" Renyi's generalized entropy of order alpha
	Detection of landscape heterogeneity at multiple scales: Use of the quadratic entropy index, 2016
	H_alpha
	"""
	import math
	alpha_entropy_order = -2
	return math.log(x**alpha_entropy_order+y**alpha_entropy_order) / 1 - alpha_entropy_order
	#return 100 - ( math.log(x**alpha_entropy_order+y**alpha_entropy_order) / 1 - alpha_entropy_order )

def metric_phi_sorensen(x,y):
	#https://en.wikipedia.org/wiki/S%C3%B8rensen%E2%80%93Dice_coefficient
	return (2*(min(x,y)) ) / (x+y)
def metric_phi_jaccard(x,y):
	#https://en.wikipedia.org/wiki/Jaccard_index
	return min(x,y) / ( x + y - min(x,y) )


# Define metrics
function_phi = {'phi_jaccard' : metric_phi_jaccard, 'phi_sorensen' : metric_phi_sorensen, 'phi_entropy' : metric_phi_entropy, 'phi_generalized_entropy_alpha' : metric_phi_generalized_entropy_alpha, 'phi' : metric_phi, 'phi_balance_index' : metric_phi_balance_index, 'phi_true_diversity' : metric_phi_true_diversity_index}
def get_phi_metrics():
	return function_phi.keys()

def compute_landuse_mix_grid(kde_activities, kde_residential, phi_metric = 'phi_entropy'):
	""" Computes the land use mix grid given residential and activities KDE's
	phi_metric defines the metric used to evaluate the mixity for each grid
	phi metrics: { 'phi','phi_entropy','phi_balance_index' }
	"""
	if ( (kde_activities is None) or (kde_residential is None) ):
		print('KDE empty')
		return None
	
	# Convert to numpy matrix
	np_kde_activities = np.matrix(kde_activities)
	np_kde_residential = np.matrix(kde_residential)

	# Intialize data structure
	lu_mix = np.zeros(shape=kde_activities.shape)
	rows, cols = lu_mix.shape[0] , lu_mix.shape[1]

	# Set function to compute
	compute_phi = function_phi[phi_metric]

	for i in range(rows): #Rows
		for j in range(cols): #Cols
			lu_mix[i,j] = compute_phi(np_kde_activities[i,j] , np_kde_residential[i,j])

	if (USE_normalise_lu_grid): # Normalise output?
		phi = lu_mix.sum()
		for i in range(rows): #Rows
			for j in range(cols): #Cols
				lu_mix[i,j] /= phi
                
	return lu_mix

def compute_phi(lu_mix_grid):
	""" Compute an indicator of land use mixity given the input grid
	Sum of grid values
	% of ...
	
	"""
	phi = lu_mix_grid.sum() / ( lu_mix_grid.shape[0]*lu_mix_grid.shape[1] )
	return phi