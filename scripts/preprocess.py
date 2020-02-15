"""
Preprocessing scripts.

Written by Ed Oughton.

Winter 2020

"""
import os
import configparser
import json
import math
import glob
import requests
import tarfile
import gzip
import shutil
# import geoio
import numpy as np
import pandas as pd
import geopandas

import urllib.request
from shapely.geometry import MultiPolygon, Polygon, mapping, box
from shapely.ops import cascaded_union
from fiona.crs import from_epsg
import rasterio
from rasterio.mask import mask
from rasterstats import zonal_stats
from geopy.distance import distance
from pathos.multiprocessing import Pool, cpu_count

from pytal.utils import load_config #,create_folder_lookup,map_roads,line_length

CONFIG = configparser.ConfigParser()
CONFIG.read(os.path.join(os.path.dirname(__file__), 'script_config.ini'))
BASE_PATH = CONFIG['file_locations']['base_path']

DATA_RAW = os.path.join(BASE_PATH, 'raw')
DATA_INTERMEDIATE = os.path.join(BASE_PATH, 'intermediate')
DATA_PROCESSED = os.path.join(BASE_PATH, 'processed')


def process_country_shapes():
    """
    Created a set of global country shapes. Adds the single national boundary for
    each country to each country folder.

    """
    path_processed = os.path.join(DATA_INTERMEDIATE,'global_countries.shp')

    if not os.path.exists(path_processed):

        print('Working on global_countries.shp')
        path_raw = os.path.join(DATA_RAW, 'gadm36_levels_shp', 'gadm36_0.shp')
        countries = geopandas.read_file(path_raw)

        print('Excluding Antarctica')
        countries = countries.loc[~countries['NAME_0'].isin(['Antarctica'])]

        print('Excluding small shapes')
        countries['geometry'] = countries.apply(exclude_small_shapes,axis=1)

        print('Simplifying geometries')
        countries['geometry'] = countries.simplify(tolerance = 0.005, preserve_topology=True) \
            .buffer(0.01).simplify(tolerance = 0.005, preserve_topology=True)

        print('Adding ISO country codes')
        glob_info_path = os.path.join(BASE_PATH, 'global_information.csv')
        load_glob_info = pd.read_csv(glob_info_path, encoding = "ISO-8859-1")

        countries = countries.merge(load_glob_info,left_on='GID_0', right_on='ISO_3digit')

        print('Writing global_countries.shp to file')
        countries.to_file(path_processed, driver='ESRI Shapefile')

    else:
        countries = geopandas.read_file(path_processed)


    for name in countries.GID_0.unique():

        path = os.path.join(DATA_INTERMEDIATE, name)

        if not os.path.exists(path):
            print('Creating directory {}'.format(path))
            os.makedirs(path)

        shape_path = os.path.join(path, 'national_outline.shp')

        if not os.path.exists(shape_path):

            print('working on {}'.format(name))

            single_country = countries[countries.GID_0 == name]

            single_country.to_file(shape_path)

    return print('All country shapes complete')


def process_regions(level):
    """
    Function for processing subnational regions.

    """
    filename = 'global_regions_{}.shp'.format(level)
    path_processed = os.path.join(DATA_INTERMEDIATE, filename)

    # if not os.path.exists(path_processed):

    print('Working on global_countries.shp')
    filename = 'gadm36_{}.shp'.format(level)
    path_regions = os.path.join(DATA_RAW, 'gadm36_levels_shp', filename)
    regions = geopandas.read_file(path_regions)

    print('Excluding Antarctica')
    regions = regions.loc[~regions['NAME_0'].isin(['Antarctica'])]
    regions = regions.loc[~regions['GID_1'].isin(['RUS.12_1'])] # Chukot
    regions = regions.loc[~regions['GID_1'].isin(['FJI.3_1'])] #Northern

    print('Excluding small shapes')
    regions['geometry'] = regions.apply(exclude_small_shapes,axis=1)

    print('Simplifying geometries')
    regions['geometry'] = regions.simplify(tolerance = 0.005, preserve_topology=True) \
        .buffer(0.01).simplify(tolerance = 0.005, preserve_topology=True)

    print('Adding ISO country codes')
    glob_info_path = os.path.join(BASE_PATH, 'global_information.csv')
    load_glob_info = pd.read_csv(glob_info_path, encoding = "ISO-8859-1")

    regions = regions.merge(load_glob_info,left_on='GID_0',right_on='ISO_3digit')
    regions.rename(columns={'coordinates':'coordinate'}, inplace=True)

    regions.reset_index(drop=True,inplace=True)

    print('Writing global_regions.shp to file')
    regions.to_file(path_processed, driver='ESRI Shapefile')

    print('Completed processing of regional shapes level {}'.format(level))

    # else:
    #     regions = geopandas.read_file(path_processed)

    return regions


def create_full_regional_layer_2():
    """

    """
    filename = 'global_regions_2.shp'
    path_processed = os.path.join(DATA_INTERMEDIATE, filename)

    if not os.path.exists(path_processed):

        #load regions and process
        regions_1 = process_regions(1)
        regions_2 = process_regions(2)

        #select desired regions
        regions_1 = regions_1.loc[regions_1['GID_0'].isin(['ESH', 'LBY', 'LSO'])]
        regions_1 = regions_1.drop_duplicates(subset='GID_1', keep="first")
        regions_2 = regions_2.loc[regions_2['gid_region'] == 2]
        regions_2 = regions_2.drop_duplicates(subset='GID_2', keep="first")

        #concatinate
        regions = pd.concat([regions_1, regions_2], sort=True)

        regions.reset_index(drop=True,inplace=True)

        print('Writing global_regions.shp to file')
        regions.to_file(path_processed, driver='ESRI Shapefile')

    return 'done'


def assemble_global_regional_layer():
    """
    Assemble a single layer of sub-national regional shapes.

    Set the desired level to be used in the 'global_information.csv' folder.

    Write each sub-national region to an individual shape in each nation's
    regions folder.

    """
    filename = 'global_regions.shp'
    path_processed = os.path.join(DATA_INTERMEDIATE, filename)

    if not os.path.exists(path_processed):

        #load regions and process
        regions_1 = process_regions(1)
        regions_2 = process_regions(2)

        #select desired regions
        regions_1 = regions_1.loc[regions_1['gid_region'] == 1]
        regions_2 = regions_2.loc[regions_2['gid_region'] == 2]

        #concatinate
        regions = pd.concat([regions_1, regions_2], sort=True)

        regions.reset_index(drop=True,inplace=True)

        print('Writing global_regions.shp to file')
        regions.to_file(path_processed, driver='ESRI Shapefile')

        print('Completed processing of regional shapes level')

        for name in regions.GID_0.unique():

            print('working on {}'.format(name))

            single_country = regions[regions.GID_0 == name]

            #try for level two regions
            try:
                for name_region in single_country.GID_2.unique():

                    single_region = single_country[single_country.GID_2 == name_region]

                    shape_path = os.path.join(path, '{}.shp'.format(name_region))
                    single_region.to_file(shape_path)
            except:
                pass

            #try for level one regions
            try:
                for name_region in single_country.GID_1.unique():
                    single_region = single_country[single_country.GID_1 == name_region]

                    shape_path = os.path.join(path, '{}.shp'.format(name_region))
                    single_region.to_file(shape_path)
            except:
                pass

    return print('Completed processing of regional shapes')


def find_country_list(continent_list):
    """

    """
    path_processed = os.path.join(DATA_INTERMEDIATE,'global_countries.shp')
    countries = geopandas.read_file(path_processed)

    subset = countries.loc[countries['continent'].isin(continent_list)]

    country_list = []
    country_regional_levels = []

    for name in subset.GID_0.unique():

        if not name in ['LBY', 'ESH']:
            continue

        country_list.append(name)

        if name in ['LBY', 'ESH'] :
            regional_level =  1
        else:
            regional_level = 2

        country_regional_levels.append({
            'country': name,
            'regional_level': regional_level,
        })

    return country_list, country_regional_levels


def process_lowest_regions(country_list, country_regional_levels):
    """
    Function for processing subnational regions.

    """
    regions = []
    for country in country_list:

        level = get_region_level(country, country_regional_levels)

        filename = 'regions_{}_{}.shp'.format(level, country)
        folder = os.path.join(DATA_INTERMEDIATE, country, 'regions_lowest')
        path_processed = os.path.join(folder, filename)

        if not os.path.exists(path_processed):

            if not os.path.exists(folder):
                os.mkdir(folder)

            print('Working on regions')
            filename = 'gadm36_{}.shp'.format(level)
            path_regions = os.path.join(DATA_RAW, 'gadm36_levels_shp', filename)
            regions = geopandas.read_file(path_regions)

            path_country = os.path.join(DATA_INTERMEDIATE, country, 'national_outline.shp')
            countries = geopandas.read_file(path_country)

            for name in countries.GID_0.unique():

                if not name == country:
                    continue

                print('Working on {}'.format(name))
                regions = regions[regions.GID_0 == name]

                # print('Excluding small shapes')
                # regions['geometry'] = regions.apply(exclude_small_shapes,axis=1)

                # print('Simplifying geometries')
                # regions['geometry'] = regions.simplify(tolerance = 0.005, preserve_topology=True) \
                #     .buffer(0.01).simplify(tolerance = 0.005, preserve_topology=True)
                try:
                    print('Writing global_regions.shp to file')
                    regions.to_file(path_processed, driver='ESRI Shapefile')
                except:
                    pass
        print('Completed processing of regional shapes level {}'.format(level))

    return print('complete')


def segment_lowest_layer(country_list, country_regional_levels):
    """

    """

    path_countries = os.path.join(DATA_INTERMEDIATE,'global_countries.shp')

    if os.path.exists(path_countries):
        countries = geopandas.read_file(path_countries)
    else:
        print('Must generate global_countries.shp first' )

    for country in countries.GID_0.unique():

        print('Working on segmenting lowest layer in {}'.format(country))

        if not country in country_list:
            continue

        level = get_region_level(country, country_regional_levels)

        filename = 'regions_{}_{}.shp'.format(level, country)
        path_regions = os.path.join(DATA_INTERMEDIATE, country, 'regions_lowest', filename)

        try:
            regions = geopandas.read_file(path_regions)

            level_name = 'GID_{}'.format(level)

            for name_region in regions[level_name]:

                single_region = regions[regions[level_name] == name_region]

                folder = os.path.join(DATA_INTERMEDIATE, country, 'regions_lowest')
                shape_path = os.path.join(folder, '{}.shp'.format(name_region))
                single_region.to_file(shape_path)
        except:
            pass

    return print('Completed processing of regional shapes')


def process_settlement_layer(country_list):
    """
    Clip the settlement layer to each country boundary and place in each country folder.

    """
    path_settlements = os.path.join(DATA_RAW,'settlement_layer','ppp_2020_1km_Aggregated.tif')

    settlements = rasterio.open(path_settlements, 'r+')
    settlements.nodata = 255
    settlements.crs = {"init": "epsg:4326"}

    path_countries = os.path.join(DATA_INTERMEDIATE,'global_countries.shp')

    if os.path.exists(path_countries):
        countries = geopandas.read_file(path_countries)
    else:
        print('Must generate global_countries.shp first' )

    num = 0
    for name in countries.GID_0.unique():

        if not name in country_list:
            continue

        print('working on {}'.format(name))

        path_country = os.path.join(DATA_INTERMEDIATE, name)
        shape_path = os.path.join(path_country, 'settlements.tif')

        # if os.path.exists(shape_path):
        #     continue

        single_country = countries[countries.GID_0 == name]

        bbox = single_country.envelope
        geo = geopandas.GeoDataFrame()
        # print(bbox)
        geo = geopandas.GeoDataFrame({'geometry': bbox})
        # print(geo)
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

        with rasterio.open(shape_path, "w", **out_meta) as dest:
                dest.write(out_img)

    return print('Completed processing of settlement layer')


def process_night_lights(country_list):
    """
    Clip the nightlights layer and place in each country folder.

    """
    path_processed = os.path.join(DATA_INTERMEDIATE,'global_countries.shp')

    filename = 'F182013.v4c_web.stable_lights.avg_vis.tif'
    path_night_lights = os.path.join(DATA_RAW, 'nightlights', '2013', filename)

    countries = geopandas.read_file(path_processed)

    for name in countries.GID_0.unique():

        if not name in country_list:
            continue

        print('working on {}'.format(name))

        path_country = os.path.join(DATA_INTERMEDIATE, name)

        existing_files = glob.glob(os.path.join(path_country, 'night_lights*'))
        for existing_file in existing_files:
            if os.path.exists(existing_file):
                os.remove(existing_file)

        single_country = countries[countries.GID_0 == name]

        bbox = single_country.envelope

        geo = geopandas.GeoDataFrame()
        geo = geopandas.GeoDataFrame({'geometry': bbox}, crs=from_epsg('4326'))

        coords = [json.loads(geo.to_json())['features'][0]['geometry']]

        night_lights = rasterio.open(path_night_lights, "r+")
        night_lights.nodata = 0

        out_img, out_transform = mask(night_lights, coords, crop=True)

        out_meta = night_lights.meta.copy()

        out_meta.update({"driver": "GTiff",
                        "height": out_img.shape[1],
                        "width": out_img.shape[2],
                        "transform": out_transform,
                        "crs": 'epsg:4326'})

        shape_path = os.path.join(path_country,'night_lights.tif')

        with rasterio.open(shape_path, "w", **out_meta) as dest:
                dest.write(out_img)

    return print('Completed processing of night lights layer')


def get_regional_data(country_list, country_regional_levels):
    """
    Extract luminosity values.

    """
    path_processed = os.path.join(DATA_INTERMEDIATE,'global_countries.shp')

    countries = geopandas.read_file(path_processed)

    for name in countries.GID_0.unique():

        if not name in country_list:
            continue

        single_country = countries[countries.GID_0 == name]

        print('working on {}'.format(name))

        path_country = os.path.join(DATA_INTERMEDIATE, name, 'regions_lowest')

        if os.path.exists(os.path.join(path_country, '..', 'luminosity.csv')):
            os.remove(os.path.join(path_country, '..', 'luminosity.csv'))

        path_night_lights = os.path.join(DATA_INTERMEDIATE, name, 'night_lights.tif')
        path_settlements = os.path.join(DATA_INTERMEDIATE, name, 'settlements.tif')

        path_regions = glob.glob(os.path.join(path_country, '*.shp'))

        level = get_region_level(name, country_regional_levels)

        results = []

        for path_region in path_regions:

            region = geopandas.read_file(path_region)
            # gid_level = 'GID_{}'.format(level)
            # print(region[gid_level].values[0])
            try:
                # print('get night light values')
                with rasterio.open(path_night_lights) as src:
                    # src.nodata = np.nan
                    affine = src.transform
                    array = src.read(1)

                    #set missing data (-999) to 0
                    # array[array == 0] = 0
                    array[array <= 0] = 0

                    # kwargs.update({'nodata': 0})
                    #get luminosity values
                    luminosity_median = [d['median'] for d in zonal_stats(
                        region, array, stats=['median'], affine=affine)][0]
                    luminosity_summation = [d['sum'] for d in zonal_stats(
                        region, array, stats=['sum'], affine=affine)][0]

                # print('#get settlement values')
                with rasterio.open(path_settlements) as src:
                    # src.nodata = np.nan
                    affine = src.transform
                    array = src.read(1)

                    # array[array == None] = 0
                    array[array <= 0] = 0

                    #get luminosity values
                    population_summation = [d['sum'] for d in zonal_stats(
                        region, array, stats=['sum'], affine=affine)][0]

                #get geographic area
                region.crs = "epsg:4326"
                region = region.to_crs("epsg:3857")

                area_km2 = region['geometry'].area[0] / 10**6

                if luminosity_median == None:
                    luminosity_median = 0
                if luminosity_summation == None:
                    luminosity_summation = 0

                gid_level = 'GID_{}'.format(level)

                results.append({
                    'GID_0': single_country.GID_0.values[0],
                    gid_level: region[gid_level].values[0],
                    'median_luminosity': luminosity_median,
                    'sum_luminosity': luminosity_summation,
                    'mean_luminosity_km2': luminosity_summation / area_km2,
                    'population': population_summation,
                    'area_km2': area_km2,
                    'population_km2': population_summation / area_km2,
                })

            except:
                pass

        results_df = pd.DataFrame(results)

        results_df.to_csv(os.path.join(path_country, '..', 'regional_data.csv'), index=False)

        print('Completed {}'.format(single_country.NAME_0.values[0]))

    return print('Completed night lights data querying')


def get_region_level(name, country_regional_levels):

    for country_regional_level in country_regional_levels:
        if country_regional_level['country'] == name:
            level = country_regional_level['regional_level']

    return level


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


def clean_coverage(x):

    # if its a single polygon, just return the polygon geometry
    if x.geometry.geom_type == 'Polygon':
        if x.geometry.area > 1e7:
            return x.geometry

    # if its a multipolygon, we start trying to simplify and remove shapes if its too big.
    elif x.geometry.geom_type == 'MultiPolygon':

        threshold = 1e7
        hole_threshold_size = 1e7

        # save remaining polygons as new multipolygon for the specific country
        new_geom = []
        for y in x.geometry:

            if y.area > threshold:
                # print(y.boundary)
                # holes =[]

                # for hole in y.interiors:
                #     if Polygon(hole).area > hole_threshold_size:
                #         holes.append(hole)
                # # print(Polygon(y.exterior.coords,[holes]))
                # poly = Polygon(y.exterior.coords,[holes])

                new_geom.append(y)

        return MultiPolygon(new_geom)


def process_coverage_shapes():
    """
    Load in coverage maps, process and export for each country.

    """
    print('Working on coverage_2g.shp')
    # path_raw = os.path.join(DATA_RAW, 'coverage_maps', 'african_coverage_2g_tiles.shp')
    path_raw = os.path.join(DATA_RAW, 'Mobile Coverage Explorer WGS84 v201812 - ESRI SHAPE', 'african_coverage_2g_tiles.shp')
    coverage = geopandas.read_file(path_raw)

    print('Setting crs for tiles')
    coverage.crs = {'init': 'epsg:3857'}

    print('Converting tiles to epsg 4326 (WGS84)')
    coverage = coverage.to_crs({'init': 'epsg:4326'})

    print('Importing global_countries.shp to get each country name')
    path_countries = os.path.join(DATA_INTERMEDIATE,'global_countries.shp')
    countries = geopandas.read_file(path_countries)

    for name in countries.GID_0.unique():

        # if not name == 'MWI':
        #     continue

        print('Working on {}'.format(name))
        path = os.path.join(DATA_INTERMEDIATE, name, 'national_outline.shp')
        national_outline = geopandas.read_file(path)

        print('Intersecting coverage tiles with country outline')
        intersection = geopandas.overlay(coverage, national_outline, how='intersection')

        if len(intersection) > 0:
            print('Exporting country coverage shape')
            output_path = os.path.join(DATA_INTERMEDIATE, name, 'coverage_2g_unprocessed.shp')
            intersection.to_file(output_path, driver='ESRI Shapefile')
        else:
            print('Nothing to write for {}'.format(name))
            continue

    for name in countries.GID_0.unique():

        # if not name == 'MWI':
        #     continue

        path = os.path.join(DATA_INTERMEDIATE, name, 'coverage_2g_unprocessed.shp')

        if os.path.exists(path):

            print('Working on {}'.format(name))

            print('Loading coverage shape')
            coverage = geopandas.read_file(path)

            print('Dissolving polygons')
            coverage['dissolve'] = 1
            coverage = coverage.dissolve(by='dissolve', aggfunc='sum')

            coverage = coverage.to_crs({'init': 'epsg:3857'})

            print('Excluding small shapes')
            coverage['geometry'] = coverage.apply(clean_coverage,axis=1)

            print('Removing empty and null geometries')
            coverage = coverage[~(coverage.is_empty)]
            coverage = coverage[coverage['geometry'].notnull()]

            if len(coverage) > 0:

                print('Simplifying geometries')
                coverage['geometry'] = coverage.simplify(tolerance = 0.005, \
                    preserve_topology=True).buffer(0.01).simplify(tolerance = 0.005, \
                    preserve_topology=True)

                print('Exporting country coverage shape')
                output_path = os.path.join(DATA_INTERMEDIATE, name, 'coverage_2g.shp')
                coverage.to_file(output_path, driver='ESRI Shapefile')


                path1 = os.path.join(DATA_INTERMEDIATE, name, 'coverage_2_unprocessed.shp')
                path2 = os.path.join(DATA_INTERMEDIATE, name, 'coverage_2_unprocessed.shx')
                path3 = os.path.join(DATA_INTERMEDIATE, name, 'coverage_2_unprocessed')
                path4 = os.path.join(DATA_INTERMEDIATE, name, 'coverage_2_unprocessed.dbf')
                path5 = os.path.join(DATA_INTERMEDIATE, name, 'coverage_2_unprocessed.cpg')
                path6 = os.path.join(DATA_INTERMEDIATE, name, 'coverage_2_unprocessed.prj')

                if os.path.exists(path1):
                    os.remove(path1)
                if os.path.exists(path2):
                    os.remove(path2)
                if os.path.exists(path3):
                    os.remove(path3)
                if os.path.exists(path4):
                    os.remove(path4)
                if os.path.exists(path5):
                    os.remove(path5)
                if os.path.exists(path5):
                    os.remove(path6)

            else:
                print('Nothing to write for {}'.format(name))
                continue

    print('Processed coverage shapes')


def process_opencellid():
    """
    Load in site data, process and export for each country.

    """
    print('Loading sites')
    path_raw = os.path.join(DATA_RAW, 'opencellid', 'cell_towers_2020-02-12-T000000.csv')
    sites = pd.read_csv(path_raw, encoding = "ISO-8859-1")#[:1000]

    print('Loading mobile country codes')
    path_raw = os.path.join(DATA_RAW, 'opencellid', 'mcc_codes.csv')
    mcc = pd.read_csv(path_raw, encoding = "ISO-8859-1")

    print('Converting mobile country codes to ints')
    sites['mcc'] = sites['mcc'].astype(int)
    mcc['mcc'] = mcc['mcc'].astype(int)

    print('Merging on mobile country codes')
    sites = sites.merge(mcc, left_on='mcc', right_on='mcc')

    print('Importing global_countries.shp to get each country name')
    path_countries = os.path.join(DATA_INTERMEDIATE,'global_countries.shp')
    countries = geopandas.read_file(path_countries)

    for name in countries.GID_0.unique():

        # if not name == 'SEN':
        #     continue

        print('Working on {}'.format(name))
        # path = os.path.join(DATA_INTERMEDIATE, name)

        sites_by_country = sites[sites.ISO_3digit == name]

        if len(sites_by_country) > 0:

            output_path = os.path.join(DATA_INTERMEDIATE, name, 'sites_opencellid.csv')

            if not os.path.exists(output_path):

                print('Exporting sites for {} as .csv'.format(name))

                sites_by_country.to_csv(output_path, index=False)

            output_path = os.path.join(DATA_INTERMEDIATE, name, 'sites_opencellid.shp')

            if not os.path.exists(output_path):

                print('Exporting sites for {} as .shp'.format(name))
                gdf = geopandas.GeoDataFrame(
                    sites_by_country, geometry=geopandas.points_from_xy(
                        sites_by_country.lon, sites_by_country.lat))
                gdf.crs = {'init': 'epsg:4326'}
                gdf.to_file(output_path)

        else:
            print('Nothing to write for {}'.format(name))
            continue

    print('Processed sites')


def process_mozilla():
    """
    Load in site data, process and export for each country.

    """
    print('Loading sites')
    path_raw = os.path.join(DATA_RAW, 'mozilla_location_service',
        'MLS-full-cell-export-2020-02-13T000000.csv')
    sites = pd.read_csv(path_raw, encoding = "ISO-8859-1")#[:1000]

    print('Loading mobile country codes')
    path_raw = os.path.join(DATA_RAW, 'opencellid', 'mcc_codes.csv')
    mcc = pd.read_csv(path_raw, encoding = "ISO-8859-1")

    print('Converting mobile country codes to ints')
    sites['mcc'] = sites['mcc'].astype(int)
    mcc['mcc'] = mcc['mcc'].astype(int)

    print('Merging on mobile country codes')
    sites = sites.merge(mcc, left_on='mcc', right_on='mcc')

    print('Importing global_countries.shp to get each country name')
    path_countries = os.path.join(DATA_INTERMEDIATE,'global_countries.shp')
    countries = geopandas.read_file(path_countries)

    for name in countries.GID_0.unique():

        if not name == 'SEN':
            continue

        print('Working on {}'.format(name))
        # path = os.path.join(DATA_INTERMEDIATE, name)

        sites_by_country = sites[sites.ISO_3digit == name]

        if len(sites_by_country) > 0:

            output_path = os.path.join(DATA_INTERMEDIATE, name, 'sites_mozilla.csv')

            if not os.path.exists(output_path):

                print('Exporting sites for {} as .csv'.format(name))

                sites_by_country.to_csv(output_path, index=False)

            output_path = os.path.join(DATA_INTERMEDIATE, name, 'sites_mozilla.shp')

            if not os.path.exists(output_path):

                print('Exporting sites for {} as .shp'.format(name))
                gdf = geopandas.GeoDataFrame(
                    sites_by_country, geometry=geopandas.points_from_xy(
                        sites_by_country.lon, sites_by_country.lat))
                gdf.crs = {'init': 'epsg:4326'}
                gdf.to_file(output_path)

        else:
            print('Nothing to write for {}'.format(name))
            continue

    print('Processed sites')


def load_extents(glob_interator):
    """
    Check the extent of each DEM tile, save to dict for future reference.

    For London DEM, this needs to be in EPSG: 4326.

    """
    extents = {}
    for tile_path in glob_interator:
        dataset = rasterio.open(tile_path)
        extents[tuple(dataset.bounds)] = tile_path

    return extents


def get_tile_path_for_point(extents, x, y):
    for (left, bottom, right, top), path in extents.items():
        if x >= left and x <= right and y <= top and y >= bottom:
            return path
    raise ValueError("No tile includes x {} y {}".format(x, y))


def query_data(regions, filepath_nl, filepath_lc, filepath_pop):
    """
    Query raster layer for each shape in regions.

    """
    shapes = []
    csv_data = []

    for region in tqdm(regions):

        geom = shape(region['geometry'])

        population = get_population(geom, filepath_pop)

        pop_density_km2, area_km2 = get_density(geom, population, 'epsg:4326', 'epsg:3857')

        shapes.append({
            'type': region['type'],
            'geometry': mapping(geom),
            # 'id': region['id'],
            'properties': {
                'population': population,
                'pop_density_km2': pop_density_km2,
                'area_km2': area_km2,
                'geotype': define_geotype(pop_density_km2),
                'GID_2': region['properties']['GID_2'],
                'GID_3': region['properties']['GID_3'],
            }
        })

        csv_data.append({
            'population': population,
            'pop_density_km2': pop_density_km2,
            'area_km2': area_km2,
            'geotype': define_geotype(pop_density_km2),
            'GID_2': region['properties']['GID_2'],
            'GID_3': region['properties']['GID_3'],
        })

    return shapes, csv_data


def get_population(geom, filepath_pop):
    """
    Get sum of population within geom.

    """
    population = zonal_stats(geom, filepath_pop, stats="sum", nodata=0)[0]['sum']

    try:
        if population >= 0:
            return population
        else:
            return 0
    except:
        return 0


def aggregate(shapes_lower, regions_upper):
    """
    Using zonal_stats on large areas can lead to a runtime warning due to an overflow.

    This function takes lower (smaller) regions and aggregates them into larger areas.

    """
    idx = index.Index()
    [idx.insert(0, shape(region['geometry']).bounds, region) for region in regions_upper]

    population_data = []

    for shape_lower in shapes_lower:
        for n in idx.intersection((shape(shape_lower['geometry']).bounds), objects=True):
            centroid = shape(shape_lower['geometry']).centroid
            upper_region_shape = shape(n.object['geometry'])
            if upper_region_shape.contains(centroid):
                population_data.append({
                    'population': shape_lower['properties']['population'],
                    'GID_2': n.object['properties']['GID_2'],
                    'GID_3': shape_lower['properties']['GID_3'],
                    })

    shapes = []
    csv_data = []

    for region in tqdm(regions_upper):

        region_id = region['properties']['GID_2']

        geom = shape(region['geometry'])

        population = aggregate_population(population_data, region_id)

        pop_density_km2, area_km2 = get_density(geom, population, 'epsg:4326', 'epsg:3857')

        shapes.append({
            'type': region['type'],
            'geometry': mapping(geom),
            'properties': {
                'population': population,
                'pop_density_km2': pop_density_km2,
                'area_km2': area_km2,
                'geotype': define_geotype(pop_density_km2),
                'GID_2': region['properties']['GID_2'],
            }
        })

        csv_data.append({
            'population': population,
            'pop_density_km2': pop_density_km2,
            'area_km2': area_km2,
            'geotype': define_geotype(pop_density_km2),
            'GID_2': region['properties']['GID_2'],
        })

    return shapes, csv_data


def aggregate_population(population_data, region_id):
    """
    Sum the population from lower level regions to
    upper level regions.

    """
    population = 0

    for item in population_data:
        if item['GID_2'] == region_id:
            population += item['population']

    return population


if __name__ == '__main__':

    # country_list = ['UGA', 'ETH', 'BGD', 'PER', 'MWI', 'ZAF']
    # country_regional_levels = [
    #     {'country': 'UGA', 'regional_level': 3},
    #     {'country': 'ETH', 'regional_level': 3},
    #     {'country': 'BGD', 'regional_level': 3},
    #     {'country': 'PER', 'regional_level': 3},
    #     {'country': 'MWI', 'regional_level': 3},
    #     {'country': 'ZAF', 'regional_level': 3},
    #     ]

    # ###create 'global_countries.shp' if not already processed
    # ###create each 'national_outline.shp' if not already processed
    # process_country_shapes()

    # # ###create 'global_regions.shp' if not already processed
    # # ###create each subnational region .shp if not already processed
    # assemble_global_regional_layer()

    # create_full_regional_layer_2()

    # country_list, country_regional_levels = find_country_list(['Africa', 'South America'])

    # # print('Processing lowest regions')
    # process_lowest_regions(country_list, country_regional_levels)

    # segment_lowest_layer(country_list, country_regional_levels)

    # print('Processing settlement layer')
    # process_settlement_layer(country_list)

    # print('Processing night lights')
    # process_night_lights(country_list)

    # get_regional_data(country_list, country_regional_levels)

    # process_coverage_shapes()

    # process_opencellid()

    process_mozilla()
