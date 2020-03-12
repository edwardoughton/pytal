"""
Preprocessing scripts.

Written by Ed Oughton.

Winter 2020

"""
import os
import configparser
import json
import pandas as pd
import gpd as gpd
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

    """
    path_processed = os.path.join(DATA_INTERMEDIATE,'global_countries.shp')
    countries = gpd.read_file(path_processed)

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


def process_country_shapes(country, path):
    """
    Created a set of global country shapes. Adds the single national boundary for
    each country to each country folder.

    """
    country_code = country['country_code']

    print('Loading all countries')
    countries = gpd.read_file(path)

    print('Getting specific country shape')
    single_country = countries[countries.GID_0 == country_code]

    print('Excluding small shapes')
    single_country['geometry'] = single_country.apply(exclude_small_shapes,axis=1)

    print('Simplifying geometries')
    single_country['geometry'] = single_country.simplify(tolerance = 0.005, preserve_topology=True) \
        .buffer(0.01).simplify(tolerance = 0.005, preserve_topology=True)

    print('Adding ISO country codes')
    glob_info_path = os.path.join(BASE_PATH, 'global_information.csv')
    load_glob_info = pd.read_csv(glob_info_path, encoding = "ISO-8859-1")
    single_country = single_country.merge(load_glob_info,left_on='GID_0', right_on='ISO_3digit')

    path = os.path.join(DATA_INTERMEDIATE, country_code)

    if not os.path.exists(path):
        print('Creating directory {}'.format(path))
        os.makedirs(path)

    shape_path = os.path.join(path, 'national_outline.shp')

    single_country.to_file(shape_path, driver='ESRI Shapefile')

    return print('All country shapes complete')


def process_lowest_regions(country):
    """
    Function for processing subnational regions.

    """
    regions = []

    country_code = country['country_code']
    level = country['regional_level']

    filename = 'regions_{}_{}.shp'.format(level, country_code)
    folder = os.path.join(DATA_INTERMEDIATE, country_code, 'regions_lowest')
    path_processed = os.path.join(folder, filename)

    if not os.path.exists(path_processed):

        if not os.path.exists(folder):
            os.mkdir(folder)

        print('Working on regions')
        filename = 'gadm36_{}.shp'.format(level)
        path_regions = os.path.join(DATA_RAW, 'gadm36_levels_shp', filename)
        regions = gpd.read_file(path_regions)

        path_country = os.path.join(DATA_INTERMEDIATE, country_code, 'national_outline.shp')
        countries = gpd.read_file(path_country)

        for name in countries.GID_0.unique():

            if not name == country_code:
                continue

            print('Working on {}'.format(name))
            regions = regions[regions.GID_0 == name]

            print('Excluding small shapes')
            regions['geometry'] = regions.apply(exclude_small_shapes,axis=1)

            print('Simplifying geometries')
            regions['geometry'] = regions.simplify(tolerance = 0.005, preserve_topology=True) \
                .buffer(0.01).simplify(tolerance = 0.005, preserve_topology=True)
            try:
                print('Writing global_regions.shp to file')
                regions.to_file(path_processed, driver='ESRI Shapefile')
            except:
                pass

    print('Completed processing of regional shapes level {}'.format(level))

    return print('complete')


def process_settlement_layer(country):
    """
    Clip the settlement layer to each country boundary and place in each country folder.

    """
    path_settlements = os.path.join(DATA_RAW,'settlement_layer','ppp_2020_1km_Aggregated.tif')

    settlements = rasterio.open(path_settlements, 'r+')
    settlements.nodata = 255
    settlements.crs = {"init": "epsg:4326"}

    country_code = country['country_code']
    path_country = os.path.join(DATA_INTERMEDIATE, country_code, 'national_outline.shp')

    if os.path.exists(path_country):
        country = gpd.read_file(path_country)
    else:
        print('Must generate national_outline.shp first' )

    path_country = os.path.join(DATA_INTERMEDIATE, country_code)
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
    Clip the nightlights layer and place in each country folder.

    """
    country_code = country['country_code']
    path_country = os.path.join(DATA_INTERMEDIATE, country_code, 'national_outline.shp')

    filename = 'F182013.v4c_web.stable_lights.avg_vis.tif'
    path_night_lights = os.path.join(DATA_RAW, 'nightlights', '2013', filename)

    country = gpd.read_file(path_country)

    print('working on {}'.format(country_code))

    path_country = os.path.join(DATA_INTERMEDIATE, country_code)

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


def get_regional_data(country):
    """
    Extract luminosity values.

    """
    level = country['regional_level']
    country_code = country['country_code']
    path_country = os.path.join(DATA_INTERMEDIATE, country_code, 'national_outline.shp')

    single_country = gpd.read_file(path_country)

    print('working on {}'.format(country_code))

    path_night_lights = os.path.join(DATA_INTERMEDIATE, country_code, 'night_lights.tif')
    path_settlements = os.path.join(DATA_INTERMEDIATE, country_code, 'settlements.tif')

    filename = 'regions_{}_{}.shp'.format(level, country_code)
    folder = os.path.join(DATA_INTERMEDIATE, country_code, 'regions_lowest')
    path = os.path.join(folder, filename)

    path_regions = gpd.read_file(path)

    project = pyproj.Transformer.from_proj(
        pyproj.Proj(init='epsg:4326'), # source coordinate system
        pyproj.Proj(init='epsg:3857')) # destination coordinate system

    results = []

    for index, region in path_regions.iterrows():

        with rasterio.open(path_night_lights) as src:

            affine = src.transform
            array = src.read(1)
            array[array <= 0] = 0

            #get luminosity values
            luminosity_median = [d['median'] for d in zonal_stats(
                region['geometry'], array, stats=['median'], affine=affine)][0]
            luminosity_summation = [d['sum'] for d in zonal_stats(
                region['geometry'], array, stats=['sum'], affine=affine)][0]

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

        # except:
        #     pass

    results_df = pd.DataFrame(results)

    results_df.to_csv(os.path.join(path_country, '..', 'regional_data.csv'), index=False)

    print('Completed {}'.format(single_country.NAME_0.values[0]))

    return print('Completed night lights data querying')


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
    coverage = gpd.read_file(path_raw)

    print('Setting crs for tiles')
    coverage.crs = {'init': 'epsg:3857'}

    print('Converting tiles to epsg 4326 (WGS84)')
    coverage = coverage.to_crs({'init': 'epsg:4326'})

    print('Importing global_countries.shp to get each country name')
    path_countries = os.path.join(DATA_INTERMEDIATE,'global_countries.shp')
    countries = gpd.read_file(path_countries)

    for name in countries.GID_0.unique():

        # if not name == 'MWI':
        #     continue

        print('Working on {}'.format(name))
        path = os.path.join(DATA_INTERMEDIATE, name, 'national_outline.shp')
        national_outline = gpd.read_file(path)

        print('Intersecting coverage tiles with country outline')
        intersection = gpd.overlay(coverage, national_outline, how='intersection')

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
            coverage = gpd.read_file(path)

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

    # country_list, country_regional_levels = find_country_list(['Africa', 'South America'])

    # country_list = [
    #     # 'UGA',
    #     # 'ETH',
    #     # 'BGD',
    #     # 'PER',
    #     'MWI',
    #     # 'ZAF'
    # ]

    countries = [
        {'country_code': 'SEN', 'regional_level': 3},
        # {'country_code': 'UGA', 'regional_level': 3},
        # {'country_code': 'ETH', 'regional_level': 3},
        # {'country_code': 'BGD', 'regional_level': 3},
        # {'country_code': 'PER', 'regional_level': 3},
        # {'country_code': 'MWI', 'regional_level': 3},
        # {'country_code': 'ZAF', 'regional_level': 3},
        ]

    for country in countries:

        # ###create 'global_countries.shp' if not already processed
        # ###create each 'national_outline.shp' if not already processed
        # path = os.path.join(DATA_RAW, 'gadm36_levels_shp', 'gadm36_0.shp')
        # process_country_shapes(country, path)

        # print('Processing lowest regions')
        # process_lowest_regions(country)

        # print('Processing settlement layer')
        # process_settlement_layer(country)

        # print('Processing night lights')
        # process_night_lights(country)

        get_regional_data(country)

        # process_coverage_shapes()
