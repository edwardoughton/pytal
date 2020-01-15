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
import geoio
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

        print('working on {}'.format(name))

        path = os.path.join(DATA_INTERMEDIATE, name)

        if not os.path.exists(path):
            os.makedirs(path)

        single_country = countries[countries.GID_0 == name]

        shape_path = os.path.join(path, 'national_outline.shp')
        single_country.to_file(shape_path)

    return print('Completed processing of country shapes')


def process_regions(level):
    """
    Function for processing subnational regions.

    """
    filename = 'global_regions_{}.shp'.format(level)
    path_processed = os.path.join(DATA_INTERMEDIATE, filename)

    if not os.path.exists(path_processed):

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

    else:
        regions = geopandas.read_file(path_processed)

    return regions


def process_lowest_regions(country_list, country_regional_levels):
    """
    Function for processing subnational regions.

    """
    regions = []
    for country in country_list:
        for country_regional_level in country_regional_levels:
            if country_regional_level['country'] == country:
                gadm_level = country_regional_level['regional_level']

        filename = 'regions_{}_{}.shp'.format(gadm_level, country)
        path_processed = os.path.join(DATA_INTERMEDIATE, country, 'regions', filename)

        if not os.path.exists(path_processed):

            print('Working on regions')
            filename = 'gadm36_{}.shp'.format(gadm_level)
            path_regions = os.path.join(DATA_RAW, 'gadm36_levels_shp', filename)
            regions = geopandas.read_file(path_regions)

            path_countries = os.path.join(DATA_INTERMEDIATE, country, 'national_outline.shp')
            countries = geopandas.read_file(path_countries)

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

                print('Writing global_regions.shp to file')
                regions.to_file(path_processed, driver='ESRI Shapefile')

        print('Completed processing of regional shapes level {}'.format(gadm_level))

    return print('complete')


def assemble_global_regional_layer():
    """
    Assemble a single layer of sub-national regional shapes.

    Set the desired level to be used in the 'global_information.csv' folder.

    Write each sub-national region to an individual shape in each nation's
    regions folder.

    """
    filename = 'global_regions.shp'
    path_processed = os.path.join(DATA_INTERMEDIATE, filename)

    #load regions and process
    regions_1 = process_regions(1)
    regions_2 = process_regions(2)

    #select desired regions
    regions_1 = regions_1.loc[regions_1['gid_region'] == 1]
    regions_2 = regions_2.loc[regions_2['gid_region'] == 2]

    #concatinate
    regions = pd.concat([regions_1, regions_2], sort=True)

    # ###get missing small countries
    # countries = geopandas.read_file(os.path.join(DATA_INTERMEDIATE, 'global_countries.shp'))

    # for name in countries.ISO_3digit.unique():
    #     if name in [
    #         'ABW', 'AIA', 'BLM', 'BVT', 'CCK', 'COK', 'CUW', 'CXR', 'FLK', 'GIB', 'HMD',
    #         'IOT', 'KIR', 'MAF', 'MCO', 'MDV', 'MHL', 'NFK', 'NIU', 'PCN', 'SGS', 'SXM',
    #         'VAT']:
    #         country = countries[countries.GID_0 == name]
    #         regions = pd.concat([regions, country], sort=True)

    regions.reset_index(drop=True,inplace=True)

    print('Writing global_regions.shp to file')
    regions.to_file(path_processed, driver='ESRI Shapefile')

    print('Completed processing of regional shapes level')

    for name in regions.GID_0.unique():

        # if not name == 'ABW':
        #     continue

        path = os.path.join(DATA_INTERMEDIATE, name, 'regions')

        #remove old files first
        existing_files = glob.glob(os.path.join(path, '*'))
        for existing_file in existing_files:
            if os.path.exists(existing_file):
                os.remove(existing_file)

        if os.path.exists(path):
            os.rmdir(path)

        if not os.path.exists(path):
            os.makedirs(path)

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

            # #catch all small countries with no sub-national regions
            # if name in ['ABW', 'AIA', 'BLM', 'BVT', 'CCK', 'COK', 'CUW', 'CXR',
            #             'FLK', 'GIB', 'HMD', 'IOT', 'KIR', 'MAF', 'MCO', 'MDV',
            #             'MHL', 'NFK', 'NIU', 'PCN', 'SGS', 'SXM', 'VAT']:
            #     country_path = os.path.join(DATA_INTERMEDIATE, name, 'national_outline.shp')
            #     country = geopandas.read_file(country_path)
            #     country.to_file(path, driver='ESRI Shapefile')
        else:
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

    # extents = load_extents(path_night_lights)

    countries = geopandas.read_file(path_processed)#[:40]

    # num = 0
    for name in countries.GID_0.unique():

        if not name in country_list:
            continue

        print('working on {}'.format(name))

        path_country = os.path.join(DATA_INTERMEDIATE, name)

        #remove old files first
        existing_files = glob.glob(os.path.join(path_country, 'night_lights*'))
        for existing_file in existing_files:
            if os.path.exists(existing_file):
                os.remove(existing_file)

        single_country = countries[countries.GID_0 == name]

        bbox = single_country.envelope

        geo = geopandas.GeoDataFrame()
        geo = geopandas.GeoDataFrame({'geometry': bbox}, crs=from_epsg('4326')) #index=[num],

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


def get_regional_data(country_list):
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

        path_country = os.path.join(DATA_INTERMEDIATE, name, 'regions')

        if os.path.exists(os.path.join(path_country, '..', 'luminosity.csv')):
            os.remove(os.path.join(path_country, '..', 'luminosity.csv'))

        path_night_lights = os.path.join(DATA_INTERMEDIATE, name, 'night_lights.tif')
        path_settlements = os.path.join(DATA_INTERMEDIATE, name, 'settlements.tif')

        path_regions = glob.glob(os.path.join(path_country, '*.shp'))

        results = []

        for path_region in path_regions:

            region = geopandas.read_file(path_region)

            try:
                #get night light values
                with rasterio.open(path_night_lights) as src:
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

                #get settlement values
                with rasterio.open(path_settlements) as src:
                    affine = src.transform
                    array = src.read(1)

                    #set missing data (-999) to 0
                    # array[array == None] = 0
                    array[array <= 0] = 0
                    # kwargs.update({'nodata': 0})

                    #get luminosity values
                    population_summation = [d['sum'] for d in zonal_stats(
                        region, array, stats=['sum'], affine=affine)][0]

                #get geographic area
                # print(region.crs)
                # region.crs = {'init' :'epsg:4326'}
                region = region.to_crs({'init': 'epsg:3857'})
                # print(region.crs)
                area_km2 = region['geometry'].area[0] / 10**6

                if luminosity_median == None:
                    luminosity_median = 0
                if luminosity_summation == None:
                    luminosity_summation = 0

                results.append({
                    'GID_0': single_country.GID_0.values[0],
                    'GID_1': region.GID_1.values[0],
                    'GID_2': region.GID_2.values[0],
                    'gid_region': region.gid_region,
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


def planet_osm():
    """
    This function will download the planet file from the OSM servers.

    """
    osm_path_in = os.path.join(DATA_RAW,'planet_osm')

    # create directory to save planet osm file if that directory does not exit yet.
    if not os.path.exists(osm_path_in):
        os.makedirs(osm_path_in)

    # if planet file is not downloaded yet, download it.
    if 'planet-latest.osm.pbf' not in os.listdir(osm_path_in):

        url = 'https://planet.openstreetmap.org/pbf/planet-latest.osm.pbf'
        urllib.request.urlretrieve(url, os.path.join(osm_path_in,'planet-latest.osm.pbf'))

    else:
        print('Planet file is already downloaded')


def poly_files(data_path, global_shape, save_shapefile=False, regionalized=False):

    """
    This function will create the .poly files from the world shapefile. These
    .poly files are used to extract data from the openstreetmap files.

    This function is adapted from the OSMPoly function in QGIS.

    Arguments:
        *data_path* : base path to location of all files.

        *global_shape*: exact path to the global shapefile used to create the poly files.

    Optional Arguments:
        *save_shape_file* : Default is **False**. Set to **True** will the new shapefile
        with the countries that we include in this analysis will be saved.

        *regionalized*  : Default is **False**. Set to **True** will perform the analysis
        on a regional level.

    Returns:
        *.poly file* for each country in a new dir in the working directory.
    """
# =============================================================================
#     """ Create output dir for .poly files if it is doesnt exist yet"""
# =============================================================================
    poly_dir = os.path.join(data_path,'country_poly_files')

    if regionalized == True:
        poly_dir = os.path.join(data_path,'regional_poly_files')

    if not os.path.exists(poly_dir):
        os.makedirs(poly_dir)

# =============================================================================
#     """ Set the paths for the files we are going to use """
# =============================================================================
    wb_poly_out = os.path.join(data_path,'input_data','country_shapes.shp')

    if regionalized == True:
        wb_poly_out = os.path.join(data_path,'input_data','regional_shapes.shp')

# =============================================================================
#   """Load country shapes and country list and only keep the required countries"""
# =============================================================================
    wb_poly = geopandas.read_file(global_shape)

    # filter polygon file
    if regionalized == True:
        wb_poly = wb_poly.loc[wb_poly['GID_0'] != '-']
        wb_poly = wb_poly.loc[wb_poly['TYPE_1'] != 'Water body']

    else:
        # print(wb_poly)
        wb_poly = wb_poly.loc[wb_poly['GID_0'] != '-']
        # wb_poly = wb_poly.loc[wb_poly['ISO_3digit'] != '-']

    wb_poly.crs = {'init' :'epsg:4326'}

    # and save the new country shapefile if requested
    if save_shapefile == True:
        wb_poly.to_file(wb_poly_out)

    # we need to simplify the country shapes a bit. If the polygon is too diffcult,
    # osmconvert cannot handle it.
#    wb_poly['geometry'] = wb_poly.simplify(tolerance = 0.1, preserve_topology=False)

# =============================================================================
#   """ The important part of this function: create .poly files to clip the country
#   data from the openstreetmap file """
# =============================================================================
    num = 0
    # iterate over the counties (rows) in the world shapefile
    for f in wb_poly.iterrows():
        f = f[1]
        num = num + 1
        geom=f.geometry

#        try:
        # this will create a list of the different subpolygons
        if geom.geom_type == 'MultiPolygon':
            polygons = geom

        # the list will be lenght 1 if it is just one polygon
        elif geom.geom_type == 'Polygon':
            polygons = [geom]

        # define the name of the output file, based on the ISO3 code
        ctry = f['GID_0']
        if regionalized == True:
            attr=f['GID_1']
        else:
            attr=f['GID_0']

        # start writing the .poly file
        f = open(poly_dir + "/" + attr +'.poly', 'w')
        f.write(attr + "\n")

        i = 0

        # loop over the different polygons, get their exterior and write the
        # coordinates of the ring to the .poly file
        for polygon in polygons:

            if ctry == 'CAN':

                x = polygon.centroid.x
                if x < -90:
                    x = -90
                y = polygon.centroid.y
                dist = distance((x,y), (83.24,-79.80), ellipsoid='WGS-84').kilometers
                if dist < 2000:
                    continue

            if ctry == 'RUS':
                x = polygon.centroid.x
                if x < -90:
                    x = -90
                if x > 90:
                    x = 90
                y = polygon.centroid.y
                dist = distance((x,y), (58.89,82.26), ellipsoid='WGS-84').kilometers
                if dist < 500:
                    continue

            polygon = np.array(polygon.exterior)

            j = 0
            f.write(str(i) + "\n")

            for ring in polygon:
                j = j + 1
                f.write("    " + str(ring[0]) + "     " + str(ring[1]) +"\n")

            i = i + 1
            # close the ring of one subpolygon if done
            f.write("END" +"\n")

        # close the file when done
        f.write("END" +"\n")
        f.close()
#        except:
#            print(f['GID_1'])


def clip_osm(data_path,planet_path,area_poly,area_pbf):
    """
    Clip the an area osm file from the larger continent (or planet) file and
    save to a new osm.pbf file. This is much faster compared to clipping the
    osm.pbf file while extracting through ogr2ogr.

    This function uses the osmconvert tool, which can be found at
    http://wiki.openstreetmap.org/wiki/Osmconvert.

    Either add the directory where this executable is located to your
    environmental variables or just put it in the 'scripts' directory.

    Arguments:
        *continent_osm*: path string to the osm.pbf file of the continent
        associated with the country.

        *area_poly*: path string to the .poly file, made through the
        'create_poly_files' function.

        *area_pbf*: path string indicating the final output dir and output
        name of the new .osm.pbf file.

    Returns:
        a clipped .osm.pbf file.
    """
    import os
    import configparser
    CONFIG = configparser.ConfigParser()
    CONFIG.read(os.path.join('scripts', 'script_config.ini'))
    BASE_PATH = CONFIG['file_locations']['base_path']

    print('{} started!'.format(area_pbf))
    # osm_convert_path = 'D:\github\pytal\data\osmconvert64\osmconvert64-0.8.8p'
    osm_convert_path = os.path.join(BASE_PATH,'osmconvert64','osmconvert64-0.8.8p')
    try:
        if (os.path.exists(area_pbf) is not True):
            os.system('{}  {} -B={} -o={}'.format( \
                osm_convert_path,planet_path,area_poly,area_pbf)) # --complete-ways
            print('{} finished!'.format(area_pbf))

    except:
        print('{} did not finish!'.format(area_pbf))

    return print('Complete')


def all_countries(subset = [], regionalized=False, reversed_order=False):
    """
    Clip all countries from the planet osm file and save them to individual osm.pbf files

    Optional Arguments:
        *subset* : allow for a pre-defined subset of countries. REquires ISO3 codes.
        Will run all countries if left empty.

        *regionalized* : Default is **False**. Set to **True** if you want to have the
        regions of a country as well.

        *reversed_order* : Default is **False**. Set to **True**  to work backwards for
        a second process of the same country set to prevent overlapping calculations.

    Returns:
        clipped osm.pbf files for the defined set of countries (either the whole world
        by default or the specified subset)

    """

    # set data path
    data_path = DATA_INTERMEDIATE

    # path to planet file
    planet_path = os.path.join(DATA_RAW,'planet_osm','planet-latest.osm.pbf')

    # global shapefile path
    if regionalized == True:
        world_path = os.path.join(data_path,'global_regions.shp')
    else:
        world_path = os.path.join(data_path,'global_countries.shp')

    # create poly files for all countries
    poly_files(data_path,world_path,save_shapefile=False,regionalized=regionalized)

    # prepare lists for multiprocessing
    if not os.path.exists(os.path.join(data_path,'country_poly_files')):
        os.makedirs(os.path.join(data_path,'country_poly_files'))

    if not os.path.exists(os.path.join(data_path,'country_osm')):
        os.makedirs(os.path.join(data_path,'country_osm'))

    if regionalized == False:

        get_poly_files = os.listdir(os.path.join(data_path,'country_poly_files'))
        if len(subset) > 0:
            polyPaths = [os.path.join(data_path,'country_poly_files',x) for x in \
                            get_poly_files if x[:3] in subset]
            area_pbfs = [os.path.join(data_path,'region_osm_admin1', \
                            x.split('.')[0]+'.osm.pbf') for x in \
                            get_poly_files if x[:3] in subset]
        else:
            polyPaths = [os.path.join(data_path,'country_poly_files',x) for x in \
                            get_poly_files]
            area_pbfs = [os.path.join(data_path,'region_osm_admin1', \
                            x.split('.')[0]+'.osm.pbf') for x in get_poly_files]

        big_osm_paths = [planet_path]*len(polyPaths)

    elif regionalized == True:

        if not os.path.exists(os.path.join(data_path,'regional_poly_files')):
            os.makedirs(os.path.join(data_path,'regional_poly_files'))

        if not os.path.exists(os.path.join(data_path,'region_osm')):
            os.makedirs(os.path.join(data_path,'region_osm_admin1'))

        get_poly_files = os.listdir(os.path.join(data_path,'regional_poly_files'))
        if len(subset) > 0:
            polyPaths = [os.path.join(data_path,'regional_poly_files',x) for x in \
                            get_poly_files if x[:3] in subset]
            area_pbfs = [os.path.join(data_path,'region_osm_admin1', \
                            x.split('.')[0]+'.osm.pbf') for x in \
                            get_poly_files if x[:3] in subset]
            big_osm_paths = [os.path.join(DATA_RAW,'planet_osm', \
                                x[:3]+'.osm.pbf') for x in \
                                get_poly_files if x[:3] in subset]
        else:
            polyPaths = [os.path.join(data_path,'regional_poly_files',x) \
                            for x in get_poly_files]
            area_pbfs = [os.path.join(data_path,'region_osm_admin1', \
                            x.split('.')[0]+'.osm.pbf') for x in get_poly_files]
            big_osm_paths = [os.path.join(DATA_RAW,'planet_osm', \
                                x[:3]+'.osm.pbf') for x in get_poly_files]

    data_paths = [data_path]*len(polyPaths)

    # allow for reversed order if you want to run two at the same time
    # (convenient to work backwards for the second process, to prevent
    # overlapping calculation)
    if reversed_order == True:
        polyPaths = polyPaths[::-1]
        area_pbfs = area_pbfs[::-1]
        big_osm_paths = big_osm_paths[::-1]

    # extract all country osm files through multiprocesing
    pool = Pool(cpu_count()-1)
    pool.starmap(clip_osm, zip(data_paths, big_osm_paths, polyPaths, area_pbfs))


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
    path_raw = os.path.join(DATA_RAW, 'coverage_maps', 'african_coverage_2g_tiles.shp')
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

if __name__ == '__main__':

    country_list = ['UGA', 'ETH', 'BGD', 'PER', 'MWI', 'ZAF']

    # ###create 'global_countries.shp' if not already processed
    # ###create each 'national_outline.shp' if not already processed
    # process_country_shapes()

    # ###create 'global_regions.shp' if not already processed
    # ###create each subnational region .shp if not already processed
    # assemble_global_regional_layer()

    country_regional_levels = [
        {'country': 'UGA', 'regional_level': 3},
        {'country': 'ETH', 'regional_level': 3},
        {'country': 'BGD', 'regional_level': 3},
        {'country': 'PER', 'regional_level': 3},
        {'country': 'MWI', 'regional_level': 3},
        {'country': 'ZAF', 'regional_level': 3},
        ]

    print('Processing lowest regions')
    process_lowest_regions(country_list, country_regional_levels)

    # print('Processing settlement layer')
    # process_settlement_layer(country_list)

    process_night_lights(country_list)

    # get_regional_data(country_list)

    # # planet_osm()

    # # poly_files()

    # # all_countries(subset = [], regionalized=False, reversed_order=True)

    # process_coverage_shapes()
