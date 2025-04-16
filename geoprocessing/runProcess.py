import sys
from qgis.core import *
import geopandas as gpd

class RunProcess:

    def __init__(self,logger):
        self.__logger=logger
        self.__logger.log(cl=self,method=sys._getframe(),message="init geoprocessing")

    def initQgis(self,prefixPath):
        self.__logger.log(cl=self,method=sys._getframe(),message="init Qgis")
        QgsApplication.setPrefixPath(prefixPath,True)
        from processing.core.Processing import Processing
        self.__qgs=QgsApplication([], False)
        self.__qgs.initQgis()
        Processing.initialize()  # needed to be able to use the functions afterwards

    def runQgisProcess(self,run,nameProcess,parameters):
        if run:
            self.__logger.log(cl=self,method=sys._getframe(),message="start  geoprocess: {}".format(nameProcess))
            import processing
            processing.run(nameProcess,parameters)
            self.__logger.log(cl=self,method=sys._getframe(),message="finish geoprocess: {}".format(nameProcess))

    def runQgisProcess_inOut(self,nameProcess,pathIn, pathOut,parameters):
        self.__logger.log(cl=self,method=sys._getframe(),message="start run geoprocess: {}, in: {}, out: {}, parameters: {}".format(nameProcess,pathIn,pathOut,parameters))

        if pathIn!=None:     parameters["INPUT"]=pathIn
        if pathOut!=None:   parameters["OUTPUT"]=pathOut
        import processing
        processing.run(nameProcess,parameters)
        self.__logger.log(cl=self,method=sys._getframe(),message="finish geoprocess: {}, out: {}".format(nameProcess,pathOut))

    def castFile (self,run,pathIn,pathOut):
        if run:
            self.__logger.log(cl=self,method=sys._getframe(),message="start  cast from: {}, to: {}".format(pathIn,pathOut))
            gdf = gpd.read_file(pathIn)
            gdf.to_file(pathOut)
            self.__logger.log(cl=self,method=sys._getframe(),message="finish cast. Out: {}".format(pathOut))



