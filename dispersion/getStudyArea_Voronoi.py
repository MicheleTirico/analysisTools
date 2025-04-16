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
from analysisTools.geoprocessing.geoTools import *

class GetStudyArea_Voronoi:
    def __init__(self, logger, parameters):
        self.__logger = logger
        self.__logger.log(cl=self, method=sys._getframe(), message="init get study area for sirane")
        if parameters != None: self.set_parameters(parameters)

    def set_parameters(self, parameters):    self.__parameters = parameters
    def get_links_in_study_area(self,run,gdfListIn,listPathOut,plotOutputs):
        if run:
            self.__logger.log(cl=None, method=None, message="get links that are in the study area")
            gdf_studyArea = gdfListIn[0]#gpd.read_file(listPathIn[0])  # study area (6th)
            gdf_links = gdfListIn[1]#gpd.read_file( listPathIn[1])  # links in 6th

            gdf_links_inStudyArea = gpd.sjoin(gdf_links, gdf_studyArea, how='inner',predicate='intersects')  # links sirane inStudyArea
            tools.storeGeoDataframe(logger=self.__logger, pathStore=listPathOut[0], df=gdf_links)

            if plotOutputs:
                fig, ax = plt.subplots(figsize=(10, 10))
                gdf_links_inStudyArea.plot(ax=ax, color='Green', edgecolor='None', linewidth=2,label="links Symuvia")
                gdf_studyArea.plot(ax=ax, color='None', edgecolor='red', linewidth=2, label="Study Area")
                ax.set_xticks([])
                ax.set_yticks([])
                plt.title("Study Area and Links")
                plt.show()
            return gdf_links_inStudyArea

    def getVoronoi(self,run,gdfListIn,listPathOut,plotOutputs):
        if run:
            self.__logger.log(cl=None, method=None, message="get voronoi")
            gdf_studyArea, gdf_links_inStudyArea=gdfListIn[0],gdfListIn[1]

            # get vertices
            vertex_data = []
            for index, row in gdf_links_inStudyArea.iterrows():
                link_id = row["ID"]  # Change "id" to the actual column name of the link identifier
                line = row.geometry
                if line.geom_type == "LineString":
                    for coord in line.coords:
                        vertex_data.append({"link_id": link_id, "geometry": Point(coord)})

            vertices_gdf = gpd.GeoDataFrame(vertex_data, crs=gdf_links_inStudyArea.crs)             # Convert to GeoDataFrame
            vertices_gdf = vertices_gdf.drop_duplicates(subset=["geometry"])            # Remove duplicate points
            points = np.array([(p.x, p.y) for p in vertices_gdf.geometry])      # get points from vertices

            vor = Voronoi(points)                   # Compute Voronoi tessellation
            voronoi_cells = self.__voronoi_polygons(vor, bbox=self.__get_boudary_poligons(gdf_links_inStudyArea))

            # Create GeoDataFrame for tessellation
            tessellation_gdf = gpd.GeoDataFrame(geometry=voronoi_cells, crs=gdf_links_inStudyArea.crs)

            gdf_links_inStudyArea= gdf_links_inStudyArea[['ID', 'TYPE', 'NDDEB', 'NDFIN', 'WG', 'WD', 'HG', 'HD', 'MODUL_EMIS','geometry', 'id']]
            # assign id link
            gdf_joined = gpd.sjoin(tessellation_gdf, gdf_links_inStudyArea, how="inner", predicate="intersects")
            # dissolve by id links
            gdf_joined = gdf_joined.dissolve(by="ID").reset_index()
            if plotOutputs:
                fig, ax = plt.subplots(figsize=(10, 10))

                gdf_joined.plot(ax=ax, color='blue', edgecolor='black', label="voronoi")
                gdf_links_inStudyArea.plot(ax=ax, color='Red', edgecolor='Red', linewidth=2, label="links")
                vertices_gdf.plot(ax=ax, color='Green', label="vertices")
                ax.set_xticks([])
                ax.set_yticks([])
                plt.title("Study Area and Links")
                plt.show()

            tools.storeGeoDataframe(logger=self.__logger, pathStore=listPathOut[0], df=gdf_joined)
            return gdf_joined

    def get_links_sym_in_voronoi(self,run,gdfListIn,listPathOut):
        if run:
            self.__logger.log(cl=None, method=None, message="get links symuvia in voronoi")
            gdf_links,gdf_voronoi=gdfListIn[0],gdfListIn[1]
            gdf_links["len_tot"]=gdf_links.length
            over = gpd.overlay(gdf_links, gdf_voronoi, how='intersection', keep_geom_type=True)
            over["len_over"] = over.length
            over["len_per"] = over.len_over / over.len_tot
            over=over[['ID_1',"ID_2","len_per","geometry"]].rename(columns={"ID_1":"ID_sym","ID_2":"ID_sir"})
            tools.storeGeoDataframe(logger=self.__logger, pathStore=listPathOut[0], df=over)
            return over

    # Function to convert Voronoi regions into polygons
    def __voronoi_polygons(self,vor, bbox):
        """Convert Voronoi regions to polygons and clip them to a bounding box."""
        regions = []
        for region in vor.regions:
            if not -1 in region and region:
                poly = Polygon([vor.vertices[i] for i in region])
                poly = poly.intersection(bbox)  # Clip to bounding box
                regions.append(poly)
        return regions

    def __get_boudary_poligons(self,gdf):
        bbox = gdf.total_bounds  # (minx, miny, maxx, maxy)
        bounding_polygon = Polygon([
            (bbox[0], bbox[1]), (bbox[2], bbox[1]),
            (bbox[2], bbox[3]), (bbox[0], bbox[3])
        ])
        return  bounding_polygon