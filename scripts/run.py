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


def load_backhaul_lut(country, path):
    """

    """
    level = country['regional_level']
    level = 'GID_{}'.format(level)

    output = {}

    with open(path, 'r') as source:
        reader = csv.DictReader(source)
        for row in reader:
            output[row[level]] = int(float(row['distance_m']))

    return output


def load_core_lut(country, path):
    """

    """
    level = country['regional_level']
    level = 'GID_{}'.format(level)

    interim = []

    with open(path, 'r') as source:
        reader = csv.DictReader(source)
        for row in reader:
            interim.append({
                'GID_id': row['GID_id'],
                'asset': row['asset'],
                'value': int(row['value']),
            })

    asset_types = [
        'core_edges',
        'core_nodes',
        'regional_edges',
        'regional_nodes'
    ]

    output = {}

    for asset_type in asset_types:
        asset_dict = {}
        for row in interim:
            if asset_type == row['asset']:
                asset_dict[row['GID_id']] = row['value']
                output[asset_type] = asset_dict

    return output


def write_results(regional_results, folder):
    """
    Write all results.

    """
    print('Writing national results')
    national_results = pd.DataFrame(regional_results)
    national_results = national_results[[
        'GID_0', 'scenario', 'strategy', 'confidence', 'population', 'area_km2',
        'sites_estimated_total', 'new_sites', 'upgraded_sites', 'total_revenue', 'total_cost'
    ]]

    national_results = national_results.groupby([
        'GID_0', 'scenario', 'strategy', 'confidence'], as_index=True).sum()

    path = os.path.join(folder,'national_results_{}.csv'.format(decision_option))
    national_results.to_csv(path,index=True)

    print('Writing decile results')
    decile_results = pd.DataFrame(regional_results)
    decile_results = decile_results[[
        'GID_0', 'scenario', 'strategy', 'decile', 'confidence', 'population', 'area_km2',
        'sites_estimated_total', 'new_sites', 'upgraded_sites','total_revenue', 'total_cost'
    ]]

    decile_results = decile_results.groupby([
        'GID_0', 'scenario', 'strategy', 'confidence', 'decile'], as_index=True).sum()

    path = os.path.join(folder,'decile_results_{}.csv'.format(decision_option))
    decile_results.to_csv(path, index=True)

    print('Writing regional results')
    regional_results = pd.DataFrame(regional_results)
    regional_results = regional_results[[
        'GID_0', 'scenario', 'strategy', 'decile', 'confidence', 'population', 'area_km2',
        'sites_estimated_total', 'new_sites', 'upgraded_sites', 'total_revenue', 'total_cost'
    ]]

    regional_results = regional_results.groupby([
        'GID_0', 'scenario', 'strategy', 'confidence', 'decile'], as_index=True).sum()

    path = os.path.join(folder,'regional_results_{}.csv'.format(decision_option))
    regional_results.to_csv(path, index=True)

    # print('Writing cost results')
    # costs_km2 = pd.DataFrame(costs_km2)
    # path = os.path.join(folder,'cost_results_{}.csv'.format(decision_option))
    # costs_km2.to_csv(path, index=False)


if __name__ == '__main__':

    BASE_YEAR = 2020
    END_YEAR = 2030
    TIMESTEP_INCREMENT = 1
    TIMESTEPS = [t for t in range(BASE_YEAR, END_YEAR + 1, TIMESTEP_INCREMENT)]

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
        'microwave_backhaul_small': 10000,
        'microwave_backhaul_medium': 20000,
        'microwave_backhaul_large': 40000,
        'fiber_backhaul_urban_m': 5,
        'fiber_backhaul_suburban_m': 5,
        'fiber_backhaul_rural_m': 5,
        'core_nodes_epc': 100000,
        'core_nodes_nsa': 150000,
        'core_nodes_sa': 200000,
        'core_edges': 20,
        'regional_nodes_epc': 100000,
        'regional_nodes_nsa': 150000,
        'regional_nodes_sa': 200000,
        'regional_edges': 10,
    }

    GLOBAL_PARAMETERS = {
        'overbooking_factor': 100,
        'return_period': 10,
        'discount_rate': 5,
        'opex_percentage_of_capex': 10,
        'sectorization': 3,
        'confidence': [50] #[5, 50, 95]
        }

    path = os.path.join(DATA_RAW, 'pysim5g', 'capacity_lut_by_frequency.csv')
    lookup = read_capacity_lookup(path)

    # countries, country_regional_levels = find_country_list(['Africa', 'South America'])

    countries = [
        {'iso3': 'BOL', 'iso2': 'BO', 'regional_level': 2, 'regional_hubs_level': 2},
        {'iso3': 'COD', 'iso2': 'CD', 'regional_level': 2, 'regional_hubs_level': 2},
        {'iso3': 'ETH', 'iso2': 'ET', 'regional_level': 3, 'regional_hubs_level': 2},
        {'iso3': 'GBR', 'iso2': 'GB', 'regional_level': 2, 'regional_hubs_level': 2},
        {'iso3': 'KEN', 'iso2': 'KE', 'regional_level': 2, 'regional_hubs_level': 2},
        {'iso3': 'MEX', 'iso2': 'MX', 'regional_level': 1, 'regional_hubs_level': 2},
        {'iso3': 'MWI', 'iso2': 'MW', 'regional_level': 2, 'regional_hubs_level': 1},
        {'iso3': 'PAK', 'iso2': 'SN', 'regional_level': 3, 'regional_hubs_level': 2},
        {'iso3': 'PER', 'iso2': 'PE', 'regional_level': 3, 'regional_hubs_level': 2},
        {'iso3': 'SEN', 'iso2': 'SN', 'regional_level': 2, 'regional_hubs_level': 2},
        {'iso3': 'TZA', 'iso2': 'TZ', 'regional_level': 2, 'regional_hubs_level': 1},
        {'iso3': 'UGA', 'iso2': 'UG', 'regional_level': 2, 'regional_hubs_level': 1},
        {'iso3': 'ZAF', 'iso2': 'ZA', 'regional_level': 2, 'regional_hubs_level': 2},
    ]

    decision_options = [
        'technology_options',
        # 'business_model_options'
    ]

    for decision_option in decision_options:

        options = OPTIONS[decision_option]

        regional_results = []

        for country in countries:

            iso3 = country['iso3']

            country_parameters = COUNTRY_PARAMETERS[iso3]

            folder = os.path.join(DATA_INTERMEDIATE, iso3, 'subscriptions')
            filename = 'subs_forecast.csv'
            penetration_lut = load_penetration(os.path.join(folder, filename))

            folder = os.path.join(DATA_INTERMEDIATE, iso3, 'backhaul')
            filename = 'backhaul_lut.csv'
            backhaul_lut = load_backhaul_lut(country, os.path.join(folder, filename))

            folder = os.path.join(DATA_INTERMEDIATE, iso3, 'core')
            filename = 'core_lut.csv'
            core_lut = load_core_lut(country, os.path.join(folder, filename))

            print('-----')
            print('Working on {} in {}'.format(decision_option, iso3))
            print(' ')

            for option in options:#[:1]:

                print('Working on {} and {}'.format(option['scenario'], option['strategy']))

                confidence_intervals = GLOBAL_PARAMETERS['confidence']

                for ci in confidence_intervals:

                    print('CI: {}'.format(ci))

                    path = os.path.join(DATA_INTERMEDIATE, iso3, 'regional_data.csv')
                    data = load_regions(path)#[:1]

                    data_initial = data.to_dict('records')

                    data_demand = estimate_demand(
                        data_initial,
                        option,
                        GLOBAL_PARAMETERS,
                        country_parameters,
                        TIMESTEPS,
                        penetration_lut
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

                    regional_results = regional_results + data_assess

        folder = os.path.join(BASE_PATH, '..', 'results')
        write_results(regional_results, folder)

        print('Completed model run')
