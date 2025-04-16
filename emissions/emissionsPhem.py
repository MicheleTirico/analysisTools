import shutil
import sys
import pandas as pd
from toolbox.control import tools
import numpy as np
class EmissionsPhem:
    def __init__(self,logger):
        self.__logger=logger
        self.__logger.log(cl=self,method=sys._getframe(),message="Init Phem estimation")

    def getSetupPhem(self): pass

    def get_df_percent_fleet(self,path_fleet_percent,run=True):
        if run:
            self.__logger.log(cl=None, method=sys._getframe(), message="Get fleet")
            # get fleet
            df_fleet=pd.read_csv(path_fleet_percent,sep=",")
            df_fleet["a"]= np.arange(1, len(df_fleet) + 1)
            return df_fleet

    def get_normalized_prob_type_vehicles (self,df_fleet,run=True):
        if run:
            self.__logger.log(cl=None, method=sys._getframe(), message="Get normalized values.")
            listOfTypeVehicles = list(df_fleet["a"])
            normalized_prob_type_vehicles = [v / sum(listOfTypeVehicles) for v in listOfTypeVehicles]
            return normalized_prob_type_vehicles

    def get_id_vehicles_random_type(self,run,df_traj,seed,listOfTypeVehicles,normalized_prob_type_vehicles):
        if run:
            self.__logger.log(cl=None, method=sys._getframe(), message="Get a DF where is associated to each id of vehicles a type of vehicle")
            np.random.seed(seed)
            df_id_type=pd.DataFrame(pd.DataFrame({'id': range(1, 10000+max(set(df_traj.id)))}))

            # Assign a new column with randomly chosen vehicle types
            df_id_type['vehicle type'] = np.random.choice(listOfTypeVehicles,size=len(df_id_type),p=normalized_prob_type_vehicles)

            return df_id_type

    def get_trajectories (self,df_traj,df_id_type,pathOut_traj_csv,pathOut_traj_fzp,run=True):
        if run:
            self.__logger.log(cl=None, method=sys._getframe(), message="Get trajectories.")

            # add type
            df_traj=df_traj.merge(df_id_type,on="id",how="left").reset_index()

            # handle columns
            df_traj = df_traj[df_traj["type"] == "VL"]
            df_traj = df_traj.rename(columns={"inst": "time", "abs": "x", "id": "vehicle number", "ord": "y", "vit": "speed"})
            df_traj["road inclination"] = "0"
            df_traj["segment number"] = "0"
            df_traj["time"] = df_traj["time"].astype(int)
            df_traj = df_traj.sort_values(["vehicle number", "time"])
            df_traj = df_traj[["time", "x", "y", "vehicle number", "speed", "road inclination", "vehicle type", "segment number"]]

            self.__logger.log(cl=None, method=None, message="Store dataframe in:{}".format(pathOut_traj_csv))
            df_traj.to_csv(pathOut_traj_csv, index=False, sep=";")

            self.__logger.log(cl=None, method=None,message="Save file {} as {}".format(pathOut_traj_csv,pathOut_traj_fzp))
            shutil.copyfile(pathOut_traj_csv, pathOut_traj_fzp)

            return df_traj



            logger.log(cl=None, method=None, message="Store dataframe in:{}".format(pathOut_traj_csv))
            df_traj.to_csv(pathOut_traj_csv, index=False, sep=";")

            logger.log(cl=None, method=None,
                       message="Save file {} as {}".format(pathOut_traj_csv, pathOut_traj_fzp.split("/")[-1]))
            shutil.copyfile(pathOut_traj_csv, pathOut_traj_fzp)

