"""
Cost module
Author: Edward Oughton
Date: April 2019

Based off the repo pysim5g:
https://github.com/edwardoughton/pysim5g

"""
import math

from utils import discount_capex_and_opex, discount_opex


def find_single_network_cost(region, sites_per_km2, strategy, geotype, costs,
    global_parameters, country_parameters):
    """
    Calculates the annual total cost using capex and opex.

    Parameters
    ----------
    region : ??
        ??
    sites_per_km2 : int
        The density of sites.
    strategy : str
        Infrastructure sharing strategy.
    costs : dict
        Contains the costs of each necessary equipment item.
    global_parameters : dict
        Contains all global_parameters.
    country_parameters :
        ???

    Returns
    -------
    output : list of dicts
        Contains a list of costs, with affliated discounted capex and
        opex costs.

    """
    generation, core, backhaul, sharing = get_strategy_options(strategy)

    cost_breakdown = get_costs(region, sharing, backhaul, geotype, costs, sites_per_km2,
        global_parameters, country_parameters)

    total_deployment_costs_km2 = 0
    for key, value in cost_breakdown.items():
        total_deployment_costs_km2 += value

    cost_breakdown['total_deployment_costs_km2'] = total_deployment_costs_km2

    return cost_breakdown


def get_costs(region, sharing, backhaul, geotype, costs, sites_per_km2,
    global_parameters, country_parameters):

    if sharing == 'baseline':
        costs = baseline(region, backhaul, geotype, costs, sites_per_km2,
            global_parameters, country_parameters)

    if sharing == 'passive':
        costs = passive(region, backhaul, geotype, costs, sites_per_km2,
            global_parameters, country_parameters)

    if sharing == 'active':
        costs = active(region, backhaul, geotype, costs, sites_per_km2,
            global_parameters, country_parameters)

    return costs


def baseline(region, backhaul, geotype, costs, sites_per_km2, global_parameters,
    country_parameters):
    """
    No sharing takes place.
    Reflects the baseline scenario of needing to build a single dedicated
    network.

    """
    backhaul_cost = get_backhaul_costs(backhaul, geotype, costs)

    cost_breakdown = {
        'single_sector_antenna': (
            discount_capex_and_opex(costs['single_sector_antenna'], global_parameters) *
            global_parameters['sectorization'] * sites_per_km2
        ),
        'single_remote_radio_unit': (
            discount_capex_and_opex(costs['single_remote_radio_unit'], global_parameters) *
            global_parameters['sectorization'] * sites_per_km2
        ),
        'single_baseband_unit': (
            discount_capex_and_opex(costs['single_baseband_unit'], global_parameters) *
            sites_per_km2
        ),
        'tower': (
            costs['tower'] * sites_per_km2
        ),
        'civil_materials': (
            costs['civil_materials'] * sites_per_km2
        ),
        'transportation': (
            costs['transportation'] * sites_per_km2
        ),
        'installation': (
            costs['installation'] * sites_per_km2
        ),
        'site_rental': (
            discount_opex(costs['site_rental'], global_parameters) * sites_per_km2
        ),
        'power_generator_battery_system': (
            discount_capex_and_opex(costs['power_generator_battery_system'], global_parameters) *
            sites_per_km2
        ),
        'high_speed_backhaul_hub': (
            discount_capex_and_opex(costs['high_speed_backhaul_hub'], global_parameters) *
            sites_per_km2
        ),
        'router': (
            discount_capex_and_opex(costs['router'], global_parameters) * sites_per_km2
        ),
        '{}_backhaul'.format(backhaul): (
            discount_capex_and_opex(backhaul_cost, global_parameters) * sites_per_km2
        ),
        'spectrum': get_spectrum_costs(region, country_parameters)
    }

    return cost_breakdown


def passive(region, backhaul, geotype, costs, sites_per_km2, global_parameters,
    country_parameters):
    """
    Sharing of:
        - Mast
        - Site compound

    """
    backhaul_cost = get_backhaul_costs(backhaul, geotype, costs)

    cost_breakdown = {
        'single_sector_antenna': (
            discount_capex_and_opex(costs['single_sector_antenna'], global_parameters) *
            global_parameters['sectorization'] * sites_per_km2
        ),
        'single_remote_radio_unit': (
            discount_capex_and_opex(costs['single_remote_radio_unit'], global_parameters) *
            global_parameters['sectorization'] * sites_per_km2
        ),
        'single_baseband_unit': (
            discount_capex_and_opex(costs['single_baseband_unit'], global_parameters) *
            sites_per_km2
        ),
        'tower': (
            costs['tower'] * sites_per_km2 / global_parameters['networks']
        ),
        'civil_materials': (
            costs['civil_materials'] * sites_per_km2 / global_parameters['networks']
        ),
        'transportation': (
            costs['transportation'] * sites_per_km2 / global_parameters['networks']
        ),
        'installation': (
            costs['installation'] * sites_per_km2 / global_parameters['networks']
        ),
        'site_rental': (
            discount_opex(costs['site_rental'], global_parameters) *
            sites_per_km2 / global_parameters['networks']
        ),
        'power_generator_battery_system': (
            discount_capex_and_opex(costs['power_generator_battery_system'], global_parameters) *
            sites_per_km2 / global_parameters['networks']
        ),
        'high_speed_backhaul_hub': (
            discount_capex_and_opex(costs['high_speed_backhaul_hub'], global_parameters) *
            sites_per_km2 / global_parameters['networks']
        ),
        'router': (
            discount_capex_and_opex(costs['router'], global_parameters) *
            sites_per_km2 / global_parameters['networks']
        ),
        '{}_backhaul'.format(backhaul): (
            discount_capex_and_opex(backhaul_cost, global_parameters) *
            sites_per_km2 / global_parameters['networks']
        ),
        'spectrum': get_spectrum_costs(region, country_parameters)
    }

    return cost_breakdown


def active(region, backhaul, geotype, costs, sites_per_km2, global_parameters,
    country_parameters):
    """
    Sharing of:
        - RAN
        - Mast
        - Site compound

    """
    backhaul_cost = get_backhaul_costs(backhaul, geotype, costs)

    cost_breakdown = {
        'single_sector_antenna': (
            discount_capex_and_opex(costs['single_sector_antenna'], global_parameters) *
            global_parameters['sectorization'] * sites_per_km2 /
            global_parameters['networks']
        ),
        'single_remote_radio_unit': (
            discount_capex_and_opex(costs['single_remote_radio_unit'], global_parameters) *
            global_parameters['sectorization'] * sites_per_km2 /
            global_parameters['networks']
        ),
        'single_baseband_unit': (
            discount_capex_and_opex(costs['single_baseband_unit'], global_parameters) *
            sites_per_km2 / global_parameters['networks']
        ),
        'tower': (
            costs['tower'] *
            sites_per_km2 / global_parameters['networks']
        ),
        'civil_materials': (
            costs['civil_materials'] *
            sites_per_km2 / global_parameters['networks']
        ),
        'transportation': (
            costs['transportation'] *
            sites_per_km2 / global_parameters['networks']
        ),
        'installation': (
            costs['installation'] *
            sites_per_km2 / global_parameters['networks']
        ),
        'site_rental': (
            discount_opex(costs['site_rental'], global_parameters) *
            sites_per_km2 / global_parameters['networks']
        ),
        'power_generator_battery_system': (
            discount_capex_and_opex(costs['power_generator_battery_system'], global_parameters) *
            sites_per_km2 / global_parameters['networks']
        ),
        'high_speed_backhaul_hub': (
            discount_capex_and_opex(costs['high_speed_backhaul_hub'], global_parameters) *
            sites_per_km2 / global_parameters['networks']
        ),
        'router': (
            discount_capex_and_opex(costs['router'], global_parameters) *
            sites_per_km2 / global_parameters['networks']
        ),
        '{}_backhaul'.format(backhaul): (
            discount_capex_and_opex(backhaul_cost, global_parameters) *
            sites_per_km2 / global_parameters['networks']
        ),
        'spectrum': get_spectrum_costs(region, country_parameters)
    }

    return cost_breakdown


def get_strategy_options(strategy):

    #strategy is 'generation_core_backhaul_sharing'
    generation = strategy.split('_')[0]
    core = strategy.split('_')[1]
    backhaul = strategy.split('_')[2]
    sharing = strategy.split('_')[3]

    return generation, core, backhaul, sharing


def get_backhaul_costs(backhaul, geotype, costs):
    """
    Calculate backhaul costs.

    """
    if backhaul == 'microwave':
        tech = '{}_backhaul_{}'.format(backhaul, geotype)
        cost = costs[tech]

    if backhaul == 'fiber':
        tech = '{}_backhaul_{}'.format(backhaul, geotype)
        cost = costs[tech]

    return cost


def get_spectrum_costs(region, country_parameters):
    """
    Calculate spectrum costs.

    """
    population = int(round(region['population']))
    frequencies = country_parameters['frequencies']
    networks = country_parameters['networks']
    frequencies = frequencies['{}_networks'.format(networks)]

    for frequency in frequencies:
        if frequency['frequency'] < 1000:
            cost_usd_mhz_pop = country_parameters['costs']['spectrum_coverage_usd_mhz_pop']
        else:
            cost_usd_mhz_pop = country_parameters['costs']['spectrum_capacity_usd_mhz_pop']

    cost = cost_usd_mhz_pop * frequency['bandwidth'] * population

    return cost
