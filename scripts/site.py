"""
Read in available site data

Written by Ed Oughton

21st April 2020

"""
import os
import csv
import configparser
import pandas as pd
import geopandas as gpd
import xlrd
import numpy as np
from shapely.geometry import MultiPolygon
from shapely.ops import transform, unary_union

CONFIG = configparser.ConfigParser()
CONFIG.read(os.path.join(os.path.dirname(__file__), 'script_config.ini'))
BASE_PATH = CONFIG['file_locations']['base_path']

DATA_RAW = os.path.join(BASE_PATH, 'raw', 'real_site_data')
DATA_INTERMEDIATE = os.path.join(BASE_PATH, 'intermediate')
DATA_PROCESSED = os.path.join(BASE_PATH, 'processed')


def process_country_shape(country):
    """
    Creates a single national boundary for the desired country.

    Parameters
    ----------
    country : string
        Three digit ISO country code.

    """
    print('----')

    iso3 = country['iso3']

    path = os.path.join(DATA_INTERMEDIATE, iso3)

    if os.path.exists(os.path.join(path, 'national_outline.shp')):
        return 'Completed national outline processing'

    if not os.path.exists(path):
        print('Creating directory {}'.format(path))
        os.makedirs(path)
    shape_path = os.path.join(path, 'national_outline.shp')

    print('Loading all country shapes')
    path = os.path.join(DATA_RAW, '..', 'gadm36_levels_shp', 'gadm36_0.shp')
    countries = gpd.read_file(path)

    print('Getting specific country shape for {}'.format(iso3))
    single_country = countries[countries.GID_0 == iso3]

    print('Excluding small shapes')
    single_country['geometry'] = single_country.apply(
        exclude_small_shapes, axis=1)

    print('Adding ISO country code and other global information')
    glob_info_path = os.path.join(BASE_PATH, 'global_information.csv')
    load_glob_info = pd.read_csv(glob_info_path, encoding = "ISO-8859-1")
    single_country = single_country.merge(
        load_glob_info,left_on='GID_0', right_on='ISO_3digit')

    print('Exporting processed country shape')
    single_country.to_file(shape_path, driver='ESRI Shapefile')

    return print('Processing country shape complete')


def process_regions(country):
    """
    Function for processing the lowest desired subnational regions for the
    chosen country.

    Parameters
    ----------
    country : string
        Three digit ISO country code.

    """
    regions = []

    iso3 = country['iso3']
    level = country['regional_level']

    for regional_level in range(1, level + 1):

        filename = 'regions_{}_{}.shp'.format(regional_level, iso3)
        folder = os.path.join(DATA_INTERMEDIATE, iso3, 'regions')
        path_processed = os.path.join(folder, filename)

        if os.path.exists(path_processed):
            continue

        print('----')
        print('Working on {} level {}'.format(iso3, regional_level))

        if not os.path.exists(folder):
            os.mkdir(folder)

        filename = 'gadm36_{}.shp'.format(regional_level)
        path_regions = os.path.join(DATA_RAW, '..',  'gadm36_levels_shp', filename)
        regions = gpd.read_file(path_regions)

        print('Subsetting {} level {}'.format(iso3, regional_level))
        regions = regions[regions.GID_0 == iso3]

        print('Excluding small shapes')
        regions['geometry'] = regions.apply(exclude_small_shapes, axis=1)

        try:
            print('Writing global_regions.shp to file')
            regions.to_file(path_processed, driver='ESRI Shapefile')
        except:
            print('Unable to write {}'.format(filename))
            pass

    print('Completed processing of regional shapes level {}'.format(level))

    return print('complete')


def exclude_small_shapes(x):
    """
    Remove small multipolygon shapes.

    Parameters
    ---------
    x : polygon
        Feature to simplify.

    Returns
    -------
    MultiPolygon : MultiPolygon
        Shapely MultiPolygon geometry without tiny shapes.

    """
    # if its a single polygon, just return the polygon geometry
    if x.geometry.geom_type == 'Polygon':
        return x.geometry

    # if its a multipolygon, we start trying to simplify
    # and remove shapes if its too big.
    elif x.geometry.geom_type == 'MultiPolygon':

        area1 = 0.01
        area2 = 50

        # dont remove shapes if total area is already very small
        if x.geometry.area < area1:
            return x.geometry
        # remove bigger shapes if country is really big

        if x['GID_0'] in ['CHL','IDN']:
            threshold = 0.01
        elif x['GID_0'] in ['RUS','GRL','CAN','USA']:
            threshold = 0.01

        elif x.geometry.area > area2:
            threshold = 0.1
        else:
            threshold = 0.001

        # save remaining polygons as new multipolygon for
        # the specific country
        new_geom = []
        for y in x.geometry:
            if y.area > threshold:
                new_geom.append(y)

        return MultiPolygon(new_geom)


def process_coverage_shapes(country):
    """
    Load in coverage maps, process and export for each country.

    Parameters
    ----------
    country : string
        Three digit ISO country code.

    """
    iso3 = country['iso3']
    iso2 = country['iso2']

    technologies = [
        'GSM',
        '3G',
        '4G'
    ]

    for tech in technologies:

        folder_coverage = os.path.join(DATA_INTERMEDIATE, iso3, 'coverage')
        filename = 'coverage_{}.shp'.format(tech)
        path_output = os.path.join(folder_coverage, filename)

        if os.path.exists(path_output):
            continue

        print('----')
        print('Working on {} in {}'.format(tech, iso3))

        filename = 'Inclusions_201812_{}.shp'.format(tech)
        folder = os.path.join(DATA_RAW, '..', 'mobile_coverage_explorer',
            'Data_MCE')
        inclusions = gpd.read_file(os.path.join(folder, filename))

        if iso2 in inclusions['CNTRY_ISO2']:

            filename = 'MCE_201812_{}.shp'.format(tech)
            folder = os.path.join(DATA_RAW, '..', 'mobile_coverage_explorer',
                'Data_MCE')
            coverage = gpd.read_file(os.path.join(folder, filename))

            coverage = coverage.loc[coverage['CNTRY_ISO3'] == iso3]

        else:

            filename = 'OCI_201812_{}.shp'.format(tech)
            folder = os.path.join(DATA_RAW, '..', 'mobile_coverage_explorer',
                'Data_OCI')
            coverage = gpd.read_file(os.path.join(folder, filename))

            coverage = coverage.loc[coverage['CNTRY_ISO3'] == iso3]

        if len(coverage) > 0:

            print('Dissolving polygons')
            coverage['dissolve'] = 1
            coverage = coverage.dissolve(by='dissolve', aggfunc='sum')

            coverage = coverage.to_crs({'init': 'epsg:3857'})

            print('Excluding small shapes')
            coverage['geometry'] = coverage.apply(clean_coverage,axis=1)

            print('Removing empty and null geometries')
            coverage = coverage[~(coverage['geometry'].is_empty)]
            coverage = coverage[coverage['geometry'].notnull()]

            print('Simplifying geometries')
            coverage['geometry'] = coverage.simplify(
                tolerance = 0.005,
                preserve_topology=True).buffer(0.0001).simplify(
                tolerance = 0.005,
                preserve_topology=True
            )

            coverage = coverage.to_crs({'init': 'epsg:4326'})

            if not os.path.exists(folder_coverage):
                os.makedirs(folder_coverage)

            coverage.to_file(path_output, driver='ESRI Shapefile')

    print('Processed coverage shapes')


def clean_coverage(x):
    """
    Cleans the coverage polygons by remove small multipolygon shapes.

    Parameters
    ---------
    x : polygon
        Feature to simplify.

    Returns
    -------
    MultiPolygon : MultiPolygon
        Shapely MultiPolygon geometry without tiny shapes.

    """
    # if its a single polygon, just return the polygon geometry
    if x.geometry.geom_type == 'Polygon':
        if x.geometry.area > 1e7:
            return x.geometry

    # if its a multipolygon, we start trying to simplify and
    # remove shapes if its too big.
    elif x.geometry.geom_type == 'MultiPolygon':

        threshold = 1e7

        # save remaining polygons as new multipolygon for
        # the specific country
        new_geom = []
        for y in x.geometry:

            if y.area > threshold:
                new_geom.append(y)

        return MultiPolygon(new_geom)


def load_regions(path):

    regions = gpd.read_file(path, crs='epsg:4326')

    return regions


def load_2G_kenya(path, regions, folder):

    print('Loading 2G')
    df_2G = pd.read_excel(path, '2G TRXs 2019_2020')
    df_2G = df_2G[['CELL ID', 'SITE ID', 'LAT', 'LON']]
    df_2G = gpd.GeoDataFrame(
        df_2G, geometry=gpd.points_from_xy(df_2G.LON, df_2G.LAT))
    df_2G = df_2G.dropna()

    print('Writing 2G shapes')
    df_2G.to_file(os.path.join(folder, '2G.shp'), crs='epsg:4326')

    f = lambda x:np.sum(df_2G.intersects(x))
    regions['sites'] = regions['geometry'].apply(f)

    sites_2G = regions[['GID_2', 'sites']]
    sites_2G['tech'] = '2G'

    return sites_2G


def load_3G_kenya(path, regions, folder):

    print('Loading 3G')
    df_3G = pd.read_excel(path, '3G TRX 2019_2020')
    df_3G = df_3G[['CELL ID', 'SITE ID', 'LAT', 'LON']]
    df_3G = gpd.GeoDataFrame(
        df_3G, geometry=gpd.points_from_xy(df_3G.LON, df_3G.LAT))
    df_3G = df_3G.dropna()

    print('Writing 3G shapes')
    df_3G.to_file(os.path.join(folder, '3G.shp'), crs='epsg:4326')

    f = lambda x:np.sum(df_3G.intersects(x))
    regions['sites'] = regions['geometry'].apply(f)

    sites_3G = regions[['GID_2', 'sites']]
    sites_3G['tech'] = '3G'

    return sites_3G


def load_4G_kenya(path, regions, folder):

    print('Loading 4G')
    df_4G = pd.read_excel(path, '4G TRX 2019_2020')
    df_4G = df_4G[['CELL ID', 'SITE ID', 'LAT', 'LON']]
    df_4G = df_4G.dropna()

    df_4G = gpd.GeoDataFrame(
        df_4G, geometry=gpd.points_from_xy(df_4G.LON, df_4G.LAT))

    print('Writing 4G shapes')
    df_4G.to_file(os.path.join(folder, '4G.shp'), crs='epsg:4326')

    f = lambda x:np.sum(df_4G.intersects(x))
    regions['sites'] = regions['geometry'].apply(f)

    sites_4G = regions[['GID_2', 'sites']]
    sites_4G['tech'] = '4G'

    return sites_4G


def process_kenya():

    print('Processing Kenya data')
    folder = os.path.join(DATA_INTERMEDIATE, 'KEN', 'sites')
    if not os.path.exists(folder):
        os.makedirs(folder)

    path = os.path.join(DATA_INTERMEDIATE, 'KEN', 'regions', 'regions_2_KEN.shp')
    regions = load_regions(path)

    path = os.path.join(DATA_RAW, 'KEN', 'Telkom Data.xlsx')
    sites_2G = load_2G_kenya(path, regions, folder)

    path = os.path.join(DATA_RAW, 'KEN', 'Telkom Data.xlsx')
    sites_3G = load_3G_kenya(path, regions, folder)

    path = os.path.join(DATA_RAW, 'KEN', 'Telkom Data.xlsx')
    sites_4G = load_4G_kenya(path, regions, folder)

    sites = [sites_2G, sites_3G, sites_4G]
    sites = pd.concat(sites)

    sites.rename(columns = {'GID_2':'GID_id'}, inplace = True)
    sites['GID_level'] = 2

    sites = sites[['GID_id', 'sites']]
    sites = sites.groupby(['GID_id'], as_index=False).sum()

    print('Writing Kenya csv data')
    sites.to_csv(os.path.join(folder, 'sites.csv'), index=False)


def load_senegal(path, regions, folder):

    print('Reading Senegal data')
    sites = pd.read_csv(path, encoding = "ISO-8859-1")
    sites = sites[['Cell_ID', 'Site_Name', 'LATITUDE', 'LONGITUDE']]
    sites = gpd.GeoDataFrame(
        sites, geometry=gpd.points_from_xy(sites.LONGITUDE, sites.LATITUDE))
    sites = sites.dropna()

    sites.crs = 'epsg:31028'
    sites = sites.to_crs('epsg:4326')

    sites.to_file(os.path.join(folder, 'sites.shp'), crs='epsg:4326')

    f = lambda x:np.sum(sites.intersects(x))
    regions['sites'] = regions['geometry'].apply(f)

    regions = regions[['GID_2', 'sites']]
    regions['tech'] = 'unknown'
    regions.rename(columns = {'GID_2':'GID_id'}, inplace = True)
    regions['GID_level'] = 2

    print('Writing Senegal csv data')
    folder = os.path.join(DATA_INTERMEDIATE, 'SEN', 'sites')
    regions.to_csv(os.path.join(folder, 'sites.csv'), index=False)

    return


def process_senegal():

    print('Processing Senegal data')
    folder = os.path.join(DATA_INTERMEDIATE, 'SEN', 'sites')
    if not os.path.exists(folder):
        os.makedirs(folder)

    path = os.path.join(DATA_INTERMEDIATE, 'SEN', 'regions', 'regions_2_SEN.shp')
    regions = load_regions(path)

    filename = 'Bilan_Couverture_Orange_Dec2017.csv'
    path = os.path.join(DATA_RAW, 'SEN', filename)

    load_senegal(path, regions, folder)


def load_albania(path, regions, folder):

    print('Reading Albania data')
    sites = pd.read_csv(path, encoding = "ISO-8859-1")
    sites = sites[['LATITUDE', 'LONGITUDE']]
    sites = sites.drop_duplicates()
    sites = gpd.GeoDataFrame(
        sites, geometry=gpd.points_from_xy(sites.LONGITUDE, sites.LATITUDE))
    sites = sites.dropna()

    print('Writing 2G')
    sites.to_file(os.path.join(folder, 'sites.shp'), crs='epsg:4326')

    f = lambda x:np.sum(sites.intersects(x))
    regions['sites'] = regions['geometry'].apply(f)

    sites = regions[['GID_2', 'sites']]
    sites['tech'] = '4G'
    sites.rename(columns = {'GID_2':'GID_id'}, inplace = True)
    sites['GID_level'] = 2

    return sites


def process_albania():

    print('Processing Albania data')
    folder = os.path.join(DATA_INTERMEDIATE, 'ALB', 'sites')
    if not os.path.exists(folder):
        os.makedirs(folder)

    path = os.path.join(DATA_INTERMEDIATE, 'ALB', 'regions', 'regions_2_ALB.shp')
    regions = load_regions(path)

    filename = 'all_data.csv'
    path = os.path.join(DATA_RAW, 'ALB', filename)

    sites = load_albania(path, regions, folder)
    sites.to_csv(os.path.join(folder, 'sites.csv'), index=False)


if __name__ == "__main__":

    countries = [
        # {'iso3': 'KEN', 'iso2': 'KE', 'regional_level': 2},
        # {'iso3': 'SEN', 'iso2': 'SN', 'regional_level': 2},
        {'iso3': 'ALB', 'iso2': 'AL', 'regional_level': 2},
    ]

    for country in countries:

        print('Processing country boundary')
        process_country_shape(country)

        print('Processing regions')
        process_regions(country)

        print('Processing coverage shapes')
        process_coverage_shapes(country)

        # if country['iso3'] == 'KEN':
        #     process_kenya()

        # if country['iso3'] == 'SEN':
        #     process_senegal()

        if country['iso3'] == 'ALB':
            process_albania()
