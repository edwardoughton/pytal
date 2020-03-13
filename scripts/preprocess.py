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
import networkx as nx
from rtree import index

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
        folder = os.path.join(DATA_RAW, 'Mobile Coverage Explorer',
            'Data_MCE')
        inclusions = gpd.read_file(os.path.join(folder, filename))

        if iso2 in inclusions['CNTRY_ISO2']:

            filename = 'MCE_201812_{}.shp'.format(tech)
            folder = os.path.join(DATA_RAW, 'Mobile Coverage Explorer',
                'Data_MCE')
            coverage = gpd.read_file(os.path.join(folder, filename))

            coverage = coverage.loc[coverage['CNTRY_ISO3'] == iso3]

        else:

            filename = 'OCI_201812_{}.shp'.format(tech)
            folder = os.path.join(DATA_RAW, 'Mobile Coverage Explorer',
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


def get_regional_data(country):
    """
    Extract regional data including luminosity and population.

    Parameters
    ----------
    country : string
        Three digit ISO country code.

    """
    level = country['regional_level']
    iso3 = country['iso3']
    path_country = os.path.join(DATA_INTERMEDIATE, iso3,
        'national_outline.shp')

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
        pyproj.Proj("EPSG:4326"), #"EPSG:4326" # source coordinate system
        pyproj.Proj("EPSG:3857")) #"EPSG:3857" # destination coordinate system

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
                'id': index,
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

    for index2, region in regions.iterrows():

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
                    'id': region['GID_{}'.format(regional_hubs_level)]
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
            node['properties']['id'],
            shape(node['geometry']).bounds,
            node)

    output = []

    for regional_hub in regional_hubs:

        geom1 = shape(regional_hub['geometry'])

        nearest = [i for i in idx.nearest((geom1.bounds))][0]

        for core_node in core_nodes:
            if nearest == core_node['properties']['id']:
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


if __name__ == '__main__':

    # countries = find_country_list(['Africa'])

    countries = [
        # {'iso3': 'SEN', 'iso2': 'SN', 'regional_level': 3, 'regional_hubs_level': 1},
        # {'iso3': 'UGA', 'iso2': 'UG', 'regional_level': 3, 'regional_hubs_level': 1},
        # {'iso3': 'ETH', 'iso2': 'ET', 'regional_level': 3, 'regional_hubs_level': 1},
        # {'iso3': 'BGD', 'iso2': 'BD', 'regional_level': 3, 'regional_hubs_level': 1},
        {'iso3': 'PER', 'iso2': 'PE', 'regional_level': 3, 'regional_hubs_level': 1},
        # {'iso3': 'MWI', 'iso2': 'MW', 'regional_level': 3, 'regional_hubs_level': 1},
        # {'iso3': 'ZAF', 'iso2': 'ZA', 'regional_level': 3, 'regional_hubs_level':2},
        ]

    pop_density_km2 = 1000
    settlement_size = 20000

    for country in countries:

        print('Processing country boundary')
        process_country_shapes(country)

        print('Processing regions')
        process_regions(country)

        print('Processing settlement layer')
        process_settlement_layer(country)

        print('Processing night lights')
        process_night_lights(country)

        print('Processing coverage shapes')
        process_coverage_shapes(country)

        print('Getting regional data')
        get_regional_data(country)

        print('Creating network')
        create_network(country, pop_density_km2, settlement_size)
