import sys
from toolbox.control.logger import Logger
from toolbox.control.handleFiles import HandleFiles
import geopandas as gpd
from lxml import etree
import xml.etree.ElementTree as ET

class EditXmlSymuvia:
    def __init__(self,logger,handleFiles):
        self.__logger=logger
        self.__hf=handleFiles
        self.__logger.log(cl=self,method=sys._getframe(),message="init editXmlSymuvia ")
    def test (self):print ("test")
    def removeLinks(self,run,pathInXml,pathOutXml,listLinksToRemove):
        if run:
            self.__logger.logSep(cl=self,method=sys._getframe(),message="start remove links")
            # self.__hf.copyListFilesInDirectory(run=True,listPathIn=[listPathInput[0]],pathOut=listPathOutput[0])
            tree = etree.parse(pathInXml)
            for element in tree.xpath("/ROOT_SYMUBRUIT/RESEAUX[1]/RESEAU[1]/TRONCONS[1]/TRONCON"):
                if element.attrib["id"] in listLinksToRemove :
                    parent = element.find("..")
                    parent.remove(element)
            tree.write(pathOutXml)
            self.__logger.log(cl=self,method=sys._getframe(),message="end remove links")
            return pathOutXml


    def removeDemandInXml(self,run ,pathInXml,pathOutXml):
        if run :
            self.__logger.logSep(cl=self,method=sys._getframe(),message="start remove demand from xml")
            input_ref=ET.parse(pathInXml)
            root_node=input_ref.getroot()
            nDem=0
            for ext in root_node.iterfind('.//TRAFIC/EXTREMITES/EXTREMITE/FLUX_TYPEVEHS/FLUX_TYPEVEH/FLUX/DEMANDES'):
                nDem = nDem+1
                for dem in ext.iterfind('DEMANDE'):
                    dem.set('niveau','0')

            for ext in root_node.iterfind('.//TRAFIC/ZONES_DE_TERMINAISON/ZONE_DE_TERMINAISON/FLUX_TYPEVEHS/FLUX_TYPEVEH/FLUX/DEMANDES'):
                nDem = nDem+1
                for dem in ext.iterfind('DEMANDE'):
                    dem.set('niveau','0')

            self.__logger.logSep(cl=self,method=sys._getframe(),message="finish remove demand from xml")
            input_ref.write(pathOutXml)


            return pathOutXml

    def addPlagesHoraires(self,run,pathInXml,pathOutXml, attributeValue):
        if run:
            self.__logger.log(cl=self,method=sys._getframe(),message="start add plage horaire. Attribute={}".format(attributeValue))
            tree = etree.parse(pathInXml)
            root=tree.getroot()
            for PLAGES_TEMPORELLES in tree.xpath("/ROOT_SYMUBRUIT/PLAGES_TEMPORELLES[1]"):
                new_element=etree.Element("PLAGE_TEMPORELLE", id=attributeValue[0],debut=attributeValue[1][0],fin=attributeValue[1][1])
                if PLAGES_TEMPORELLES is not None:
                    PLAGES_TEMPORELLES.insert(0, new_element)
                else: self.__logger.warning(cl=self,method=sys._getframe(),message="parent does not found: {}".format(str(PLAGES_TEMPORELLES)),doQuit=False)
            tree.write(pathOutXml)
            return pathOutXml

    def addDynamicLimit(self,run,pathInXml,pathOutXml,listLinkschageAttribute, attributeValue):
        if run:
            self.__logger.logSep(cl=self,method=sys._getframe(),message="start add dynamic limits")
            tree = etree.parse(pathInXml)
            for TRONÇON in tree.xpath("/ROOT_SYMUBRUIT/RESEAUX[1]/RESEAU[1]/TRONCONS[1]/TRONCON"):
                try: vit_reg=TRONÇON.attrib["vit_reg"]
                except : vit_reg="0"
                if TRONÇON.attrib["id"] in listLinkschageAttribute :
                    VITESSES_REG = etree.Element("VITESSES_REG")
                    if TRONÇON is not None:
                        TRONÇON.insert(0, VITESSES_REG)
                        VITESSE_REG=etree.Element("VITESSE_REG", duree=attributeValue["namePlage"])
                        if VITESSES_REG is not None:
                            VITESSES_REG.insert(0, VITESSE_REG)
                            # before and after
                            VITESSE_REG_before=etree.Element("VITESSE_REG", duree="before_"+attributeValue["namePlage"])
                            VITESSE_REG_PAR_TYPE_before=etree.Element("VITESSE_REG_PAR_TYPE", types_vehicules="VL")
                            VITESSE_REG_PAR_VOIE_before=etree.Element("VITESSE_REG_PAR_VOIE",vitesse=vit_reg)
                            VITESSES_REG.insert(0, VITESSE_REG_before)
                            VITESSE_REG_before.insert(0, VITESSE_REG_PAR_TYPE_before)
                            VITESSE_REG_PAR_TYPE_before.insert(0, VITESSE_REG_PAR_VOIE_before)
                            VITESSE_REG_after=etree.Element("VITESSE_REG", duree="after_"+attributeValue["namePlage"])
                            VITESSE_REG_PAR_TYPE_after=etree.Element("VITESSE_REG_PAR_TYPE", types_vehicules="VL")
                            VITESSE_REG_PAR_VOIE_after=etree.Element("VITESSE_REG_PAR_VOIE",vitesse=vit_reg)
                            VITESSES_REG.insert(0, VITESSE_REG_after)
                            VITESSE_REG_after.insert(0, VITESSE_REG_PAR_TYPE_after)
                            VITESSE_REG_PAR_TYPE_after.insert(0, VITESSE_REG_PAR_VOIE_after)

                            VITESSE_REG_PAR_TYPE=etree.Element("VITESSE_REG_PAR_TYPE", types_vehicules="VL")
                            if VITESSE_REG is not None:
                                VITESSE_REG.insert(0, VITESSE_REG_PAR_TYPE)
                                VITESSE_REG_PAR_VOIE=etree.Element("VITESSE_REG_PAR_VOIE",vitesse="{}".format(attributeValue["dynamicLimits"]))
                                if VITESSE_REG_PAR_TYPE is not None:
                                    VITESSE_REG_PAR_TYPE.insert(0, VITESSE_REG_PAR_VOIE)
                                else: self.__logger.warning(cl=self,method=sys._getframe(),message="parent does not found: {}".format(str(VITESSE_REG_PAR_TYPE)),doQuit=False)
                            else: self.__logger.warning(cl=self,method=sys._getframe(),message="parent does not found: {}".format(str(VITESSE_REG)),doQuit=False)
                        else: self.__logger.warning(cl=self,method=sys._getframe(),message="parent does not found: {}".format(str(VITESSES_REG)),doQuit=False)
                    else: self.__logger.warning(cl=self,method=sys._getframe(),message="parent does not found: {}".format(str(TRONÇON)),doQuit=False)


            tree.write(pathOutXml)
        self.__logger.log(cl=self,method=sys._getframe(),message="end add dynamic limits")
        return pathOutXml

    def addCapteurs_nameCap(self,run,pathInXml,pathOutXml,list_sen,id_sen,nameCap):
        if run:
            self.__logger.logSep(cl=self,method=sys._getframe(),message="start add capteurs")
            tree = etree.parse(pathInXml)
            root=tree.getroot()
            parent = root.find('./TRAFICS[1]/TRAFIC[1]/PARAMETRAGE_CAPTEURS[1]/CAPTEURS[1]')

            # Create the new capteur and add an attribute
            new_element = etree.Element(nameCap, id=id_sen)

            # Insert the new element at a specific position (e.g., index 1)
            if parent is not None: parent.insert(0, new_element)
            else: self.__logger.warning(cl=self,method=sys._getframe(),message="parent does not found: {}".format(str(parent)),doQuit=False)

            # add tronçons
            TRONCONS=etree.Element('TRONCONS')
            if new_element is not None: new_element.insert(0, TRONCONS)
            else: self.__logger.warning(cl=self,method=sys._getframe(),message="parent does not found: {}".format(str(new_element)),doQuit=False)

            # add tronçon
            for link in list_sen:
                e=etree.Element("TRONCON",id=link)
                if TRONCONS is not None: TRONCONS.insert(0, e)
                else: self.__logger.warning(cl=self,method=sys._getframe(),message="parent does not found: {}".format(str(e)),doQuit=False)

            # store
            tree.write(pathOutXml)

        self.__logger.log(cl=self,method=sys._getframe(),message="end add capteurs")
        return pathOutXml

    def addSensors(self,run,pathInXml,pathOutXml,list_sen,id_sen):
        if run:
            self.__logger.log(cl=self,method=sys._getframe(),message="Add sensors. id sen={},list sen={}".format(id_sen,list_sen))
            tree = etree.parse(pathInXml)
            root=tree.getroot()
            parent = root.find('./TRAFICS[1]/TRAFIC[1]/PARAMETRAGE_CAPTEURS[1]/CAPTEURS[1]')

            # Create the new capteur and add an attribute
            new_element = etree.Element("CAPTEUR_MFD", id=id_sen)

            # Insert the new element at a specific position (e.g., index 1)
            if parent is not None: parent.insert(0, new_element)
            else: self.__logger.warning(cl=self,method=sys._getframe(),message="parent does not found: {}".format(str(parent)),doQuit=False)

            # add tronçons
            TRONCONS=etree.Element('TRONCONS')
            if new_element is not None: new_element.insert(0, TRONCONS)
            else: self.__logger.warning(cl=self,method=sys._getframe(),message="parent does not found: {}".format(str(new_element)),doQuit=False)

            # add tronçon
            for link in list_sen:
                e=etree.Element("TRONCON",id=link)
                if TRONCONS is not None: TRONCONS.insert(0, e)
                else: self.__logger.warning(cl=self,method=sys._getframe(),message="parent does not found: {}".format(str(e)),doQuit=False)

            # store
            tree.write(pathOutXml)

        return pathOutXml

    def getListLinksWithAttribute (self,run,listPathInput,attribute_name,attribute_value):
        if run:
            self.__logger.logSep(cl=self,method=sys._getframe(),message="start get list links")
            listLinks=None
            gdf_01=gpd.read_file(listPathInput[0])
            try:
                listLinks=list(gdf_01[gdf_01[attribute_name]==attribute_value]['ID'].drop_duplicates())
            except KeyError:
                self.__logger.warning(cl=self,method=sys._getframe(),message="attribute not funded. keep one from the list = {}".format(str(gdf_01.columns)),doQuit=False)
            self.__logger.log(cl=self,method=sys._getframe(),message="end get list links")
        return listLinks

    def changeAttribute(self,run,pathInXml,pathOutXml,listLinkschageAttribute, attributeValue):
        if run:
            self.__logger.logSep(cl=self,method=sys._getframe(),message="start change attribute of link")
            # self.__hf.copyListFilesInDirectory(run=True,listPathIn=[listPathInput[0]],pathOut=listPathOutput[0])
            tree = etree.parse(pathInXml)
            for element in tree.xpath("/ROOT_SYMUBRUIT/RESEAUX[1]/RESEAU[1]/TRONCONS[1]/TRONCON"):
                if element.attrib["id"] in listLinkschageAttribute :
                    # self.__logger.log(cl=self,method=sys._getframe(),message="update link {} with : {} = {}".format(element.attrib["id"],attributeValue[0],attributeValue[1]))
                    element.set(attributeValue[0],attributeValue[1])
            tree.write(pathOutXml)
        self.__logger.log(cl=self,method=sys._getframe(),message="end change attribute of link")
        return pathOutXml

    def changeAttributeRoot(self,run,pathInXml,pathOutXml,listAttributesValues,root):
        if run:
            self.__logger.logSep(cl=self,method=sys._getframe(),message="start change attribute")
            # self.__hf.copyListFilesInDirectory(run=True,listPathIn=[listPathInput[0]],pathOut=listPathOutput[0])
            tree = etree.parse(pathInXml)
            for element in tree.xpath(root):
                    # self.__logger.log(cl=self,method=sys._getframe(),message="update link {} with : {} = {}".format(element.attrib["id"],attributeValue[0],attributeValue[1]))
                for attribute, value in listAttributesValues.items():
                        element.set(attribute,value)
            tree.write(pathOutXml)
            self.__logger.log(cl=self,method=sys._getframe(),message="end change attribute")
            return pathOutXml


    def changeConfig(self,run,pathInXml,pathOutXml,root, attributeName, attributeValue):
        if run:
            self.__logger.log(cl=self,method=sys._getframe(),message="change attribute. Root={}, {}={}".format(root,attributeName,attributeValue))
            tree = etree.parse(pathInXml)
            for element in tree.xpath(root):
                element.set(attributeName,attributeValue)
            tree.write(pathOutXml)
        # self.__logger.log(cl=self,method=sys._getframe(),message="end change attribute of root")
        return pathOutXml

    # test class
def main():
    # ----------------------------------------------------------------------------------------------------------------------
    # paths and parametetes
    prefix="l63v-school"
    scenario=prefix+"_"+"02"
    pathOutputDir="outputs/"+scenario+"/"
    pathResources="resources/"

    name_study_area="l63v-study-area"
    name_schools="schools"
    name_links="links028"
    name_xml="L63V_1_0"
    name_demand="L63V_demand"

    path_study_area=pathOutputDir+name_study_area+".shp"
    path_links=pathOutputDir+name_links+".shp"
    path_schools=pathOutputDir+name_schools+".shp"

    path_schools_selected=pathOutputDir+prefix+"_"+"schools_selected.shp"
    path_links_nx=pathOutputDir+name_links+prefix+"_"+".gml"
    path_links_closestSchools=pathOutputDir+prefix+"_"+"links_closestSchools.csv"

    path_links_depth=pathOutputDir+prefix+"_"+"links_depth"+"_1.csv"
    path_links_d2=pathOutputDir+prefix+"_"+"links_depth"+"_2.csv"

    path_links_withSchools=pathOutputDir+prefix+"_links_withSchools.shp"
    path_links_withSchools_01=pathOutputDir+prefix+"_links_withSchools_01.shp"
    path_links_withSchools_02=pathOutputDir+prefix+"_links_withSchools_02.shp"

    path_xmlSimulation=pathOutputDir+name_xml+".xml"
    path_xmlSimulation_output=pathOutputDir+prefix+"_xmlSimulation"
    path_xmlSimulation_01=pathOutputDir+prefix+"_xmlSimulation_01.xml"

    path_xmlSimulation_removeScools=pathOutputDir+prefix+"_xmlSimulation_removeScools.xml"

    # logger and handleFiles
    # ----------------------------------------------------------------------------------------------------------------------
    hf=HandleFiles(logger=None)
    hf.createDirectories(["outputs/",pathOutputDir])
    logger=Logger(storeLog=True,initStore=True,pathLog="outputs/"+scenario+"/"+prefix+"_log_edit_xml.md")
    hf.setLogger(logger=logger)
    logger.setDisplay(True,True,True,True)
    logger.storeLocal(False)
    cwd=hf.getDefCwd()
    logger.logSep(cl=None,method=None,message="start  compute edit xml")

    # copy file resource folder in scenario folder
    hf.copyListFilesInDirectory(run=True,listPathIn=[pathResources+name_xml+_ for _ in [".xml"]],pathOut=pathOutputDir)
    hf.copyListFilesInDirectory(run=True,listPathIn=[pathResources+name_demand+_ for _ in [".csv"]],pathOut=pathOutputDir)

    # compute geoprocessing
    # ----------------------------------------------------------------------------------------------------------------------
    exs =EditXmlSymuvia(logger=logger,handleFiles=hf)

    # edit attribute (e.g. speed limits)
    n=0
    linksCloseSchools=exs.getListLinksWithAttribute(run=True, listPathInput=[path_links_withSchools_01],attribute_name="isCloSco",attribute_value=1.0)
    linkSchools=exs.getListLinksWithAttribute(run=True, listPathInput=[path_links_withSchools],attribute_name="isSchool",attribute_value=1.0)
    linkObs=exs.getListLinksWithAttribute(run=True, listPathInput=[path_links_withSchools_02],attribute_name="isObs",attribute_value=1.0)

    # # change speed limits
    # exs.changeAttribute(run=True, listPathInput=[path_xmlSimulation],listPathOutput=["{0}_{1:0>2}.xml".format(path_xmlSimulation_output,n)],listLinkschageAttribute=linksCloseSchools, attributeValue=["vit_reg","100"])
    #
    # # remove links
    # n+=1
    # exs.removeLinks(run=True, listPathInput=["{0}_{1:0>2}.xml".format(path_xmlSimulation_output,n-1)],listPathOutput=["{0}_{1:0>2}.xml".format(path_xmlSimulation_output,n)],listLinksToRemove=linkSchools)
    #
    # # create capteurs
    # n+=1    # add capteurs schools
    # exs.addCapteurs(run=True, listPathInput=["{0}_{1:0>2}.xml".format(path_xmlSimulation_output,n-1)],listPathOutput=["{0}_{1:0>2}.xml".format(path_xmlSimulation_output,n)],list_sen=linkSchools,id_sen='MFD_schools')
    #
    # n+=1    # add capteurs close schools
    # exs.addCapteurs(run=True, listPathInput=["{0}_{1:0>2}.xml".format(path_xmlSimulation_output,n-1)],listPathOutput=["{0}_{1:0>2}.xml".format(path_xmlSimulation_output,n)],list_sen=linksCloseSchools,id_sen='MFD_closeSchools')
    #
    # n+=1    # add capteurs observation
    # exs.addCapteurs(run=True, listPathInput=["{0}_{1:0>2}.xml".format(path_xmlSimulation_output,n-1)],listPathOutput=["{0}_{1:0>2}.xml".format(path_xmlSimulation_output,n)],list_sen=linkObs,id_sen='MFD_observed')



    # add capteurs observed area


if __name__ == "__main__":  main()
