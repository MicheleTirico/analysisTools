import os

import geopandas as gpd
import matplotlib.pyplot as plt
from shapely.geometry import LineString

from toolbox.control import tools
from analysisTools.geoprocessing.geoTools import *

class GetStudyArea_linksSymuvia:
    def __init__(self, logger, parameters):
        self.__logger = logger
        self.__logger.log(cl=self, method=sys._getframe(), message="init get study area for sirane")
        if parameters != None: self.set_parameters(parameters)

    def set_parameters(self, parameters):    self.__parameters = parameters
    def get_links_in_study_area(self,run,gdfListIn,listPathOut,plotOutputs):
        if run:
            self.__logger.log(cl=None, method=None, message="get Sirane links that are in the study area")
            gdf_studyArea = gdfListIn[0]#gpd.read_file(listPathIn[0])  # study area (6th)
            gdf_links = gdfListIn[1]#gpd.read_file( listPathIn[1])  # links in 6th

            gdf_links_inStudyArea = gpd.sjoin(gdf_links, gdf_studyArea, how='inner',predicate='intersects')  # links sirane inStudyArea
            tools.storeGeoDataframe(logger=self.__logger, pathStore=listPathOut[0], df=gdf_links)

            if plotOutputs:
                fig, ax = plt.subplots(figsize=(10, 10))
                gdf_links_inStudyArea.plot(ax=ax, color='Green', edgecolor='None', linewidth=2,label="links Symuvia")
                gdf_studyArea.plot(ax=ax, color='None', edgecolor='red', linewidth=2, label="Study Area")
                ax.set_xticks([])
                ax.set_yticks([])
                plt.title("Study Area and Links")
                plt.show()
            return gdf_links_inStudyArea

    def get_links_without_overlaps(self,run,gdfListIn,listPathOut,plotOutputs):
        if run:
            self.__logger.log(cl=None, method=None, message="get links without overlaps")
            gdf_links = gdfListIn[0]#gpd.read_file( listPathIn[1])  # links in 6th


            self.__logger.log(cl=None, method=None, message="list 2 dataframes: 1. couples of nodes and all links, 2. all couples of nodes with more than one link")
            df_nodes_allLinks, df_overlapLinks = get_links_overlap(logger=self.__logger, gdf=gdf_links)


            # add 4 new columns to df_overlapLinks which are the coordinates of nodes
            df_overlapLinks[['n0_x', 'n0_y']] = df_overlapLinks['n0'].apply(lambda id_: pd.Series(get_coordinates(gdf_links, id_)))
            df_overlapLinks[['n1_x', 'n1_y']] = df_overlapLinks['n1'].apply(lambda id_: pd.Series(get_coordinates(gdf_links, id_)))

            gdf_filtered=gdf_links.copy()
            print(df_overlapLinks.columns)
            # add new links
            for index, row in df_overlapLinks.iterrows():
                new_line = LineString([(row.n0_x,row.n0_y),(row.n1_x,row.n1_y)])
                new_line_gdf = gpd.GeoDataFrame({'ID': [row.ID],'geometry': [new_line],"links":[row.links]},crs=gdf_filtered.crs)
                gdf_filtered = gdf_filtered._append(new_line_gdf,ignore_index=True)

            # remove links
            links_to_remove=set(" ".join(list(df_overlapLinks.links)).split(" "))
            gdf_filtered = gdf_filtered[~gdf_filtered.ID.isin(links_to_remove)]

            # fill ID of link if it is not new
            gdf_filtered ["links"] = gdf_filtered ["links"].fillna(gdf_filtered.ID)

            tools.storeGeoDataframe(logger=self.__logger, pathStore=listPathOut[0], df=gdf_filtered)

            if plotOutputs:
                fig, ax = plt.subplots(figsize=(10, 10))
                gdf_links.plot(ax=ax, color='Red', edgecolor='None', linewidth=2, label="links Symuvia")
                gdf_filtered.plot(ax=ax, color='Green', edgecolor='None', linewidth=2,label="links filtered")
                ax.set_xticks([])
                ax.set_yticks([])
                plt.title("Study Area and Links")
                plt.show()
            return gdf_filtered


    def get_links_without_overlaps_old_01(self,run,gdfListIn,listPathOut,plotOutputs):
        if run:
            self.__logger.log(cl=None, method=None, message="get links without overlaps")
            gdf_links = gdfListIn[0]#gpd.read_file( listPathIn[1])  # links in 6th

            run_allTime=True
            # get matches
            if os.path.exists(listPathOut[0])==False or run_allTime==True:

                self.__logger.log(cl=None, method=None, message="list of links matches has not been computed. Do it.")
                df_matches , df_nodes_to_drop = get_links_overlap_old_01(logger=self.__logger, gdf=gdf_links)

                # df_matches , df_nodes_to_drop = get_links_overlap_old_01(logger=self.__logger, gdf=gdf_links)
                tools.storeDataframe(logger=self.__logger,pathStore=listPathOut[0],df=df_matches)
                tools.storeDataframe(logger=self.__logger,pathStore=listPathOut[1],df=df_nodes_to_drop)

            else:
                self.__logger.log(cl=None, method=None, message="list of links matches has yet been computed. Do not do it and read csv.")
                df_matches=pd.read_csv(listPathOut[0],sep=";")
                df_nodes_to_drop=pd.read_csv(listPathOut[1],sep=";")

            print(df_matches)
            print(df_nodes_to_drop)

            # create links between
            n=0
            for index, row in df_matches.iterrows():
                line1 = gdf_links[gdf_links.ID == row.ID1].geometry.iloc[0]
                line2 = gdf_links[gdf_links.ID == row.ID2].geometry.iloc[0]

                # find the midpoint for each pairs of closer vertices
                midpoint_1, midpoint_2=get_midpoint_pairs_of_coordinates(logger=self.__logger,lines=[line1,line2])

                # Create a new line between the midpoints
                new_line = LineString([midpoint_1, midpoint_2])

                # Add this new line to a new GeoDataFrame with an ID
                new_line_gdf = gpd.GeoDataFrame({'ID': ["midLine_{}".format(n)],'geometry': [new_line],},crs=gdf_links.crs)

                # # Add the new line to the GeoDataFrame
                gdf_links = gdf_links._append(new_line_gdf,ignore_index=True)
                n+=1

            # remove previous links

            listToRemove=list(set(list(df_matches.ID1)+list(df_matches.ID2)))

            print(listToRemove)
            # gdf_filtered = gdf_links[~gdf_links['ID'].isin(listToRemove)]
            to_remove = set(df_nodes_to_drop[["NodeUpID","NodeDownID"]].itertuples(index=False, name=None))
            gdf_filtered = gdf_links[~gdf_links[["NodeUpID","NodeDownID"]].apply(tuple, axis=1).isin(to_remove)]




            tools.storeGeoDataframe(logger=self.__logger, pathStore=listPathOut[2], df=gdf_filtered)

            if plotOutputs:
                fig, ax = plt.subplots(figsize=(10, 10))
                gdf_filtered.plot(ax=ax, color='Green', edgecolor='None', linewidth=2,label="links Symuvia")
                ax.set_xticks([])
                ax.set_yticks([])
                plt.title("Study Area and Links")
                plt.show()


            # create a new link between matches

