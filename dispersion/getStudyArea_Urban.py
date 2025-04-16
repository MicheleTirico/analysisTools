# import os
# import geopandas as gpd
# import pandas as pd
# from shapely.geometry import Polygon
# import geopandas as gpd
# import numpy as np
# from shapely.geometry import LineString, MultiPoint, Polygon
#
# from scipy.spatial import Voronoi
# import matplotlib.pyplot as plt
# from shapely.geometry import Point
#
# import geopandas as gpd
# import matplotlib.pyplot as plt
# from shapely.geometry import LineString
#
# from toolbox.control import tools
from analysisTools.geoprocessing.geoTools import *

class GetStudyArea_Urban:
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

    def get_corresp_in_area (self,df_corresp,gdf_links,id_corresp,id_links,listPathOut,run=True):
        if run:
            self.__logger.log(cl=None, method=None, message="get table of correspondence where links are in the area (by pandas merge, not by geopandas overlay)")
            df1=df_corresp.merge(gdf_links[[id_links]],left_on=id_corresp,right_on=id_links).reset_index().drop([id_links],axis=1)
            tools.storeDataframe(logger=self.__logger,pathStore=listPathOut[0],df=df1)
            return df1

    def set_corresp(self,run,pathIn,gdfListIn):
        if run:
            self.__logger.log(cl=None, method=None, message="set corresp table to input links")
            df_corresp=pd.read_csv(pathIn[0],delimiter='\t')

            gdf_links_sir =gdfListIn[0]
            print(gdf_links_sir)
            print(df_corresp)

            df_links_sir=gdf_links_sir[['ID', 'TYPE', 'NDDEB', 'NDFIN', 'WG', 'WD', 'HG', 'HD', 'MODUL_EMIS']].merge(df_corresp,left_on="ID",right_on="ID_STREET")
            print(df_links_sir)

    # not implemented
    def set_hight_sensors(self,run,gdfListIn,plot=False):
        return  gdfListIn[0]
        # if run:
        #     self.__logger.log(cl=None, method=None,message="get sensors as a set of points in the middle of line")
        #     midpoints = gdfListIn[0].copy()
        #     links = gdfListIn[1].copy()
        #     print(midpoints)
        #     print(links)




    def get_sensors_midpoint(self,run,gdfListIn,plot=False):
        if run:
            self.__logger.log(cl=None, method=None,message="get sensors as a set of points in the middle of line")
            links=gdfListIn[0].copy()
            def get_midpoint(line): return line.interpolate(0.5, normalized=True)

            links['midpoint'] = links['geometry'].apply(get_midpoint)
            midpoints = gpd.GeoDataFrame(links.drop(columns='geometry'),geometry=links['midpoint'],crs=links.crs)

            if plot:
                fig, ax = plt.subplots(figsize=(10, 10))
                links.plot(ax=ax, color='black', edgecolor='none', linewidth=2, label="links")
                midpoints.plot(ax=ax, color='blue', edgecolor='None', linewidth=2, label="midpoints")
                ax.set_xticks([])
                ax.set_yticks([])
                plt.title("Study Area and Links")
                plt.show()
            return midpoints

    def set_zones_to_sensors(self,run,gdfListIn,plot=False):
        if run:
            self.__logger.log(cl=None, method=None, message="set zones to sensors")
            midpoints = gdfListIn[0].copy()
            zones = gdfListIn[1].copy()
            gdf_joined = gpd.sjoin_nearest(midpoints, zones[['geometry', 'zone']], how="left").drop(columns=["midpoint"],axis=1)

            if plot:
                fig, ax = plt.subplots(figsize=(10, 10))
                zones.plot(ax=ax, color='black', edgecolor='none', linewidth=2, label="zones")
                gdf_joined.plot(ax=ax,column="zone", cmap='tab20', categorical=True, k=4 , legend=True, label="midpoints")
                ax.set_xticks([])
                ax.set_yticks([])
                plt.title("Study Area and Links")
                plt.show()
            return gdf_joined


