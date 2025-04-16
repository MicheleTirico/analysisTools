import sys
from toolbox.control import tools
import geopandas as gpd
import matplotlib.pyplot as plt

class GetStudyArea_linksSirane:
    def __init__(self, logger, parameters):
        self.__logger = logger
        self.__logger.log(cl=self, method=sys._getframe(), message="init get study area for sirane")
        if parameters != None: self.set_parameters(parameters)

    def set_parameters(self, parameters):    self.__parameters = parameters

    def get_gdf_with_crs(self,  run,  listPathIn,plotOutputs):
        if run:
            self.__logger.log(cl=None, method=None, message="Set crs for all gdf. Return list of gdf",)
            # links Symuvia
            gdf_links_sirane = gpd.read_file(listPathIn[2])
            gdf_links_symuvia = gpd.read_file(listPathIn[0])
            gdf_studyArea = gpd.read_file(listPathIn[1])
            gdf_links_symuvia=gdf_links_symuvia.set_crs(gdf_links_sirane.crs,inplace=True)
            gdf_studyArea = gdf_studyArea.to_crs(gdf_links_sirane.crs)

            if plotOutputs:
                fig, ax = plt.subplots(figsize=(10, 10))
                gdf_links_symuvia.plot(ax=ax, color='blue', edgecolor='None', linewidth=2, label="links Symuvia")
                gdf_links_sirane.plot(ax=ax, color='Green', edgecolor='None', linewidth=2,label="links Sirane")
                gdf_studyArea.plot(ax=ax, color='None', edgecolor='red', linewidth=2,label="study area")
                ax.set_xticks([])
                ax.set_yticks([])
                handles, labels = ax.get_legend_handles_labels()
                ax.legend(handles, labels, loc="upper right")
                plt.title("Study Area and Links")
                plt.show()

            return [gdf_links_symuvia ,gdf_studyArea ,gdf_links_sirane]
        else: return None

    def getLinksInStudyArea(self, run, listGdfIn, listPathOut, plotOutputs):

        if run:
            self.__logger.log(cl=None, method=None, message="get Sirane links that are in the study area")
            gdf_studyArea = listGdfIn[1]  # study area (6th)
            gdf_links_sirane = listGdfIn[2]  # links sirane in 6th
            gdf_links_sirane_inStudyArea = gpd.sjoin(gdf_links_sirane, gdf_studyArea, how='inner',predicate='intersects')  # links sirane inStudyArea
            tools.storeGeoDataframe(logger=self.__logger, pathStore=listPathOut[0], df=gdf_links_sirane)
            if plotOutputs:
                fig, ax = plt.subplots(figsize=(10, 10))
                gdf_studyArea.plot(ax=ax, color='None', edgecolor='red', linewidth=2, label="Study Area")
                gdf_links_sirane_inStudyArea.plot(ax=ax, color='Green', edgecolor='None', linewidth=2,label="links Sirane")
                ax.set_xticks([])
                ax.set_yticks([])
                plt.title("Study Area and Links")
                plt.show()
            return listGdfIn + [gdf_links_sirane_inStudyArea]
        else:   return listGdfIn

    # get df closest links
    def getDfclosestLinks (self, run, listGdfIn,listPathOut):
        if run :
            self.__logger.log(cl=None, method=None, message="compute df closest Sirane links for each Symuvia link ")
            gdf_links_symuvia = listGdfIn[0]        # links Symuvia
            gdf_links_sirane_inStudyArea = listGdfIn[3]         # links sirane inStudyArea
            gdf_links_sirane = gdf_links_sirane_inStudyArea.drop(columns=['index_right'], errors='ignore')  # Drop it if not needed
            joined_near = gpd.sjoin_nearest(gdf_links_sirane, gdf_links_symuvia, how="right", distance_col="distance")
            df_closest = joined_near[["ID_right", "ID_left", "distance"]].groupby('ID_right').min().reset_index()
            df_closest = df_closest.rename(columns={"ID_right": "id_sym", "ID_left": 'id_sir'})# gdf closest links
            tools.storeDataframe(logger=self.__logger, pathStore=listPathOut[0], df=df_closest)
            return listGdfIn+ [df_closest]
        else:return listGdfIn
    # get links Sirane in zones
    def linkSirInzones (self, run, listGdfIn,  listPathIn,listPathOut,plotOutputs):
        if run :
            self.__logger.log(cl=None, method=None, message="get Sirane links in zones")

            # update df_closest
            df_closest = listGdfIn[4]
            gdf_links_simuvia_zones = gpd.read_file(listPathIn[0])
            df_closest = df_closest.merge(gdf_links_simuvia_zones[["ID", "zone"]], left_on='id_sym', right_on="ID",how="left")
            df_closest = df_closest[['id_sym', 'id_sir', 'distance', 'zone']]
            df_closest["zone"] = df_closest["zone"].fillna(-1)
            tools.storeDataframe(logger=self.__logger, pathStore=listPathOut[0], df=df_closest)

            gdf_links_sirane_inStudyArea = listGdfIn[3]         # links sirane inStudyArea
            gdf_links_sirane_inStudyArea["ID"] = gdf_links_sirane_inStudyArea["ID"].astype(str)
            gdf_links_sirane_inStudyArea = gdf_links_sirane_inStudyArea.merge(df_closest[["id_sir", "zone"]], left_on='ID',right_on="id_sir", how="left")
            gdf_links_sirane_inStudyArea["zone"] = gdf_links_sirane_inStudyArea["zone"].fillna(-1)
            gdf_links_sirane_inStudyArea=gdf_links_sirane_inStudyArea.drop_duplicates()

            tools.storeGeoDataframe(logger=self.__logger, pathStore=listPathOut[1], df=gdf_links_sirane_inStudyArea)

            if plotOutputs:
                fig, ax = plt.subplots(figsize=(10, 10))
                listGdfIn[1].plot(ax=ax, color='None', edgecolor='red', linewidth=2, label="Study Area")
                gdf_links_sirane_inStudyArea.plot(ax=ax, color='Green', edgecolor='None', linewidth=2,label="links Sirane")
                ax.set_xticks([])
                ax.set_yticks([])
                plt.title("Study Area and Links")
                plt.show()

            listGdfIn[3]=gdf_links_sirane_inStudyArea
            listGdfIn[4]=df_closest
            return listGdfIn
        else:            return listGdfIn

    # get center of Sirane links
    def get_middle_point_links (self, run,  listGdfIn,listPathOut,plotOutputs):
        if run :
            self.__logger.log(cl=None, method=None, message="get the middles of a set of links ")
    
            gdf_links_sirane_inStudyArea = listGdfIn[3]         # links sirane inStudyArea
    
            def get_midpoint(line):    return line.interpolate(0.5, normalized=True)
    
            gdf_links_sirane_inStudyArea['midpoint'] = gdf_links_sirane_inStudyArea['geometry'].apply(get_midpoint)
            midpoints_gdf = gpd.GeoDataFrame(gdf_links_sirane_inStudyArea.drop(columns='geometry'), geometry=gdf_links_sirane_inStudyArea['midpoint'], crs=gdf_links_sirane_inStudyArea.crs)
            midpoints_gdf = midpoints_gdf[['ID', "midpoint", "zone"]]
            midpoints_gdf = midpoints_gdf.rename(columns={"midpoint": "geometry", "ID": "id_sir"}).drop_duplicates()
            tools.storeGeoDataframe(logger=self.__logger, pathStore=listPathOut[0], df=midpoints_gdf)
            if plotOutputs:
                fig, ax = plt.subplots(figsize=(10, 10))
                listGdfIn[1].plot(ax=ax, color='None', edgecolor='red', linewidth=2, label="Study Area")
                gdf_links_sirane_inStudyArea.plot(ax=ax, color='Green', edgecolor='None', linewidth=2,label="links Sirane")
                midpoints_gdf.plot(ax=ax, color='blue', edgecolor='None', linewidth=2,label="midpoint")
                ax.set_xticks([])
                ax.set_yticks([])
                plt.show()
            return listGdfIn+[midpoints_gdf]
        else: return listGdfIn