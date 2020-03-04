"""
Optimize supply

Written by Ed Oughton.

Winter 2020

"""
from itertools import tee

from costs import find_single_network_cost


def estimate_supply(regions, lookup, option, global_parameters, country_parameters, costs):
    """
    For each region, optimize the network design and estimate the financial cost.

    Parameters
    ----------
    regions : dataframe
        Geopandas dataframe of all regions.
    lookup : dict
        A dictionary containing the lookup capacities.
    option : dict
        Contains the scenario, strategy, and frequencies with bandwidths.
    global_parameters : dict
        All global model parameters.
    country_parameters : dict
        All country specific parameters.
    costs : dict
        All equipment costs.

    """
    output = []

    regions = regions.to_dict('records')

    for region in regions:

        network = optimize_network(region, option, country_parameters, costs, lookup)

        region['network'] = network[0][4]

        all_costs_km2 = find_single_network_cost(
            network[0][4],
            option['strategy'],
            region['geotype'].split(' ')[0],
            costs,
            global_parameters
        )

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


def optimize_network(region, option, parameters, costs, lookup):
    """
    For a given region, provide an optmized network.

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
