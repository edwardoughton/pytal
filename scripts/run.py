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

from options import OPTIONS
from costs import find_single_network_cost

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
    regions = pd.read_csv(path)

    try:
        #[0,10,20,30,40,50,60,70,80,90,100] #labels=[100,90,80,70,60,50,40,30,20,10,0],
        regions['decile'] = pd.qcut(regions['population'], q=11, precision=0,
                            labels=[0,10,20,30,40,50,60,70,80,90,100], duplicates='drop')
    except:
        #[0,25,50,75,100] #labels=[100, 75, 50, 25, 0],
        regions['decile'] = pd.qcut(regions['population'], q=5, precision=0,
                            labels=[0,25,50,75,100], duplicates='drop')

    regions['geotype'] = regions.apply(define_geotype, axis=1)

    return regions


def define_geotype(x):
    """
    Allocate geotype given a specific population density.

    """
    if x['population_km2'] > 2000:
        return 'urban'
    elif x['population_km2'] > 1500:
        return 'suburban 1'
    elif x['population_km2'] > 1000:
        return 'suburban 2'
    elif x['population_km2'] > 500:
        return 'rural 1'
    elif x['population_km2'] > 100:
        return 'rural 2'
    elif x['population_km2'] > 50:
        return 'rural 3'
    elif x['population_km2'] > 10:
        return 'rural 4'
    else:
        return 'rural 5'


def estimate_demand(regions, option, parameters):
    """
    Estimate the total revenue based on current demand.

    arpu : int
        Average Revenue Per User for cellular per month.
    cell_penetration : float
        Number of cell phones per membeer of the population.
    phones : int
        Total number of phones in a region.
    return_period : int
        Total revenue based on 12 months and the specifies
        number of years as the return period (5).
    user_demand : float
        Total demand in mbps / km^2.

    """
    #economic demand
    #ARPU discounting really needs to be the same as the cost discounting
    regions['arpu'] = regions.apply(estimate_arpu, axis=1)

    regions['cell_pen'] = parameters['penetration']

    regions['phones'] =  (
        regions['population'] * regions['cell_pen'] / parameters['networks']
        )

    regions['revenue'] = (regions['arpu'] * regions['phones'])

    regions['revenue_km2'] = regions['revenue'] / regions['area_km2']

    #data demand
    obf = parameters['overbooking_factor']
    user_demand = option['scenario'].split('_')[1]
    regions['smartphone_pen'] = parameters['smartphone_pen']

    regions['demand_mbps_km2'] = (
        regions['population'] * regions['cell_pen'] * regions['smartphone_pen']
        / parameters['networks'] * int(user_demand) / obf / regions['area_km2']
        )

    return regions


def estimate_arpu(x):
    """
    Allocate consumption category given a specific luminosity.

    """
    arpu = 0
    if x['mean_luminosity_km2'] > 5:
        # #10 year time horizon
        # for i in range(0, 10):
        #     #discounted_arpu = (arpu*months) / (1 + discount_rate) ** year
        #     arpu += (
        #         (20*12) / (1 + 0.03) ** i
        #     )
        return 20 * 12 * 10#arpu
    elif x['mean_luminosity_km2'] > 1:
        # for i in range(0, 10):
        #     #discounted_arpu = (arpu*months) / (1 + discount_rate) ** year
        #     arpu += (
        #         (5*12) / (1 + 0.03) ** i
        #     )
        return 5 * 12 * 10#arpu
    else:
        # for i in range(0, 10):
        #     #discounted_arpu = (arpu*months) / (1 + discount_rate) ** year
        #     arpu += (
        #         (2*12) / (1 + 0.03) ** i
        #     )
        return 2 * 12 * 10#arpu


def estimate_phones(x):
    """
    Allocate consumption category given a specific luminosity.

    """
    if x['mean_luminosity_km2'] > 5:
        return 10
    elif x['mean_luminosity_km2'] > 1:
        return 5
    else:
        return 1


def read_capacity_lookup(path):
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


def estimate_supply(regions, lookup, option, parameters, costs):
    """

    """
    output = []

    regions = regions.to_dict('records')

    for region in regions:

        network = optimize_network(region, option, parameters, costs)

        region['network'] = network[0][4]

        all_costs_km2 = find_single_network_cost(
            network[0][4], option['strategy'], region['geotype'].split(' ')[0], costs, parameters)

        cost_km2 = all_costs_km2['total_deployment_costs_km2']

        region['total_cost'] = cost_km2 * region['area_km2'] #/ 1e6

        region['viability'] = region['revenue'] - region['total_cost']

        # if region['phones']:
        #     region['cost_per_user'] = region['total_cost'] / region['phones']
        # else:
        #     region['cost_per_user'] = 0

        # if region['population'] > 0:
        #     region['cost_by_total_potential_users'] = (
        #         region['total_cost'] / region['population'])
        # # print(region['cost_by_total_potential_users'])
        region_id = find_lowest_region(region)

        output.append({
            'country': region['GID_0'],
            'scenario': option['scenario'],
            'strategy': option['strategy'],
            'region_level': region_id,
            'population': region['population'],
            'area_km2': region['area_km2'],
            'population_km2': region['population_km2'],
            'mean_luminosity_km2': region['mean_luminosity_km2'],
            'geotype': region['geotype'],
            'decile': region['decile'],
            'arpu': region['arpu'],
            'phones': region['phones'],
            'revenue': region['revenue'],
            # 'revenue_km2': region['revenue_km2'],
            # 'demand_mbps_km2': region['demand_mbps_km2'],
            # 'network': region['network'],
            # 'cost_km2': cost_km2,
            'total_cost': region['total_cost'],
            'viability': region['viability'],
            # 'cost_per_user': region['cost_per_user'],
            # 'cost_by_total_potential_users': region['cost_by_total_potential_users'],
        })

    return output


def find_lowest_region(region):

    if 'GID_4' in region:
        return region['GID_4']
    elif 'GID_3' in region:
        return region['GID_3']
    elif 'GID_2' in region:
        return region['GID_2']
    elif 'GID_1' in region:
        return region['GID_1']


def optimize_network(region, option, parameters, costs):
    """

    """
    demand = region['demand_mbps_km2']
    geotype = region['geotype'].split(' ')[0]
    ant_type = 'macro'
    frequencies = option['frequencies']

    generation, core, backhaul, sharing = get_strategy_options(option['strategy'])

    networks = parameters['networks']

    network = []

    capacity = 0

    for item in frequencies:

        if capacity > demand:
            break

        frequency = str(item['frequency'])
        bandwidth = str(item['bandwidth'])

        density_capacities = lookup_capacity(
            lookup,
            geotype,
            ant_type,
            frequency,
            bandwidth,
            generation,
            )

        bandwidth = str(int(float(bandwidth) * round(4 / networks, 1)))

        max_density, max_capacity = density_capacities[-1]

        if demand > max_capacity:
            network.append((str(frequency), str(bandwidth), geotype, demand, max_density))
            capacity += max_capacity

        for a, b in pairwise(density_capacities):

            lower_density, lower_capacity  = a
            upper_density, upper_capacity  = b

            #networks takes into account how spectrum is shared across networks
            lower_capacity = lower_capacity * (4 / networks)
            upper_capacity = upper_capacity * (4 / networks)

            if lower_capacity <= demand and demand < upper_capacity:

                optimal_density = interpolate(
                    lower_capacity, lower_density,
                    upper_capacity, upper_density,
                    demand
                )

                network.append((str(frequency), str(bandwidth), geotype, demand, optimal_density))
                capacity += upper_capacity

    if not len(network) > 1:
        network.append((str(frequency), str(bandwidth), geotype, demand, 0))

    return network


def get_strategy_options(strategy):

    #strategy is 'generation_core_backhaul_sharing'
    generation = strategy.split('_')[0]
    core = strategy.split('_')[1]
    backhaul = strategy.split('_')[2]
    sharing = strategy.split('_')[3]

    return generation, core, backhaul, sharing


def lookup_cost(lookup, strategy, environment):
    """
    Find cost of network.

    """
    if (strategy, environment) not in lookup:
        raise KeyError("Combination %s not found in lookup table",
                       (strategy, environment))

    density_capacities = lookup[
        (strategy, environment)
    ]

    return density_capacities


def lookup_capacity(lookup, environment, ant_type, frequency,
    bandwidth, generation):
    """
    Use lookup table to find the combination of spectrum bands
    which meets capacity by clutter environment geotype, frequency,
    bandwidth, technology generation and site density.

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


def find_country_list(continent_list):
    """

    """
    path_processed = os.path.join(DATA_INTERMEDIATE,'global_countries.shp')
    countries = geopandas.read_file(path_processed)

    subset = countries.loc[countries['continent'].isin(continent_list)]

    country_list = []
    country_regional_levels = []

    for name in subset.GID_0.unique():

        country_list.append(name)

        if name in ['ESH', 'LBY', 'LSO'] :
            regional_level =  1
        else:
            regional_level = 2

        country_regional_levels.append({
            'country': name,
            'regional_level': regional_level,
        })

    return country_list, country_regional_levels


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

    COSTS = {
        #all costs in $USD
        'single_sector_antenna': 1500,
        'single_remote_radio_unit': 4000,
        'single_baseband_unit': 10000,
        'tower': 10000,
        'civil_materials': 5000,
        'transportation': 10000,
        'installation': 5000,
        'site_rental': 9600,
        'power_generator_battery_system': 5000,
        'high_speed_backhaul_hub': 15000,
        'router': 2000,
        'microwave_backhaul_urban': 10000,
        'microwave_backhaul_suburban': 15000,
        'microwave_backhaul_rural': 25000,
        'fiber_backhaul_urban': 20000,
        'fiber_backhaul_suburban': 35000,
        'fiber_backhaul_rural': 60000,
    }

    PARAMETERS = {
        'overbooking_factor': 50,
        'penetration': 0.3,
        'smartphone_pen': 0.15,
        'networks': 2,
        'return_period': 10,
        'discount_rate': 3,
        'opex_percentage_of_capex': 10,
        'sectorization': 3,
        }

    path = os.path.join(DATA_RAW, 'pysim5g', 'capacity_lut_by_frequency_50.csv')
    lookup = read_capacity_lookup(path)

    # country_list, country_regional_levels = find_country_list(['Africa', 'South America'])
    country_list = ['UGA', 'ETH', 'BGD', 'PER', 'MWI', 'ZAF']

    decision_options = [
        'technology_options',
        'business_model_options'
    ]

    for decision_option in decision_options:

        options = OPTIONS[decision_option]

        data_to_write = []

        for country in country_list:

            # if not country == 'ESH':
            #     continue

            print('-----')
            print('Working on {} in {}'.format(decision_option, country))
            print(' ')

            for option in options:

                print('Working on {} and {}'.format(option['scenario'], option['strategy']))

                try:
                    path = os.path.join(DATA_INTERMEDIATE, country, 'regional_data.csv')
                    data = load_regions(path)#[:100]

                    data = estimate_demand(data, option, PARAMETERS)

                    data = estimate_supply(data, lookup, option, PARAMETERS, COSTS)

                    data_to_write = data_to_write + data

                except:
                    print('Unable to process {} for {} and {}'.format(
                        country, option['scenario'], option['strategy']))
                    pass

        path_results = os.path.join(BASE_PATH, '..', 'results')

        csv_writer(data_to_write, path_results, 'results_{}_{}.csv'.format(
            decision_option, len(country_list)))
