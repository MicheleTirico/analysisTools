import sys
from analysisTools.control.logger import Logger
from analysisTools.control.handleFiles import HandleFiles
import os
import geopandas as gpd
from scripts.parameters import parameters
from ctypes import cdll
import ctypes
import pandas as pd

# from analysisTools.simulation.symuvia_run_with_rerouting import  Symuvia_run_with_rerouting
# from symuvia_run_with_demand import Symuvia_run_with_demand

pd.set_option('display.max_columns', None)

class Symuvia:
    def __init__(self,logger):
        self.__logger=logger
        self.__logger.log(cl=self,method=sys._getframe(),message="init simulation Symuvia")

    def test (self):print ("test")
    def TEST_runcompleteSimulation(self):
        self.__logger.log(cl=self, method=sys._getframe(), message="TEST")

        # Load symuvia DLL into memory.
        lib_path = '/home/mtirico-lmfa/anaconda3/envs/symupy/lib/'
        lib_name = 'libSymuFlow.so'

        full_name = lib_path + lib_name
        os.chdir(lib_path)
        os.environ['PATH'] = lib_path + ';' + os.environ['PATH']
        self.__symuvia_dll = cdll.LoadLibrary(full_name)

    def setTime(self,start,end):
        self.__logger.log(cl=self, method=sys._getframe(), message="set time sim")
        start=start.split(":")
        end=end.split(":")
        time_sim="{}{}{}_{}{}{}".format(start[0],start[1],start[2],end [0],end [1],end [2])
        self.__timeSimString=time_sim
        t=time_sim.split("_")
        self.__timeSimHms=[ [int(t[0][0:2]),int(t[0][2:4]),int(t[0][4:6])],[int(t[1][0:2]),int(t[1][2:4]),int(t[1][4:6])]]
        self.__timeSimSec=[self.__timeSimHms[0][0]*60*60+self.__timeSimHms[0][1]*60+self.__timeSimHms[0][2],self.__timeSimHms[1][0]*60*60+self.__timeSimHms[1][1]*60+self.__timeSimHms[1][2]]
        self.__timeSimTs=[int(self.__timeSimSec[0]/15/60),int(self.__timeSimSec[1]/15/60+1)]

    def checkFileExist(self, path_sym_od, path_sym_input):
        self.__path_sym_od = path_sym_od
        self.path_sym_input = path_sym_input
        if os.path.exists(path_sym_od) == False:
            self.__logger.error(cl=None, method=None,message="file input od matrix  does not exist: {}".format(path_sym_od),error="not defined")
        else:
            self.__logger.log(cl=None, method=None, message="file input od matrix loaded : {}".format(path_sym_od))

        if os.path.exists(path_sym_input) == False:
            self.__logger.error(cl=None, method=None,message="file input simulation does not exist: {}".format(path_sym_input),error="not defined")
        else:
            self.__logger.log(cl=None, method=None, message="file input simulation loaded: {}".format(path_sym_input))

    def loadSymuflow(self,path_lib):
        self.__logger.log(cl=None,method=None,message="Start load library ({})".format(path_lib))

        self.__symuflow_ddl = cdll.LoadLibrary(path_lib)
        if self.__symuflow_ddl is None:
            self.__logger.error(cl=None,method=None,message="Symuflow lib not load",error="not defined")
            self.__logger.log(cl=None,method=None,message="end  load lib")

        self.__symuflow_ddl.SymGetTotalTravelTimeEx.restype = ctypes.c_double
        self.__symuflow_ddl.SymGetTotalTravelDistanceEx.restype = ctypes.c_double
        self.__logger.log(cl=None,method=None,message="Library was loaded")

    def loadSymuViaInput (self):                # SymuVia input loading
        self.__m = self.__symuflow_ddl.SymLoadNetworkEx(self.path_sym_input.encode('UTF8'))
        if(self.__m!=1):       self.__logger.error(cl=None,method=None,message="SymuVia input file not loaded !",error="not defined")
        else:           self.__logger.log(cl=None,method=None,message="SymuVia input data are loaded")

    def loadDemand(self,printDemand, setCreationToZero):            # demand loading
        self.__logger.log(cl=None,method=None,message="Load demand")
        self.__demand = pd.read_csv(self.__path_sym_od,sep=";")   #columns: origin;typeofvehicle;creation;path;destination
        # self.__demand["creation"]=self.__demand["creation"]+6*60*60+30*60
        # self.__demand=self.__demand[self.__demand["creation"]>=self.__timeSimSec[0]]
        # self.__demand["creation"] = self.__demand["creation"] -(6 * 60 * 60 + 30 * 60)
        if printDemand: print (self.__demand)

    def symuvia_input(self):    return self.__m
    def demand(self):           return self.__demand
    def logger(self):           return self.__logger
    def symuflow_ddl (self):    return self.__symuflow_ddl
    def timeSimSec(self):       return self.__timeSimSec

def main():
    # logger and handleFiles
    # ----------------------------------------------------------------------------------------------------------------------
    hf = HandleFiles(logger=None)
    hf.createDirectories([parameters.outputs, parameters.outputScenario, parameters.outputScenarioFig,parameters.outputSimulation])
    logger = Logger(storeLog=True, initStore=True, pathLog=parameters.pathFileLog)
    logger.logSep(cl=None, method=None, message="run Symuvia simulation")
    hf.setLogger(logger=logger)
    logger.setDisplay(True, True, True, True)
    logger.storeLocal(False)

    # get zones
    zones = gpd.read_file(parameters.zones)
    id_zone_0=list(zones[zones.zone==0].ID)

    # copyFilesInNewFolder
    hf.copyListFilesInDirectory(run=True,listPathIn=["{}{}".format(parameters.resourcesSimulation, _) for _ in os.listdir(parameters.resourcesSimulation)],pathOut=parameters.outputSimulation)
    s=Symuvia(logger=logger)
    s.checkFileExist(path_sym_od=parameters.sym_demand,path_sym_input=parameters.sym_sim_input)
    s.setTime(start=parameters.start_end_sim[0],end=parameters.start_end_sim[1])
    s.loadSymuflow(path_lib=parameters.sim_path_lib)
    s.loadDemand(printDemand=False, setCreationToZero=True)
    s.loadSymuViaInput()

    # sim_with_demand = Symuvia_run_with_demand(symuvia=s).run(run=False)
    # sim_with_rerouting = Symuvia_run_with_rerouting(symuvia=s).run(run=True,withPath=True,listLinksToCheck=id_zone_0,dynamicTimeSlot=parameters.dynamicTimeSlot)

if __name__ == "__main__":  main()
