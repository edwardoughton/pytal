"""
Generate data for modeling.

Written by Ed Oughton.

Winter 2020

"""
import os
import csv
import configparser
import numpy as np
import pandas as pd
import geopandas
import pyproj
import fiona
from shapely.geometry import MultiPolygon, Polygon, mapping, box, shape
from shapely.ops import cascaded_union, transform
import rasterio
from rasterio.mask import mask
from rasterstats import zonal_stats
from tqdm import tqdm
from collections import OrderedDict
from rtree import index
from itertools import tee

CONFIG = configparser.ConfigParser()
CONFIG.read(os.path.join(os.path.dirname(__file__), 'script_config.ini'))
BASE_PATH = CONFIG['file_locations']['base_path']

DATA_RAW = os.path.join(BASE_PATH, 'raw')
DATA_INTERMEDIATE = os.path.join(BASE_PATH, 'intermediate')
DATA_PROCESSED = os.path.join(BASE_PATH, 'processed')


def load_regions(path):
    """
    Load country regions.

    """
    countries = []

    with fiona.open(path, 'r') as source:
        for item in source:
            countries.append(item)

    return countries


def get_density(geom, population, old_crs, new_crs):
    """
    Transform to epsg: 3859, get area, and find pop density.

    """
    project = pyproj.Transformer.from_proj(
        pyproj.Proj(old_crs), # source coordinate system
        pyproj.Proj(new_crs)) # destination coordinate system

    geom_transformed = transform(project.transform, geom)

    area_km2 = (geom_transformed.area / 1e6)

    return population / area_km2, area_km2


def query_data(regions, filepath_nl, filepath_lc, filepath_pop):
    """
    Query raster layer for each shape in regions.

    """
    shapes = []
    csv_data = []

    for region in tqdm(regions):

        geom = shape(region['geometry'])

        population = get_population(geom, filepath_pop)

        pop_density_km2, area_km2 = get_density(geom, population, 'epsg:4326', 'epsg:3857')

        shapes.append({
            'type': region['type'],
            'geometry': mapping(geom),
            # 'id': region['id'],
            'properties': {
                'population': population,
                'pop_density_km2': pop_density_km2,
                'area_km2': area_km2,
                'geotype': define_geotype(pop_density_km2),
                'GID_2': region['properties']['GID_2'],
                'GID_3': region['properties']['GID_3'],
            }
        })

        csv_data.append({
            'population': population,
            'pop_density_km2': pop_density_km2,
            'area_km2': area_km2,
            'geotype': define_geotype(pop_density_km2),
            'GID_2': region['properties']['GID_2'],
            'GID_3': region['properties']['GID_3'],
        })

    return shapes, csv_data


def get_population(geom, filepath_pop):
    """
    Get sum of population within geom.

    """
    population = zonal_stats(geom, filepath_pop, stats="sum", nodata=0)[0]['sum']

    try:
        if population >= 0:
            return population
        else:
            return 0
    except:
        return 0


def aggregate(shapes_lower, regions_upper):
    """
    Using zonal_stats on large areas can lead to a runtime warning due to an overflow.

    This function takes lower (smaller) regions and aggregates them into larger areas.

    """
    idx = index.Index()
    [idx.insert(0, shape(region['geometry']).bounds, region) for region in regions_upper]

    population_data = []

    for shape_lower in shapes_lower:
        for n in idx.intersection((shape(shape_lower['geometry']).bounds), objects=True):
            centroid = shape(shape_lower['geometry']).centroid
            upper_region_shape = shape(n.object['geometry'])
            if upper_region_shape.contains(centroid):
                population_data.append({
                    'population': shape_lower['properties']['population'],
                    'GID_2': n.object['properties']['GID_2'],
                    'GID_3': shape_lower['properties']['GID_3'],
                    })

    shapes = []
    csv_data = []

    for region in tqdm(regions_upper):

        region_id = region['properties']['GID_2']

        geom = shape(region['geometry'])

        population = aggregate_population(population_data, region_id)

        pop_density_km2, area_km2 = get_density(geom, population, 'epsg:4326', 'epsg:3857')

        shapes.append({
            'type': region['type'],
            'geometry': mapping(geom),
            'properties': {
                'population': population,
                'pop_density_km2': pop_density_km2,
                'area_km2': area_km2,
                'geotype': define_geotype(pop_density_km2),
                'GID_2': region['properties']['GID_2'],
            }
        })

        csv_data.append({
            'population': population,
            'pop_density_km2': pop_density_km2,
            'area_km2': area_km2,
            'geotype': define_geotype(pop_density_km2),
            'GID_2': region['properties']['GID_2'],
        })

    return shapes, csv_data


def aggregate_population(population_data, region_id):
    """
    Sum the population from lower level regions to
    upper level regions.

    """
    population = 0

    for item in population_data:
        if item['GID_2'] == region_id:
            population += item['population']

    return population


def define_geotype(pop_density_km2):
    """
    Allocate geotype given a specific population density.

    """
    if pop_density_km2 > 2000:
        return 'urban'
    elif pop_density_km2 > 1500:
        return 'suburban 1'
    elif pop_density_km2 > 1000:
        return 'suburban 2'
    elif pop_density_km2 > 500:
        return 'rural 1'
    elif pop_density_km2 > 100:
        return 'rural 2'
    elif pop_density_km2 > 50:
        return 'rural 3'
    elif pop_density_km2 > 10:
        return 'rural 4'
    else:
        return 'rural 5'


def read_lookup_table(path):
    """

    """
    capacity_lookup_table = {}

    with open(path, 'r') as capacity_lookup_file:
        reader = csv.DictReader(capacity_lookup_file)
        for row in reader:
            if float(row["capacity_mbps_km2"]) <= 0:
                continue
            environment = row["environment"].lower()
            ant_type = row["ant_type"]
            frequency_GHz = str(int(float(row["frequency_GHz"]) * 1e3))
            bandwidth_MHz = str(row["bandwidth_MHz"])
            generation = str(row["generation"])

            sites_per_km2 = float(row["sites_per_km2"])
            capacity_mbps_km2 = float(row["capacity_mbps_km2"])

            if (environment, ant_type, frequency_GHz, bandwidth_MHz, generation) \
                not in capacity_lookup_table:
                capacity_lookup_table[(
                    environment, ant_type, frequency_GHz, bandwidth_MHz, generation)
                    ] = []

            capacity_lookup_table[(
                environment, ant_type, frequency_GHz, bandwidth_MHz, generation
                )].append((
                    sites_per_km2, capacity_mbps_km2
                ))

        for key, value_list in capacity_lookup_table.items():
            value_list.sort(key=lambda tup: tup[0])

    return capacity_lookup_table


def estimate_results(regions, lookup, scenarios, strategies, parameters):
    """
    Function to estimate results.

    """
    output = []


    obf = parameters['overbooking_factor']

    for scenario in scenarios:

        for strategy in strategies:

            for region in regions:

                if not region['population'] > 0:

                    output.append({
                        'scenario': scenario,
                        'strategy': strategy,
                        'population': region['population'],
                        'pop_density_km2': region['pop_density_km2'],
                        'area_km2': region['area_km2'],
                        'geotype': region['geotype'],
                        'GID_2': region['GID_2'],
                        'GID_3': region['GID_3'],
                        'ant_type': 'no population',
                        'frequency': 'no population',
                        'bandwidth': 'no population',
                        'generation': 'no population',
                        'site_density_km2': 'no population',
                        'total_sites': 'no population',
                        'total_cost': 'NA',
                        'demand_km2': 'no population',
                    })

                    continue

                results = []

                user_demand = int(scenario.split('_')[1])

                demand = region['population'] * user_demand / obf / region['area_km2']

                ant_type = 'macro'
                spectrum = ['800', '2600']
                bandwidth = '10'
                generation = '4G'

                for frequency in spectrum:

                    density_capacities = lookup_capacity(
                        lookup,
                        region['geotype'].split(' ')[0].lower(),
                        ant_type,
                        frequency,
                        bandwidth,
                        generation,
                        )

                    for a, b in pairwise(density_capacities):

                        lower_density, lower_capacity = a
                        upper_density, upper_capacity = b

                        if lower_capacity <= demand and demand < upper_capacity:

                            optimal_density = interpolate(
                                lower_capacity, lower_density,
                                upper_capacity, upper_density,
                                demand
                            )

                            results.append((frequency, demand, optimal_density))

                    if len(results) > 0:
                        highest_density = max(results, key = lambda t: t[2])
                        frequency = highest_density[0]
                        site_density_km2 = highest_density[2]
                        total_sites = highest_density[2] * region['area_km2']
                        total_cost = total_sites * 250000

                    else:
                        print(region['population'], demand,
                            len(density_capacities), optimal_density)
                        frequency = 'cannot be achieved using 800MHz'
                        site_density_km2 = 'cannot be achieved using 800MHz'
                        total_sites = 'cannot be achieved using 800MHz'
                        total_cost = 'NA'

                    output.append({
                        'country': 'Malawi',
                        'scenario': scenario,
                        'strategy': strategy,
                        'population': region['population'],
                        'pop_density_km2': region['pop_density_km2'],
                        'area_km2': region['area_km2'],
                        'geotype': region['geotype'],
                        'GID_2': region['GID_2'],
                        'GID_3': region['GID_3'],
                        'ant_type': ant_type,
                        'frequency': frequency,
                        'bandwidth': bandwidth,
                        'generation': generation,
                        'site_density_km2': site_density_km2,
                        'total_sites': total_sites,
                        'total_cost': total_cost,
                        'demand_km2': demand,
                    })

    return output


def lookup_capacity(lookup, environment, ant_type, frequency, bandwidth, generation):
    """
    Use lookup table to find the combination of spectrum bands which meets capacity
    by clutter environment geotype, frequency, bandwidth, technology generation and
    site density.

    """
    if (environment, ant_type, frequency, bandwidth, generation) not in lookup:
        raise KeyError("Combination %s not found in lookup table",
                       (environment, ant_type, frequency, bandwidth, generation))

    density_capacities = lookup[
        (environment, ant_type,  frequency, bandwidth, generation)
    ]

    return density_capacities


def interpolate(x0, y0, x1, y1, x):
    """
    Linear interpolation between two values.

    """
    y = (y0 * (x1 - x) + y1 * (x - x0)) / (x1 - x0)

    return y


def pairwise(iterable):
    """
    Return iterable of 2-tuples in a sliding window.
    >>> list(pairwise([1,2,3,4]))
    [(1,2),(2,3),(3,4)]
    """
    a, b = tee(iterable)
    next(b, None)
    return zip(a, b)


def csv_writer(data, directory, filename):
    """
    Write data to a CSV file path.
    Parameters
    ----------
    data : list of dicts
        Data to be written.
    directory : string
        Path to export folder
    filename : string
        Desired filename.
    """
    # Create path
    if not os.path.exists(directory):
        os.makedirs(directory)

    fieldnames = []
    for name, value in data[0].items():
        fieldnames.append(name)

    with open(os.path.join(directory, filename), 'w') as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames, lineterminator = '\n')
        writer.writeheader()
        writer.writerows(data)


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


    SCENARIOS = ['S_1', 'S_2', 'S_3']
    STRATEGIES = ['scorched earth 1', 'scorched earth 2', 'scorched earth 3']
    PARAMETERS = {'overbooking_factor': 50}

    path = os.path.join(DATA_INTERMEDIATE, 'MWI', 'regions', 'regions_3_MWI.shp')
    regions_lower = load_regions(path)#[:10]

    filepath_nl = 'a'
    filepath_lc =  'b'
    filepath_pop = os.path.join(DATA_INTERMEDIATE, 'MWI', 'settlements.tif')

    shapes_lower, csv_data = query_data(regions_lower, filepath_nl, filepath_lc, filepath_pop)

    # path_results = os.path.join(BASE_PATH, '..', 'results')
    # csv_writer(csv_data, path_results, 'results_regions_3.csv')
    # write_shapefile(shapes_lower, path_results, 'results_regions_3.shp', 'epsg:4326')

    # path = os.path.join(DATA_INTERMEDIATE, 'MWI', 'regions', 'regions_2_MWI.shp')
    # regions_upper = load_regions(path)

    # shapes_upper, csv_data = aggregate(shapes_lower, regions_upper)

    # path_results = os.path.join(BASE_PATH, '..', 'results')
    # csv_writer(csv_data, path_results, 'results_regions_2.csv')
    # write_shapefile(shapes_upper, path_results, 'results_regions_2.shp', 'epsg:4326')

    path = os.path.join(DATA_RAW, 'pysim5g', 'capacity_lut_by_frequency_50.csv')
    lookup = read_lookup_table(path)
    print(len(csv_data))
    csv_data = estimate_results(csv_data, lookup, SCENARIOS, STRATEGIES, PARAMETERS)
    print(len(csv_data))
    path_results = os.path.join(BASE_PATH, '..', 'results')
    csv_writer(csv_data, path_results, 'results_with_density.csv')
