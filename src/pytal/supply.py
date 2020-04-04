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

        region = estimate_site_upgrades(region, strategy, total_sites_required, country_parameters)

        total_network_cost = find_single_network_cost(
            country,
            region,
            option['strategy'],
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

    generation = option['strategy'].split('_')[0]

    frequencies = country_parameters['frequencies']
    # frequencies = {
    #     '4G':[
    #         {
    #             'frequency': 800,
    #             'bandwidth': 10,
    #         },
    #         {
    #             'frequency': 2600,
    #             'bandwidth': 10,
    #         },
    #     ],
    #     '5G':[
    #         {
    #             'frequency': 700,
    #             'bandwidth': 10,
    #         },
    #         {
    #             'frequency': 3500,
    #             'bandwidth': 50,
    #         },
    #     ],
    # }
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


def estimate_site_upgrades(region, strategy, total_sites_required, country_parameters):
    """
    Estimate the number of greenfield sites and brownfield upgrades.

    Parameters
    ----------
    region : dict
        Contains all regional data.
    total_sites_required : int
        Number of sites needed to meet demand.
    country_parameters : dict
        All country specific parameters.

    Returns
    -------
    region : dict
        Contains all regional data.

    """
    generation = strategy.split('_')[0]

    existing_sites = (
        region['sites_estimated_total'] *
        (country_parameters['proportion_of_sites'] / 100)
    )

    if total_sites_required > existing_sites:

        region['new_sites'] = int(round(total_sites_required - existing_sites))

        if generation == '4G' and region['sites_4g'] > 0 :
            region['upgraded_sites'] = existing_sites - region['sites_4g']
        else:
            region['upgraded_sites'] = existing_sites

    else:
        region['new_sites'] = 0

        if generation == '4G' and region['sites_4g'] > 0 :
            region['upgraded_sites'] = total_sites_required - region['sites_4g']
        else:
            region['upgraded_sites'] = total_sites_required

    return region
