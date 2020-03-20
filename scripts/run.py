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


def aggregate_country_results(data_to_write):
    """
    Aggregate results for cross-country comparative insights.

    """
    output = []

    countries = set()
    scenarios =  set()
    strategies = set()
    confidence_ints = set()

    for item in data_to_write:
        countries.add(item['GID_0'])
        scenarios.add(item['scenario'])
        strategies.add(item['strategy'])
        confidence_ints.add(item['confidence'])

    for country in list(countries):
        for scenario in list(scenarios):
            for strategy in list(strategies):
                for ci in confidence_ints:

                    population = 0
                    area_km2 = 0
                    coverage_GSM_km2 = 0
                    coverage_3G_km2 = 0
                    coverage_4G_km2 = 0
                    sites_total = 0
                    pop_w_phones = 0
                    phones_on_net = 0
                    pop_w_sphones = 0
                    sphones_on_net = 0
                    total_revenue = 0
                    total_network_cost = 0
                    total_spectrum_cost = 0
                    total_profit = 0
                    total_tax = 0

                    for item in data_to_write:
                        if (
                            item['GID_0'] == country and
                            item['scenario'] == scenario and
                            item['strategy'] == strategy and
                            item['confidence'] == ci
                            ):

                            population += item['population']
                            area_km2 += item['area_km2']
                            coverage_GSM_km2 += item['coverage_GSM_km2']
                            coverage_3G_km2 += item['coverage_3G_km2']
                            coverage_4G_km2 += item['coverage_4G_km2']
                            sites_total += item['sites_total']
                            pop_w_phones += item['population_with_phones']
                            phones_on_net += item['phones_on_network']
                            pop_w_sphones += item['population_with_smartphones']
                            sphones_on_net += item['smartphones_on_network']
                            total_revenue += item['total_revenue']
                            total_network_cost += item['total_network_cost']
                            total_spectrum_cost += item['total_spectrum_cost']
                            total_profit += item['total_profit']
                            total_tax += item['total_tax']

                    output.append({
                        'country': country,
                        'scenario': scenario,
                        'strategy': strategy,
                        'confidence': ci,
                        'population_m': int(population / 1e6),
                        'area_km2_m': int(area_km2 / 1e6),
                        'coverage_GSM_perc': percentage(coverage_GSM_km2, area_km2),
                        'coverage_3G_perc': percentage(coverage_3G_km2, area_km2),
                        'coverage_4G_perc': percentage(coverage_4G_km2, area_km2),
                        'sites_total': int(sites_total),
                        'population_with_phones_perc': percentage(pop_w_phones, population),
                        'phones_on_network_perc': percentage(phones_on_net, population),
                        'pop_with_sphones_perc': percentage(pop_w_sphones, population),
                        'sphones_on_net_perc': percentage(sphones_on_net, population),
                        'total_revenue_bn': avoid_zeros(total_revenue / 1e9),
                        'total_network_cost_bn':  avoid_zeros(total_network_cost / 1e9),
                        'total_spectrum_cost_bn': avoid_zeros(total_spectrum_cost / 1e9),
                        'total_profit_bn':  avoid_zeros(total_profit / 1e9),
                        'total_tax_bn':  avoid_zeros(total_tax / 1e9),
                    })

    return output


def percentage(numerator, denominator):
    """
    Generic percentage function.

    """
    return int(round(numerator / denominator * 100))


def avoid_zeros(value):
    """
    Make value 0 if negative.

    """
    if value >= 0:
        return round(value, 1)
    else:
        return 0


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
        'microwave_backhaul_medium': 15000,
        'microwave_backhaul_large': 25000,
        'fiber_backhaul_urban': 20000,
        'fiber_backhaul_suburban': 35000,
        'fiber_backhaul_rural': 60000,
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
        {'iso3': 'MEX', 'iso2': 'MX', 'regional_level': 2, 'regional_hubs_level': 2},
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

        data_to_write = []

        for country in countries:

            iso3 = country['iso3']

            country_parameters = COUNTRY_PARAMETERS[iso3]

            folder = os.path.join(DATA_INTERMEDIATE, iso3, 'subscriptions')
            filename = 'subs_forecast.csv'
            penetration_lut = load_penetration(os.path.join(folder, filename))

            folder = os.path.join(DATA_INTERMEDIATE, iso3, 'backhaul')
            filename = 'backhaul.csv'
            backhaul_lut = load_backhaul_lut(country, os.path.join(folder, filename))

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
                        ci
                    )

                    data_assess = assess(
                        country,
                        data_supply,
                        option,
                        GLOBAL_PARAMETERS,
                        country_parameters,
                    )

                    data_to_write = data_to_write + data_assess

        path_results = os.path.join(BASE_PATH, '..', 'results')

        csv_writer(data_to_write, path_results, 'regional_results_{}_{}.csv'.format(
            decision_option, len(countries)))

        country_results = aggregate_country_results(data_to_write)

        csv_writer(country_results, path_results, 'country_results_{}_{}.csv'.format(
            decision_option, len(countries)))
