"""
Preprocessing scripts.

Written by Ed Oughton.

Winter 2020

"""
import os
import configparser
import json
import pandas as pd
import geopandas as gpd
import pyproj
from shapely.geometry import MultiPolygon
from fiona.crs import from_epsg
import rasterio
from rasterio.mask import mask
from rasterstats import zonal_stats
from shapely.ops import transform

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
            'country_code_ISO3': country['GID_0'],
            'country_code_ISO2': country['ISO_2digit'],
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
    country_code_ISO3 = country['country_code_ISO3']

    print('Loading all country shapes')
    path = os.path.join(DATA_RAW, 'gadm36_levels_shp', 'gadm36_0.shp')
    countries = gpd.read_file(path)

    print('Getting specific country shape for {}'.format(country_code_ISO3))
    single_country = countries[countries.GID_0 == country_code_ISO3]

    print('Excluding small shapes')
    single_country['geometry'] = single_country.apply(
        exclude_small_shapes, axis=1)

    print('Simplifying geometries')
    single_country['geometry'] = single_country.simplify(
        tolerance = 0.005,
        preserve_topology=True).buffer(0.01).simplify(
        tolerance = 0.005,
        preserve_topology=True
    )

    print('Adding ISO country code and other global information')
    glob_info_path = os.path.join(BASE_PATH, 'global_information.csv')
    load_glob_info = pd.read_csv(glob_info_path, encoding = "ISO-8859-1")
    single_country = single_country.merge(
        load_glob_info,left_on='GID_0', right_on='ISO_3digit')

    print('Exporting processed country shape')
    path = os.path.join(DATA_INTERMEDIATE, country_code_ISO3)
    if not os.path.exists(path):
        print('Creating directory {}'.format(path))
        os.makedirs(path)
    shape_path = os.path.join(path, 'national_outline.shp')
    single_country.to_file(shape_path, driver='ESRI Shapefile')

    return print('Processing country shape complete')


def process_lowest_regions(country):
    """
    Function for processing the lowest desired subnational regions for the
    chosen country.

    Parameters
    ----------
    country : string
        Three digit ISO country code.

    """
    regions = []

    country_code_ISO3 = country['country_code_ISO3']
    level = country['regional_level']

    filename = 'regions_{}_{}.shp'.format(level, country_code_ISO3)
    folder = os.path.join(DATA_INTERMEDIATE, country_code_ISO3,
        'regions_lowest')
    path_processed = os.path.join(folder, filename)

    if not os.path.exists(path_processed):

        if not os.path.exists(folder):
            os.mkdir(folder)

        print('Working on regions')
        filename = 'gadm36_{}.shp'.format(level)
        path_regions = os.path.join(DATA_RAW, 'gadm36_levels_shp', filename)
        regions = gpd.read_file(path_regions)

        path_country = os.path.join(DATA_INTERMEDIATE, country_code_ISO3,
            'national_outline.shp')
        countries = gpd.read_file(path_country)

        for name in countries.GID_0.unique():

            if not name == country_code_ISO3:
                continue

            print('Working on {}'.format(name))
            regions = regions[regions.GID_0 == name]

            print('Excluding small shapes')
            regions['geometry'] = regions.apply(exclude_small_shapes, axis=1)

            print('Simplifying geometries')
            regions['geometry'] = regions.simplify(
                tolerance = 0.005,
                preserve_topology=True).buffer(0.01).simplify(
                    tolerance = 0.005,
                    preserve_topology=True
                )
            try:
                print('Writing global_regions.shp to file')
                regions.to_file(path_processed, driver='ESRI Shapefile')
            except:
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
    path_settlements = os.path.join(DATA_RAW,'settlement_layer',
        'ppp_2020_1km_Aggregated.tif')

    settlements = rasterio.open(path_settlements, 'r+')
    settlements.nodata = 255
    settlements.crs = {"init": "epsg:4326"}

    country_code_ISO3 = country['country_code_ISO3']
    path_country = os.path.join(DATA_INTERMEDIATE, country_code_ISO3,
        'national_outline.shp')

    if os.path.exists(path_country):
        country = gpd.read_file(path_country)
    else:
        print('Must generate national_outline.shp first' )

    path_country = os.path.join(DATA_INTERMEDIATE, country_code_ISO3)
    shape_path = os.path.join(path_country, 'settlements.tif')

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
    country_code_ISO3 = country['country_code_ISO3']
    path_country = os.path.join(DATA_INTERMEDIATE, country_code_ISO3,
        'national_outline.shp')

    filename = 'F182013.v4c_web.stable_lights.avg_vis.tif'
    path_night_lights = os.path.join(DATA_RAW, 'nightlights', '2013',
        filename)

    country = gpd.read_file(path_country)

    print('working on {}'.format(country_code_ISO3))

    path_country = os.path.join(DATA_INTERMEDIATE, country_code_ISO3)

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

    shape_path = os.path.join(path_country,'night_lights.tif')

    with rasterio.open(shape_path, "w", **out_meta) as dest:
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
    country_code_ISO3 = country['country_code_ISO3']
    country_code_ISO2 = country['country_code_ISO2']

    technologies = [
        'GSM',
        '3G',
        '4G'
    ]

    for tech in technologies:

        print('Working on {} in {}'.format(tech, country_code_ISO3))

        filename = 'Inclusions_201812_{}.shp'.format(tech)
        folder = os.path.join(DATA_RAW, 'Mobile Coverage Explorer',
            'Data_MCE')
        inclusions = gpd.read_file(os.path.join(folder, filename))

        if country_code_ISO2 in inclusions['CNTRY_ISO2']:

            filename = 'MCE_201812_{}.shp'.format(tech)
            folder = os.path.join(DATA_RAW, 'Mobile Coverage Explorer',
                'Data_MCE')
            coverage = gpd.read_file(os.path.join(folder, filename))

            coverage = coverage.loc[coverage['CNTRY_ISO3'] == country_code_ISO3]

        else:

            filename = 'OCI_201812_{}.shp'.format(tech)
            folder = os.path.join(DATA_RAW, 'Mobile Coverage Explorer',
                'Data_OCI')
            coverage = gpd.read_file(os.path.join(folder, filename))

            coverage = coverage.loc[coverage['CNTRY_ISO3'] == country_code_ISO3]

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
                preserve_topology=True).buffer(0.01).simplify(
                tolerance = 0.005,
                preserve_topology=True
            )

            folder = os.path.join(DATA_INTERMEDIATE, country_code_ISO3,
                'coverage')

            if not os.path.exists(folder):
                os.makedirs(folder)

            filename = 'coverage_{}.shp'.format(tech)
            path = os.path.join(folder, filename)
            coverage.to_file(path, driver='ESRI Shapefile')

    print('Processed coverage shapes')


def get_regional_data(country):
    """
    Extract regional data including luminosity and population.

    Parameters
    ----------
    country : string
        Three digit ISO country code.

    """
    level = country['regional_level']
    country_code_ISO3 = country['country_code_ISO3']
    path_country = os.path.join(DATA_INTERMEDIATE, country_code_ISO3,
        'national_outline.shp')

    single_country = gpd.read_file(path_country)

    print('working on {}'.format(country_code_ISO3))

    path_night_lights = os.path.join(DATA_INTERMEDIATE, country_code_ISO3,
        'night_lights.tif')
    path_settlements = os.path.join(DATA_INTERMEDIATE, country_code_ISO3,
        'settlements.tif')

    filename = 'regions_{}_{}.shp'.format(level, country_code_ISO3)
    folder = os.path.join(DATA_INTERMEDIATE, country_code_ISO3,
        'regions_lowest')
    path = os.path.join(folder, filename)

    path_regions = gpd.read_file(path)

    project = pyproj.Transformer.from_proj(
        pyproj.Proj(init='epsg:4326'), # source coordinate system
        pyproj.Proj(init='epsg:3857')) # destination coordinate system

    results = []

    for index, region in path_regions.iterrows():

        try:

            with rasterio.open(path_night_lights) as src:

                affine = src.transform
                array = src.read(1)
                array[array <= 0] = 0

                #get luminosity values
                luminosity_median = [d['median'] for d in zonal_stats(
                    region['geometry'],
                    array,
                    stats=['median'],
                    affine=affine)][0]

                luminosity_summation = [d['sum'] for d in zonal_stats(
                    region['geometry'],
                    array,
                    stats=['sum'],
                    affine=affine)][0]

            with rasterio.open(path_settlements) as src:

                affine = src.transform
                array = src.read(1)
                array[array <= 0] = 0

                #get luminosity values
                population_summation = [d['sum'] for d in zonal_stats(
                    region['geometry'], array, stats=['sum'], affine=affine)][0]

            geom = transform(project.transform, region['geometry'])

            area_km2 = geom.area / 10**6

            if luminosity_median == None:
                luminosity_median = 0
            if luminosity_summation == None:
                luminosity_summation = 0

            gid_level = 'GID_{}'.format(level)

            results.append({
                'GID_0': region['GID_0'],
                gid_level: region[gid_level],
                'median_luminosity': luminosity_median,
                'sum_luminosity': luminosity_summation,
                'mean_luminosity_km2': luminosity_summation / area_km2,
                'population': population_summation,
                'area_km2': area_km2,
                'population_km2': population_summation / area_km2,
            })

        except:
            print('Could not extract regional data for {}'.format(
                region['GID_0']))
            pass

    results_df = pd.DataFrame(results)

    path = os.path.join(path_country, '..', 'regional_data.csv')
    results_df.to_csv(path, index=False)

    print('Completed {}'.format(single_country.NAME_0.values[0]))

    return print('Completed night lights data querying')


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


if __name__ == '__main__':

    # countries = find_country_list(['Africa'])

    countries = [
        # {'country_code_ISO3': 'SEN', 'country_code_ISO2': 'SN', 'regional_level': 3},
        # {'country_code_ISO3': 'UGA', 'country_code_ISO2': 'UG', 'regional_level': 3},
        # {'country_code_ISO3': 'ETH', 'country_code_ISO2': 'ET', 'regional_level': 3},
        # {'country_code_ISO3': 'BGD', 'country_code_ISO2': 'BD', 'regional_level': 3},
        {'country_code_ISO3': 'PER', 'country_code_ISO2': 'PE', 'regional_level': 3},
        # {'country_code_ISO3': 'MWI', 'country_code_ISO2': 'MW', 'regional_level': 3},
        # {'country_code_ISO3': 'ZAF', 'country_code_ISO2': 'ZA', 'regional_level': 3},
        ]

    for country in countries:

        print('Processing country boundary')
        process_country_shapes(country)

        print('Processing lowest regions')
        process_lowest_regions(country)

        print('Processing settlement layer')
        process_settlement_layer(country)

        print('Processing night lights')
        process_night_lights(country)

        print('Processing coverage shapes')
        process_coverage_shapes(country)

        print('Getting regional data')
        get_regional_data(country)
