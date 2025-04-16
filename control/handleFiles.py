import os
import sys
import shutil

class HandleFiles:
    def __init__(self,logger):
        self.__logger =logger
        self.__cwd=os.getcwd()+"/"

    def getDefCwd(self):   return self.__cwd
    def setLogger(self,logger): self.__logger=logger

    def deleteDirectories(self,paths):
        for path in paths :
            if os.path.exists(path):
                self.__logger.log(cl=self,method=sys._getframe(),message="delete directory: " +path)
                os.system("rm -r "+path)

    def createDirectories(self,paths):
        for path in paths :
            if os.path.exists(path)==False:
                try:self.__logger.log(cl=self,method=sys._getframe(),message="create directory in: "+path)
                except AttributeError: pass

                try: os.mkdir(self.__cwd+path)
                except FileExistsError: self.__logger.warning(cl=self,method=sys._getframe(),message="directory: {} exist".format(path),doQuit=False)

    def copyListFilesInDirectory(self,run,listPathIn,pathOut):
        if run:
            for path in listPathIn:
                self.__logger.log(cl=self,method=sys._getframe(),message="copy file {} in {}".format(path,pathOut))
                try :                shutil.copy(path, pathOut)
                except FileNotFoundError: self.__logger.warning(cl=self,method=sys._getframe(),message="file {} not founded".format(path),doQuit=False)

    def copyFilesFromDirectory(self,source_folder,destination_folder):
        for file_name in os.listdir(source_folder):
            # construct full file path
            source = source_folder + file_name
            destination = destination_folder + file_name
            # copy only files
            if os.path.isfile(source):
                shutil.copy(source, destination)
                self.__logger.log(cl=self,method=sys._getframe(),message="copy file {} from {} to {}".format(file_name,source_folder,destination_folder))

    def copyTree (self, run, source_dir, destination_dir):
        if run :
            self.__logger.log(cl=self,method=sys._getframe(),message="copy tree {} in {}".format(source_dir, destination_dir))
            try: shutil.copytree(source_dir, destination_dir)
            except FileExistsError : self.__logger.warning(cl=self,method=sys._getframe(),message="copy tree not allowed, tree in {} exist".format(source_dir, destination_dir),doQuit=False)

    def removeTreeAndCopyNewTree (self, run, source_dir, destination_dir):
        if run :
            self.__logger.log(cl=self,method=sys._getframe(),message="copy tree {} in {}. Remove old tree if exist.".format(source_dir, destination_dir))
            if os.path.exists(destination_dir):
                self.__logger.warning(cl=self, method=sys._getframe(),message="Remove old tree.",doQuit=False)
                shutil.rmtree(destination_dir)
            shutil.copytree(source_dir, destination_dir)

    def storeDataframe(self, pathStore, df):
        self.__logger.log(cl=None, method=None, message="Store dataframe in:{}".format(pathStore))
        df.to_csv(pathStore, sep=';')

    def storeGeoDataframe(self, pathStore, df):
        self.__logger.log(cl=None, method=None, message="Store geo-dataframe in:{}".format(pathStore))
        df.to_file(pathStore)

    def saveFig(self,fig, pathSave):
        self.__logger.log(cl=None,method=None,message="store figure at:{}".format(pathSave))
        fig.savefig(pathSave, bbox_inches="tight")
