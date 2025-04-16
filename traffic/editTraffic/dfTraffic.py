import sys
# from numpy import np
import csv
import pandas as pd
from lxml import etree
from toolbox.control import handleFiles
import sys
import pandas as pd
from toolbox.control import tools
import numpy as np
import geopandas as gpd



class DfTraffic:
    def __init__(self,logger,parameters):
        self.__logger=logger
        self.__logger.log(cl=self,method=sys._getframe(),message="init edit df traffic")
        self.set_parameters(parameters)

    def set_parameters(self,parameters):    self.__parameters=parameters

    # deprecated
    def setTme(self):
        # get start and end time of simulation
        t_second_start=[int(_) for _ in self.__parameters.start_end_results[0].split(":")]
        t_second_end=[int(_) for _ in self.__parameters.start_end_results[1].split(":")]
        self.__start_end_results_seconds=[t_second_start[0]*60*60+t_second_start[1]*60+t_second_start[2],t_second_end[0]*60*60+t_second_end[1]*60+t_second_end[2]]

    def createDfTraffic(self, run, listPathInput, listPathOutput):
        if run:
            self.__logger.logSep(cl=self, method=sys._getframe(), message="start compute traffic")
            df1 = pd.read_csv(filepath_or_buffer=listPathInput[0], sep=";")
            self.__logger.log(cl=None, method=None, message="handle name columns")
            df1 = df1.rename(columns={'p': "ts", 'id': "id_capt", 'distance_totale_parcourue': "td", 'vitesse_spatiale': 'av_sp_mps','debit_sortie': "nVeh", 'temps_total_passe': "tt"})
            df1["id_link"] = df1["id_capt"].str.replace("CAPT_", "")  # get id links
            df1=df1.drop(["id_capt","Unnamed: 0"],axis=1)
            tools.storeDataframe(logger=self.__logger, pathStore=listPathOutput[0], df=df1)
            return df1


    def addSpatialSpeed(self,run,listPathInput, listPathOutput):
        if run:
            self.__logger.log(cl=None, method=None, message="compute spatial speed")
            df1 = pd.read_csv(filepath_or_buffer=listPathInput[0], sep=";")
            df1.loc[df1["av_sp_mps"] > 90 / 3.6, "av_sp_mps"] = 90 / 3.6
            df1["av_sp_kph"] = df1["av_sp_mps"] * 3.6
            df1["av_sp_kph_round"] = np.round(df1["av_sp_mps"] * 3.6).astype("int")
            df1["av_sp_mps_round"] = np.round(df1["av_sp_mps"]).astype("int")
            tools.storeDataframe(logger=self.__logger, pathStore=listPathOutput[0], df=df1)
            return df1

    def addLength(self, run, listPathInput, listPathOutput):
        if run:
            self.__logger.log(cl=None, method=None, message="add length")
            df1 = pd.read_csv(filepath_or_buffer=listPathInput[0], sep=";")
            df1_len = gpd.read_file(listPathInput[1])
            df1_len["length"] = df1_len.length
            df1_len = df1_len[["ID", "length"]]
            df1 = pd.merge(df1, df1_len, right_on="ID", left_on="id_link", how="left")
            df1 = df1.dropna()
            tools.storeDataframe(logger=self.__logger, pathStore=listPathOutput[0], df=df1)
            return df1

    def addZonesSchools(self, run, listPathInput, listPathOutput):
        if run:
            self.__logger.log(cl=None, method=None, message="add zones schools")
            df1 = pd.read_csv(filepath_or_buffer=listPathInput[0], sep=";")
            gdf_zones=gpd.read_file(listPathInput[1])
            df1=df1.merge(gdf_zones[["ID","zone",'isSchool', 'is6th']],on="ID").reset_index()
            df1=df1.drop(['Unnamed: 0.2', 'Unnamed: 0.1', 'Unnamed: 0'],axis=1)
            tools.storeDataframe(logger=self.__logger, pathStore=listPathOutput[0], df=df1)
            return df1

    def concatDf(self,run,list_name_df,listPathOutput):
        if run:
            self.__logger.log(cl=None, method=None, message="concat df traffic")
            listdf=[]
            for i in range(len(list_name_df)):
                df=pd.read_csv("{}{}{}".format(self.__parameters.outputScenario,list_name_df[i],"_df_traffic.csv"),sep=";")
                df["sim"]=list_name_df[i]
                listdf.append(df)
            df1=pd.concat(listdf)
            tools.storeDataframe(logger=self.__logger, pathStore=listPathOutput[0], df=df1)
            return df1

    def set_datetime(self,run, listPathInput, listPathOutput,name_datetime,name_seconds,format):
        if run:
            self.__logger.log(cl=None, method=None, message="set datetime")
            df1 = pd.read_csv(filepath_or_buffer=listPathInput[0], sep=";")
            df1[name_datetime] = pd.to_datetime(df1[name_seconds], unit='s').dt.strftime(format)
            tools.storeDataframe(logger=self.__logger, pathStore=listPathOutput[0], df=df1)
            return df1

    def addSpeedVariability(self, run, listPathInput, listPathOutput):
        print("TODO")
        quit()
        if run:
            self.__logger.log(cl=None, method=None, message="add column density")
            df1 = pd.read_csv(filepath_or_buffer=listPathInput[0], sep=";")


    def addDensity(self, run, listPathInput, listPathOutput):
        if run:
            self.__logger.log(cl=None, method=None, message="add column density")
            df1 = pd.read_csv(filepath_or_buffer=listPathInput[0], sep=";")
            if "length" in df1.columns :self.__logger.warning(cl=None, method=None, message="column length has been added previously",doQuit=False)
            else:                       self.__logger.error(cl=None, method=None, message="should add column length",error=None)
            df1["density"]=df1.nVeh/df1.length
            tools.storeDataframe(logger=self.__logger, pathStore=listPathOutput[0], df=df1)
            return df1

    def setTimeStartSimulation(self, run, listPathInput, listPathOutput):
        if run:
            self.__logger.log(cl=None, method=None, message="set time start simulation")
            df1 = pd.read_csv(filepath_or_buffer=listPathInput[0], sep=";")

            df1["ts"]=df1.ts+self.__parameters.start_end_results_seconds[0]

            tools.storeDataframe(logger=self.__logger, pathStore=listPathOutput[0], df=df1)
            return df1


    def setStartEndTimeResults(self, run, listPathInput, listPathOutput):
        if run:
            self.__logger.log(cl=None, method=None, message="cut dataframe by time")
            df1 = pd.read_csv(filepath_or_buffer=listPathInput[0], sep=";")
            df1=df1[df1.ts>=self.__parameters.start_end_results_seconds[0]]
            df1 = df1[df1.ts < self.__parameters.start_end_results_seconds[1]]
            tools.storeDataframe(logger=self.__logger, pathStore=listPathOutput[0], df=df1)
            return df1

    def get_df_groupby_ts(self, run, df, groupby, indicators, listPathOut):
        if run:
            df = df[indicators]
            self.__logger.log(cl=self, method=sys._getframe(),message="get df grouped by ts. Compute average speed and density")
            df1 = df.groupby(by=groupby).sum().reset_index()[indicators]
            df1["av_sp_mps"] = df1.td / df1.tt
            df1["av_sp_kpm"] = df1.td / df1.tt * 3.6
            df1_density = df.groupby(by=groupby).mean().reset_index()[groupby + ["density"]]
            df1 = df1.merge(df1_density, on=groupby, suffixes=("_x", ""))
            if listPathOut != None: tools.storeDataframe(logger=self.__logger, pathStore=listPathOut[0], df=df1)
            return df1

    # TODO
    def addPeriod(self, run, listPathInput, listPathOutput):
        if run:
            self.__logger.log(cl=None, method=None, message="add length")
            df1 = pd.read_csv(filepath_or_buffer=listPathInput[0], sep=";")
            df1["period"] = 1
            df1.loc[(df1['ts'] <= self.__parameters.start_end_control_seconds[0]), "period"] = 0
            df1.loc[(df1['ts'] > self.__parameters.start_end_control_seconds[1]), "period"] = 2
            df1 = df1.dropna()
            tools.storeDataframe(logger=self.__logger, pathStore=listPathOutput[0], df=df1)
            return df1
