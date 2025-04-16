import numpy as np
import pandas as pd
import sys
import geopandas as gpd

import os
import geopandas as gpd
import pandas as pd
from shapely.geometry import Polygon
import geopandas as gpd
import numpy as np
from shapely.geometry import LineString, MultiPoint, Polygon

from scipy.spatial import Voronoi
import matplotlib.pyplot as plt
from shapely.geometry import Point

import geopandas as gpd
import matplotlib.pyplot as plt
from shapely.geometry import LineString

from toolbox.control import tools


class Geoprocessing:
    def __init__(self,logger):
        self.__logger=logger
        self.__logger.log(cl=self,method=sys._getframe(),message="init Geoprocessing class")


