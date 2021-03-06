"""
Generate data for modeling.

Written by Ed Oughton.

Winter 2020

"""
import os
import csv
import configparser
import pandas as pd
import geopandas
from tqdm import tqdm
from collections import OrderedDict

from options import OPTIONS, COUNTRY_PARAMETERS
from pytal.demand import estimate_demand
from pytal.supply import estimate_supply
from pytal.assess import assess
from write import define_deciles, write_mno_demand, write_results

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

    regions['geotype'] = regions.apply(define_geotype, axis=1)

    regions.columns = regions.columns.str.replace(
        'sites_estimated_total', #old column name
        'total_estimated_sites' #new column name
    )

    return regions


def define_geotype(x):
    """
    Allocate geotype given a specific population density.

    """
    if x['population_km2'] > 5000:
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
            generation = str(row["generation"])
            ci = str(row['confidence_interval'])

            if (environment, ant_type, frequency_GHz, generation, ci) \
                not in capacity_lookup_table:
                capacity_lookup_table[(
                    environment, ant_type, frequency_GHz, generation, ci)
                    ] = []

            capacity_lookup_table[(
                environment,
                ant_type,
                frequency_GHz,
                generation,
                ci)].append((
                    float(row["sites_per_km2"]),
                    float(row["capacity_mbps_km2"])
                ))

        for key, value_list in capacity_lookup_table.items():
            value_list.sort(key=lambda tup: tup[0])

    return capacity_lookup_table


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


def load_cluster(path, iso3):
    """
    Load cluster number. You need to make sure the
    R clustering script (pytal/vis/clustering/clustering.r)
    has been run first.

    """
    with open(path, 'r') as source:
        reader = csv.DictReader(source)
        for row in reader:
            if row['ISO_3digit'] == iso3:
                return row['cluster']


def load_penetration(path):
    """
    Load penetration forecast.

    """
    output = {}

    with open(path, 'r') as source:
        reader = csv.DictReader(source)
        for row in reader:
            output[int(row['year'])] = float(row['penetration'])

    return output


def load_smartphones(country, path):
    """
    Load phone types forecast. The function either uses the specific data
    for the country being modeled, or data from another country in the same
    cluster. If no data are present for the country of the cluster, it
    defaults to the mean values across all surveyed countries.

    """
    output = {}
    settlement_types = [
        'urban',
        'rural']

    for settlement_type in settlement_types:
        with open(path, 'r') as source:
            reader = csv.DictReader(source)
            intermediate = {}
            for row in reader:
                if settlement_type == row['settlement_type']:
                    intermediate[int(row['year'])] = float(row['penetration'])
            output[settlement_type] = intermediate

    return output


def load_core_lut(path):
    """

    """
    interim = []

    with open(path, 'r') as source:
        reader = csv.DictReader(source)
        for row in reader:
            interim.append({
                'GID_id': row['GID_id'],
                'asset': row['asset'],
                'source': row['source'],
                'value': int(round(float(row['value']))),
            })

    asset_types = [
        'core_edge',
        'core_node',
        'regional_edge',
        'regional_node'
    ]

    output = {}

    for asset_type in asset_types:
        asset_dict = {}
        for row in interim:
            if asset_type == row['asset']:
                combined_key = '{}_{}'.format(row['GID_id'], row['source'])
                asset_dict[combined_key] = row['value']
                output[asset_type] = asset_dict

    return output


def allocate_deciles(data):
    """
    Convert to pandas df, define deciles, and then return as a list of dicts.

    """
    data = pd.DataFrame(data)

    data = define_deciles(data)

    data = data.to_dict('records')

    return data


if __name__ == '__main__':

    BASE_YEAR = 2020
    END_YEAR = 2030
    TIMESTEP_INCREMENT = 1
    TIMESTEPS = [t for t in range(BASE_YEAR, END_YEAR + 1, TIMESTEP_INCREMENT)]

    COSTS = {
        #all costs in $USD
        'single_sector_antenna': 1500,
        'single_remote_radio_unit': 4000,
        'io_fronthaul': 1500,
        'processing': 1500,
        'io_s1_x2': 1500,
        'control_unit': 1500,
        'cooling_fans': 250,
        'distributed_power_supply_converter': 250,
        'power_generator_battery_system_4G': 5000,
        'power_generator_battery_system_5G': 15000,
        'bbu_cabinet': 500,
        'cots_processing': 500,
        'io_n2_n3': 1500,
        'low_latency_switch': 500,
        'rack': 500,
        'cloud_power_supply_converter': 1000,
        'tower': 5000,
        'civil_materials': 5000,
        'transportation': 5000,
        'installation': 5000,
        'site_rental_urban': 9600,
        'site_rental_suburban': 4000,
        'site_rental_rural': 1000,
        'router': 2000,
        'microwave_small': 30000,
        'microwave_medium': 40000,
        'microwave_large': 80000,
        'fiber_urban_m': 25,
        'fiber_suburban_m': 15,
        'fiber_rural_m': 5,
        'core_node_epc': 75000,
        'core_node_nsa': 75000,
        'core_node_sa': 250000,
        'core_edge': 5,
        'regional_node_epc': 40000,
        'regional_node_nsa': 40000,
        'regional_node_sa': 100000,
        'regional_edge': 5,
        'regional_node_lower_epc': 20000,
        'regional_node_lower_nsa': 20000,
        'regional_node_lower_sa': 100000,
        'power_4G': 5000,
        'power_5G': 10000,
    }

    GLOBAL_PARAMETERS = {
        'overbooking_factor': 20,
        'return_period': 10,
        'discount_rate': 5,
        'opex_percentage_of_capex': 10,
        'sectorization': 3,
        'confidence': [50], #[5, 50, 95],
        # 'networks': 3,
        'local_node_spacing_km2': 40,
        'io_n2_n3': 1,
        'cots_processing_split_urban': 2,
        'cots_processing_split_suburban': 4,
        'cots_processing_split_rural': 16,
        'io_n2_n3_split': 7,
        'low_latency_switch_split': 7,
        'rack_split': 7,
        'cloud_power_supply_converter_split': 7,
        'cloud_backhaul_split': 7,
        'tdd_dl_to_ul': '70:30'
        }

    path = os.path.join(DATA_RAW, 'pysim5g', 'capacity_lut_by_frequency.csv')
    capacity_lut = read_capacity_lookup(path)

    countries = [
        {'iso3': 'MWI', 'iso2': 'MW', 'regional_level': 2, 'regional_nodes_level': 2},
        {'iso3': 'UGA', 'iso2': 'UG', 'regional_level': 2, 'regional_nodes_level': 2},
        {'iso3': 'SEN', 'iso2': 'SN', 'regional_level': 2, 'regional_nodes_level': 2},
        {'iso3': 'KEN', 'iso2': 'KE', 'regional_level': 2, 'regional_nodes_level': 1},
        {'iso3': 'PAK', 'iso2': 'PK', 'regional_level': 3, 'regional_nodes_level': 2},
        {'iso3': 'ALB', 'iso2': 'AL', 'regional_level': 2, 'regional_nodes_level': 1},
        {'iso3': 'PER', 'iso2': 'PE', 'regional_level': 2, 'regional_nodes_level': 1},
        {'iso3': 'MEX', 'iso2': 'MX', 'regional_level': 3, 'regional_nodes_level': 1},
        ]

    decision_options = [
        'technology_options',
        'business_model_options',
        'policy_options',
        'mixed_options',
    ]

    all_results = []

    for decision_option in decision_options:#[:1]:

        options = OPTIONS[decision_option]#[:1]

        regional_annual_demand = []
        regional_results = []
        regional_cost_structure = []

        for country in countries:

            iso3 = country['iso3']

            country_parameters = COUNTRY_PARAMETERS[iso3]

            folder = os.path.join(BASE_PATH, '..', 'vis', 'clustering', 'results')
            filename = 'data_clustering_results.csv'
            country['cluster'] = load_cluster(os.path.join(folder, filename), iso3)

            folder = os.path.join(DATA_INTERMEDIATE, iso3, 'subscriptions')
            filename = 'subs_forecast.csv'
            penetration_lut = load_penetration(os.path.join(folder, filename))

            folder = os.path.join(DATA_INTERMEDIATE, iso3, 'smartphones')
            filename = 'smartphone_forecast.csv'
            smartphone_lut = load_smartphones(country, os.path.join(folder, filename))

            folder = os.path.join(DATA_INTERMEDIATE, iso3)
            filename = 'core_lut.csv'
            core_lut = load_core_lut(os.path.join(folder, filename))

            print('-----')
            print('Working on {} in {}'.format(decision_option, iso3))
            print('-----')

            for option in options:

                print('Assessing {} and {}'.format(option['scenario'], option['strategy']))

                confidence_intervals = GLOBAL_PARAMETERS['confidence']

                for ci in confidence_intervals:

                    # print('CI: {}'.format(ci))

                    path = os.path.join(DATA_INTERMEDIATE, iso3, 'regional_data.csv')
                    data = load_regions(path)

                    data_initial = data.to_dict('records')

                    data_demand, annual_demand = estimate_demand(
                        data_initial,
                        option,
                        GLOBAL_PARAMETERS,
                        country_parameters,
                        TIMESTEPS,
                        penetration_lut,
                        smartphone_lut
                    )

                    data_supply = estimate_supply(
                        country,
                        data_demand,
                        capacity_lut,
                        option,
                        GLOBAL_PARAMETERS,
                        country_parameters,
                        COSTS,
                        core_lut,
                        ci
                    )

                    data_assess = assess(
                        country,
                        data_supply,
                        option,
                        GLOBAL_PARAMETERS,
                        country_parameters,
                        TIMESTEPS,
                        COSTS
                    )

                    final_results = allocate_deciles(data_assess)

                    regional_annual_demand = regional_annual_demand + annual_demand
                    regional_results = regional_results + final_results

        folder = os.path.join(BASE_PATH, '..', 'results')
        path = os.path.join(folder, 'regional_annual_demand_{}.csv'.format(decision_option))
        write_mno_demand(regional_annual_demand, folder, decision_option, path)

        write_results(regional_results, folder, decision_option)

        all_results = all_results + regional_results

    folder = os.path.join(BASE_PATH, '..', 'results')
    write_results(all_results, folder, 'all_options')

    print('Completed model run')
