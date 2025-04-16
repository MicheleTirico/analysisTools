import sys
import pandas as pd
from toolbox.control import tools

class EmissionsCopert:
    def __init__(self,logger,parameters):
        self.__logger=logger
        self.__logger.logSep(cl=self,method=sys._getframe(),message="Init Copert estimation")
        self.__parameters = parameters
        self.__listPols= ["nox","pm10","no","no2"]

    def createDf(self,  run,listPathInput,listPathOutput):
        if run:
            self.__logger.log(cl=self,method=sys._getframe(),message="start create df Copert")
            df1=pd.read_csv(filepath_or_buffer=listPathInput[0],sep=",")
            self.__dfCopert=df1.rename(columns={"VIT":"av_sp_kph","Co2":"co2_g/km","Nox":"nox_g/km","Pm":"pm10_g/km"})[["av_sp_kph","nox_g/km","pm10_g/km","co2_g/km"]]# set_index("speedInKph",inplace=True)
            tools.storeDataframe(logger=self.__logger,pathStore=listPathOutput[0],df=df1)
            return self.__dfCopert

    def computeEmissions(self,run,listPathInput,listPathOutput):
        if run:
            self.__logger.logSep(cl=self,method=sys._getframe(),message="compute Copert emissions")
            df_traffic=pd.read_csv(filepath_or_buffer=listPathInput[0],sep=";")
            df_traffic=df_traffic.drop_duplicates()
            df1=pd.merge(df_traffic,self.__dfCopert,left_on="av_sp_kph_round",right_on="av_sp_kph")
            pols=["nox","pm10","co2"]
            for pol in pols:    df1[pol+"_g"]=df1[pol+"_g/km"]*df1.td/1000
            #df1=df1.drop(["nox_g/km","pm10_g/km","co2_g/km"],axis=1)
            tools.storeDataframe(logger=self.__logger,pathStore=listPathOutput[0],df=df1)
            return df1

    def setDateTime(self,run,df_emi,timestamp="timestamp",set_hh=True,set_mm=True):
        if run:
            self.__logger.log(cl=self,method=sys._getframe(),message="set datetime in column: {}".format(timestamp))
            df_emi = df_emi.copy()
            df_emi["ts"] = df_emi.ts - 30 * 60
            df_emi[timestamp] = pd.to_datetime(df_emi['ts'], unit='s')
            if set_hh: df_emi['hh'] = df_emi[timestamp].dt.hour
            if set_mm: df_emi['mm'] = df_emi[timestamp].dt.minute

            return df_emi

    def computeEmissionsNOx(self,run,df_emi,perNO):
        if run:
            self.__logger.log(cl=self,method=sys._getframe(),message="compute NO and NO2")
            df_emi = df_emi.copy()
            df_emi["no_g"] = perNO * df_emi["nox_g"]
            df_emi["no2_g"] = df_emi["nox_g"] - df_emi["no_g"]
            return df_emi

    def computeEmissionsPerDistance(self,run,df_emi,name_id='ID',distance="m"):
        if run:
            self.__logger.log(cl=self,method=sys._getframe(),message="compute emissions per distance: {}".format(distance))
            df_emi = df_emi.copy()
            for pol in self.__listPols: df_emi[pol+"_g/"+distance]=df_emi[pol+"_g"]/df_emi["length"]
            return df_emi

    def computeEmissions_groupped_per_period(self,run,df_emi,name_id='ID',period="hh"):
        if run:
            self.__logger.log(cl=self,method=sys._getframe(), message="group emission per period : {}".format(period))
            print(df_emi.info())
            df_emi = df_emi.copy()
            df_emi = df_emi.groupby(by=[name_id,"hh"]).sum().reset_index()
            return df_emi


    def computeEmissionsPerSecond(self,run,df_emi,grouppedBy="hh"):
        if run:
            self.__logger.log(cl=self,method=sys._getframe(),message="compute per period second")
            df_emi = df_emi.copy()

            # compute per second
            split=0
            if grouppedBy=="hh":    split=3600
            elif grouppedBy=="mm":  split= 60
            else:                   self.__logger.warning(cl=self,method=sys._getframe(), message="to implement",doQuit=False)

            for pol in self.__listPols: df_emi[pol + "_g/s"] = df_emi[pol + "_g"] / split

            return df_emi
