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
from shapely.geometry import MultiPolygon, mapping, shape, LineString
from shapely.ops import transform, unary_union
from fiona.crs import from_epsg
import rasterio
from rasterio.mask import mask
from rasterstats import zonal_stats
import networkx as nx
from rtree import index
import numpy as np
from sklearn.linear_model import LinearRegression

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

    print('Loading all country shapes')
    path = os.path.join(DATA_RAW, 'gadm36_levels_shp', 'gadm36_0.shp')
    countries = gpd.read_file(path)

    print('Getting specific country shape for {}'.format(iso3))
    single_country = countries[countries.GID_0 == iso3]

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
    path = os.path.join(DATA_INTERMEDIATE, iso3)
    if not os.path.exists(path):
        print('Creating directory {}'.format(path))
        os.makedirs(path)
    shape_path = os.path.join(path, 'national_outline.shp')
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

        print('----')
        print('Working on {} level {}'.format(iso3, regional_level))

        filename = 'regions_{}_{}.shp'.format(regional_level, iso3)
        folder = os.path.join(DATA_INTERMEDIATE, iso3, 'regions')
        path_processed = os.path.join(folder, filename)

        if not os.path.exists(folder):
            os.mkdir(folder)

        filename = 'gadm36_{}.shp'.format(regional_level)
        path_regions = os.path.join(DATA_RAW, 'gadm36_levels_shp', filename)
        regions = gpd.read_file(path_regions)

        print('Subsetting {} level {}'.format(iso3, regional_level))
        regions = regions[regions.GID_0 == iso3]

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
    print('----')

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
    path_country = os.path.join(DATA_INTERMEDIATE, iso3,
        'national_outline.shp')

    filename = 'F182013.v4c_web.stable_lights.avg_vis.tif'
    path_night_lights = os.path.join(DATA_RAW, 'nightlights', '2013',
        filename)

    country = gpd.read_file(path_country)

    print('----')
    print('working on {}'.format(iso3))

    path_country = os.path.join(DATA_INTERMEDIATE, iso3)

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
    iso3 = country['iso3']
    iso2 = country['iso2']

    technologies = [
        'GSM',
        '3G',
        '4G'
    ]

    for tech in technologies:

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
                preserve_topology=True).buffer(0.01).simplify(
                tolerance = 0.005,
                preserve_topology=True
            )

            folder = os.path.join(DATA_INTERMEDIATE, iso3,
                'coverage')

            if not os.path.exists(folder):
                os.makedirs(folder)

            filename = 'coverage_{}.shp'.format(tech)
            path = os.path.join(folder, filename)
            coverage.to_file(path, driver='ESRI Shapefile')

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

            coverage.crs = {'init': 'epsg:3857'}

            coverage = coverage.to_crs({'init': 'epsg:4326'})

            segments = gpd.overlay(regions, coverage, how='intersection')

            segments = segments.to_crs({'init': 'epsg:3857'})

            tech_coverage = {}

            for idx, region in segments.iterrows():

                geom = region['geometry']

                area_km2 = geom.area / 1e6

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

    path_country = os.path.join(DATA_INTERMEDIATE, iso3,
        'national_outline.shp')

    coverage = process_regional_coverage(country)

    site_estimator = setup_site_estimator('SEN')

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

    path_regions = gpd.read_file(path)

    project = pyproj.Transformer.from_proj(
        pyproj.Proj("EPSG:4326"), # source coordinate system
        pyproj.Proj("EPSG:3857")) # destination coordinate system

    results = []

    for index, region in path_regions.iterrows():

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

        try:
            sites_km2 = estimate_numers_of_sites(
                    site_estimator,
                    np.array([(population_summation / area_km2)]).reshape(-1, 1)
                )
        except:
            sites_km2 = 0

        try:
            sites_total = (
                estimate_numers_of_sites(
                site_estimator,
                np.array([(population_summation / area_km2)]).reshape(-1, 1)
                ) * coverage_GSM_km2
            )
        except:
            sites_total = 0

        results.append({
            'GID_0': region['GID_0'],
            gid_level: region[gid_level],
            'median_luminosity': luminosity_median,
            'sum_luminosity': luminosity_summation,
            'mean_luminosity_km2': luminosity_summation / area_km2,
            'population': population_summation,
            'area_km2': area_km2,
            'population_km2': population_summation / area_km2,
            'coverage_GSM_km2': coverage_GSM_km2,
            'coverage_3G_km2': coverage_3G_km2,
            'coverage_4G_km2': coverage_4G_km2,
            'sites_km2': sites_km2,
            'sites_total': sites_total,
        })

    results_df = pd.DataFrame(results)

    path = os.path.join(path_country, '..', 'regional_data.csv')
    results_df.to_csv(path, index=False)

    print('Completed {}'.format(single_country.NAME_0.values[0]))

    return print('Completed night lights data querying')


def setup_site_estimator(iso3):
    """
    Imports data and creates a linear_regressor object.

    Parameters
    ----------
    iso3 : string
        The three digit ISO3 code for the country site data that
        we want to use.

    Returns
    -------
    linear_regressor : object
        Linear regression object.

    """
    path = os.path.join(DATA_RAW, 'real_site_data', iso3, 'results.csv')

    data = pd.read_csv(path)

    data = data.loc[data['country'] == iso3]

    # values converts it into a numpy array
    X = data['population_km2'].values.reshape(-1, 1)
    # -1 means that calculate the dimension of rows, but have 1 column
    Y = data['sites_km2'].values.reshape(-1, 1)
    # create object for the class
    linear_regressor = LinearRegression()
    # perform linear regression
    linear_regressor.fit(X, Y)

    return linear_regressor


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


def fit_edges(nodes):
    """
    Fit edges to the identified nodes using a minimum spanning tree.

    Parameters
    ----------
    nodes : list of dicts
        Core nodes as Geojson objects.

    Returns
    -------
    edges : list of dicts
        Minimum spanning tree connecting all provided nodes.

    """
    all_possible_edges = []

    for node1_id, node1 in enumerate(nodes):
        for node2_id, node2 in enumerate(nodes):
            if node1_id != node2_id:
                geom1 = shape(node1['geometry'])
                geom2 = shape(node2['geometry'])
                line = LineString([geom1, geom2])
                all_possible_edges.append({
                    'type': 'Feature',
                    'geometry': mapping(line),
                    'properties':{
                        'network_layer': 'core',
                        'from': node1_id,
                        'to':  node2_id,
                        'length': line.length,
                    }
                })

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

    return edges


def estimate_regional_hubs(path, nodes, regional_hubs_level, iso3):
    """
    Identify new regional hub locations to connect.

    Parameters
    ----------
    path : string
        Path to the GADM regions to be used in the analysis.
    nodes : dataframe
        A geopandas dataframe containing settlement nodes.
    regional_hubs_level : int
        Relates to the GADM regional levels to be used.
    iso3 : string
        ISO 3 digit country code.

    Returns
    -------
    output : list of dicts
        Contains new regional hub nodes as Geojson objects.

    """
    output = []

    regions = gpd.read_file(path)

    nodes = gpd.GeoDataFrame.from_features(nodes)

    for row_number, region in regions.iterrows():

        if not region['GID_0'] == iso3:
            continue

        indicator = 0
        for index1, node in nodes.iterrows():
            if node['geometry'].intersects(region['geometry']):
                indicator = 1

        if indicator == 0:
            output.append({
                'type': 'Feature',
                'geometry': mapping(region['geometry'].centroid),
                'properties': {
                    'id': 'regional_hub_{}'.format(row_number),
                    'hub_number': row_number,
                    'network_layer': 'regional_hub',
                }
            })
        else:
            pass

    return output


def fit_regional_edges(core_nodes, regional_hubs):
    """
    Fit edges to the identified nodes using a minimum spanning tree.

    Parameters
    ----------
    core_nodes : dataframe
        A geopandas dataframe containing settlement nodes.
    regional_hubs :

    Returns
    -------
    edges : list of dicts
        Minimum spanning tree connecting all provided nodes.

    """
    idx = index.Index()

    for node in core_nodes:
        idx.insert(
            node['properties']['node_number'],
            shape(node['geometry']).bounds,
            node)

    output = []

    for regional_hub in regional_hubs:

        geom1 = shape(regional_hub['geometry'])

        nearest = [i for i in idx.nearest((geom1.bounds))][0]

        for core_node in core_nodes:
            if nearest == core_node['properties']['node_number']:
                geom2 = shape(core_node['geometry'])
                output.append({
                    'type': 'Feature',
                    'geometry': {
                        'type': 'LineString',
                        'coordinates': (
                            (list(geom1.coords)[0][0], list(geom1.coords)[0][1]),
                            (list(geom2.coords)[0][0], list(geom2.coords)[0][1])
                            )
                        },
                    'properties': {
                        'regional_hub': regional_hub['properties']['id'],
                        'core_node': core_node['properties']['id'],
                        },
                    })

    return output


def create_network(country, pop_density_km2, settlement_size):
    """
    Create a core network and any necessary regional hubs.

    Parameters
    ----------
    country : dict
        Contains specific country information.
    pop_density_km2 : int
        Population density threshold per km^2.
    settlement_size : int
        Overall settlement size.

    """
    print('---')

    iso3 = country['iso3']
    regional_hubs_level = country['regional_hubs_level']

    print('Working on {}'.format(iso3))

    print('Generating core nodes')
    core_nodes = estimate_core_nodes(
        iso3,
        pop_density_km2,
        settlement_size
    )

    print('Generating core edges')
    core_edges = fit_edges(core_nodes)

    print('Generating regional hubs')
    filename = 'regions_{}_{}.shp'.format(regional_hubs_level, iso3)
    folder = os.path.join(DATA_INTERMEDIATE, iso3, 'regions')
    path = os.path.join(folder, filename)

    regional_hubs = estimate_regional_hubs(path, core_nodes,
        regional_hubs_level, iso3)

    #Countries like Bangladesh with have a node in every region unless the
    #settlement size is adapted (hence there will be no regional hubs)
    if len(regional_hubs) > 0:

        print('Generating regional edges')
        regional_edges = fit_regional_edges(core_nodes, regional_hubs)

        path = os.path.join(DATA_INTERMEDIATE, iso3, 'regional_hubs')
        if not os.path.exists(path):
            os.makedirs(path)

        regional_hubs = gpd.GeoDataFrame.from_features(regional_hubs, crs='epsg:4326')
        regional_hubs.to_file(os.path.join(path, 'regional_hubs.shp'))

        regional_edges = gpd.GeoDataFrame.from_features(regional_edges, crs='epsg:4326')
        path = os.path.join(DATA_INTERMEDIATE, iso3, 'regional_hubs', 'regional_edges.shp')
        regional_edges.to_file(path)

    path = os.path.join(DATA_INTERMEDIATE, iso3, 'core')
    if not os.path.exists(path):
        os.makedirs(path)

    core_nodes = gpd.GeoDataFrame.from_features(core_nodes, crs='epsg:4326')
    core_nodes.to_file(os.path.join(path, 'core_nodes.shp'))

    core_edges = gpd.GeoDataFrame.from_features(core_edges, crs='epsg:4326')
    core_edges.to_file(os.path.join(path, 'core_edges.shp'))

    print('Completed {}'.format(iso3))


def backhaul_distance(country):
    """
    Function to calculate the backhaul distance.

    """
    country_id = country['iso3']
    level = country['regional_level']

    filename = 'regions_{}_{}.shp'.format(level, country_id)
    folder = os.path.join(DATA_INTERMEDIATE, country_id, 'regions')
    path = os.path.join(folder, filename)

    regions = gpd.read_file(path)
    regions.crs = 'epsg:4326'
    regions = regions.to_crs({'init': 'epsg:3857'})

    path1 = os.path.join(DATA_INTERMEDIATE, country_id, 'core', 'core_nodes.shp')
    path2 = os.path.join(DATA_INTERMEDIATE, country_id, 'regional_hubs', 'regional_hubs.shp')
    files = [path1, path2]
    nodes = pd.concat([gpd.read_file(shp) for shp in files]).pipe(gpd.GeoDataFrame)

    nodes.crs = 'epsg:4326'
    nodes = nodes.to_crs({'init': 'epsg:3857'})

    idx = index.Index()

    routing_locations = []

    point_id = 0
    for row, node in nodes.iterrows():
        routing_location = {
            'type': 'Polygon',
            'geometry': node['geometry'],
            'properties': {
                'id': point_id,
            }
        }
        routing_locations.append(routing_location)
        idx.insert(
            point_id,
            node['geometry'].bounds,
            routing_location)
        point_id += 1

    output_csv = []
    output_shape = []

    for row_number, region in regions.iterrows():

        geom = region['geometry'].representative_point()

        nearest = [i for i in idx.nearest((geom.bounds))][0]

        for routing_location in routing_locations:

            if nearest == routing_location['properties']['id']:

                geom2 = routing_location['geometry']

                x1 = list(geom2.coords)[0][0]
                y1 = list(geom2.coords)[0][1]

        geom1 = unary_union(region['geometry']).representative_point()

        x2 = list(geom1.coords)[0][0]
        y2 = list(geom1.coords)[0][1]

        line = LineString([
            (x1, y1),
            (x2, y2)
        ])

        output_csv.append({
            'GID_{}'.format(level): region['GID_{}'.format(level)],
            'distance_m': int(line.length),
        })

        output_shape.append({
            'type': 'Feature',
            'geometry': {
                'type': 'LineString',
                'coordinates': (
                    (list(geom1.coords)[0][0], list(geom1.coords)[0][1]),
                    (list(geom2.coords)[0][0], list(geom2.coords)[0][1])
                )
            },
            'properties': {
                'region': region['GID_{}'.format(level)],
            }
        })

    folder = os.path.join(DATA_INTERMEDIATE, country_id, 'backhaul')

    if not os.path.exists(folder):
        os.makedirs(folder)

    shapes = gpd.GeoDataFrame.from_features(output_shape, 'epsg:3857')
    shapes = shapes.to_crs({'init': 'epsg:4326'})
    shapes.to_file(os.path.join(folder, 'backhaul.shp'))

    output_csv = pd.DataFrame(output_csv)
    output_csv.to_csv(os.path.join(folder, 'backhaul.csv'), index=False)

    return output_csv


if __name__ == '__main__':

    # countries = find_country_list(['Africa'])

    countries = [
        {'iso3': 'SEN', 'iso2': 'SN', 'regional_level': 2, 'regional_hubs_level': 1},
        # {'iso3': 'KEN', 'iso2': 'KE', 'regional_level': 2, 'regional_hubs_level': 1},
        # {'iso3': 'UGA', 'iso2': 'UG', 'regional_level': 2, 'regional_hubs_level': 1},
        # {'iso3': 'ETH', 'iso2': 'ET', 'regional_level': 2, 'regional_hubs_level': 1},
        # {'iso3': 'BGD', 'iso2': 'BD', 'regional_level': 2, 'regional_hubs_level': 1},
        # {'iso3': 'PER', 'iso2': 'PE', 'regional_level': 2, 'regional_hubs_level': 1},
        # {'iso3': 'MWI', 'iso2': 'MW', 'regional_level': 2, 'regional_hubs_level': 1},
        # {'iso3': 'ZAF', 'iso2': 'ZA', 'regional_level': 2, 'regional_hubs_level':2},
        ]

    pop_density_km2 = 1000
    settlement_size = 20000

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

        # print('Getting regional data')
        # get_regional_data(country)

        print('Creating network')
        create_network(country, pop_density_km2, settlement_size)

        print('Create backhaul lookup table')
        output = backhaul_distance(country)
        # print(output)
