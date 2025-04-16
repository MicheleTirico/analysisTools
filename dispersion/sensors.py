import sys
import pandas as pd
import geopandas as gpd
import toolbox
import os
from analysisTools import tools
from analysisTools.control.tools import storeDataframe
from analysisTools.tools import get_list_period_day_hh
from scripts.parameters import parameters
from datetime import datetime, timedelta

class Sensors:
    def __init__(self, logger):
        self.__logger = logger
        self.__logger.log(cl=self, method=sys._getframe(), message="init Sensors analysis")
        self.__sensors=None

    def get_df_sensors(self,run,pathIn,period_day,period_hh,listPathOutput):
        if run:
            self.__logger.log(cl=self, method=sys._getframe(),message="get a df with all sensors data")
            list_day_hh = get_list_period_day_hh(period_day, period_hh)

            list_YYYYMMDDHHMM=[datetime.strptime(_, "%d/%m/%Y %H:%M").strftime("%Y%m%d%H") for _ in list_day_hh]
            df=pd.DataFrame()
            for file_name in os.listdir(pathIn):
                file_path = os.path.join(pathIn, file_name)  # Get full path
                if os.path.isfile(file_path):  # Ensure it's a file (not a directory)
                    YYYYMMDDHHMM=file_path.split("/")[-1].split(".")[0].split("_")[1]
                    if file_path.split("/")[-1].split(".")[0].split("_")[1] in list_YYYYMMDDHHMM:
                        df1=pd.read_csv(file_path,sep="\t")
                        df1["date"]=YYYYMMDDHHMM
                        df1["ymd"]=YYYYMMDDHHMM[:-2]
                        df1["hh"]=YYYYMMDDHHMM[-2:]
                        df1["mm"] = YYYYMMDDHHMM[4:6]

                        df=pd.concat((df,df1))
            storeDataframe(logger=self.__logger, pathStore=listPathOutput[0], df=df)
            return df

    def add_zones_to_sensors(self,run,df_out_sensors,gpd_sensors,listPathOutput):
        if run:
            self.__logger.log(cl=self, method=sys._getframe(),message="Add zones to sensors.")
            df_out_sensors=pd.merge(df_out_sensors,gpd_sensors[['ID',"zone"]],left_on="Id",right_on="ID",how="left").drop(columns="ID")
            storeDataframe(logger=self.__logger, pathStore=listPathOutput[0], df=df_out_sensors)
            return df_out_sensors

    def get_df_sensors_mean(self,run,df_out_sensors,listPathOutput):
        if run:
            self.__logger.log(cl=self, method=sys._getframe(), message="get annual mean")
            df1=df_out_sensors.copy()[['Id','NO2', 'NO', 'O3', 'PM',  'hh']]
            df1=df1.groupby(["Id","hh"]).mean().reset_index()
            df1=pd.merge(df1,df_out_sensors[['Id',"zone",'X','Y','Z',"sim"]],how="left").drop_duplicates()
            storeDataframe(logger=self.__logger, pathStore=listPathOutput[0], df=df1)
            return df1


