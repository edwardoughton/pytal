"""

"""
import configparser
import os
import numpy
import pandas
import geopandas
# import country_converter as coco
# import urllib.request
# from tqdm import tqdm
# from pathos.multiprocessing import Pool,cpu_count

from shapely.geometry import MultiPolygon
# from geopy.distance import vincenty
import rasterio
from rasterio.plot import show

CONFIG = configparser.ConfigParser()
CONFIG.read(os.path.join(os.path.dirname(__file__), 'script_config.ini'))
BASE_PATH = CONFIG['file_locations']['base_path']

DATA_RAW = os.path.join(BASE_PATH, 'raw')
DATA_INTERMEDIATE = os.path.join(BASE_PATH, 'intermediate')
DATA_PROCESSED = os.path.join(BASE_PATH, 'processed')

def get_country_outline(country):

    output = []

    path = os.path.join(DATA_RAW, 'gadm36_levels_shp', 'gadm36_0.shp')
    countries = geopandas.read_file(path)

    countries = countries.loc[~countries['NAME_0'].isin(['Antarctica'])]

    # simplify geometries
    countries['geometry'] = countries.simplify(tolerance = 0.005, preserve_topology=True) \
        .buffer(0.01).simplify(tolerance = 0.005, preserve_topology=True)

    #save to new country file
    countries_path = os.path.join(DATA_INTERMEDIATE,'global_countries.shp')
    countries.to_file(countries_path)

    # uk = countries[countries.GID_0 == 'UGA']

    # # remove tiny shapes to reduce size substantially
    # uk['geometry'] =   uk.apply(remove_tiny_shapes,axis=1)

    # print(uk)
    return output



def remove_tiny_shapes(x,regionalized=False):
    """
    This function will remove the small shapes of multipolygons. Will reduce the size
        of the file.

    Arguments:
        *x* : a geometry feature (Polygon) to simplify. Countries which are very large will
        see larger (unhabitated) islands being removed.

    Optional Arguments:
        *regionalized*  : Default is **False**. Set to **True** will use lower threshold
        settings (default: **False**).

    Returns:
        *MultiPolygon* : a shapely geometry MultiPolygon without tiny shapes.

    """

    # if its a single polygon, just return the polygon geometry
    if x.geometry.geom_type == 'Polygon':
        return x.geometry

    # if its a multipolygon, we start trying to simplify and remove shapes if its too big.
    elif x.geometry.geom_type == 'MultiPolygon':

        if regionalized == False:
            area1 = 0.1
            area2 = 250

        elif regionalized == True:
            area1 = 0.01
            area2 = 50

        # dont remove shapes if total area is already very small
        if x.geometry.area < area1:
            return x.geometry
        # remove bigger shapes if country is really big

        if x['GID_0'] in ['CHL','IDN']:
            threshold = 0.01
        elif x['GID_0'] in ['RUS','GRL','CAN','USA']:
            if regionalized == True:
                threshold = 0.01
            else:
                threshold = 0.01

        elif x.geometry.area > area2:
            threshold = 0.1
        else:
            threshold = 0.001

        # save remaining polygons as new multipolygon for the specific country
        new_geom = []
        for y in x.geometry:
            if y.area > threshold:
                new_geom.append(y)

        return MultiPolygon(new_geom)


if __name__ == '__main__':

    uk = get_country_outline('UK')


    # data = rasterio.open(os.path.join(DATA_RAW, 'settlement_layer', 'ppp_2020_1km_Aggregated.tif'))

    # show((data, 4), cmap='terrain')
