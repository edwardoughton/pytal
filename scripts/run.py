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
    cluster = country['cluster']
    iso3 = country['iso3']

    countries = set()

    with open(path, 'r') as source:
        reader = csv.DictReader(source)
        for row in reader:
            countries.add(row['iso3'])

    output = {}
    all_data = {
        'urban': [],
        'rural': []
    }

    with open(path, 'r') as source:
        reader = csv.DictReader(source)
        for row in reader:
            if iso3 in list(countries):
                if row['iso3'] == iso3:
                    iso3 = row['iso3']
                    settlement = row['Settlement'].lower()
                    output[settlement] = {
                        'basic': float(row['Basic']) / 100,
                        'feature': float(row['Feature']) / 100,
                        'smartphone': float(row['Smartphone']) / 100,
                    }
            elif row['cluster'] == cluster:
                settlement = row['Settlement'].lower()
                output[settlement] = {
                    'basic': float(row['Basic']) / 100,
                    'feature': float(row['Feature']) / 100,
                    'smartphone': float(row['Smartphone']) / 100,
                }
            else:
                settlement = row['Settlement'].lower()
                all_data[settlement].append(float(row['Smartphone']) / 100)

    if len(output) == 0:
        output = {
            'urban': {'smartphone': sum(all_data['urban']) / len(all_data['urban'])},
            'rural': {'smartphone': sum(all_data['rural']) / len(all_data['rural'])},
        }

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
                asset_dict[row['GID_id']] = row['value']
                output[asset_type] = asset_dict

    return output


def load_backhaul_lut(path):
    """
    Simulations show that for every 10x increase in node density,
    there is a 3.2x decrease in backhaul length.

    node_density_km2, average_distance_km, increase_in_density, decrease_in_distance
    0.000001, 606.0, 10, 3.2
    0.00001, 189.0, 10, 3.8
    0.0001, 50.0, 10, 3.1
    0.001, 16.0, 10, 3.2
    0.01, 5.0, 10, 3.2
    0.1, 1.6, 10, 3.2
    1.0, 0.5,

    """
    # output = []

    # with open(path, 'r') as source:
    #     reader = csv.DictReader(source)
    #     for row in reader:
    #         output.append({
    #             'node_density_km2': float(row['node_density_km2']),
    #             'average_distance_km': int(round(float(row['average_distance_km']))),
    #         })

    output = [
        {'node_density_km2': 0.00000001, 'average_distance_m': 5242880},
        {'node_density_km2': 0.0000001, 'average_distance_m': 1638400},
        {'node_density_km2': 0.000001, 'average_distance_m': 512000},
        {'node_density_km2': 0.00001, 'average_distance_m': 160000},
        {'node_density_km2': 0.0001, 'average_distance_m': 50000},
        {'node_density_km2': 0.001, 'average_distance_m': 16000},
        {'node_density_km2': 0.01, 'average_distance_m': 5000},
        {'node_density_km2': 0.1, 'average_distance_m': 1500},
        {'node_density_km2': 1.0,	'average_distance_m': 500},
    ]

    return output


def define_deciles(regions):

    regions = regions.sort_values(by='population_km2', ascending=True)

    regions['decile'] = regions.groupby([
        'GID_0', 'scenario', 'strategy', 'confidence'], as_index=True).population_km2.apply( #cost_per_sp_user
            pd.qcut, q=11, precision=0,
            labels=[100,90,80,70,60,50,40,30,20,10,0], duplicates='drop') # [0,10,20,30,40,50,60,70,80,90,100]

    return regions


def write_results(regional_results, folder, metric):
    """
    Write all results.

    """
    print('Writing national results')
    national_results = pd.DataFrame(regional_results)
    national_results = national_results[[
        'GID_0', 'scenario', 'strategy', 'confidence', 'population', 'area_km2',
        'population_km2', 'phones_on_network',
        'upgraded_sites', 'new_sites', 'total_revenue', 'total_cost',
    ]]

    national_results = national_results.groupby([
        'GID_0', 'scenario', 'strategy', 'confidence'], as_index=True).sum()
    national_results['cost_per_network_user'] = (
        national_results['total_cost'] / national_results['phones_on_network'])

    path = os.path.join(folder,'national_results_{}.csv'.format(metric))
    national_results.to_csv(path, index=True)

    print('Writing general decile results')
    decile_results = pd.DataFrame(regional_results)
    decile_results = define_deciles(decile_results)
    decile_results = decile_results[[
        'GID_0', 'scenario', 'strategy', 'decile', 'confidence', 'population', 'population_km2',
        'phones_on_network',
        'area_km2', 'upgraded_sites', 'new_sites', 'total_revenue', 'total_cost',
    ]]
    decile_results = decile_results.groupby([
        'GID_0', 'scenario', 'strategy', 'confidence', 'decile'], as_index=True).sum()
    decile_results['cost_per_network_user'] = (
        decile_results['total_cost'] / decile_results['phones_on_network'])

    path = os.path.join(folder,'decile_results_{}.csv'.format(metric))
    decile_results.to_csv(path, index=True)

    print('Writing cost decile results')
    decile_cost_results = pd.DataFrame(regional_results)
    decile_cost_results = define_deciles(decile_cost_results)
    decile_cost_results = decile_cost_results[[
        'GID_0', 'scenario', 'strategy', 'decile', 'confidence', 'population', 'population_km2',
        'phones_on_network',
        'total_revenue', 'ran', 'backhaul_fronthaul', 'civils', 'core_network',
        'spectrum_cost', 'tax', 'profit_margin', 'total_cost',
        'available_cross_subsidy', 'deficit', 'used_cross_subsidy',
        'required_state_subsidy',
    ]]

    decile_cost_results = decile_cost_results.groupby([
        'GID_0', 'scenario', 'strategy', 'confidence', 'decile'], as_index=True).sum()
    decile_cost_results['cost_per_network_user'] = (
        decile_cost_results['total_cost'] / decile_cost_results['phones_on_network'])

    path = os.path.join(folder,'decile_cost_results_{}.csv'.format(metric))
    decile_cost_results.to_csv(path, index=True)

    print('Writing regional results')
    regional_results = pd.DataFrame(regional_results)
    regional_results = define_deciles(regional_results)
    regional_results = regional_results[[
        'GID_0', 'scenario', 'strategy', 'decile',
        'confidence', 'population', 'area_km2',
        'population_km2', 'phones_on_network',
        'upgraded_sites','new_sites', 'total_revenue', 'total_cost',
    ]]
    regional_results['cost_per_network_user'] = (
        regional_results['total_cost'] / regional_results['phones_on_network'])

    path = os.path.join(folder,'regional_results_{}.csv'.format(metric))
    regional_results.to_csv(path, index=True)


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
        'power_generator_battery_system': 5000,
        'bbu_cabinet': 500,
        'fiber_fronthaul_urban_m': 10,
        'fiber_fronthaul_suburban_m': 5,
        'fiber_fronthaul_rural_m': 2,
        'cots_processing': 500,
        'io_n2_n3': 1500,
        'low_latency_switch': 500,
        'rack': 500,
        'cloud_power_supply_converter': 1000,
        'software': 50,
        'tower': 10000,
        'civil_materials': 5000,
        'transportation': 5000,
        'installation': 5000,
        'site_rental_urban': 9600,
        'site_rental_suburban': 4000,
        'site_rental_rural': 2000,
        'router': 2000,
        'microwave_backhaul_small': 5000,
        'microwave_backhaul_medium': 10000,
        'microwave_backhaul_large': 15000,
        'fiber_backhaul_urban_m': 25,
        'fiber_backhaul_suburban_m': 15,
        'fiber_backhaul_rural_m': 10,
        'core_node_epc': 50000,
        'core_node_nsa': 50000,
        'core_node_sa': 50000,
        'core_edge': 10,
        'regional_node_epc': 25000,
        'regional_node_nsa': 25000,
        'regional_node_sa': 100000,
        'regional_edge': 5,
        'regional_node_lower_epc': 5000,
        'regional_node_lower_nsa': 5000,
        'regional_node_lower_sa': 10000,
    }

    GLOBAL_PARAMETERS = {
        'overbooking_factor': 100,
        'return_period': 10,
        'discount_rate': 5,
        'opex_percentage_of_capex': 10,
        'sectorization': 3,
        'confidence': [50], #[5, 50, 95],
        'networks': 3,
        'io_n2_n3': 1,
        'cots_processing_split_urban': 2,
        'cots_processing_split_suburban': 4,
        'cots_processing_split_rural': 16,
        'io_n2_n3_split': 7,
        'low_latency_switch_split': 7,
        'rack_split': 7,
        'cloud_power_supply_converter_split': 7,
        'software_split': 7,
        'cloud_backhaul_split': 7,
        }

    path = os.path.join(DATA_RAW, 'pysim5g', 'capacity_lut_by_frequency.csv')
    lookup = read_capacity_lookup(path)

    # countries, country_regional_levels = find_country_list(['Africa', 'South America'])

    countries = [
        {'iso3': 'UGA', 'iso2': 'UG', 'regional_level': 2, 'regional_nodes_level': 2},
        {'iso3': 'MWI', 'iso2': 'MW', 'regional_level': 2, 'regional_nodes_level': 2},
        {'iso3': 'KEN', 'iso2': 'KE', 'regional_level': 2, 'regional_nodes_level': 1},
        {'iso3': 'SEN', 'iso2': 'SN', 'regional_level': 2, 'regional_nodes_level': 2},
        {'iso3': 'PAK', 'iso2': 'PK', 'regional_level': 3, 'regional_nodes_level': 2},
        {'iso3': 'ALB', 'iso2': 'AL', 'regional_level': 2, 'regional_nodes_level': 1},
        {'iso3': 'PER', 'iso2': 'PE', 'regional_level': 2, 'regional_nodes_level': 1},
        {'iso3': 'MEX', 'iso2': 'MX', 'regional_level': 2, 'regional_nodes_level': 1},
        ]

    decision_options = [
        'technology_options',
        'business_model_options',
        'policy_options'
    ]

    for decision_option in decision_options:#[:1]:

        options = OPTIONS[decision_option]

        regional_results = []
        regional_cost_structure = []

        for country in countries:#[:1]:

            iso3 = country['iso3']

            country_parameters = COUNTRY_PARAMETERS[iso3]

            folder = os.path.join(BASE_PATH, '..', 'vis', 'clustering', 'results')
            filename = 'data_clustering_results.csv'
            country['cluster'] = load_cluster(os.path.join(folder, filename), iso3)

            folder = os.path.join(DATA_INTERMEDIATE, iso3, 'subscriptions')
            filename = 'subs_forecast.csv'
            penetration_lut = load_penetration(os.path.join(folder, filename))

            folder = os.path.join(DATA_RAW, 'wb_smartphone_survey')
            filename = 'wb_smartphone_survey.csv'
            smartphone_lut = load_smartphones(country, os.path.join(folder, filename))

            folder = os.path.join(DATA_INTERMEDIATE, iso3)
            filename = 'core_lut.csv'
            core_lut = load_core_lut(os.path.join(folder, filename))

            folder = os.path.join(DATA_INTERMEDIATE)
            filename = 'backhaul_lut.csv'
            backhaul_lut = load_backhaul_lut(os.path.join(folder, filename))

            print('-----')
            print('Working on {} in {}'.format(decision_option, iso3))
            print(' ')

            for option in options:#[:3]:

                print('Working on {} and {}'.format(option['scenario'], option['strategy']))

                confidence_intervals = GLOBAL_PARAMETERS['confidence']

                for ci in confidence_intervals:

                    print('CI: {}'.format(ci))

                    path = os.path.join(DATA_INTERMEDIATE, iso3, 'regional_data.csv')
                    data = load_regions(path)

                    data_initial = data.to_dict('records')

                    data_demand = estimate_demand(
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
                        lookup,
                        option,
                        GLOBAL_PARAMETERS,
                        country_parameters,
                        COSTS,
                        backhaul_lut,
                        core_lut,
                        ci
                    )

                    data_assess = assess(
                        country,
                        data_supply,
                        option,
                        GLOBAL_PARAMETERS,
                        country_parameters,
                    )

                    final_results = allocate_deciles(data_assess)

                    regional_results = regional_results + final_results

        folder = os.path.join(BASE_PATH, '..', 'results')
        write_results(regional_results, folder, decision_option)

        print('Completed model run')
