import sys
import os
import csv
import pandas as pd
from lxml import etree
from toolbox.control import handleFiles
from toolbox.control.handleFiles import HandleFiles
from toolbox.control.logger import Logger

from analysisTools.traffic.getTrajectories.analysisCapteurs import AnalysisCapteurs
from scripts.parameters import parameters

import lxml
import pandas as pd
from toolbox.control import tools
from toolbox.control.logger import Logger
from toolbox.control.handleFiles import HandleFiles
import geopandas as gpd
from lxml import etree

class GetTrajectories:
    def __init__(self, logger):
        self.__logger = logger
        self.__logger.log(cl=self, method=sys._getframe(), message="init get trajectories")

    def get_trajectories_noiseModelling (self):
        self.__logger.logSep(cl=None, method=None, message="start get trajectories for noise analysis")

def main():
    # logger and handleFiles
    # ----------------------------------------------------------------------------------------------------------------------
    hf = HandleFiles(logger=None)
    hf.createDirectories([parameters.outputs, parameters.outputScenario])
    logger = Logger(storeLog=True, initStore=True, pathLog=parameters.pathFileLog)
    logger.logSep(cl=None, method=None, message="run Symuvia simulation")
    hf.setLogger(logger=logger)
    logger.setDisplay(True, True, True, True)
    logger.storeLocal(False)
    run_copyFiles=True
    run_trip=True
    run_list_links=True
    run_filter_trip=True

    for scenario in parameters.list_name_files:
        logger.logSep(cl=None, method=sys._getframe(), message="Run scenario: {}".format(scenario))
        parameters.outputSimulation_scenario=parameters.outputSimulation+scenario+"/"
        parameters.outputScenario_trajectories=parameters.outputSimulation_scenario+"traj/"
        parameters.outputSimulation_scenario_outXml=parameters.outputSimulation_scenario+"OUT/defaultOut_063000_093000_traf.xml"
        parameters.outputSimulation_scenario_traj=parameters.outputScenario_trajectories+"trajectories.csv"
        parameters.outputSimulation_scenario_traj_filtered = parameters.outputScenario_trajectories + "trajectories_filtered.csv"
        parameters.outputSimulation_scenario_output_sim_traj = parameters.outputScenario_trajectories + "output_sim_traj.csv"
        parameters.outputSimulation_scenario_output_sim_traj_inArea = parameters.outputScenario_trajectories + "output_sim_traj_inArea.csv"
        parameters.links_symuvia_inStudyArea = parameters.outputScenario_trajectories + parameters.name_links_6th + ".shp"

        hf.createDirectories([parameters.outputScenario_trajectories])

        # copy initial files
        hf.copyListFilesInDirectory(run=run_copyFiles,listPathIn=[parameters.resources + parameters.name_links_6th + _ for _ in [".cpg", ".dbf", ".prj", ".qmd", ".shp", ".shx"]],pathOut=parameters.outputScenario_trajectories)

        # get trip of all vehicles in the simulation
        if run_trip:
            logger.log(cl=None, method=None, message="get df {}.".format(parameters.outputSimulation_scenario_traj))
            ac = AnalysisCapteurs(logger=logger)
            try:
                ac.setTree(run=run_trip, path=parameters.outputSimulation_scenario_outXml)
            except OSError:
                logger.warning(cl=None, method=None, message="file not founded: {}".format(parameters.outputSimulation_scenario_outXml),doQuit=False)
                return
            except lxml.etree.XMLSyntaxError:
                logger.warning(cl=None, method=None, message="simulation not completed", doQuit=False)
                return
            ac.computeTrips(run=run_trip, pathStore=parameters.outputSimulation_scenario_traj)
        else:
            logger.log(cl=None, method=None, message="Df {} not computed.".format(parameters.outputSimulation_scenario_traj))

        df_trip = pd.read_csv(parameters.outputSimulation_scenario_traj, sep=";")

        # get only vehicles in the study area
        df_links_6th = None
        if run_list_links:
            logger.log(cl=None, method=None, message="compute df with links of study area {}.".format(parameters.outputSimulation_scenario_traj))
            gdf_links_6th = gpd.read_file(parameters.links_symuvia_inStudyArea)
            df_links_6th = pd.DataFrame(gdf_links_6th)
            tools.storeDataframe(logger=logger, pathStore=parameters.links_symuvia_inStudyArea, df=df_links_6th)
        else:
            logger.log(cl=None, method=None,  message="not compute df with links of study area. Use the df {}.".format(df_links_6th))
            df_links_6th = pd.read_csv(parameters.links_symuvia_inStudyArea, sep=";")


        # get list of vehicles that are pass through the study area
        list_links = list(df_links_6th.ID)

        df_trip_fil = None
        if run_filter_trip:
            # get list of links
            pattern = '|'.join(list_links)
            df_trip_fil = df_trip[df_trip['itineraire'].str.contains(pattern, case=False, na=False)]
            tools.storeDataframe(logger=logger, pathStore=parameters.outputSimulation_scenario_traj_filtered, df=df_trip_fil)
        else:
            df_trip_fil = pd.read_csv(parameters.outputSimulation_scenario_traj_filtered, sep=";")

        # Get all traj of vehicles. All vehicles, no filter, with algo lower memory
        logger.log(cl=None, method=None, message="TEST. Compute csv traj {}.".format(parameters.outputSimulation_scenario_traj))
        ac = AnalysisCapteurs(logger=logger)
        ac.setTree_LF(run=True, path=parameters.outputSimulation_scenario_outXml, isLf=True)
        ac.computeTrajectories_LF(run=False, pathStore=parameters.outputSimulation_scenario_output_sim_traj)

        # get traj for veh in area
        logger.log(cl=None, method=None, message="TEST. Compute csv traj in area {}.".format(parameters.outputSimulation_scenario_traj))
        ac.setLinksInArea(run=True, listLinks=list_links)
        ac.computeTrajectories_LF_area(run=True, pathStore=parameters.outputSimulation_scenario_output_sim_traj_inArea)

        # return path_df_traj_inArea




if __name__ == "__main__":  main()
