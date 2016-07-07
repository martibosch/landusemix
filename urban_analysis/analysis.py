import numpy as np

import loaders
import plots
import spatial_measures
import lu_mix
import utils
import extract_uses.shp_utils


class Analysis(object):
    """ Stores results and information about the analysis of city/urban area

    """

    def __init__(self, city_ref, bbox=None, pois_shp_path=None, grid_step=.0015):
        super(Analysis, self).__init__()
        # basic info
        self.city_ref = city_ref
        if bbox is None:
            self.bbox = extract_uses.shp_utils.getBoundingBox(pois_shp_path)
        else:
            self.bbox = bbox
        self._pois_shp_path = pois_shp_path
        self._grid_step = grid_step
        self._grid = None

        # data
        self._pois = None
        self._kde = None
        self._graph = None
        # self.graph_centrality = None

        # parameters
        self._phi_metric = 'phi_entropy'

        # indicators
        self._moran = None
        self._entropy = None
        self._relative_entropy = None
        self._lu_mix = None
        self._dissimilarity = None
        self._kde_dissimilarity = None

        # stuff to cache
        self._f_count_act = None
        self._f_count_res = None
        self._f_kde_act = None
        self._f_kde_res = None
        self._f_lu_mix_grid = None

    # STORED DATA STRUCTURES

    @property
    def pois(self):
        if self._pois is not None:
            pass
        else:
            self._pois = loaders.load_pois(self.city_ref, self._pois_shp_path)
        if (self.bbox is None): # If bounding box is not set
            self.bbox = extract_uses.shp_utils.getBoundingBox(self._pois_shp_path)
        return self._pois

    @property
    def kde(self):
        if self._kde is not None:
            pass
        else:
            self._kde = loaders.load_grid_kde(
                self.city_ref, self.pois, self.bbox, self._grid_step)
        return self._kde

    @property
    def graph(self):
        if self._graph is not None:
            pass
        else:
            self._graph = loaders.load_graph(self.city_ref, self.bbox)
        return self._graph

    # DATA STRUCTURES DERIVED FROM STORED DATA STRUCTURES

    @property
    def grid(self):
        if self._grid is not None:
            pass
        else:
            self._grid = utils.grid_from_bbox(self.bbox, self._grid_step)
        return self._grid

    @property
    def grid_step(self):
        return self._grid_step

    @grid_step.setter
    def grid_step(self, value):
        if value != self._grid_step:
            self._grid_step = value
            # not valid anymore:
            self._grid = None
            self._kde = None
            self._moran = None
            self._entropy = None
            self._relative_entropy = None
            self._lu_mix = None
            self._dissimilarity = None
            self._kde_dissimilarity = None
            self._f_lu_mix_grid = None
            self._f_count_act = None
            self._f_count_res = None
            self._f_kde_act = None
            self._f_kde_res = None

    @property
    def f_lu_mix_grid(self):
        if self._f_lu_mix_grid is not None:
            pass
        else:
            self._f_lu_mix_grid = lu_mix.compute_landuse_mix_grid(
                self.f_kde_act, self.f_kde_res)
        return self._f_lu_mix_grid

    @property
    def f_count_act(self):
        if self._f_count_act is not None:
            pass
        else:
            self._f_count_act = spatial_measures.grid_cell_pois_count(
                self.pois[self.pois['category'] == 'activity'], *self.grid)
        return self._f_count_act

    @property
    def f_count_res(self):
        if self._f_count_res is not None:
            pass
        else:
            self._f_count_res = spatial_measures.grid_cell_pois_count(
                self.pois[self.pois['category'] == 'residential'], *self.grid)
        return self._f_count_res

    @property
    def f_kde_act(self):
        if self._f_kde_act is not None:
            pass
        else:
            self._f_kde_act = spatial_measures.grid_cell_kde_average(
                self.kde['activity'].values)
        return self._f_kde_act

    @property
    def f_kde_res(self):
        if self._f_kde_res is not None:
            pass
        else:
            self._f_kde_res = spatial_measures.grid_cell_kde_average(
                self.kde['residential'].values)
        return self._f_kde_res

    # MEASURES

    @property
    def moran(self):
        if self._moran:
            pass
        else:
            xx, yy = self.grid
            self._moran = {
                'activity': spatial_measures.moran_index(self.f_count_act, xx, yy),
                'residential': spatial_measures.moran_index(self.f_count_res, xx, yy)
            }
        return self._moran

    @property
    def lu_mix(self):
        if self._lu_mix:
            pass
        else:
            self._lu_mix = lu_mix.compute_phi(self.f_lu_mix_grid)
        return self._lu_mix

    @property
    def entropy(self):
        if self._entropy:
            pass
        else:
            self._entropy = {
                'activity': spatial_measures.shannon_entropy(self.f_kde_act),
                'residential': spatial_measures.shannon_entropy(self.f_kde_res)
            }
        return self._entropy

    @property
    def relative_entropy(self):
        if self._relative_entropy:
            pass
        else:
            # could also be np.log(self.f_kde_res.size)
            self._relative_entropy = {
                'activity': self.entropy['activity'] / np.log(self.f_kde_act.size),
                'residential': self.entropy['residential'] / np.log(self.f_kde_act.size)
            }
        return self._relative_entropy

    @property
    def dissimilarity(self):
        if self._dissimilarity:
            pass
        else:
            self._dissimilarity = spatial_measures.dissimilarity(
                self.f_count_act, self.f_count_res)
        return self._dissimilarity

    @property
    def kde_dissimilarity(self):
        if self._kde_dissimilarity:
            pass
        else:
            self._kde_dissimilarity = spatial_measures.dissimilarity(
                self.f_kde_act, self.f_kde_res)
        return self._kde_dissimilarity

    # PERSISTENCE

    def __getstate__(self):
        result = self.__dict__.copy()
        # do not pickle the data structures
        del result['_pois']
        del result['_kde']
        del result['_graph']

        # do not pickle the cached magnitude arrays
        del result['_f_count_act']
        del result['_f_count_res']
        del result['_f_kde_act']
        del result['_f_kde_res']
        del result['_f_lu_mix_grid']

        return result

    # TODO: to_pickle method

    # PLOTS
    def scatter_pois(self, overlap=True, base_figsize=10):
        plots.pois_scatter(self.pois, overlap=overlap,
                           base_figsize=base_figsize, scatter_kws={'alpha':0.2}, title=self.city_ref)
