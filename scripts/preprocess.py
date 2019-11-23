"""

"""
import configparser
import os
import numpy
import pandas
import geopandas

from shapely.geometry import MultiPolygon, mapping, box
from fiona.crs import from_epsg
import rasterio
from rasterio.mask import mask
import json

CONFIG = configparser.ConfigParser()
CONFIG.read(os.path.join(os.path.dirname(__file__), 'script_config.ini'))
BASE_PATH = CONFIG['file_locations']['base_path']

DATA_RAW = os.path.join(BASE_PATH, 'raw')
DATA_INTERMEDIATE = os.path.join(BASE_PATH, 'intermediate')
DATA_PROCESSED = os.path.join(BASE_PATH, 'processed')

def process_country_shapes():
    """
    Processes both country and regional shapes.

    """
    path_processed = os.path.join(DATA_INTERMEDIATE,'global_countries.shp')

    if not os.path.exists(path_processed):

        print('Working on global_countries.shp')
        path_raw = os.path.join(DATA_RAW, 'gadm36_levels_shp', 'gadm36_0.shp')
        countries = geopandas.read_file(path_raw)#[1:3]

        print('Excluding Antarctica')
        countries = countries.loc[~countries['NAME_0'].isin(['Antarctica'])]

        print('Simplifying geometries')
        countries['geometry'] = countries.simplify(tolerance = 0.005, preserve_topology=True) \
            .buffer(0.01).simplify(tolerance = 0.005, preserve_topology=True)

        print('Excluding small shapes')
        countries['geometry'] = countries.apply(exclude_small_shapes,axis=1)

        print('Writing global_countries.shp to file')
        countries.to_file(path_processed, driver='ESRI Shapefile')

    else:
        countries = geopandas.read_file(path_processed)

    for name in countries.GID_0.unique():

        print('working on {}'.format(name))

        path = os.path.join(DATA_INTERMEDIATE, name)

        if not os.path.exists(path):
            os.makedirs(path)

        single_country = countries[countries.GID_0 == name]

        shape_path = os.path.join(path, 'national_outline.shp')
        single_country.to_file(shape_path)

    return print('Completed processing of country shapes')


def process_regional_shapes():
    """
    Process sub-national regional shapes.

    """
    path_processed = os.path.join(DATA_INTERMEDIATE,'global_regions.shp')

    if not os.path.exists(path_processed):

        print('Working on global_countries.shp')
        path_regions = os.path.join(DATA_RAW, 'gadm36_levels_shp', 'gadm36_2.shp')
        regions = geopandas.read_file(path_regions)#[:10]

        print('Excluding Antarctica')
        regions = regions.loc[~regions['NAME_0'].isin(['Antarctica'])]

        print('Simplifying geometries')
        regions['geometry'] = regions.simplify(tolerance = 0.005, preserve_topology=True) \
            .buffer(0.01).simplify(tolerance = 0.005, preserve_topology=True)

        print('Excluding small shapes')
        regions['geometry'] = regions.apply(exclude_small_shapes,axis=1)

        print('Writing global_regions.shp to file')
        regions.to_file(path_processed, driver='ESRI Shapefile')

    else:

        regions = geopandas.read_file(path_processed)

    for name in regions.GID_0.unique():

        print('working on {}'.format(name))

        path = os.path.join(DATA_INTERMEDIATE, name, 'regions')

        if not os.path.exists(path):
            os.makedirs(path)

        single_country = regions[regions.GID_0 == name]

        for name_region in single_country.GID_2.unique():

            single_region = single_country[single_country.GID_2 == name_region]

            shape_path = os.path.join(path, '{}.shp'.format(name_region))
            single_region.to_file(shape_path)

    return print('Completed processing of regional shapes')


def process_settlement_layer():
    """

    """
    path_settlements = os.path.join(DATA_RAW,'settlement_layer','ppp_2020_1km_Aggregated.tif')

    settlements = rasterio.open(path_settlements)

    path_countries = os.path.join(DATA_INTERMEDIATE,'global_countries.shp')

    if os.path.exists(path_countries):
        countries = geopandas.read_file(path_countries)
    else:
        print('Must generate global_countries.shp first' )

    num = 0
    for name in countries.GID_0.unique():

        print('working on {}'.format(name))

        path_country = os.path.join(DATA_INTERMEDIATE, name)

        single_country = countries[countries.GID_0 == name]

        bbox = single_country.envelope
        geo = geopandas.GeoDataFrame()

        geo = geopandas.GeoDataFrame({'geometry': bbox}, index=[num], crs=from_epsg('4326'))
        num += 1
        coords = [json.loads(geo.to_json())['features'][0]['geometry']]

        #chop on coords
        out_img, out_transform = mask(settlements, coords, crop=True)

        # Copy the metadata
        out_meta = settlements.meta.copy()

        out_meta.update({"driver": "GTiff",
                        "height": out_img.shape[1],
                        "width": out_img.shape[2],
                        "transform": out_transform,
                        "crs": 'epsg:4326'})

        shape_path = os.path.join(path_country, 'settlements.tif')
        with rasterio.open(shape_path, "w", **out_meta) as dest:
                dest.write(out_img)

    return print('Completed processing of settlement layer')


def exclude_small_shapes(x,regionalized=False):
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

    process_country_shapes()

    process_regional_shapes()

    process_settlement_layer()
