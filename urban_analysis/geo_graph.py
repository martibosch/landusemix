import matplotlib.pyplot as plt
import networkx as nx
from pandas import DataFrame

# UTILS

def _from_dfs(nodes_df, edges_df, clean=True):
    """Create a networkx directed graph given a network from pandana

    :param network: pandana.Network object representing a urban graph
    :param clean: bool indicating whether parallell edges and disconnected components should be included
    :returns: transformed directed graph
    :rtype: networkx.DiGraph

    """
    get_node = nodes_df.ix
    digraph_df = DataFrame([
        [edge_row[1]['distance'], # use 'cost'
         GeoNode(get_node[edge_row[0][0]]),
         GeoNode(get_node[edge_row[0][1]])]
        for edge_row in edges_df.iterrows()], columns=['dist', 'from', 'to'])
    
    if clean:
        digraph_df.groupby(['from', 'to']).mean() # avoid parallel edges
        G = nx.from_pandas_dataframe(digraph_df, 'from', 'to', 'dist', create_using=nx.DiGraph())
        return G.subgraph(max(nx.weakly_connected_components(G), key=len))
    else:
        return nx.from_pandas_dataframe(digraph_df, 'from', 'to', 'dist', create_using=nx.DiGraph())

  
# CLASSES
    
class GeoNode(object):
    """Node with position attribute
    """
    def __init__(self, ser):
        """Create geo-referenced node

        :param ser: 

        """
        self.id = ser.name
        self.pos = (ser['lon'], ser['lat'])
        
    def __str__(self):
        return "GeoNode:" + str(self.id) # + ' at ' + str(self.pos)

    def __repr__(self):
        return str(self)
     
    def __eq__(self, other):
        try:
            # do not accept more than one node in the same position
            return self.id == self.id
        except AttributeError:
            return False
    
    def __hash__(self):
        return hash(self.id)
    

class GeoGraph(object):
    """Graph with geo-referenced nodes
    """
    
    def __init__(self, nodes_df, edges_df, pos=True):
        """Create geo-referenced graph given a network from pandana

        :param nodes_df: 
        :param edges_df: 
        :param pos: bool indicating whether a position dict should be created for posterior plotting

        """
        self._G =  _from_dfs(nodes_df, edges_df)
        self.CENTRALITY_DICT = {
            'betweenness' : self.get_betweenness_centrality,
            'closeness' : self.get_closeness_centrality,
            'degree' : self.get_degree_centrality,
        }

        if pos:
            self.set_position_dict()

    def set_position_dict(self):
        """Creates a dict with the position of the nodes for posterior plotting
        """
        self._pos_dict = { node: node.pos for node in self._G.nodes() }
    
    def plot(self, ax=None, node_color=None, **kwargs):
        """Plots the graph

        :param ax: matplotlib Axes to plot on
        :param node_color: str or array of floats with a color value for each node
        """
        if self._pos_dict:
            nx.draw(self._G, pos=self._pos_dict, ax=ax, node_color=node_color, **kwargs)
        else:
            self.set_position_dict()
            nx.draw(self._G, pos=self._pos_dict, ax=ax, node_color=node_color, **kwargs)

    def plot_series(self, series, ax=None, **kwargs):
        """Plots the graph with the nodes colored according to `series`

        :param series: pandas.Series indexed by the graph's nodes
        :param ax: matplotlib Axes to plot on

        """
        if not self._pos_dict:
            self.set_position_dict()

        self.plot(ax=ax, node_color=[nearest_df[key][k][node.id] for node in self._G], **kwargs)

    def get_betweenness_centrality(self):
        return nx.betweenness_centrality(self._G)

    def get_closeness_centrality(self):
        return nx.closeness_centrality(self._G)
    
    def get_degree_centrality(self):
        return nx.degree_centrality(self._G)
    
            
    def get_centrality_df(self):
        centrality_df = DataFrame({ label: method() for (label, method) in self.CENTRALITY_DICT.items() })
        centrality_df.index = centrality_df.index.map(lambda geo_node: geo_node.id)
        return centrality_df

    def plot_centrality(self):
        fig, axes = plt.subplots(1,3)
        for ax, centrality_key in zip(axes, centrality_dict.iterkeys()):
            ax.set_subtitle(centrality_key)
            self.plot(ax=ax, node_color=[self.CENTRALITY_DICT[centrality][node] for node in self._G])
    
    def __iter__(self):
        """Iterate over the graph nodes
        """
        return self._G.__iter__()

    def __len__(self):
        """Number of nodes in the graph
        """
        return len(self._G)
