import sys
import pandas as pd
from toolbox.control import tools
import numpy as np
import geopandas as gpd

class EditZones:
    def __init__    (self, logger,parameters):
        self.__logger = logger
        self.__logger.log(cl=self, method=sys._getframe(), message="init edit df zones")
        if parameters!=None: self.set_parameters(parameters)

    def set_parameters(self, parameters):    self.__parameters = parameters

    def createDfZones(self,run,listPathInput, listPathOutput):
        if run:
            self.__logger.logSep(cl=self, method=sys._getframe(), message="start create zones")
            df0 = pd.read_csv(filepath_or_buffer=listPathInput[0], sep=";")
            df1 = pd.read_csv(filepath_or_buffer=listPathInput[1], sep=";")
            df2 = pd.read_csv(filepath_or_buffer=listPathInput[2], sep=";")
            gdf_links=gpd.read_file(listPathInput[3])
            gdf_links_6th=gpd.read_file(listPathInput[4])
            # find zones
            set_6th=set(gdf_links_6th.ID)
            set_zone0=set(df0.closest_link_id)
            set_zone1=set(df1.closest_link_id)
            set_zone2=set(df2.id_n1)
            # drop nan
            set_zone1 = {x for x in set_zone1 if not (isinstance(x, float) and np.isnan(x))}
            # set zones
            gdf_links["zone"]=4
            gdf_links.loc[gdf_links['ID'].isin(set_6th), 'zone'] = 3
            gdf_links.loc[gdf_links['ID'].isin(set_zone2), 'zone'] = 2
            gdf_links.loc[gdf_links['ID'].isin(set_zone1), 'zone'] = 1
            gdf_links.loc[gdf_links['ID'].isin(set_zone0), 'zone'] = 0
            # store
            tools.storeGeoDataframe(logger=self.__logger,pathStore=listPathOutput[0],df=gdf_links)
            return gdf_links

    # TODO
    def addCumZones(self,run,listPathInput,gdf_links, listPathOutput):
        if run:
            self.__logger.logSep(cl=self, method=sys._getframe(), message="add cumulative zone (schools=0+1+2, 6th=0+1+2+3)")

            if listPathInput==None:             df1=gdf_links
            else: df1 = pd.read_csv(filepath_or_buffer=listPathInput[0], sep=";")

            df1["isSchool"]=0
            df1.loc[(df1.zone==0) | (df1.zone==1) | (df1.zone==2),"isSchool"]=1

            df1["is6th"]=0
            df1.loc[(df1.zone==0) | (df1.zone==1) | (df1.zone==2) | (df1.zone==3),"is6th"]=1
            tools.storeGeoDataframe(logger=self.__logger,pathStore=listPathOutput[0],df=gdf_links)
            return gdf_links

