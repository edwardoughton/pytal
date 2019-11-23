
"""

"""

import os
import json
# import rasterio
# import numpy
# import geopandas
from osgeo import ogr
# import country_converter as coco
# from collections import defaultdict
# import shutil
# from scipy import integrate
# from geopy.distance import vincenty
# from boltons.iterutils import pairwise
# from rasterstats import point_query


def load_config():
    """Read config.json
    """
    config_path = os.path.join(os.path.dirname(__file__), '..', 'config.json')
    with open(config_path, 'r') as config_fh:
        config = json.load(config_fh)
    return config



def load_osm_data(data_path,country):
    """
    Load osm data for an entire country.

    Arguments:
        *data_path* : file path to location of all data.

        *country* : unique ID of the country for which we want to extract data from
        OpenStreetMap. Must be matching with the country ID used for saving the .osm.pbf file.
    """
    osm_path = os.path.join(data_path,'country_osm','{}.osm.pbf'.format(country))

    driver=ogr.GetDriverByName('OSM')
    return driver.Open(osm_path)

def load_osm_data_region(data_path,region):
    """
    Load osm data for a specific region.

    Arguments:
        *data_path* : file path to location of all data.

        *region* : unique ID of the region for which we want to extract data from
        OpenStreetMap. Must be matching with the region ID used for saving the .osm.pbf file.

    """
    osm_path = os.path.join(data_path,'region_osm','{}.osm.pbf'.format(region))

    driver=ogr.GetDriverByName('OSM')
    return driver.Open(osm_path)
