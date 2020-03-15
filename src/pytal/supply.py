"""
Optimize supply

Written by Ed Oughton.

Winter 2020

"""
from itertools import tee
from operator import itemgetter

from pytal.costs import find_single_network_cost


def estimate_supply(regions, lookup, option, global_parameters,
    country_parameters, costs):
    """
    For each region, optimize the network design and estimate
    the financial cost.

    Parameters
    ----------
    regions : dataframe
        Geopandas dataframe of all regions.
    lookup : dict
        A dictionary containing the lookup capacities.
    option : dict
        Contains the scenario, strategy, and frequencies
        with bandwidths.
    global_parameters : dict
        All global model parameters.
    country_parameters : dict
        All country specific parameters.
    costs : dict
        All equipment costs.

    """
    output = []

    confidence_intervals = global_parameters['confidence']

    for region in regions:

        network = optimize_network(region, option,
            global_parameters, country_parameters, costs, lookup)

        costs_by_site_densities = {}

        for item in network:

            costs_by_site_densities['site_density_{}'.format(
                item['confidence'])] = (item['site_density'])

            all_costs_km2 = find_single_network_cost(
                region,
                item['site_density'],
                option['strategy'],
                region['geotype'].split(' ')[0],
                costs,
                global_parameters,
                country_parameters,
            )

            costs_by_site_densities['spectrum'] = all_costs_km2['spectrum']

            costs_by_site_densities['cost_km2_{}'.format(item['confidence'])] = (
                all_costs_km2['total_deployment_costs_km2']
            )

            costs_by_site_densities['total_cost_{}'.format(item['confidence'])] = (
                all_costs_km2['total_deployment_costs_km2'] *
                region['area_km2']
            )

            # print(costs_by_site_densities)
            # region['viability'] = region['revenue'] - region['total_cost']

        # if region['phones']:
        #     region['cost_per_user'] = region['total_cost'] / region['phones']
        # else:
        #     region['cost_per_user'] = 0

        # if region['population'] > 0:
        #     region['cost_by_total_potential_users'] = (
        #         region['total_cost'] / region['population'])

        region_id = find_lowest_region(region)

        try:
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
                'population_with_phones': region['population_with_phones'],
                'phones_on_network': region['phones_on_network'],
                'population_with_smartphones': region['population_with_smartphones'],
                'smartphones_on_network': region['smartphones_on_network'],
                'revenue': region['revenue'],
                'revenue_km2': region['revenue_km2'],
                'demand_mbps_km2': region['demand_mbps_km2'],
                'site_density_{}'.format(confidence_intervals[0]): (
                    costs_by_site_densities['site_density_{}'.format(confidence_intervals[0])]
                ),
                'site_density_{}'.format(confidence_intervals[1]): (
                    costs_by_site_densities['site_density_{}'.format(confidence_intervals[1])]
                ),
                'site_density_{}'.format(confidence_intervals[2]): (
                    costs_by_site_densities['site_density_{}'.format(confidence_intervals[2])]
                ),
                'spectrum_total_cost_usd': costs_by_site_densities['spectrum'],
                'spectrum_total_cost_usd_km2': (
                    costs_by_site_densities['spectrum'] / region['area_km2']
                ),
                'cost_km2_{}'.format(confidence_intervals[0]): (
                    costs_by_site_densities['cost_km2_{}'.format(confidence_intervals[0])]
                ),
                'cost_km2_{}'.format(confidence_intervals[1]): (
                    costs_by_site_densities['cost_km2_{}'.format(confidence_intervals[1])]
                ),
                'cost_km2_{}'.format(confidence_intervals[2]): (
                    costs_by_site_densities['cost_km2_{}'.format(confidence_intervals[2])]
                ),
                'total_cost_{}'.format(confidence_intervals[0]): (
                    costs_by_site_densities['total_cost_{}'.format(confidence_intervals[0])]
                ),
                'total_cost_{}'.format(confidence_intervals[1]): (
                    costs_by_site_densities['total_cost_{}'.format(confidence_intervals[1])]
                ),
                'total_cost_{}'.format(confidence_intervals[2]): (
                    costs_by_site_densities['total_cost_{}'.format(confidence_intervals[2])]
                ),
                # 'viability': region['viability'],
                # 'cost_per_user': region['cost_per_user'],
                # 'cost_by_total_potential_users': region['cost_by_total_potential_users'],
            })

        except:
            pass
            # print('Could not write supply lut for the following region:')
            # print(region)

    return output


def optimize_network(region, option, global_parameters, country_parameters, costs, lookup):
    """
    For a given region, provide an optmized network.

    """
    confidence_intervals = global_parameters['confidence']

    networks = country_parameters['networks']
    demand = region['demand_mbps_km2']
    geotype = region['geotype'].split(' ')[0]
    ant_type = 'macro'

    generation, core, backhaul, sharing = get_strategy_options(option['strategy'])

    frequencies = country_parameters['frequencies']
    frequencies = frequencies[generation]

    frequencies = frequencies['{}_networks'.format(networks)]

    network = []

    capacity = 0

    for confidence_int in confidence_intervals:

        confidence_str = 'capacity_mbps_km2_{}ci'.format(confidence_int)

        for item in frequencies:

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

            max_density, max_capacities = density_capacities[-1]
            min_density, min_capacities = density_capacities[0]

            if demand > max_capacities[confidence_str]:
                network.append(
                    {
                        'frequency': str(frequency),
                        'bandwidth': str(bandwidth),
                        'geotype': geotype,
                        'demand': demand,
                        'site_density': max_density,
                        'confidence': confidence_int,
                    }
                )
                capacity += max_capacities[confidence_str]


            else:
                for a, b in pairwise(density_capacities):

                    lower_density, lower_capacities  = a
                    upper_density, upper_capacities  = b

                    if (lower_capacities[confidence_str] <= demand and
                        demand < upper_capacities[confidence_str]):

                        site_density = interpolate(
                            lower_capacities[confidence_str], lower_density,
                            upper_capacities[confidence_str], upper_density,
                            demand
                        )

                        network.append(
                            {
                                'frequency': str(frequency),
                                'bandwidth': str(bandwidth),
                                'geotype': geotype,
                                'demand': demand,
                                'site_density': site_density,
                                'confidence': confidence_int,
                            }
                        )
                        capacity += upper_capacities[confidence_str]

        if not len(network) >= 1:
            network.append(
                        {
                            'frequency': str(frequency),
                            'bandwidth': str(bandwidth),
                            'geotype': geotype,
                            'demand': demand,
                            'site_density': 0,
                            'confidence': confidence_int,
                        }
                    )

    return network


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


def find_lowest_region(region):
    """
    Find the lowest regional level being used based on the GADM data.

    """
    if 'GID_4' in region:
        return region['GID_4']
    elif 'GID_3' in region:
        return region['GID_3']
    elif 'GID_2' in region:
        return region['GID_2']
    elif 'GID_1' in region:
        return region['GID_1']


def get_strategy_options(strategy):
    """
    Take a single string containing all strategy components, and return
    each component as an individual string.

    """
    #strategy is 'generation_core_backhaul_sharing'
    generation = strategy.split('_')[0]
    core = strategy.split('_')[1]
    backhaul = strategy.split('_')[2]
    sharing = strategy.split('_')[3]

    return generation, core, backhaul, sharing


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
