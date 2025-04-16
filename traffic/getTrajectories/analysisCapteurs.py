import sys
import os
import csv
import pandas as pd
from lxml import etree
from toolbox.control import handleFiles

class AnalysisCapteurs:
    def __init__(self,logger):
        self.__logger=logger
        self.__logger.log(cl=self,method=sys._getframe(),message="init compute capteurs")

    def setParams(self,listInput):
        self.__listInput=listInput

    def setTree (self,run,path):
        if run:
            self.__logger.log(cl=None,method=None,message="set Tree")
            self.__tree=etree.parse(path)
            self.__context = etree.iterparse(path, events=("end",), tag="INST")
            self.__logger.log(cl=self, method=sys._getframe(), message="Tree set")

    def setLinksInArea(self,run,listLinks):
        if run:
            self.__logger.log(cl=None,method=None,message="set list links")
            self.__listLinks=listLinks

    def setTree_LF (self,run,path,isLf):
        if run:
            self.__logger.log(cl=None,method=None,message="set Tree, LF")
            if isLf:    self.__context = etree.iterparse(path, events=("end",), tag="INST")
            else:       self.__tree=etree.parse(path)

    def computeCapteurs_mfd(self,run,pathStore,xpath="/OUT/SIMULATION/GESTION_CAPTEUR/CAPTEURS_MFD"):
        if run:
            self.__logger.log(cl=None,method=None,message="start  compute compute list of selected values")
            p,id,distance_totale_parcourue,vitesse_spatiale,debit_sortie ,temps_total_passe= [],[],[],[],[],[]
            for CAPTEURS_MFD in self.__tree.xpath(xpath):
                print("capteurs_mfd"+str(CAPTEURS_MFD))
                # self.__logger.log(cl=None,method=None,message="read the period: {}".format(periode))
                for periode in CAPTEURS_MFD :
                    for capt in periode.xpath('CAPTEURS/CAPTEUR'):
                        p.append(float(periode.get("debut")))
                        id.append(str(capt.get("id")))
                        distance_totale_parcourue.append(float(capt.get("distance_totale_parcourue")))
                        vitesse_spatiale.append(float(capt.get("vitesse_spatiale")))
                        debit_sortie.append(float(capt.get("debit_sortie")))
                        temps_total_passe.append(float(capt.get("temps_total_passe")))
                        if capt.get("id")=="CAPT_T_997243908_toRef":break

            df2 = pd.DataFrame({"p" : p,"id": id,"distance_totale_parcourue": distance_totale_parcourue,"vitesse_spatiale": vitesse_spatiale,"debit_sortie":debit_sortie,"temps_total_passe":temps_total_passe})

            self.__logger.log(cl=None,method=None,message="start store dataframe in:{}".format(pathStore))
            df2.to_csv(pathStore, sep=';')
            self.__logger.log(cl=None,method=None,message="finish compute compute list of selected values")


    def computeSelectedColums(self,run,pathStore,xpath="/OUT/SIMULATION/GESTION_CAPTEUR/CAPTEURS_MFD"):
        if run:
            self.__logger.log(cl=None,method=None,message="start  compute compute list of selected values")
            p,id,distance_totale_parcourue,vitesse_spatiale,debit_sortie ,temps_total_passe= [],[],[],[],[],[]
            for periode in self.__tree.xpath(xpath):
                # self.__logger.log(cl=None,method=None,message="read the period: {}".format(periode))
                for capt in periode.xpath("CAPTEURS/CAPTEUR"):
                    print(capt)
                    p.append(float(periode.get("debut")))
                    id.append(str(capt.get("id")))
                    distance_totale_parcourue.append(float(capt.get("distance_totale_parcourue")))
                    vitesse_spatiale.append(float(capt.get("vitesse_spatiale")))
                    debit_sortie.append(float(capt.get("debit_sortie")))
                    temps_total_passe.append(float(capt.get("temps_total_passe")))
                    if capt.get("id")=="CAPT_T_997243908_toRef":break

            df2 = pd.DataFrame({"p" : p,"id": id,"distance_totale_parcourue": distance_totale_parcourue,"vitesse_spatiale": vitesse_spatiale,"debit_sortie":debit_sortie,"temps_total_passe":temps_total_passe})

            self.__logger.log(cl=None,method=None,message="start store dataframe in:{}".format(pathStore))
            df2.to_csv(pathStore, sep=';')
            self.__logger.log(cl=None,method=None,message="finish compute compute list of selected values")


    def computeCapteursGlobal(self,run,pathStore):
        if run:
            self.__logger.log(cl=None,method=None,message="start  compute compute capteurs global")
            with open(pathStore, 'w') as f:
                writer=csv.writer(f,delimiter=";")
                header=[i for i in self.__tree.xpath("/OUT/SIMULATION/GESTION_CAPTEUR/CAPTEUR_GLOBAL/PERIODE")[0].attrib]
                writer.writerow(header)

                for periode in self.__tree.xpath("/OUT/SIMULATION/GESTION_CAPTEUR/CAPTEUR_GLOBAL/PERIODE"):
                    # self.__logger.log(cl=None,method=None,message="read the period: {}".format(periode))
                    line =[]
                    for attrib in periode.attrib:    line.append(periode.get(attrib))
                    writer.writerow(line)

            self.__logger.log(cl=None,method=None,message="csv stored in:{}".format(pathStore))
            self.__logger.log(cl=None,method=None,message="finish compute capteurs global ")

    def computeTrajectories_LF_area(self,run,pathStore):
        if run:
            self.__logger.log(cl=None,method=None,message="start  compute compute trajectoires in area")
            with open(pathStore, 'w') as f:

                writer=csv.writer(f,delimiter=";")
                # header=[i for i in self.__tree.xpath("/OUT/SIMULATION/VEHS/VEH")[0].attrib]
                header=["inst","abs","acc","dst","id","ord","tron","type","vit","voie","z"]

                with open(pathStore, 'w', newline='') as f:
                    writer = csv.writer(f, delimiter=";")
                    writer.writerow(header)  # Write the header

                    # Iterate over the XML context for each INST element
                    for event, inst in self.__context:
                        t = inst.attrib["val"]
                        if float(t)%60==0: self.__logger.log(cl=None,method=None,message="time: {}.".format(t))

                        for traj in inst.xpath("TRAJS/TRAJ"):
                            # Write the line with trajectory data
                            if traj.attrib['tron'] in self.__listLinks:
                                line = [t] + [traj.attrib.get(attr, "") for attr in header[1:]]
                                writer.writerow(line)
                            # else:   self.__logger.warning(cl=None,method=None,message="veh not in area",doQuit=False)

                        # Free up memory by clearing the processed element
                        inst.clear()
                        while inst.getprevious() is not None:
                            del inst.getparent()[0]

            self.__logger.log(cl=None,method=None,message="csv stored in:{}".format(pathStore))
            self.__logger.log(cl=None,method=None,message="finish compute trajectoires ")

    def computeTrips(self,run,pathStore):
        if run:
            self.__logger.log(cl=None,method=None,message="start  compute compute trips")
            with open(pathStore, 'w') as f:
                writer=csv.writer(f,delimiter=";")
                # header=[i for i in self.__tree.xpath("/OUT/SIMULATION/VEHS/VEH")[0].attrib]
                header=["id","dstParcourue","entree","instC","instE","instS","itineraire","sortie","lib","type","vx","w"]

                writer.writerow(header)
                for veh in self.__tree.xpath("/OUT/SIMULATION/VEHS/VEH"):
                    line =[]
                    for attrib in header:        line.append(veh.get(attrib))
                    writer.writerow(line)

            self.__logger.log(cl=None,method=None,message="csv stored in:{}".format(pathStore))
            self.__logger.log(cl=None,method=None,message="finish compute trajectoires ")


def main():
    # ----------------------------------------------------------------------------------------------------------------------
    # run class
    # ----------------------------------------------------------------------------------------------------------------------
    pathResources="resources/"
    pathOutputDir="outputs/"
    pathOutput=pathOutputDir+"output_03/"
    pathOutputSim=pathResources#pathOutput+"OUT2/"
    prefix,time,suffix="defaultOut_","063000_110000","_traf_2.xml"
    name_file_output=prefix+time+suffix
    pathOutputXml=pathOutputSim+name_file_output

    # ----------------------------------------------------------------------------------------------------------------------
    hf=handleFiles.HandleFiles(logger=None)
    hf.createDirectories([pathOutputDir,pathOutput])
    logger=logger.Logger(storeLog=True,initStore=True,pathLog=pathOutput+"log_parseCapteurs.md")
    hf.setLogger(logger=logger)
    logger.setDisplay(True,True,True,True)
    logger.storeLocal(False)
    cwd=hf.getDefCwd()
    logger.log(cl=None,method=None,message="start  compute parse Symuvia capteurs")

    # test file exist
    #---------------------------------------------------------------------------
    if os.path.exists(pathOutputXml)==False:
        logger.error(cl=None,method=None,message="file input does not exist: {}".format(pathOutputXml),error="not defined")
        quit()
    else :
        logger.log(cl=None,method=None,message="file input loaded : {}".format(pathOutputXml))


    # run capteurs
    # ----------------------------------------------------------------------------------------------------------------------
    ac=AnalysisCapteurs(logger=logger)
    ac.setTree(run=True,path=pathOutputXml)
    ac.computeSelectedColums(run=True,pathStore=pathOutput+prefix+time+"_sym_capteurs_selected_2.csv")
    ac.computeCapteursGlobal(run=True,pathStore=pathOutput+prefix+time+"_sym_capteurs_global_2.csv")
    ac.computeTrips(run=True,pathStore=pathOutput+prefix+time+"_sym_capteurs_trajectoires_2.csv")

if __name__ == "__main__":  main()
