"""
Create 10km x 10km grid.
Written by Ed Oughton.
Winter 2020
"""
import os
import configparser
import geopandas as gpd
from shapely.geometry import Point, LineString, Polygon, shape, MultiPoint, mapping
from shapely.ops import unary_union
import pandas as pd
import numpy as np
import rasterio
from rasterstats import zonal_stats
from rtree import index
import networkx as nx
from collections import OrderedDict
from pyproj import Transformer
import fiona

CONFIG = configparser.ConfigParser()
CONFIG.read(os.path.join(os.path.dirname(__file__), 'script_config.ini'))
BASE_PATH = CONFIG['file_locations']['base_path']

DATA_RAW = os.path.join(BASE_PATH, 'raw')
DATA_INTERMEDIATE = os.path.join(BASE_PATH, 'intermediate')
DATA_PROCESSED = os.path.join(BASE_PATH, 'processed')


def estimate_core_nodes(country_id, population_threshold_km2,
    overall_settlement_size):
    """
    This function identifies settlements which exceed a desired settlement
    size. It is assumed fiber exists at settlements over, for example,
    20,000 inhabitants.

    Parameters
    ----------
    country_id : string
        ISO 3 digit country code.
    population_threshold_km2 : int
        Population density threshold for identifying built up areas.
    overall_settlement_size : int
        Overall sittelement size assumption, e.g. 20,000 inhabitants.

    Returns
    -------
    output : list of dicts
        Identified major settlements as Geojson objects.

    """
    path = os.path.join(DATA_INTERMEDIATE, country_id, 'settlements.tif')

    with rasterio.open(path) as src:
        data = src.read()
        threshold = population_threshold_km2
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

    nodes = nodes[nodes['sum'] >= overall_settlement_size]

    nodes['geometry'] = nodes['geometry'].centroid

    nodes = get_points_inside_country(nodes, country_id)

    path = os.path.join(DATA_INTERMEDIATE, country_id, 'backhaul')
    filename = 'backhaul_routing_locations.shp'

    if not os.path.exists(path):
        os.mkdir(path)

    nodes.to_file(os.path.join(path, filename))

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


def get_points_inside_country(nodes, country_id):
    """
    Check settlement locations lie inside target country.

    Parameters
    ----------
    nodes : dataframe
        A geopandas dataframe containing settlement nodes.
    country_id : string
        ISO 3 digit country code.

    Returns
    -------
    nodes : dataframe
        A geopandas dataframe containing settlement nodes.

    """
    filename = 'national_outline.shp'
    path = os.path.join(DATA_INTERMEDIATE, country_id, filename)

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


def estimate_regional_hubs(path, nodes, regional_hubs_level, country_id):
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
    country_id : string
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

        if not region['GID_0'] == country_id:
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

    fibre_points_with_id = []

    for node in core_nodes:
        # fibre_points_with_id.append(fibre_point)
        idx.insert(
            node['properties']['id'],
            shape(node['geometry']).bounds,
            node)

    # transformer = Transformer.from_crs("EPSG:4326", "EPSG:3857")

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


def backhaul_distance(nodes, country, path_regions):
    """



    """
    country_id = country['country']
    level = country['regional_level']

    filename = 'regions_{}_{}.shp'.format(level, country_id)
    folder = os.path.join(DATA_INTERMEDIATE, country_id, 'regions_lowest')
    path = os.path.join(folder, filename)

    region_data = gpd.read_file(path)
    regions = region_data.to_dict('records')

    idx = index.Index()

    fibre_points_with_id = []
    point_id = 0
    for node in nodes:
        fibre_point = {
            'type': 'Polygon',
            'geometry': node['geometry'],
            'properties': {
                'point_id': point_id,
            }
        }
        fibre_points_with_id.append(fibre_point)
        idx.insert(
            point_id,
            shape(node['geometry']).bounds,
            fibre_point)
        point_id += 1

    transformer = Transformer.from_crs("EPSG:4326", "EPSG:3857")

    output_csv = []
    output_shape = []

    for region in regions:

        geom = shape(region['geometry']).representative_point()

        nearest = [i for i in idx.nearest((geom.bounds))][0]
        region['point_id'] = nearest

        for fibre_point in fibre_points_with_id:
            if nearest == fibre_point['properties']['point_id']:

                geom1 = shape(fibre_point['geometry'])

                x1 = list(geom1.coords)[0][0]
                y1 = list(geom1.coords)[0][1]

                x1, y1 = transformer.transform(x1, y1)

        geom2 = unary_union(region['geometry']).representative_point()

        x2 = list(geom2.coords)[0][0]
        y2 = list(geom2.coords)[0][1]

        x2, y2 = transformer.transform(x2, y2)

        line = LineString([
            (x1, y1),
            (x2, y2)
        ])

        output_csv.append({
            'GID_{}'.format(level): region['GID_{}'.format(level)],
            'distance_km': line.length,
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

    output_csv = pd.DataFrame(output_csv)

    return output_csv, output_shape


def write_shapefile(data, directory, filename, crs):
    """
    Write geojson data to shapefile.
    """
    prop_schema = []
    for name, value in data[0]['properties'].items():
        fiona_prop_type = next((
            fiona_type for fiona_type, python_type in \
                fiona.FIELD_TYPES_MAP.items() if \
                python_type == type(value)), None
            )

        prop_schema.append((name, fiona_prop_type))

    sink_driver = 'ESRI Shapefile'
    sink_crs = {'init': crs}
    sink_schema = {
        'geometry': data[0]['geometry']['type'],
        'properties': OrderedDict(prop_schema)
    }

    if not os.path.exists(directory):
        os.makedirs(directory)

    with fiona.open(
        os.path.join(directory, filename), 'w',
        driver=sink_driver, crs=sink_crs, schema=sink_schema) as sink:
        for datum in data:
            sink.write(datum)


if __name__ == '__main__':

    population_density_threshold_km2 = 1000
    overall_settlement_size = 20000

    country_list = [
        {'country': 'UGA', 'regional_level': 3, 'regional_hubs_level': 1},
        {'country': 'ETH', 'regional_level': 3, 'regional_hubs_level': 1},
        {'country': 'BGD', 'regional_level': 3, 'regional_hubs_level': 1},
        {'country': 'PER', 'regional_level': 3, 'regional_hubs_level': 1},
        {'country': 'MWI', 'regional_level': 3, 'regional_hubs_level': 1},
        {'country': 'ZAF', 'regional_level': 3, 'regional_hubs_level': 2},
        ]

    for country in country_list:

        country_id = country['country']

        print('Working on {}'.format(country_id))

        print('Generating core nodes')
        core_nodes = estimate_core_nodes(
            country_id,
            population_density_threshold_km2,
            overall_settlement_size
        )

        folder = os.path.join(DATA_INTERMEDIATE, country_id, 'core')
        write_shapefile(core_nodes, folder, 'core_nodes.shp', 'epsg:4326')

        print('Generating core edges')
        core_edges = fit_edges(core_nodes)

        folder = os.path.join(DATA_INTERMEDIATE, country_id, 'core')
        write_shapefile(core_edges, folder, 'core_edges.shp', 'epsg:4326')

        print('Generating regional hubs')
        filename = 'global_regions_{}.shp'.format(country['regional_hubs_level'])
        path = os.path.join(DATA_INTERMEDIATE, filename)

        regional_hubs = estimate_regional_hubs(path, core_nodes,
            country['regional_hubs_level'], country_id)

        #Countries like Bangladesh with have a node in every region unless the
        #settlement size is adapted (hence there will be no regional hubs)
        if len(regional_hubs) > 0:

            folder = os.path.join(DATA_INTERMEDIATE, country_id, 'regional_hubs')
            write_shapefile(regional_hubs, folder, 'regional_hubs.shp', 'epsg:4326')

            print('Generating regional edges')
            regional_edges = fit_regional_edges(core_nodes, regional_hubs)

            folder = os.path.join(DATA_INTERMEDIATE, country_id, 'regional_hubs')
            write_shapefile(regional_edges, folder, 'regional_edges.shp', 'epsg:4326')

        print('Completed {}'.format(country_id))
