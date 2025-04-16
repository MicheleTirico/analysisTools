import numpy as np
import pandas as pd
import sys
import geopandas as gpd

import os
import geopandas as gpd
import pandas as pd
from shapely.geometry import Polygon
import geopandas as gpd
import numpy as np
from shapely.geometry import LineString, MultiPoint, Polygon

from scipy.spatial import Voronoi
import matplotlib.pyplot as plt
from shapely.geometry import Point

import geopandas as gpd
import matplotlib.pyplot as plt
from shapely.geometry import LineString

from toolbox.control import tools


def set_gdf_new_crs(logger,crs, listGdf):
    listOut=[]
    logger.log(cl=None, method=sys._getframe(), message="set to a list of gdf the crs : {}".format( crs))

    for pos in range(len(listGdf)):
        logger.log(cl=None, method=sys._getframe(),message="set to gdf : {} crs : {}".format(pos,crs))
        try:
            gdf=listGdf[pos].to_crs(crs)
        except ValueError:
            logger.warning(cl=None, method=sys._getframe(), message="Cannot transform naive geometries. Try with .to_crs",doQuit=False)
            gdf=listGdf[pos].set_crs(crs)
        listOut.append(gdf)
    if len(listOut)==1: return listOut[0]
    else :              return tuple(listOut)

def get_links_overlap(logger,gdf,addNewId=True):
    logger.log(cl=None, method=sys._getframe(), message="get couples of links where opposite vertices are the same")

    # get couples of nodes
    df_unique_pairs = gdf.apply(lambda row: tuple(sorted([row["NodeUpID"], row['NodeDownID']])), axis=1)
    unique_pairs = df_unique_pairs.drop_duplicates().tolist()
    list_all_links=[]
    n0,n1=[],[]
    for a,b in unique_pairs:
        n0.append(a)
        n1.append(b)
        filtered_ids = gdf[(gdf["NodeUpID"] == a) & (gdf['NodeDownID'] == b) | (gdf["NodeUpID"] == b) & (gdf['NodeDownID'] == a)]['ID'].tolist()
        list_all_links.append(" ".join(filtered_ids))

    df_nodes_allLinks=pd.DataFrame({"n0":n0,"n1":n1,"links":list_all_links})
    df_overlapLinks = df_nodes_allLinks[df_nodes_allLinks['links'].str.contains(" ", na=False)]

    if addNewId: df_overlapLinks.insert(0, 'ID', [f"midLn_{i}" for i in range(1, len(df_overlapLinks) + 1)])

    return df_nodes_allLinks, df_overlapLinks


def get_coordinates(gdf, node_id):
    row = gdf[(gdf['NodeUpID'] == node_id) | (gdf['NodeDownID'] == node_id)]
    if not row.empty:
        line = row.geometry.iloc[0]  # Get LineString
        if gdf['NodeUpID'].iloc[0] == node_id:  # If node_id is NodeUpID → Start Point
            return line.coords[0]  # First point (x, y)
        else:  # If node_id is NodeDownID → End Point
            return line.coords[-1]  # Last point (x, y)
    return None  # ID not found

def get_midpoint_pairs_of_coordinates(logger,lines):
    # Create a GeoDataFrame
    from itertools import combinations
    # Get the endpoints of the lines
    start1, end1 = lines[0].coords[0], lines[0].coords[-1]
    start2, end2 = lines[1].coords[0], lines[1].coords[-1]

    points = [start1, end1, start2, end2]

    # Function to calculate Euclidean distance
    def euclidean_distance(point1, point2):
        return np.sqrt((point1[0] - point2[0]) ** 2 + (point1[1] - point2[1]) ** 2)

    # Function to calculate midpoint
    def midpoint(point1, point2):
        return ((point1[0] + point2[0]) / 2, (point1[1] + point2[1]) / 2)

    # Calculate distances between all pairs of points
    distances = []
    midpoints = []
    for (point1, point2) in combinations(range(len(points)), 2):
        dist = euclidean_distance(points[point1], points[point2])
        mid = midpoint(points[point1], points[point2])  # Calculate midpoint
        distances.append(((point1, point2), dist))
        midpoints.append(((point1, point2), mid))  # Store the midpoint

    # Sort the distances by the distance value
    distances.sort(key=lambda x: x[1])

    # The two closest pairs
    closest_pair_1 = distances[0]
    closest_pair_2 = distances[1]

    # Get the midpoints for the closest pairs
    midpoint_1 = midpoint(points[closest_pair_1[0][0]], points[closest_pair_1[0][1]])
    midpoint_2 = midpoint(points[closest_pair_2[0][0]], points[closest_pair_2[0][1]])

    return midpoint_1, midpoint_2

    # get df closest links
def getDfclosestLinks ( links_in, links_out):
    joined_near = gpd.sjoin_nearest(links_out, links_in, how="right", distance_col="distance")
    df_closest = joined_near.loc[joined_near.groupby('ID_right')['distance'].idxmin()]
    return df_closest

def getObjetctOverArea(object,area,plot):
    over = gpd.overlay(object, area, how="intersection")

    if plot:
        fig, ax = plt.subplots(figsize=(10, 10))
        object.plot(ax=ax, color='Green', edgecolor='None', linewidth=2, label="Input objects")
        area.plot(ax=ax, color='None', edgecolor='red', linewidth=2, label="Study Area")
        over.plot(ax=ax, color='blue', edgecolor='None', linewidth=2, label="Over")

        ax.set_xticks([])
        ax.set_yticks([])
        plt.title("Study Area and Links")
        plt.show()

    return over


def test(a): print (a)