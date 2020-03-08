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
# import networkx as nx
from collections import OrderedDict
from pyproj import Transformer
import fiona

CONFIG = configparser.ConfigParser()
CONFIG.read(os.path.join(os.path.dirname(__file__), 'script_config.ini'))
BASE_PATH = CONFIG['file_locations']['base_path']

DATA_RAW = os.path.join(BASE_PATH, 'raw')
DATA_INTERMEDIATE = os.path.join(BASE_PATH, 'intermediate')
DATA_PROCESSED = os.path.join(BASE_PATH, 'processed')


def extract_large_settlements(country_id, population_threshold_km2, overall_settlement_size):
    """

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

    df = pd.concat([shapes_df, stats_df], axis=1).drop(columns='value')

    df = df[df['sum'] >= overall_settlement_size]

    df['geometry'] = df['geometry'].centroid

    df = get_points_inside_country(df, country_id)

    path = os.path.join(DATA_INTERMEDIATE, country_id, 'backhaul')
    filename = 'backhaul_routing_locations.shp'

    if not os.path.exists(path):
        os.mkdir(path)

    df.to_file(os.path.join(path, filename))

    lst = [i for i in df['geometry'].values]

    return lst


def get_points_inside_country(df, country_id):
    """
    Check routing locations lie inside country.

    """

    path = os.path.join(DATA_INTERMEDIATE, country_id, 'national_outline.shp')

    national_outline = gpd.read_file(path)

    bool_list = df.intersects(national_outline.unary_union)

    df = pd.concat([df, bool_list], axis=1)

    df = df[df[0] == True].drop(columns=0)

    return df


def design_network(nodes):

    links = []

    edges = []

    for node1_id, node1 in enumerate(nodes):
        for node2_id, node2 in enumerate(nodes):
            if node1_id != node2_id:
                # geom1 = Point(node1['geometry']['coordinates'])
                # geom2 = Point(node2['geometry']['coordinates'])
                line = LineString([node1, node2])
                edges.append({
                    'type': 'Feature',
                    'geometry': mapping(line),
                    'properties':{
                        'from': node1_id,
                        'to':  node2_id,
                        'length': line.length,
                    }
                })

    G = nx.Graph()

    for node in nodes:
        G.add_node(node['properties']['OLO'], object=node)

    for edge in edges:
        G.add_edge(edge['properties']['from'], edge['properties']['to'],
            object=edge, weight=edge['properties']['length'])

    tree = nx.minimum_spanning_edges(G)

    for branch in tree:
        link = branch[2]['object']
        if link['properties']['length'] > 0:
            links.append(link)

    return links


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
    for geom in nodes:
        fibre_point = {
            'type': 'Polygon',
            'geom': geom,
            'properties': {
                'point_id': point_id,
            }
        }
        fibre_points_with_id.append(fibre_point)
        idx.insert(
            point_id,
            geom.bounds,
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
                geom1 = fibre_point['geom']

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
        {'country': 'UGA', 'regional_level': 3},
        {'country': 'ETH', 'regional_level': 3},
        {'country': 'BGD', 'regional_level': 3},
        {'country': 'PER', 'regional_level': 3},
        {'country': 'MWI', 'regional_level': 3},
        {'country': 'ZAF', 'regional_level': 3},
        ]

    for country in country_list:

        country_id = country['country']

        print('Working on {}'.format(country_id))

        nodes = extract_large_settlements(
            country_id,
            population_density_threshold_km2,
            overall_settlement_size
        )

        # links = design_network(nodes)

        path = os.path.join(DATA_INTERMEDIATE, country_id, 'regions_lowest')

        if os.path.exists(path):

            output_csv, output_shapes = backhaul_distance(nodes, country, path)

            folder = os.path.join(DATA_INTERMEDIATE, country_id, 'backhaul')

            path = os.path.join(folder, 'backhaul.csv')
            output_csv.to_csv(path, index=False)

            folder = os.path.join(DATA_INTERMEDIATE, country_id, 'backhaul')
            write_shapefile(output_shapes, folder, 'backhaul.shp', 'epsg:4326')

        else:

            print('Regions not found for {}: Run preprocess.py first'.format(country_id))
