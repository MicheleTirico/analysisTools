import sys
import csv
from lxml import etree

class GetTrajectories:
    def __init__(self, logger):
        self.__logger = logger
        self.__logger.log(cl=self, method=sys._getframe(), message="init get trajectories")

    # def setInputFiles(self,path_symuvia_xml):
    #     self.__logger.log(cl=None, method=None, message="input xml is: {}".format(path_symuvia_xml))
    #     self.__path_symuvia_xml=path_symuvia_xml
    # def setOutputPath(self,path_output):        self.path_output=path_output

    def setTree (self,run,path):
        if run:
            self.__logger.log(cl=None,method=None,message="set Tree")
            self.__tree=etree.parse(path)
            self.__context = etree.iterparse(path, events=("end",), tag="INST")

    def setTree_LF (self,run,path,isLf):
        if run:
            self.__logger.log(cl=None,method=None,message="set Tree, LF")
            if isLf:    self.__context = etree.iterparse(path, events=("end",), tag="INST")
            else:       self.__tree=etree.parse(path)

    def computeTrips(self,run,pathStore):
        if run:
            self.__logger.log(cl=None,method=None,message="start  compute compute trajectories")
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
            self.__logger.log(cl=None,method=None,message="finish compute trajectories ")


    def computeTrajectories(self,run,pathStore):
        if run:
            self.__logger.log(cl=None,method=None,message="start  compute compute trajectories")
            with open(pathStore, 'w') as f:

                writer=csv.writer(f,delimiter=";")
                # header=[i for i in self.__tree.xpath("/OUT/SIMULATION/VEHS/VEH")[0].attrib]
                header=["inst","abs","acc","dst","id","ord","tron","type","vit","voie","z"]

                writer.writerow(header)
                print(self.__tree)
                for inst in self.__tree.xpath("/OUT/SIMULATION/INSTANTS/INST"):
                    t=inst.attrib["val"]
                    for traj in inst.xpath("TRAJS/TRAJ"):
                        line =[t]+[traj.attrib[_] for _ in header[1:]]
                        writer.writerow(line)

            self.__logger.log(cl=None,method=None,message="csv stored in:{}".format(pathStore))
            self.__logger.log(cl=None,method=None,message="finish compute trajectories ")

    def computeTrajectories_LF(self,run,pathStore):
        if run:
            self.__logger.log(cl=None,method=None,message="start  compute compute trajectories")
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
                        if float(t)%60==0:  self.__logger.log(cl=None,method=None,message="time: {}.".format(t))

                        for traj in inst.xpath("TRAJS/TRAJ"):
                            # Write the line with trajectory data
                            line = [t] + [traj.attrib.get(attr, "") for attr in header[1:]]
                            writer.writerow(line)

                        # Free up memory by clearing the processed element
                        inst.clear()
                        while inst.getprevious() is not None:
                            del inst.getparent()[0]

            self.__logger.log(cl=None,method=None,message="csv stored in:{}".format(pathStore))
            self.__logger.log(cl=None,method=None,message="finish compute trajectories ")



