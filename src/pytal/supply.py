"""
Optimize supply

Written by Ed Oughton.

Winter 2020

"""
from itertools import tee
from operator import itemgetter

from pytal.costs import find_single_network_cost


def estimate_supply(country, regions, lookup, option, global_parameters,
    country_parameters, costs, backhaul_lut, core_lut, ci):
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
    backhaul_lut : dict
        Backhaul distance by region.
    core_lut : ???
        ???
    ci : int
        Confidence interval.

    """
    output_regions = []

    for region in regions:

        site_density = find_site_density(region, option,
            country_parameters, lookup, ci)

        total_sites_required = site_density * region['area_km2']

        if total_sites_required > region['sites_estimated_total']:
            region['new_sites'] = int(round(total_sites_required - region['sites_estimated_total']))
            region['upgraded_sites'] = int(round(region['sites_estimated_total']))
        else:
            region['new_sites'] = 0
            region['upgraded_sites'] = int(round(total_sites_required))

        total_network_cost = find_single_network_cost(
            country,
            region,
            option['strategy'],
            region['geotype'].split(' ')[0],
            costs,
            global_parameters,
            country_parameters,
            backhaul_lut,
            core_lut
        )

        region['scenario'] = option['scenario']
        region['strategy'] = option['strategy']
        region['confidence'] = ci
        region['site_density'] = site_density
        region['total_network_cost'] = total_network_cost
        # print('----total network cost {}'.format(total_network_cost))
        output_regions.append(region)

        # for cost_result in cost_results:
        #     cost_result['GID_0'] = iso3
        #     cost_result['GID_id'] = region['GID_id']
        #     output_costs.append(cost_result)

    return output_regions#, output_costs


def find_site_density(region, option, country_parameters, lookup, ci):
    """
    For a given region, provide an optmized network.

    """
    networks = country_parameters['networks']
    demand = region['demand_mbps_km2']
    geotype = region['geotype'].split(' ')[0]
    ant_type = 'macro'

    generation, core, backhaul, sharing = get_strategy_options(option['strategy'])

    frequencies = country_parameters['frequencies']
    frequencies = frequencies[generation]

    ci = str(ci)

    unique_densities = set()

    capacity = 0

    for item in frequencies:

        frequency = str(item['frequency'])
        bandwidth = float(item['bandwidth'])

        density_capacities = lookup_capacity(
            lookup,
            geotype,
            ant_type,
            frequency,
            generation,
            ci
            )

        for item in density_capacities:
            site_density, capacity = item
            unique_densities.add(site_density)

    density_lut = []

    for density in list(unique_densities):
        capacity = 0
        for item in frequencies:

            frequency = str(item['frequency'])
            bandwidth = float(item['bandwidth'])

            density_capacities = lookup_capacity(
                lookup,
                geotype,
                ant_type,
                frequency,
                generation,
                ci
            )

            for density_capacity in density_capacities:

                if density_capacity[0] == density:
                    capacity += density_capacity[1]

        density_lut.append((density, capacity))

    density_lut = sorted(density_lut, key=lambda tup: tup[0])
    # print(density_lut)
    max_density, max_capacity = density_lut[-1]
    min_density, min_capacity = density_lut[0]

    max_capacity = max_capacity * bandwidth
    min_capacity = min_capacity * bandwidth

    if demand > max_capacity:

        return max_density

    elif demand < min_capacity:

        return min_density

    else:

        for a, b in pairwise(density_lut):

            lower_density, lower_capacity  = a
            upper_density, upper_capacity  = b

            lower_capacity = lower_capacity * bandwidth
            upper_capacity = upper_capacity * bandwidth

            if lower_capacity <= demand < upper_capacity:

                site_density = interpolate(
                    lower_capacity, lower_density,
                    upper_capacity, upper_density,
                    demand
                )
                return site_density


def lookup_capacity(lookup, environment, ant_type, frequency,
    generation, ci):
    """
    Use lookup table to find the combination of spectrum bands
    which meets capacity by clutter environment geotype, frequency,
    bandwidth, technology generation and site density.

    """
    if (environment, ant_type, frequency, generation, ci) not in lookup:
        raise KeyError("Combination %s not found in lookup table",
                       (environment, ant_type, frequency, generation, ci))

    density_capacities = lookup[
        (environment, ant_type,  frequency, generation, ci)
    ]

    return density_capacities


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
