import loaders



class Analysis(object):
    """ Stores results and information about the analysis of city/urban area

    """
    def __init__(self, city_ref, bbox, grid_step=.0015):
        super(Analysis, self).__init__()
        self.city_ref = city_ref
        self.bbox = bbox
        self.grid_step

    def load_data(self):
        self.graph = loaders.load_graph(self.city_ref, self.bbox)
        self.graph_centrality = loaders.load_centrality
        self.pois = loaders.load_pois(self.city_ref)
