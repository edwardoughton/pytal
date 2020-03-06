"""
Create 10km x 10km grid.
Written by Ed Oughton.
Winter 2020
"""
import argparse
import os
import configparser
import geopandas as gpd
from shapely.geometry import Point, Polygon, MultiPoint, mapping
from sklearn.cluster import DBSCAN
import pandas as pd
import numpy as np
import rasterio
from rasterstats import zonal_stats

CONFIG = configparser.ConfigParser()
CONFIG.read(os.path.join(os.path.dirname(__file__), 'script_config.ini'))
BASE_PATH = CONFIG['file_locations']['base_path']

DATA_RAW = os.path.join(BASE_PATH, 'raw')
DATA_INTERMEDIATE = os.path.join(BASE_PATH, 'intermediate')
DATA_PROCESSED = os.path.join(BASE_PATH, 'processed')


def test_func(population_threshold_km2):

    path = os.path.join(DATA_INTERMEDIATE, 'MWI', 'settlements.tif')

    with rasterio.open(path) as src:
        data = src.read()
        threshold = population_threshold_km2
        data[data < threshold] = 0
        data[data >= threshold] = 1
        shapes = rasterio.features.shapes(data, transform=src.transform)
        shapes_df = gpd.GeoDataFrame.from_features(
            [
                {'geometry': shape, 'properties':{'value':value}}
                for shape, value in shapes
                if value > 0
            ],
            crs='epsg:4326'
        )

    stats = zonal_stats(shapes_df['geometry'], path, stats=['count', 'sum'])

    stats_df = pd.DataFrame(stats)

    df = pd.concat([shapes_df, stats_df], axis=1).drop(columns='value')

    df = df[df['sum'] >= 20000]

    df.to_file(os.path.join(DATA_INTERMEDIATE, 'MWI', 'grid.shp'))


def design_network(nodes):

    links = []

    edges = []
    for node1_id, node1 in enumerate(nodes):
        for node2_id, node2 in enumerate(nodes):
            if node1_id != node2_id:
                geom1 = Point(node1['geometry']['coordinates'])
                geom2 = Point(node2['geometry']['coordinates'])
                line = LineString([geom1, geom2])
                edges.append({
                    'type': 'Feature',
                    'geometry': mapping(line),
                    'properties':{
                        'from': node1['properties']['OLO'],
                        'to':  node2['properties']['OLO'],
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

if __name__ == '__main__':

    population_density_threshold_km2 = 1000

    test_func(population_density_threshold_km2)

    # country_list = [
    #     # 'UGA',
    #     # 'ETH',
    #     # 'BGD',
    #     # 'PER',
    #     'MWI',
    #     # 'ZAF'
    # ]

    # for country in country_list:

    #     generate_grid(country, population_density_threshold_km2)

        # nodes = urban_areas()

        # links = design_network(nodes)
