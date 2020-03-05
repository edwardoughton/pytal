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


def generate_grid(country):
    """
    Generate a 10x10km spatial grid for the chosen country.

    """
    filename = 'national_outline.shp'
    country_outline = gpd.read_file(os.path.join(DATA_INTERMEDIATE, country, filename))

    country_outline.crs = "epsg:4326"
    country_outline = country_outline.to_crs("epsg:3857")

    xmin,ymin,xmax,ymax = country_outline.total_bounds

    #10km sides, leading to 100km^2 area
    length = 1e5
    wide = 1e5

    cols = list(range(int(np.floor(xmin)), int(np.ceil(xmax)), int(wide)))
    rows = list(range(int(np.floor(ymin)), int(np.ceil(ymax)), int(length)))
    rows.reverse()

    polygons = []
    for x in cols:
        for y in rows:
            # print(x, y)
            # polygons.append(Point(x, y))
            polygons.append(Polygon([(x,y), (x+wide, y), (x+wide, y-length), (x, y-length)]))

    grid = gpd.GeoDataFrame({'geometry': polygons})
    intersection = gpd.overlay(grid, country_outline, how='intersection')
    intersection.crs = "epsg:3857"
    intersection = intersection.to_crs("epsg:4326")

    final_grid = query_settlement_layer(intersection)

    final_grid = final_grid[final_grid.geometry.notnull()]

    points = final_grid.to_dict('records')

    to_cluster = []

    for point in points:
        to_cluster.append({
            'type': 'Point',
            'geometry': mapping(point['geometry'].representative_point()),
            'properties': {
                'population': point['population'],
            }
        })

    points = np.vstack([[float(i) for i in point['geometry']['coordinates']] for point in to_cluster])

    db = DBSCAN(eps=1, min_samples=1).fit(points)
    core_samples_mask = np.zeros_like(db.labels_, dtype=bool)
    core_samples_mask[db.core_sample_indices_] = True
    labels = db.labels_
    n_clusters_ = len(set(labels)) - (1 if -1 in labels else 0)
    clusters = [points[labels == i] for i in range(n_clusters_)]

    agglomerations = []
    for idx, cluster in enumerate(clusters):
        geom = MultiPoint(cluster)
        rep_point = geom.representative_point()
        agglomerations.append({
                'type': "Feature",
                'geometry': {
                    "type": "Point",
                    "coordinates": [rep_point.x, rep_point.y]
                },
                'properties': {
                }
            })

    final_grid = gpd.GeoDataFrame([i['geometry'] for i in agglomerations])
    final_grid.to_file(os.path.join(DATA_INTERMEDIATE, country, 'grid.shp'))

    print('Completed grid generation process')


def query_settlement_layer(grid):
    """
    Query the settlement layer to get an estimated population for each grid square.

    """
    path = os.path.join(DATA_INTERMEDIATE, country, 'settlements.tif')

    grid['population'] = pd.DataFrame(
        zonal_stats(vectors=grid['geometry'], raster=path, stats='sum'))['sum']

    grid = grid.replace([np.inf, -np.inf], np.nan)

    return grid


if __name__ == '__main__':

    country_list = [
        # 'UGA',
        # 'ETH',
        # 'BGD',
        # 'PER',
        'MWI',
        # 'ZAF'
    ]

    for country in country_list:

        generate_grid(country)
