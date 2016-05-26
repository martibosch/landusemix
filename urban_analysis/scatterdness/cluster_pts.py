import pandas as pd, numpy as np, matplotlib.pyplot as plt
import extract_uses.utils as utils

def calculateScatterdness(pts_shapefile):
    print('Hola')
    
    # Use the clustering method
    
    # Associate the number of points to each cluster: count
    # Use weighting function? Estimated residential value
    #cluster_centroids
    #pd.DataFrame(closest_centroids).drop_duplicates()
    
def getCoordinates(pts_shapefile):
    # Read data-set
    point_shapes , df_points = utils.read_shp_dbf(pts_shapefile)
    # Get point_shapes lat, lon columns. Points are pairs of (longitude,latitude)
    longitude = [ point.points[0][0] for point in point_shapes ]
    latitude = [ point.points[0][1] for point in point_shapes ]

    coordinates = pd.DataFrame({'lon': longitude, 'lat':latitude})
    return coordinates

def cluster_meanshift(pts_shapefile):
    from sklearn.cluster import MeanShift, estimate_bandwidth
    from sklearn.datasets.samples_generator import make_blobs
    
    coordinates = getCoordinates(pts_shapefile)
    coords = coordinates.as_matrix(columns=['lon','lat'])

    ###############################################################################
    # Compute clustering with MeanShift
    X = coords

    # The following bandwidth can be automatically detected using
    bandwidth = estimate_bandwidth(X, quantile=0.05, n_samples=200)

    ms = MeanShift(bandwidth=bandwidth, bin_seeding=True)
    ms.fit(X)
    labels = ms.labels_
    cluster_centers = ms.cluster_centers_

    labels_unique = np.unique(labels)
    n_clusters_ = len(labels_unique)

    ###############################################################################
    # Plot result
    import matplotlib.pyplot as plt
    from itertools import cycle

    plt.figure(1)
    plt.clf()

    colors = cycle('bgrcmykbgrcmykbgrcmykbgrcmyk')
    for k, col in zip(range(n_clusters_), colors):
        my_members = labels == k
        cluster_center = cluster_centers[k]
        plt.plot(X[my_members, 0], X[my_members, 1], col + '.')
        plt.plot(cluster_center[0], cluster_center[1], 'o', markerfacecolor=col,
                 markeredgecolor='k', markersize=14)
    plt.title('MeanShift: Estimated number of clusters: %d' % n_clusters_)
    plt.show()

def cluster_kmeans(pts_shapefile):
    from scipy.cluster.vq import kmeans2, whiten
    
    coordinates = getCoordinates(pts_shapefile)
    coords = coordinates.as_matrix(columns=['lon','lat'])

    performWhitening = True
    k = 30
    i = 100 # iterations
    
    N = len(coords)
    ''' http://docs.scipy.org/doc/scipy/reference/generated/scipy.cluster.vq.whiten.html#scipy.cluster.vq.whiten
    Each feature is divided by its standard deviation across all observations to give it unit variance.
    At the end, you can compare the results of running k-means on both whitened and un-whitened data sets. 
    The whitened data yields results that are more spatially representative of the original, full data set.
    '''
    if (performWhitening):
        w = whiten(coords)
    else:
        w = coords

    cluster_centroids, closest_centroids = kmeans2(w, k, iter=i, minit='points')
    plt.figure(figsize=(10, 6), dpi=100)
    plt.scatter(w[:,0], w[:,1], c='r', alpha=.4, s=10)
    plt.scatter(cluster_centroids[:,0], cluster_centroids[:,1], c='b', alpha=.9, s=150)
    plt.title('Kmeans. Number of clusters set: '+str(k))
    plt.show()
    
def cluster_dbscan(pts_shapefile):
    from sklearn.cluster import DBSCAN
    from geopy.distance import great_circle
    
    coordinates = getCoordinates(pts_shapefile)
    
    #http://geoffboeing.com/2014/08/clustering-to-reduce-spatial-data-set-size/
    '''
    DBSCAN clusters a spatial data set based on two parameters: a physical distance from each point, and a minimum cluster size. 
    This works much better for spatial lat-long data.
    '''
    db = DBSCAN(eps=.0075, min_samples=1).fit(coordinates)
    labels = db.labels_
    num_clusters = len(set(labels)) - (1 if -1 in labels else 0)
    clusters = pd.Series([coordinates[labels == i] for i in xrange(num_clusters)])

    '''
    def getCentroid(points):
        n = points.shape[0]
        sum_lon = np.sum(points[:, 1])
        sum_lat = np.sum(points[:, 0])
        return (sum_lon/n, sum_lat/n)

    # Compute the big centroid, the centroid weighted by each cluster's centroid
    '''

    plt.figure(figsize=(10, 6), dpi=100)
    colors = ('bgrcmykbgrcmykbgrcmykbgrcmyk')
    for i, color in zip(range(len(clusters)),colors):
        cluster = clusters[i]
        rs_scatter = plt.scatter(cluster.lon, cluster.lat, c=color, alpha=.4, s=10)
    plt.title('DBSCAN. Estimated number of clusters: '+str(len(clusters)))
    plt.xlabel('Longitude')
    plt.ylabel('Latitude')
    plt.show()
