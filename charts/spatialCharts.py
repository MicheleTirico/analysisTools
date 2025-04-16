import math
import sys
import pandas as pd
from toolbox.control import tools
import geopandas as gpd
import contextily as cx
import matplotlib.pyplot as plt
import rasterio
from PIL import Image
import numpy as np
import mapclassify as mc
import matplotlib.colors as mcolors
from matplotlib.patches import Patch
class SpatialCharts:

    def __init__(self, logger, parameters=None):
        self.__logger = logger
        self.__logger.logSep(cl=self, method=sys._getframe(), message="init get spatial charts")
        if parameters != None: self.set_parameters(parameters)

    def set_parameters(self, parameters):    self.__parameters = parameters

    def merge_ShpInd(self,run,listPathInput, listPathOutput,on,indicators):
        if run:
            self.__logger.logSep(cl=self, method=sys._getframe(), message="merge a shp file with a dataframe")
            gdf1= gpd.read_file(listPathInput[0])
            df1 = pd.read_csv(filepath_or_buffer=listPathInput[1], sep=";")

            try:gdf1=gdf1.merge(df1,left_on=on[0],right_on=on[1],how="right")#[indicators]
            except KeyError:self.__logger.error(cl=self,method=sys._getframe(),message="Error in on=[]. Here name columns of: \ngdf1: {}\ndf1: {}".format(gdf1.columns,df1.columns),error=KeyError)

            if indicators !=None:
                self.__logger.warning(cl=self, method=sys._getframe(),message="You should select columns from:\ngdf: {}\ndf: {}".format(gdf1.columns,df1.columns), doQuit=False)
                self.__logger.log(cl=self, method=sys._getframe(), message="select indicators: {}".format([indicators[0]+indicators[1]]))
                gdf1=gdf1[indicators[0]+indicators[1]]

            if listPathOutput!=None:    tools.storeGeoDataframe(logger=self.__logger,pathStore=listPathOutput[0],df=gdf1)

            return gdf1


    def getChart_studyArea(self,run, listPathOutput,listGdf=None):
        if run:
            self.__logger.logSep(cl=self, method=sys._getframe(), message="get chart with zones")
            gdf_zones=listGdf[0]
            gdf_schools = listGdf[1]

            fig, ax = plt.subplots(figsize=(10, 6))  # Set figure size
            colors = ["red", "blue", "green","black"]  # Define your colors
            zone_labels = ["Zone " + str(label) for label in gdf_zones["zone"].astype("category").cat.categories]  # Get zone labels
            gdf_zones["color"] = gdf_zones["zone"].astype("category").cat.codes  # Convert zones to numbers
            gdf_zones.plot(color=[colors[i] for i in gdf_zones["color"]], legend=True, ax=ax, linewidth=1)
            gdf_schools.plot(ax=ax, color='red', edgecolor='None', linewidth=2, label="Schools")

            legend_patches = [Patch(color=colors[i], label=zone_labels[i]) for i in range(len(zone_labels))]
            from matplotlib.lines import Line2D

            # Add a dot for schools in the legend
            school_dot = Line2D([0], [0], marker='o', color='w', markersize=8, markerfacecolor='red', label="Schools")

            # Add legend to the plot
            ax.legend(handles=legend_patches + [school_dot], loc="upper right")  # Adjust location as needed

            ax.set_xticks([])
            ax.set_yticks([])
            cx.add_basemap(ax)
            self.__logger.log(cl=self, method=sys._getframe(), message="Chart stored at :{}".format(listPathOutput[0]))
            plt.savefig(listPathOutput[0], dpi=300, bbox_inches="tight")

    def getChartZones(self,run, listPathOutput,listGdf=None,listPathInput=None):
        if run:
            self.__logger.logSep(cl=self, method=sys._getframe(), message="get chart with zones")
            try:                gdf_links = gpd.read_file(listPathInput[0])
            except TypeError:   gdf_links=listGdf[0]
            try:                gdf_schools = gpd.read_file(listPathInput[1])
            except TypeError:   gdf_schools = listGdf[1]

            gdf_links.to_crs('EPSG:3857', inplace=True)
            fig, ax = plt.subplots(figsize=(10, 6))  # Set figure size
            gdf_links.plot(column="zone", cmap="Accent", categorical=True, legend=True, ax=ax,linewidth=1)
            ax.set_xticks([])
            ax.set_yticks([])
            cx.add_basemap(ax)
            self.__logger.log(cl=self, method=sys._getframe(), message="Chart stored at :{}".format(listPathOutput[0]))
            plt.savefig(listPathOutput[0], dpi=300, bbox_inches="tight")

    def getChartGrd(self,run,listPathInput, listPathOutput,vals,colors="Spectral_r", scheme="Quantiles",k_classes = 40,setTitle=True,setLegend=True):
        if run:
            self.__logger.log(cl=self, method=sys._getframe(), message="get chart GRD")
            with rasterio.open(listPathInput[0]) as dataset:
                data = dataset.read(1)  # Read the first band
                nodata = dataset.nodata  # Get nodata value

                # Mask nodata values
                if nodata is not None:                    data = np.ma.masked_where(data == nodata, data)

                classifier=self.__get_classifier(data,k_classes, scheme)
                bins = classifier.bins  # Bin edges

                # Define a colormap and normalization
                cmap = plt.get_cmap(colors, len(bins) + 1)
                norm = mcolors.BoundaryNorm([data.min()] + list(bins), cmap.N)

                # Create a figure
                fig, ax = plt.subplots(figsize=(8, 6))
                img = ax.imshow(data, cmap=cmap, norm=norm, extent=dataset.bounds, origin="upper")

                # Add a colorbar (legend)
                if setLegend:   cbar = plt.colorbar(img, ax=ax, orientation="vertical", ticks=[data.min()] + list(bins))
                if setTitle:    ax.set_title("scenario: {},pollutant: {}, period: {}".format(vals[0],vals[1],vals[2]))
                ax.set_xticks([])
                ax.set_yticks([])

                self.__logger.log(cl=self, method=sys._getframe(),message="Chart stored at :{}".format(listPathOutput[0]))
                plt.savefig(listPathOutput[0], dpi=300, bbox_inches="tight")

    def get_animated_gif(self,run,image_files , listPathOutput,duration=500):
        if run:
            self.__logger.log(cl=self, method=sys._getframe(), message="get an animated gif")
            images = [Image.open(img) for img in image_files]
            images[0].save( listPathOutput[0], save_all=True, append_images=images[1:], duration=duration, loop=0)

    def get_pixel_wise_difference(self,run,listPathInput, listPathOutput,vals,colors="redGreen",setTitle=True,setLegend=True,roundCeil=True):
        if run:
            self.__logger.log(cl=self, method=sys._getframe(), message="get pixel-wise difference between two GRD : {} and {}".format(listPathInput[0],listPathInput[1]))

            with (rasterio.open(listPathInput[0] ) as dataset1, rasterio.open(listPathInput[1]) as dataset2):            # Open the first raster file
                data1 = dataset1.read(1)                # Read the first band from each file
                data2 = dataset2.read(1)
                if data1.shape != data2.shape:                    raise ValueError("Raster dimensions do not match!")                # Ensure both rasters have the same shape
                delta = data1 - data2                # Compute the pixel-wise difference (Delta)
                # Handle NoData values
                nodata1 = dataset1.nodata
                nodata2 = dataset2.nodata
                if nodata1 is not None:                    delta = np.ma.masked_where(data1 == nodata1, delta)
                if nodata2 is not None:                    delta = np.ma.masked_where(data2 == nodata2, delta)

                # Define a diverging colormap for positive/negative differences
                if colors=="redGreen":
                    from matplotlib.colors import LinearSegmentedColormap
                    colors = LinearSegmentedColormap.from_list("red_white_green_cmap", ["red", "white", "green"])

                cmap = plt.get_cmap(colors)  # Red-Blue colormap
                if roundCeil:
                    min_val = - math.ceil(max(abs(delta.min()),abs(delta.max())))
                    max_val = math.ceil(max(abs(delta.min()),abs(delta.max())))
                else:
                    min_val = delta.min()
                    max_val = delta.max()
                norm =  mcolors.TwoSlopeNorm(vmin=min_val, vcenter=0, vmax=max_val) #mcolors.BoundaryNorm([delta.min()] + list(bins), cmap.N)

                # Create a figure and axis
                fig, ax = plt.subplots(figsize=(8, 6))
                img = ax.imshow(delta, cmap=cmap, norm=norm, extent=dataset1.bounds, origin="upper")
                if setTitle:    ax.set_title("Difference (Δ = {} - {}), pol: {}, t: {}".format(vals[0],vals[1],vals[2],vals[3]), fontsize=14, fontweight="bold")
                if setLegend:
                    cbar_ticks = np.linspace(min_val, max_val, num=10)
                    cbar = plt.colorbar(img, ax=ax, orientation="vertical", ticks=cbar_ticks)
                    cbar.set_label("{}".format(vals[2]))
                ax.set_xticks([])
                ax.set_yticks([])
                for path in listPathOutput:
                    self.__logger.log(cl=None, method=sys._getframe(), message="store figure at:{}".format(path))
                    plt.savefig(path, dpi=300, bbox_inches="tight")
                plt.close()
    def merge_spatial_diff(self,row_labels, col_labels,image_paths,pathOutputs,figsize=(8, 10)):
        fig, axes = plt.subplots(len(row_labels), len(col_labels), figsize=figsize)  # 4 rows, 3 columns
        for r in range(len(image_paths[0])): # row
            for c in range(len(image_paths)):
                img=Image.open(image_paths[c][r])
                ax = axes[c, r]
                ax.imshow(img)
                ax.set_xticks([])
                ax.set_yticks([])
                ax.set_xlabel('')
                ax.set_ylabel('')
                for spine in ax.spines.values(): spine.set_visible(True)  # Keep the borders (spines) visible

        for y in range(len(col_labels)):    axes[0, y].set_title(col_labels[y], fontsize=12)
        for x in range(len(row_labels)):    axes[x, 0].set_ylabel(row_labels[x], fontsize=12)

        plt.tight_layout()
        for path in pathOutputs:
            self.__logger.log(cl=None, method=sys._getframe(), message="store figure at:{}".format(path))
            plt.savefig("{}".format(path), dpi=300, bbox_inches="tight")
        plt.close()

    def __get_classifier(self,data,k_classes, scheme):
        # Compute classification using mapclassify
        if scheme == "Quantiles":
            classifier = mc.Quantiles(data.compressed(), k=k_classes)
        elif scheme == "EqualInterval":
            classifier = mc.EqualInterval(data.compressed(), k=k_classes)
        elif scheme == "NaturalBreaks":
            classifier = mc.NaturalBreaks(data.compressed(), k=k_classes)
        else:
            raise ValueError("Invalid classification scheme selected!")

        return classifier
