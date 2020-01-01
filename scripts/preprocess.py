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


def process_settlement_layer():
    """
    Clip the settlement layer to each country boundary and place in each country folder.

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



def get_nightlight_data(path, data_year):
    """
    Download the nighlight data from NOAA.

    As these files are large, they can take a couple of minutes to download.

    Parameters
    ----------
    path : string
        Path to the desired data location.

    """
    if not os.path.exists(path):
        os.makedirs(path)

    for year in [data_year]:
        year = str(year)
        url = ('https://ngdc.noaa.gov/eog/data/web_data/v4composites/F18'
                + year + '.v4.tar')
        target = os.path.join(path, year)
        if not os.path.exists(target):
            os.makedirs(target, exist_ok=True)
        target += '/nightlights_data'
        response = requests.get(url, stream=True)
        if not os.path.exists(target):
            if response.status_code == 200:
                print('Downloading data')
                with open(target, 'wb') as f:
                    f.write(response.raw.read())
    print('Data download complete')

    for year in [data_year]:

        print('Working on {}'.format(year))
        folder_loc = os.path.join(path, str(year))
        file_loc = os.path.join(folder_loc, 'nightlights_data')

        print('Unzipping data')
        tar = tarfile.open(file_loc)
        tar.extractall(path=folder_loc)

        files = os.listdir(folder_loc)
        for filename in files:
            file_path = os.path.join(path, str(year), filename)
            if 'stable' in filename: # only need stable_lights
                if file_path.split('.')[-1] == 'gz':
                    # unzip the file is a .gz file
                    with gzip.open(file_path, 'rb') as f_in:
                        with open(file_path[:-3], 'wb') as f_out:
                            shutil.copyfileobj(f_in, f_out)

    return print('Downloaded and processed night light data')


def process_wb_survey_data(path):
    """
    This function takes the World Bank Living Standards Measurement
    Survey and processes all the data.

    I've used the 2016-2017 Household LSMS survey data for Malawi from
    https://microdata.worldbank.org/index.php/catalog/lsms.
    It should be in ../data/raw/LSMS/malawi-2016

    IHS4 Consumption Aggregate.csv contains:

    - Case ID: Unique household ID
    - rexpagg: Total annual per capita consumption,
        spatially & (within IHS4) temporally adjust (rexpagg)
    - adulteq: Adult equivalence
    - hh_wgt: Household sampling weight

    HouseholdGeovariablesIHS4.csv contains:

    - Case ID: Unique household ID
    - HHID: Survey solutions unique HH identifier
    - lat_modified: GPS Latitude Modified
    - lon_modified: GPS Longitude Modified

    """
    ## Path to non-spatial consumption results
    file_path = os.path.join(path, 'IHS4 Consumption Aggregate.csv')

    ##Read results
    df = pd.read_csv(file_path)

    ##Estimate daily consumption accounting for adult equivalence
    df['cons'] = df['rexpagg'] / (365 * df['adulteq'])
    df['cons'] = df['cons'] * 107.62 / (116.28 * 166.12)

    ## Rename column
    df.rename(columns={'hh_wgt': 'weight'}, inplace=True)

    ## Subset desired columns
    df = df[['case_id', 'cons', 'weight', 'urban']]

    ##Read geolocated survey data
    df_geo = pd.read_csv(os.path.join(path,
        'HouseholdGeovariables_csv/HouseholdGeovariablesIHS4.csv'))

    ##Subset household coordinates
    df_cords = df_geo[['case_id', 'HHID', 'lat_modified', 'lon_modified']]
    df_cords.rename(columns={
        'lat_modified': 'lat', 'lon_modified': 'lon'}, inplace=True)

    ##Merge to add coordinates to aggregate consumption data
    df = pd.merge(df, df_cords[['case_id', 'HHID']], on='case_id')

    ##Repeat to get df_combined
    df_combined = pd.merge(df, df_cords, on=['case_id', 'HHID'])

    ##Drop case id variable
    df_combined.drop('case_id', axis=1, inplace=True)

    ##Drop incomplete
    df_combined.dropna(inplace=True) # can't use na values

    print('Combined shape is {}'.format(df_combined.shape))

    ##Find cluster constant average
    clust_cons_avg = df_combined.groupby(
                        ['lat', 'lon']).mean().reset_index()[
                        ['lat', 'lon', 'cons']]

    ##Merge dataframes
    df_combined = pd.merge(df_combined.drop(
                        'cons', axis=1), clust_cons_avg, on=[
                        'lat', 'lon'])

    ##Get uniques
    df_uniques = df_combined.drop_duplicates(subset=
                        ['lat', 'lon'])

    print('Processed WB Living Standards Measurement Survey')

    return df_uniques, df_combined


def query_nightlight_data(filename, df_uniques, df_combined, path):
    """
    Query the nighlight data and export results.

    """
    img = geoio.GeoImage(filename)
    ##Convert points in projection space to points in raster space.
    xPixel, yPixel = img.proj_to_raster(34.915074, -14.683761)

    ##Remove single-dimensional entries from the shape of an array.
    im_array = np.squeeze(img.get_data())

    ##Get the nightlight values
    im_array[int(yPixel),int(xPixel)]

    household_nightlights = []
    for i,r in df_uniques.iterrows():

        ##Create 10km^2 bounding box around point
        min_lat, min_lon, max_lat, max_lon = create_space(r.lat, r.lon)

        ##Convert point coordinaces to raster space
        xminPixel, yminPixel = img.proj_to_raster(min_lon, min_lat)
        xmaxPixel, ymaxPixel = img.proj_to_raster(max_lon, max_lat)

        ##Get min max values
        xminPixel, xmaxPixel = (min(xminPixel, xmaxPixel),
                                max(xminPixel, xmaxPixel))
        yminPixel, ymaxPixel = (min(yminPixel, ymaxPixel),
                                max(yminPixel, ymaxPixel))
        xminPixel, yminPixel, xmaxPixel, ymaxPixel = (
                                int(xminPixel), int(yminPixel),
                                int(xmaxPixel), int(ymaxPixel))

        ##Append mean value data to df
        household_nightlights.append(
            im_array[yminPixel:ymaxPixel,xminPixel:xmaxPixel].mean())

    df_uniques['nightlights'] = household_nightlights

    df_combined = pd.merge(df_combined, df_uniques[
                    ['lat', 'lon', 'nightlights']], on=['lat', 'lon'])

    print('Complete querying process')

    return df_combined


def create_space(lat, lon):
    """
    Creates a 10km^2 area bounding box.

    Parameters
    ----------
    lat : float
        Latitude
    lon : float
        Longitude

    """
    bottom = lat - (180 / math.pi) * (5000 / 6378137)
    left = lon - (180 / math.pi) * (5000 / 6378137) / math.cos(lat)
    top = lat + (180 / math.pi) * (5000 / 6378137)
    right = lon + (180 / math.pi) * (5000 / 6378137) / math.cos(lat)

    return bottom, left, top, right


def create_clusters(df_combined):
    """

    """
    # encode "RURAL" as 0 and "URBAN" as 1
    df_combined['urban_encoded'] = pd.factorize(df_combined['urban'])[0]

    clust_groups = df_combined.groupby(['lat', 'lon'])

    clust_averages = clust_groups.mean().reset_index()

    counts = clust_groups.count().reset_index()[['lat', 'lon', 'cons']]
    counts.rename(columns={'cons': 'num_households'}, inplace=True)
    clust_averages = pd.merge(clust_averages, counts, on=['lat', 'lon'])

    # if more than 0.5 average within a clust, label it as 1 (URBAN), else 0
    clust_averages['urban_encoded'] = clust_averages['urban_encoded'].apply(
        lambda x: round(x))

    clust_averages['urban_encoded'] = clust_averages['urban_encoded'].apply(
        lambda x: 'Rural' if x == 0 else 'Urban')

    clust_averages = clust_averages.drop('urban', axis=1)

    clust_averages.rename(columns={'urban_encoded': 'urban'}, inplace=True)

    return clust_averages


def get_r2_numpy_corrcoef(x, y):
    """
    Calculate correlation coefficient using np.corrcoef.

    """
    return np.corrcoef(x, y)[0, 1]**2


def process_night_lights():
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

        if not name == 'MWI':
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

        night_lights = rasterio.open(path_night_lights)
        # print(night_lights.nodata)
        #chop on coords
        out_img, out_transform = mask(night_lights, coords, crop=True)
        # print(out_transform)
        # Copy the metadata
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


def get_regional_data():
    """
    Extract luminosity values.

    """
    path_processed = os.path.join(DATA_INTERMEDIATE,'global_countries.shp')

    countries = geopandas.read_file(path_processed)

    for name in countries.GID_0.unique():

        if not name == 'MWI':
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

        print('Working on {}'.format(name))
        path = os.path.join(DATA_INTERMEDIATE, name, 'national_outline.shp')
        national_outline = geopandas.read_file(path)

        print('Intersecting coverage tiles with country outline')
        intersection = geopandas.overlay(coverage, national_outline, how='intersection')

        if len(intersection) > 0:
            print('Exporting country coverage shape')
            output_path = os.path.join(DATA_INTERMEDIATE, name, 'coverage_2g.shp')
            intersection.to_file(output_path, driver='ESRI Shapefile')
        else:
            print('Nothing to write for {}'.format(name))
            continue

    for name in countries.GID_0.unique():

        path = os.path.join(DATA_INTERMEDIATE, name, 'coverage_2g.shp')

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
                output_path = os.path.join(DATA_INTERMEDIATE, name, 'coverage_2g_processed.shp')
                coverage.to_file(output_path, driver='ESRI Shapefile')

            else:
                print('Nothing to write for {}'.format(name))
                continue

    print('Processed coverage shapes')

if __name__ == '__main__':

    # ###create 'global_countries.shp' if not already processed
    # ###create each 'national_outline.shp' if not already processed
    # process_country_shapes()

    # ###create 'global_regions.shp' if not already processed
    # ###create each subnational region .shp if not already processed
    # assemble_global_regional_layer()

    # process_settlement_layer()

    year = 2013
    path_nightlights = os.path.join(DATA_RAW, 'nightlights')
    filename = 'F182013.v4c_web.stable_lights.avg_vis.tif'
    filepath = os.path.join(path_nightlights, str(year), filename)

    if not os.path.exists(filepath):
        print('Need to download nightlight data first')
        get_nightlight_data(path_nightlights, year)
    else:
        print('Nightlight data already exists in data folder')

    print('Processing World Bank Living Standards Measurement Survey')
    path = os.path.join(DATA_RAW, 'lsms', 'malawi_2016')
    df_uniques, df_combined = process_wb_survey_data(path)

    print('Querying nightlight data')
    df_combined = query_nightlight_data(filepath, df_uniques,
                df_combined, os.path.join(path_nightlights, str(year)))

    print('Creating clusters')
    clust_averages = create_clusters(df_combined)

    # print('Writing Living Standards Measurement Survey data')
    # df_combined.to_csv(os.path.join(DATA_INTERMEDIATE, 'MWI',
    #             'lsms-household-2016.csv'), index=False)

    clust_averages = clust_averages.drop(clust_averages[clust_averages.cons > 50].index)

    print('Getting coefficient value')
    nl_coefficient = get_r2_numpy_corrcoef(clust_averages.cons, clust_averages.nightlights)

    clust_averages['cons_pred'] = clust_averages['nightlights'] * (1 + nl_coefficient)

    print('Writing all other data')
    clust_averages.to_csv(os.path.join(DATA_INTERMEDIATE, 'MWI',
        'lsms-cluster-2016.csv'), index=False)



    import matplotlib.pyplot as plt
    import seaborn as sns
    to_plot = clust_averages[["nightlights", "cons", "urban"]]

    fig, ax = plt.subplots()
    g = sns.scatterplot(x="nightlights", y="cons", hue="urban", data=to_plot, ax=ax)
    g.set(xlabel='Nighttime Luminosity', ylabel='Household Consumption ($ per day)',
        title='Nighttime Luminosity vs Consumption')

    handles, labels = ax.get_legend_handles_labels()
    ax.legend(handles=reversed(handles[1:3]), labels=reversed(labels[1:3]))
    fig.savefig(os.path.join(BASE_PATH, '..', 'vis','figures','nightlights_vs_cons.pdf'))

    to_plot = clust_averages[["cons_pred", "cons", "urban"]]

    fig, ax = plt.subplots()
    g = sns.scatterplot(x="cons_pred", y="cons", hue="urban", data=to_plot, ax=ax)
    g.set(xlabel='Predicted Consumption ($ per day)', ylabel='Household Consumption ($ per day)',
        title='Predicted Consumption vs Consumption')

    handles, labels = ax.get_legend_handles_labels()
    ax.legend(handles=reversed(handles[1:3]), labels=reversed(labels[1:3]))
    fig.savefig(os.path.join(BASE_PATH, '..', 'vis','figures','pred_cons_vs_cons.pdf'))




    # g.set(xscale="log")

    # print(nl_coefficient)
    # process_night_lights()

    # get_regional_data()

    # # planet_osm()

    # # poly_files()

    # # all_countries(subset = [], regionalized=False, reversed_order=True)

    # process_coverage_shapes()
