"""
Preprocessing scripts.

Written by Ed Oughton.

Winter 2020

"""
import os
import configparser
import json
import csv
import pandas as pd
import geopandas as gpd
import pyproj
from shapely.geometry import Polygon, MultiPolygon, mapping, shape, MultiLineString, LineString
from shapely.ops import transform, unary_union
from fiona.crs import from_epsg
import rasterio
from rasterio.mask import mask
from rasterstats import zonal_stats
import networkx as nx
from rtree import index
import numpy as np
from sklearn.linear_model import LinearRegression
import random
import math

CONFIG = configparser.ConfigParser()
CONFIG.read(os.path.join(os.path.dirname(__file__), 'script_config.ini'))
BASE_PATH = CONFIG['file_locations']['base_path']

DATA_RAW = os.path.join(BASE_PATH, 'raw')
DATA_INTERMEDIATE = os.path.join(BASE_PATH, 'intermediate')
DATA_PROCESSED = os.path.join(BASE_PATH, 'processed')


def find_country_list(continent_list):
    """
    This function produces country information by continent.

    Parameters
    ----------
    continent_list : list
        Contains the name of the desired continent, e.g. ['Africa']

    Returns
    -------
    countries : list of dicts
        Contains all desired country information for countries in
        the stated continent.

    """
    print('----')
    print('Loading all countries')
    path = os.path.join(DATA_RAW, 'gadm36_levels_shp', 'gadm36_0.shp')
    countries = gpd.read_file(path)

    print('Adding continent information to country shapes')
    glob_info_path = os.path.join(BASE_PATH, 'global_information.csv')
    load_glob_info = pd.read_csv(glob_info_path, encoding = "ISO-8859-1")
    countries = countries.merge(load_glob_info, left_on='GID_0',
        right_on='ISO_3digit')

    subset = countries.loc[countries['continent'].isin(continent_list)]

    countries = []

    for index, country in subset.iterrows():

        if country['GID_0'] in ['LBY', 'ESH']:
            continue

        if country['GID_0'] in ['LBY', 'ESH'] :
            regional_level =  1
        else:
            regional_level = 2

        countries.append({
            'country_name': country['country'],
            'iso3': country['GID_0'],
            'iso2': country['ISO_2digit'],
            'regional_level': regional_level,
        })

    return countries


def process_country_shapes(country):
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
    path = os.path.join(DATA_RAW, 'gadm36_levels_shp', 'gadm36_0.shp')
    countries = gpd.read_file(path)

    print('Getting specific country shape for {}'.format(iso3))
    single_country = countries[countries.GID_0 == iso3]

    print('Excluding small shapes')
    single_country['geometry'] = single_country.apply(
        exclude_small_shapes, axis=1)

    # print('Simplifying geometries')
    # single_country['geometry'] = single_country.simplify(
    #     tolerance = 0.0005,
    #     preserve_topology=True).buffer(0.0001).simplify(
    #     tolerance = 0.0005,
    #     preserve_topology=True
    # )

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
        path_regions = os.path.join(DATA_RAW, 'gadm36_levels_shp', filename)
        regions = gpd.read_file(path_regions)

        print('Subsetting {} level {}'.format(iso3, regional_level))
        regions = regions[regions.GID_0 == iso3]

        print('Excluding small shapes')
        regions['geometry'] = regions.apply(exclude_small_shapes, axis=1)

        # print('Simplifying geometries')
        # regions['geometry'] = regions.simplify(
        #     tolerance = 0.0005,
        #     preserve_topology=True).buffer(0.0001).simplify(
        #         tolerance = 0.0005,
        #         preserve_topology=True
        #     )
        try:
            print('Writing global_regions.shp to file')
            regions.to_file(path_processed, driver='ESRI Shapefile')
        except:
            print('Unable to write {}'.format(filename))
            pass

    print('Completed processing of regional shapes level {}'.format(level))

    return print('complete')


def process_settlement_layer(country):
    """
    Clip the settlement layer to the chosen country boundary and place in
    desired country folder.

    Parameters
    ----------
    country : string
        Three digit ISO country code.

    """
    iso3 = country['iso3']
    regional_level = country['regional_level']

    path_settlements = os.path.join(DATA_RAW,'settlement_layer',
        'ppp_2020_1km_Aggregated.tif')

    settlements = rasterio.open(path_settlements, 'r+')
    settlements.nodata = 255
    settlements.crs = {"init": "epsg:4326"}

    iso3 = country['iso3']
    path_country = os.path.join(DATA_INTERMEDIATE, iso3,
        'national_outline.shp')

    if os.path.exists(path_country):
        country = gpd.read_file(path_country)
    else:
        print('Must generate national_outline.shp first' )

    path_country = os.path.join(DATA_INTERMEDIATE, iso3)
    shape_path = os.path.join(path_country, 'settlements.tif')

    if os.path.exists(shape_path):
        return print('Completed settlement layer processing')

    print('----')
    print('Working on {} level {}'.format(iso3, regional_level))

    bbox = country.envelope
    geo = gpd.GeoDataFrame()

    geo = gpd.GeoDataFrame({'geometry': bbox})

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


def process_night_lights(country):
    """
    Clip the nightlights layer to the chosen country boundary and place in
    desired country folder.

    Parameters
    ----------
    country : string
        Three digit ISO country code.

    """
    iso3 = country['iso3']

    folder = os.path.join(DATA_INTERMEDIATE, iso3)
    path_output = os.path.join(folder,'night_lights.tif')

    if os.path.exists(path_output):
        return print('Completed processing of nightlight layer')

    path_country = os.path.join(folder, 'national_outline.shp')

    filename = 'F182013.v4c_web.stable_lights.avg_vis.tif'
    path_night_lights = os.path.join(DATA_RAW, 'nightlights', '2013',
        filename)

    country = gpd.read_file(path_country)

    print('----')
    print('working on {}'.format(iso3))

    bbox = country.envelope

    geo = gpd.GeoDataFrame()
    geo = gpd.GeoDataFrame({'geometry': bbox}, crs=from_epsg('4326'))

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

    with rasterio.open(path_output, "w", **out_meta) as dest:
            dest.write(out_img)

    return print('Completed processing of night lights layer')


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
        folder = os.path.join(DATA_RAW, 'mobile_coverage_explorer',
            'Data_MCE')
        inclusions = gpd.read_file(os.path.join(folder, filename))

        if iso2 in inclusions['CNTRY_ISO2']:

            filename = 'MCE_201812_{}.shp'.format(tech)
            folder = os.path.join(DATA_RAW, 'mobile_coverage_explorer',
                'Data_MCE')
            coverage = gpd.read_file(os.path.join(folder, filename))

            coverage = coverage.loc[coverage['CNTRY_ISO3'] == iso3]

        else:

            filename = 'OCI_201812_{}.shp'.format(tech)
            folder = os.path.join(DATA_RAW, 'mobile_coverage_explorer',
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


def process_regional_coverage(country):
    """
    This functions estimates the area covered by each cellular
    technology.

    Parameters
    ----------
    country : dict
        Contains specific country parameters.

    Returns
    -------
    output : dict
        Results for cellular coverage by each technology for
        each region.

    """
    level = country['regional_level']
    iso3 = country['iso3']
    gid_level = 'GID_{}'.format(level)

    filename = 'regions_{}_{}.shp'.format(level, iso3)
    folder = os.path.join(DATA_INTERMEDIATE, iso3, 'regions')
    path = os.path.join(folder, filename)
    regions = gpd.read_file(path)

    technologies = [
        'GSM',
        '3G',
        '4G'
    ]

    output = {}

    for tech in technologies:

        folder = os.path.join(DATA_INTERMEDIATE, iso3, 'coverage')
        path =  os.path.join(folder, 'coverage_{}.shp'.format(tech))

        if os.path.exists(path):

            coverage = gpd.read_file(path)

            segments = gpd.overlay(regions, coverage, how='intersection')

            tech_coverage = {}

            for idx, region in segments.iterrows():

                area_km2 = round(area_of_polygon(region['geometry']) / 1e6)

                tech_coverage[region[gid_level]] = area_km2

            output[tech] = tech_coverage

    return output


def get_regional_data(country):
    """
    Extract regional data including luminosity and population.

    Parameters
    ----------
    country : string
        Three digit ISO country code.

    """
    iso3 = country['iso3']
    level = country['regional_level']
    gid_level = 'GID_{}'.format(level)

    path_output = os.path.join(DATA_INTERMEDIATE, iso3, 'regional_data.csv')

    # if os.path.exists(path_output):
    #     return print('Regional data already exists')

    path_country = os.path.join(DATA_INTERMEDIATE, iso3,
        'national_outline.shp')

    coverage = process_regional_coverage(country)

    single_country = gpd.read_file(path_country)

    print('----')
    print('working on {}'.format(iso3))

    path_night_lights = os.path.join(DATA_INTERMEDIATE, iso3,
        'night_lights.tif')
    path_settlements = os.path.join(DATA_INTERMEDIATE, iso3,
        'settlements.tif')

    filename = 'regions_{}_{}.shp'.format(level, iso3)
    folder = os.path.join(DATA_INTERMEDIATE, iso3, 'regions')
    path = os.path.join(folder, filename)

    regions = gpd.read_file(path)

    results = []

    for index, region in regions.iterrows():

        with rasterio.open(path_night_lights) as src:

            affine = src.transform
            array = src.read(1)
            array[array <= 0] = 0

            luminosity_summation = [d['sum'] for d in zonal_stats(
                region['geometry'],
                array,
                stats=['sum'],
                affine=affine)][0]

        with rasterio.open(path_settlements) as src:

            affine = src.transform
            array = src.read(1)
            array[array <= 0] = 0

            population_summation = [d['sum'] for d in zonal_stats(
                region['geometry'], array, stats=['sum'], affine=affine)][0]

        area_km2 = round(area_of_polygon(region['geometry']) / 1e6)

        if luminosity_summation == None:
            luminosity_summation = 0

        if 'GSM' in [c for c in coverage.keys()]:
            if region[gid_level] in coverage['GSM']:
                coverage_GSM_km2 = coverage['GSM'][region[gid_level]]
            else:
                coverage_GSM_km2 = 0
        else:
            coverage_GSM_km2 = 0

        if '3G' in [c for c in coverage.keys()]:
            if region[gid_level] in coverage['3G']:
                coverage_3G_km2 = coverage['3G'][region[gid_level]]
            else:
                coverage_3G_km2 = 0
        else:
            coverage_3G_km2 = 0

        if '4G' in [c for c in coverage.keys()]:
            if region[gid_level] in coverage['4G']:
                coverage_4G_km2 = coverage['4G'][region[gid_level]]
            else:
                coverage_4G_km2 = 0
        else:
            coverage_4G_km2 = 0

        results.append({
            'GID_0': region['GID_0'],
            'GID_id': region[gid_level],
            'GID_level': gid_level,
            'mean_luminosity_km2': luminosity_summation / area_km2 if luminosity_summation else 0,
            'population': population_summation,
            'area_km2': area_km2,
            'population_km2': population_summation / area_km2 if population_summation else 0,
            'coverage_GSM_percent': round(coverage_GSM_km2 / area_km2 * 100 if coverage_GSM_km2 else 0, 1),
            'coverage_3G_percent': round(coverage_3G_km2 / area_km2 * 100 if coverage_3G_km2 else 0, 1),
            'coverage_4G_percent': round(coverage_4G_km2 / area_km2 * 100 if coverage_4G_km2 else 0, 1),
        })

    print('Working on backhaul')
    backhaul_lut = estimate_backhaul(iso3, country['region'], '2025')

    print('Working on estimating sites')
    results = estimate_sites(results, iso3, backhaul_lut)

    results_df = pd.DataFrame(results)

    results_df.to_csv(path_output, index=False)

    print('Completed {}'.format(single_country.NAME_0.values[0]))

    return print('Completed night lights data querying')


def estimate_sites(data, iso3, backhaul_lut):
    """

    """
    output = []

    existing_site_data_path = os.path.join(DATA_INTERMEDIATE, iso3, 'sites', 'sites.csv')

    existing_site_data = {}
    if os.path.exists(existing_site_data_path):
        site_data = pd.read_csv(existing_site_data_path)
        site_data = site_data.to_dict('records')
        for item in site_data:
            existing_site_data[item['GID_id']] = item['sites']

    population = 0

    for region in data:

        if region['population'] == None:
            continue

        population += int(region['population'])

    path = os.path.join(DATA_RAW, 'wb_mobile_coverage', 'wb_population_coverage.csv')
    coverage = pd.read_csv(path)
    coverage = coverage.loc[coverage['Country ISO3'] == iso3]
    coverage = coverage['2016'].values[0]

    population_covered = population * (coverage / 100)

    path = os.path.join(DATA_RAW, 'real_site_data', 'tower_counts', 'tower_counts.csv')
    towers = pd.read_csv(path, encoding = "ISO-8859-1")
    towers = towers.loc[towers['ISO_3digit'] == iso3]
    towers = towers['count'].values[0]

    towers_per_pop = towers / population_covered

    tower_backhaul_lut = estimate_backhaul_type(backhaul_lut)

    data = sorted(data, key=lambda k: k['population_km2'], reverse=True)

    covered_pop_so_far = 0

    for region in data:

        #first try to use actual data
        if len(existing_site_data) > 0:
            sites_estimated_total = existing_site_data[region['GID_id']]
            sites_estimated_km2 = sites_estimated_total / region['area_km2']

        #or if we don't have data estimate sites per area
        else:
            if covered_pop_so_far < population_covered:
                sites_estimated_total = region['population'] * towers_per_pop
                sites_estimated_km2 = region['population_km2'] * towers_per_pop

            else:
                sites_estimated_total = 0
                sites_estimated_km2 = 0

        backhaul_fiber = 0
        backhaul_copper = 0
        backhaul_microwave = 0
        backhaul_satellite = 0

        for i in range(1, int(round(sites_estimated_total)) + 1):

            num = random.uniform(0, 1)

            if num <= tower_backhaul_lut['fiber']:
                backhaul_fiber += 1
            elif tower_backhaul_lut['fiber'] < num <= tower_backhaul_lut['copper']:
                backhaul_copper += 1
            elif tower_backhaul_lut['copper'] < num <= tower_backhaul_lut['microwave']:
                backhaul_microwave += 1
            elif tower_backhaul_lut['microwave'] < num:
                backhaul_satellite += 1

        output.append({
                'GID_0': region['GID_0'],
                'GID_id': region['GID_id'],
                'GID_level': region['GID_level'],
                'mean_luminosity_km2': region['mean_luminosity_km2'],
                'population': region['population'],
                'area_km2': region['area_km2'],
                'population_km2': region['population_km2'],
                'coverage_GSM_percent': region['coverage_GSM_percent'],
                'coverage_3G_percent': region['coverage_3G_percent'],
                'coverage_4G_percent': region['coverage_4G_percent'],
                'sites_estimated_total': sites_estimated_total,
                'sites_estimated_km2': sites_estimated_km2,
                'sites_3G': sites_estimated_total * (region['coverage_3G_percent'] /100),
                'sites_4G': sites_estimated_total * (region['coverage_4G_percent'] /100),
                'backhaul_fiber': backhaul_fiber,
                'backhaul_copper': backhaul_copper,
                'backhaul_microwave': backhaul_microwave,
                'backhaul_satellite': backhaul_satellite,
            })

        if region['population'] == None:
            continue

        covered_pop_so_far += region['population']

    return output


def estimate_backhaul(iso3, region, year):
    """

    """
    output = []

    path = os.path.join(BASE_PATH, 'raw', 'gsma', 'backhaul.csv')
    backhaul_lut = pd.read_csv(path)
    backhaul_lut = backhaul_lut.to_dict('records')

    for item in backhaul_lut:
        if region == item['Region'] and int(item['Year']) == int(year):
            output.append({
                'tech': item['Technology'],
                'percentage': int(item['Value']),
            })

    return output


def estimate_backhaul_type(backhaul_lut):
    """
    Estimate backhaul type.

    """
    output = {}

    preference = [
        'fiber',
        'copper',
        'microwave',
        'satellite'
    ]

    perc_so_far = 0

    for tech in preference:
        for item in backhaul_lut:
            if tech == item['tech'].lower():
                perc = item['percentage']
                output[tech] = (perc + perc_so_far) / 100
                perc_so_far += perc

    return output


def area_of_polygon(geom):
    """
    Returns the area of a polygon. Assume WGS84 as crs.

    """
    geod = pyproj.Geod(ellps="WGS84")

    poly_area, poly_perimeter = geod.geometry_area_perimeter(
        geom
    )

    return abs(poly_area)


def length_of_line(geom):
    """
    Returns the length of a linestring. Assume WGS84 as crs.

    """
    geod = pyproj.Geod(ellps="WGS84")

    total_length = geod.line_length(*geom.xy)

    return abs(total_length)


def estimate_numers_of_sites(linear_regressor, x_value):
    """
    Function to predict the y value from the stated x value.

    Parameters
    ----------
    linear_regressor : object
        Linear regression object.
    x_value : float
        The stated x value we want to use to predict y.

    Returns
    -------
    result : float
        The predicted y value.

    """
    if not x_value == 0:
        result = linear_regressor.predict(x_value)
        result = result[0,0]
    else:
        result = 0

    return result


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


def estimate_core_nodes(iso3, pop_density_km2, settlement_size):
    """
    This function identifies settlements which exceed a desired settlement
    size. It is assumed fiber exists at settlements over, for example,
    20,000 inhabitants.

    Parameters
    ----------
    iso3 : string
        ISO 3 digit country code.
    pop_density_km2 : int
        Population density threshold for identifying built up areas.
    settlement_size : int
        Overall sittelement size assumption, e.g. 20,000 inhabitants.

    Returns
    -------
    output : list of dicts
        Identified major settlements as Geojson objects.

    """
    path = os.path.join(DATA_INTERMEDIATE, iso3, 'settlements.tif')

    with rasterio.open(path) as src:
        data = src.read()
        threshold = pop_density_km2
        data[data < threshold] = 0
        data[data >= threshold] = 1
        polygons = rasterio.features.shapes(data, transform=src.transform)
        shapes_df = gpd.GeoDataFrame.from_features(
            [
                {'geometry': poly, 'properties':{'value':value}}
                for poly, value in polygons
                if value > 0
            ],
            crs='epsg:4326'
        )

    stats = zonal_stats(shapes_df['geometry'], path, stats=['count', 'sum'])

    stats_df = pd.DataFrame(stats)

    nodes = pd.concat([shapes_df, stats_df], axis=1).drop(columns='value')

    nodes = nodes[nodes['sum'] >= settlement_size]

    nodes['geometry'] = nodes['geometry'].centroid

    nodes = get_points_inside_country(nodes, iso3)

    output = []

    for index, item in enumerate(nodes.to_dict('records')):
        output.append({

            'type': 'Feature',
            'geometry': mapping(item['geometry']),
            'properties': {
                'network_layer': 'core',
                'id': 'core_{}'.format(index),
                'node_number': index,
            }
        })

    return output


def get_points_inside_country(nodes, iso3):
    """
    Check settlement locations lie inside target country.

    Parameters
    ----------
    nodes : dataframe
        A geopandas dataframe containing settlement nodes.
    iso3 : string
        ISO 3 digit country code.

    Returns
    -------
    nodes : dataframe
        A geopandas dataframe containing settlement nodes.

    """
    filename = 'national_outline.shp'
    path = os.path.join(DATA_INTERMEDIATE, iso3, filename)

    national_outline = gpd.read_file(path)

    bool_list = nodes.intersects(national_outline.unary_union)

    nodes = pd.concat([nodes, bool_list], axis=1)

    nodes = nodes[nodes[0] == True].drop(columns=0)

    return nodes


def generate_agglomeration_lut(country):
    """
    Generate a lookup table of agglomerations.

    """
    iso3 = country['iso3']
    regional_level = country['regional_level']
    GID_level = 'GID_{}'.format(regional_level)

    folder = os.path.join(DATA_INTERMEDIATE, iso3, 'agglomerations')
    if not os.path.exists(folder):
        os.makedirs(folder)
    path_output = os.path.join(folder, 'agglomerations.shp')

    if os.path.exists(path_output):
        return print('Agglomeration processing has already completed')

    print('Working on {} agglomeration lookup table'.format(iso3))

    filename = 'regions_{}_{}.shp'.format(regional_level, iso3)
    folder = os.path.join(DATA_INTERMEDIATE, iso3, 'regions')
    path = os.path.join(folder, filename)
    regions = gpd.read_file(path, crs="epsg:4326")

    path_settlements = os.path.join(DATA_INTERMEDIATE, iso3, 'settlements.tif')
    settlements = rasterio.open(path_settlements, 'r+')
    settlements.nodata = 255
    settlements.crs = {"init": "epsg:4326"}

    folder_tifs = os.path.join(DATA_INTERMEDIATE, iso3, 'agglomerations', 'tifs')
    if not os.path.exists(folder_tifs):
        os.makedirs(folder_tifs)

    for idx, region in regions.iterrows():

        bbox = region['geometry'].envelope
        geo = gpd.GeoDataFrame()
        geo = gpd.GeoDataFrame({'geometry': bbox}, index=[idx])
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

        path_output = os.path.join(folder_tifs, region[GID_level] + '.tif')

        with rasterio.open(path_output, "w", **out_meta) as dest:
                dest.write(out_img)

    print('Completed settlement.tif regional segmentation')

    nodes, missing_nodes = find_nodes(country, regions)

    missing_nodes = get_missing_nodes(country, regions, missing_nodes, 10, 10)

    nodes = nodes + missing_nodes

    nodes = gpd.GeoDataFrame.from_features(nodes, crs='epsg:4326')

    bool_list = nodes.intersects(regions['geometry'].unary_union)
    nodes = pd.concat([nodes, bool_list], axis=1)
    nodes = nodes[nodes[0] == True].drop(columns=0)

    agglomerations = []

    print('Identifying agglomerations')
    for idx1, region in regions.iterrows():
        seen = set()
        for idx2, node in nodes.iterrows():
            if node['geometry'].intersects(region['geometry']):
                agglomerations.append({
                    'type': 'Feature',
                    'geometry': mapping(node['geometry']),
                    'properties': {
                        'id': idx1,
                        'GID_0': region['GID_0'],
                        GID_level: region[GID_level],
                        'population': node['sum'],
                    }
                })
                seen.add(region[GID_level])
        if len(seen) == 0:
            agglomerations.append({
                    'type': 'Feature',
                    'geometry': mapping(region['geometry'].centroid),
                    'properties': {
                        'id': 'regional_node',
                        'GID_0': region['GID_0'],
                        GID_level: region[GID_level],
                        'population': 1,
                    }
                })

    agglomerations = gpd.GeoDataFrame.from_features(
            [
                {
                    'geometry': item['geometry'],
                    'properties': {
                        'id': item['properties']['id'],
                        'GID_0':item['properties']['GID_0'],
                        GID_level: item['properties'][GID_level],
                        'population': item['properties']['population'],
                    }
                }
                for item in agglomerations
            ],
            crs='epsg:4326'
        )

    folder = os.path.join(DATA_INTERMEDIATE, iso3, 'agglomerations')
    path_output = os.path.join(folder, 'agglomerations' + '.shp')

    agglomerations.to_file(path_output)

    agglomerations['lon'] = agglomerations['geometry'].x
    agglomerations['lat'] = agglomerations['geometry'].y
    agglomerations = agglomerations[['lon', 'lat', GID_level, 'population']]
    agglomerations.to_csv(os.path.join(folder, 'agglomerations.csv'), index=False)

    return print('Agglomerations layer complete')


def find_nodes(country, regions):
    """
    Find key nodes.

    """
    iso3 = country['iso3']
    regional_level = country['regional_level']
    GID_level = 'GID_{}'.format(regional_level)

    threshold = country['pop_density_km2']
    settlement_size = country['settlement_size']

    folder_tifs = os.path.join(DATA_INTERMEDIATE, iso3, 'agglomerations', 'tifs')

    interim = []
    missing_nodes = set()

    print('Working on gathering data from regional rasters')
    for idx, region in regions.iterrows():

        path = os.path.join(folder_tifs, region[GID_level] + '.tif')

        with rasterio.open(path) as src:
            data = src.read()
            data[data < threshold] = 0
            data[data >= threshold] = 1
            polygons = rasterio.features.shapes(data, transform=src.transform)
            shapes_df = gpd.GeoDataFrame.from_features(
                [
                    {'geometry': poly, 'properties':{'value':value}}
                    for poly, value in polygons
                    if value > 0
                ],
                crs='epsg:4326'
            )

        geojson_region = [
            {
                'geometry': region['geometry'],
                'properties': {
                    GID_level: region[GID_level]
                }
            }
        ]

        gpd_region = gpd.GeoDataFrame.from_features(
                [
                    {'geometry': poly['geometry'],
                    'properties':{
                        GID_level: poly['properties'][GID_level]
                        }}
                    for poly in geojson_region
                ], crs='epsg:4326'
            )

        if len(shapes_df) == 0:
            continue

        nodes = gpd.overlay(shapes_df, gpd_region, how='intersection')

        stats = zonal_stats(shapes_df['geometry'], path, stats=['count', 'sum'])

        stats_df = pd.DataFrame(stats)

        nodes = pd.concat([shapes_df, stats_df], axis=1).drop(columns='value')

        nodes_subset = nodes[nodes['sum'] >= settlement_size]

        if len(nodes_subset) == 0:
            missing_nodes.add(region[GID_level])

        for idx, item in nodes_subset.iterrows():
            interim.append({
                    'geometry': item['geometry'].centroid,
                    'properties': {
                        GID_level: region[GID_level],
                        'count': item['count'],
                        'sum': item['sum']
                    }
            })

    return interim, missing_nodes


def get_missing_nodes(country, regions, missing_nodes, threshold, settlement_size):
    """
    Find any missing nodes

    """
    iso3 = country['iso3']
    regional_level = country['regional_level']
    GID_level = 'GID_{}'.format(regional_level)

    folder_tifs = os.path.join(DATA_INTERMEDIATE, iso3, 'agglomerations', 'tifs')

    interim = []

    for idx, region in regions.iterrows():

        if not region[GID_level] in list(missing_nodes):
            continue

        path = os.path.join(folder_tifs, region[GID_level] + '.tif')

        with rasterio.open(path) as src:
            data = src.read()
            data[data < threshold] = 0
            data[data >= threshold] = 1
            polygons = rasterio.features.shapes(data, transform=src.transform)
            shapes_df = gpd.GeoDataFrame.from_features(
                [
                    {'geometry': poly, 'properties':{'value':value}}
                    for poly, value in polygons
                    if value > 0
                ],
                crs='epsg:4326'
            )

        geojson_region = [
            {
                'geometry': region['geometry'],
                'properties': {
                    GID_level: region[GID_level]
                }
            }
        ]

        gpd_region = gpd.GeoDataFrame.from_features(
                [
                    {'geometry': poly['geometry'],
                    'properties':{
                        GID_level: poly['properties'][GID_level]
                        }}
                    for poly in geojson_region
                ], crs='epsg:4326'
            )

        nodes = gpd.overlay(shapes_df, gpd_region, how='intersection')

        stats = zonal_stats(shapes_df['geometry'], path, stats=['count', 'sum'])

        stats_df = pd.DataFrame(stats)

        nodes = pd.concat([shapes_df, stats_df], axis=1).drop(columns='value')

        max_sum = nodes['sum'].max()

        nodes = nodes[nodes['sum'] > max_sum - 1]

        for idx, item in nodes.iterrows():
            interim.append({
                    'geometry': item['geometry'].centroid,
                    'properties': {
                        GID_level: region[GID_level],
                        'count': item['count'],
                        'sum': item['sum']
                    }
            })

    return interim


def find_regional_nodes(country):
    """

    """
    iso3 = country['iso3']
    regional_level = country['regional_level']
    GID_level = 'GID_{}'.format(regional_level)

    folder = os.path.join(DATA_INTERMEDIATE, iso3)
    input_path = os.path.join(folder, 'agglomerations', 'agglomerations.shp')
    output_path = os.path.join(folder, 'network', 'core_nodes.shp')
    regional_output_path = os.path.join(folder, 'network', 'regional_nodes')

    if os.path.exists(output_path):
        return print('Regional nodes layer already generated')

    folder = os.path.dirname(output_path)
    if not os.path.exists(folder):
        os.makedirs(folder)

    if not os.path.exists(regional_output_path):
        os.makedirs(regional_output_path)

    regions = gpd.read_file(input_path, crs="epsg:4326")

    unique_regions = regions[GID_level].unique()

    output = []

    for unique_region in unique_regions:
        agglomerations = []
        for idx, region in regions.iterrows():
            if unique_region == region[GID_level]:
                agglomerations.append({
                    'type': 'Feature',
                    'geometry': region['geometry'],
                    'properties': {
                        GID_level: region[GID_level],
                        'population': region['population']
                    }
                })

        regional_nodes = gpd.GeoDataFrame.from_features(agglomerations, crs='epsg:4326')
        path = os.path.join(regional_output_path, unique_region + '.shp')
        regional_nodes.to_file(path)

        agglomerations = sorted(agglomerations, key=lambda k: k['properties']['population'], reverse=True)

        output.append(agglomerations[0])

    output = gpd.GeoDataFrame.from_features(
        [
            {'geometry': item['geometry'], 'properties': item['properties']}
            for item in output
        ],
        crs='epsg:4326'
    )
    output.to_file(output_path)

    output = []

    for unique_region in unique_regions:

        path = os.path.join(regional_output_path, unique_region + '.shp')
        if os.path.exists(path):
            regional_nodes = gpd.read_file(path, crs='epsg:4326')

            for idx, regional_node in regional_nodes.iterrows():
                output.append({
                    'geometry': regional_node['geometry'],
                    'properties': {
                        'value': regional_node['population'],
                    }
                })

    output = gpd.GeoDataFrame.from_features(output, crs='epsg:4326')
    path = os.path.join(folder, 'regional_nodes.shp')
    output.to_file(path)

    return print('Completed regional node estimation')


def fit_edges(input_path, output_path):
    """
    Fit edges to nodes using a minimum spanning tree.

    Parameters
    ----------
    path : string
        Path to nodes shapefile.

    """
    folder = os.path.dirname(output_path)
    if not os.path.exists(folder):
        os.makedirs(folder)

    nodes = gpd.read_file(input_path, crs='epsg:4326')
    nodes = nodes.to_crs('epsg:3857')

    all_possible_edges = []

    for node1_id, node1 in nodes.iterrows():
        for node2_id, node2 in nodes.iterrows():
            if node1_id != node2_id:
                geom1 = shape(node1['geometry'])
                geom2 = shape(node2['geometry'])
                line = LineString([geom1, geom2])
                all_possible_edges.append({
                    'type': 'Feature',
                    'geometry': mapping(line),
                    'properties':{
                        # 'network_layer': 'core',
                        'from': node1_id,
                        'to':  node2_id,
                        'length': line.length,
                    }
                })
    if len(all_possible_edges) == 0:
        return

    G = nx.Graph()

    for node_id, node in enumerate(nodes):
        G.add_node(node_id, object=node)

    for edge in all_possible_edges:
        G.add_edge(edge['properties']['from'], edge['properties']['to'],
            object=edge, weight=edge['properties']['length'])

    tree = nx.minimum_spanning_edges(G)

    edges = []

    for branch in tree:
        link = branch[2]['object']
        if link['properties']['length'] > 0:
            edges.append(link)

    edges = gpd.GeoDataFrame.from_features(edges, crs='epsg:3857')

    if len(edges) > 0:
        edges = edges.to_crs('epsg:4326')
        edges.to_file(output_path)

    return

def fit_regional_edges(country):
    """

    """
    iso3 = country['iso3']
    regional_level = country['regional_level']
    GID_level = 'GID_{}'.format(regional_level)

    folder = os.path.join(DATA_INTERMEDIATE, iso3, 'network')
    nodes = gpd.read_file(os.path.join(folder, 'core_nodes.shp'), crs="epsg:4326")
    unique_regions = nodes[GID_level].unique()

    for unique_region in unique_regions:

        input_path = os.path.join(folder, 'regional_nodes', unique_region + '.shp')
        output_path = os.path.join(DATA_INTERMEDIATE, country['iso3'], 'network', 'regional_edges', unique_region + '.shp')
        fit_edges(input_path, output_path)

    output = []

    for unique_region in unique_regions:

        path = os.path.join(DATA_INTERMEDIATE, country['iso3'], 'network', 'regional_edges', unique_region + '.shp')
        if os.path.exists(path):
            regional_edges = gpd.read_file(path, crs='epsg:4326')

            for idx, regional_edge in regional_edges.iterrows():
                output.append({
                    'geometry': regional_edge['geometry'],
                    'properties': {
                        'value': regional_edge['length'],
                    }
                })

    output = gpd.GeoDataFrame.from_features(output, crs='epsg:4326')
    path = os.path.join(folder, 'regional_edges.shp')
    output.to_file(path)

    return print('Regional edge fitting complete')


def generate_core_lut(country):
    """
    Generate core lut.

    """
    iso3 = country['iso3']
    level = country['regional_level']
    regional_level = 'GID_{}'.format(level)

    filename = 'core_lut.csv'
    folder = os.path.join(DATA_INTERMEDIATE, iso3)
    output_path = os.path.join(folder, filename)

    if os.path.exists(output_path):
        return print('Core LUT already generated')

    filename = 'regions_{}_{}.shp'.format(level, iso3)
    folder = os.path.join(DATA_INTERMEDIATE, iso3, 'regions')
    path = os.path.join(folder, filename)
    regions = gpd.read_file(path)
    regions.crs = 'epsg:4326'

    output = []

    path = os.path.join(DATA_INTERMEDIATE, iso3, 'network', 'core_edges.shp')
    core_edges = gpd.read_file(path)
    core_edges.crs = 'epsg:4326'
    core_edges = core_edges['geometry'].unary_union
    core_edges = gpd.GeoDataFrame({'geometry': core_edges})

    core_edges = gpd.clip(regions, core_edges)
    core_edges = core_edges.to_crs('epsg:3857')
    core_edges['length'] = core_edges['geometry'].length

    for idx, edge in core_edges.iterrows():
        output.append({
            'GID_id': edge[regional_level],
            'asset': 'core_edge',
            'value': edge['length']
        })

    path = os.path.join(DATA_INTERMEDIATE, iso3, 'network', 'regional_edges.shp')
    if os.path.exists(path):
        regional_edges = gpd.read_file(path, crs='epsg:4326')

        regional_edges = gpd.clip(regions, regional_edges)
        regional_edges = regional_edges.to_crs('epsg:3857')
        regional_edges['length'] = regional_edges['geometry'].length

        for idx, edge in regional_edges.iterrows():
            output.append({
                'GID_id': edge[regional_level],
                'asset': 'regional_edge',
                'value': edge['length']
            })

    path = os.path.join(DATA_INTERMEDIATE, iso3, 'network', 'core_nodes.shp')
    nodes = gpd.read_file(path, crs='epsg:4326')

    f = lambda x:np.sum(nodes.intersects(x))
    regions['nodes'] = regions['geometry'].apply(f)

    for idx, region in regions.iterrows():
        output.append({
            'GID_id': region[regional_level],
            'asset': 'core_node',
            'value': region['nodes']
        })

    path = os.path.join(DATA_INTERMEDIATE, iso3, 'network', 'regional_nodes.shp')
    regional_nodes = gpd.read_file(path, crs='epsg:4326')

    f = lambda x:np.sum(regional_nodes.intersects(x))
    regions['regional_nodes'] = regions['geometry'].apply(f)

    for idx, region in regions.iterrows():
        output.append({
            'GID_id': region[regional_level],
            'asset': 'regional_node',
            'value': region['regional_nodes']
        })

    output = pd.DataFrame(output)

    output.to_csv(output_path, index=False)

    return print('Completed core lut')


def generate_backhaul_lut(country):
    """
    Simulate backhaul distance given a 100km^2 area.
      Simulations show that for every 10x increase in node density,
      there is a 3.2x decrease in backhaul length.

    node_density_km2	average_distance_km
    0.000001	606.0	10	 3.2
    0.00001	189.0	10	 3.8
    0.0001	50.0	10	 3.1
    0.001	16.0	10	 3.2
    0.01	5.0	10	 3.2
    0.1	1.6	10	 3.2
    1	0.5

    """
    filename = 'backhaul_lut.csv'
    folder = os.path.join(DATA_INTERMEDIATE)
    path = os.path.join(folder, filename)

    if os.path.exists(path):
        return print('Backhaul LUT already generated')

    output = []

    number_of_regional_nodes_range = [1, 10, 100, 1000, 10000]

    area_km2 = 1e6

    for number_of_regional_nodes in number_of_regional_nodes_range:

        sites = []

        for i in range(1, int(round(max(number_of_regional_nodes_range) + 1))):
            x = random.uniform(0, round(math.sqrt(area_km2)))
            y = random.uniform(0, round(math.sqrt(area_km2)))
            sites.append({
                'geometry': {
                    'type': 'Point',
                    'coordinates': (x, y)
                },
                'properties': {
                    'id': i
                }
            })

        regional_nodes = []

        for i in range(1, number_of_regional_nodes + 1):
            x = random.uniform(0, round(math.sqrt(area_km2)))
            y = random.uniform(0, round(math.sqrt(area_km2)))
            regional_nodes.append({
                'geometry': {
                    'type': 'Point',
                    'coordinates': (x, y)
                },
                'properties': {
                    'id': i
                }
            })

        distances = []

        idx = index.Index()

        for regional_node in regional_nodes:
            idx.insert(
                regional_node['properties']['id'],
                shape(regional_node['geometry']).bounds,
                regional_node)

        for site in sites:

            geom1 = shape(site['geometry'])

            nearest_regional_node = [i for i in idx.nearest((geom1.bounds))][0]

            for regional_node in regional_nodes:
                if regional_node['properties']['id'] == nearest_regional_node:

                    x1 = site['geometry']['coordinates'][0]
                    x2 = regional_node['geometry']['coordinates'][0]
                    y1 = site['geometry']['coordinates'][1]
                    y2 = regional_node['geometry']['coordinates'][1]

                    distance = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)

                    distances.append(distance)

        output.append({
            'node_density_km2': round(number_of_regional_nodes / area_km2, 8),
            'average_distance_km': int(round(sum(distances) / len(distances))),
        })

    output = pd.DataFrame(output)
    output.to_csv(path, index=False)

    return print('Completed backhaul LUT processing')


def load_subscription_data(path, iso3):
    """
    Load in itu cell phone subscription data.

    Parameters
    ----------
    path : string
        Location of itu data as .csv.
    country : string
        ISO3 digital country code.
    country_lut : list of dicts
        Lookup table containing country name to ISO3 digit code.

    Returns
    -------
    output :
        Time series data of cell phone subscriptions.

    """
    output = []

    historical_data = pd.read_csv(path, encoding = "ISO-8859-1")
    historical_data = historical_data.to_dict('records')

    for year in range(2010, 2021):
        year = str(year)
        for item in historical_data:
            if item['iso3'] == iso3:
                output.append({
                    'country': iso3,
                    'penetration': float(item[year]) * 100,
                    'year':  year,
                })

    return output


def forecast_subscriptions(country):
    """

    """
    iso3 = country['iso3']

    path = os.path.join(DATA_RAW, 'gsma', 'gsma_unique_subscribers.csv')
    historical_data = load_subscription_data(path, country['iso3'])

    start_point = 2021
    end_point = 2030
    horizon = 4

    forecast = forecast_linear(
        country,
        historical_data,
        start_point,
        end_point,
        horizon
    )

    forecast_df = pd.DataFrame(historical_data + forecast)

    path = os.path.join(DATA_INTERMEDIATE, iso3, 'subscriptions')

    if not os.path.exists(path):
        os.mkdir(path)

    forecast_df.to_csv(os.path.join(path, 'subs_forecast.csv'), index=False)

    path = os.path.join(BASE_PATH, '..', 'vis', 'subscriptions')
    forecast_df.to_csv(os.path.join(path, '{}.csv'.format(iso3)), index=False)

    return print('Completed subscription forecast')


def forecast_linear(country, historical_data, start_point, end_point, horizon):
    """
    Forcasts subscription adoption rate.

    Parameters
    ----------
    historical_data : list of dicts
        Past penetration data.
    start_point : int
        Starting year of forecast period.
    end_point : int
        Final year of forecast period.
    horizon : int
        Number of years to use to estimate mean growth rate.

    """
    output = []

    subs_growth = country['subs_growth']

    year_0 = sorted(historical_data, key = lambda i: i['year'], reverse=True)[0]

    for year in range(start_point, end_point + 1):
        if year == start_point:

            penetration = year_0['penetration'] * (1 + (subs_growth/100))
        else:
            penetration = penetration * (1 + (subs_growth/100))

        if year not in [item['year'] for item in output]:

            output.append({
                'country': country['iso3'],
                'year': year,
                'penetration': round(penetration, 2),
            })

    return output


if __name__ == '__main__':

    # countries = find_country_list(['Africa'])

    countries = [
        # {'iso3': 'UGA', 'iso2': 'UG', 'regional_level': 2, 'regional_nodes_level': 2,
        #     'region': 'SSA', 'pop_density_km2': 500, 'settlement_size': 1000, 'subs_growth': 1.5,
        # },
        # {'iso3': 'MWI', 'iso2': 'MW', 'regional_level': 2, 'regional_nodes_level': 2,
        #     'region': 'SSA', 'pop_density_km2': 500, 'settlement_size': 1000, 'subs_growth': 1.5,
        # },
        # {'iso3': 'KEN', 'iso2': 'KE', 'regional_level': 2, 'regional_nodes_level': 1,
        #     'region': 'SSA', 'pop_density_km2': 500, 'settlement_size': 1000, 'subs_growth': 1.5,
        # },
        # {'iso3': 'SEN', 'iso2': 'SN', 'regional_level': 2, 'regional_nodes_level': 2,
        #     'region': 'SSA', 'pop_density_km2': 100, 'settlement_size': 1000, 'subs_growth': 1.5,
        # },
        # {'iso3': 'PAK', 'iso2': 'PK', 'regional_level': 3, 'regional_nodes_level': 2,
        #     'region': 'S&SE Asia', 'pop_density_km2': 500, 'settlement_size': 1000, 'subs_growth': 1.5,
        # },
        {'iso3': 'ALB', 'iso2': 'AL', 'regional_level': 2, 'regional_nodes_level': 2,
            'region': 'Europe', 'pop_density_km2': 500, 'settlement_size': 1000, 'subs_growth': 1.5,
        },
        # {'iso3': 'PER', 'iso2': 'PE', 'regional_level': 2, 'regional_nodes_level': 1,
        #     'region': 'LAC', 'pop_density_km2': 500, 'settlement_size': 1000, 'subs_growth': 1.5,
        # },
        # {'iso3': 'MEX', 'iso2': 'MX', 'regional_level': 1, 'regional_nodes_level': 1,
        #     'region': 'LAC', 'pop_density_km2': 500, 'settlement_size': 1000, 'subs_growth': 1.5,
        # },
    ]

    for country in countries:

        # print('Processing country boundary')
        # process_country_shapes(country)

        # print('Processing regions')
        # process_regions(country)

        # print('Processing settlement layer')
        # process_settlement_layer(country)

        # print('Processing night lights')
        # process_night_lights(country)

        # print('Processing coverage shapes')
        # process_coverage_shapes(country)

        print('Getting regional data')
        get_regional_data(country)

        # print('Generating agglomeration lookup table')
        # generate_agglomeration_lut(country)

        # print('Find regional nodes')
        # find_regional_nodes(country)

        # print('Fit edges')
        # input_path = os.path.join(DATA_INTERMEDIATE, country['iso3'], 'network', 'core_nodes.shp')
        # output_path = os.path.join(DATA_INTERMEDIATE, country['iso3'], 'network', 'core_edges.shp')
        # fit_edges(input_path, output_path)

        # print('Fit regional edges')
        # fit_regional_edges(country)

        # print('Create core lookup table')
        # generate_core_lut(country)

        # print('Create backhaul lookup table')
        # generate_backhaul_lut(country)

        # print('Create subscription forcast')
        # forecast_subscriptions(country)
