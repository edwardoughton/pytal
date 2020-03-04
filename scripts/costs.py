"""
Cost module
Author: Edward Oughton
Date: April 2019

Based off the repo pysim5g:
https://github.com/edwardoughton/pysim5g

"""
import math

from utils import discount_capex_and_opex, discount_opex


def find_single_network_cost(sites_per_km2, strategy, geotype, costs, parameters):
    """
    Calculates the annual total cost using capex and opex.

    Parameters
    ----------
    sites_per_km2 : int
        The density of sites.
    strategy : str
        Infrastructure sharing strategy.
    costs : dict
        Contains the costs of each necessary equipment item.
    parameters : dict
        Contains all parameters.

    Returns
    -------
    output : list of dicts
        Contains a list of costs, with affliated discounted capex and opex costs.

    """
    generation, core, backhaul, sharing = get_strategy_options(strategy)

    cost_breakdown = get_costs(sharing, backhaul, geotype, costs, sites_per_km2, parameters)

    total_deployment_costs_km2 = 0
    for key, value in cost_breakdown.items():
        total_deployment_costs_km2 += value

    cost_breakdown['total_deployment_costs_km2'] = total_deployment_costs_km2

    return cost_breakdown


def get_costs(sharing, backhaul, geotype, costs, sites_per_km2, parameters):

    if sharing == 'baseline':
        costs = baseline(backhaul, geotype, costs, sites_per_km2, parameters)
    if sharing == 'passive':
        costs = passive(backhaul, geotype, costs, sites_per_km2, parameters)
    if sharing == 'active':
        costs = active(backhaul, geotype, costs, sites_per_km2, parameters)

    return costs


def baseline(backhaul, geotype, costs, sites_per_km2, parameters):
    """
    No sharing takes place.
    Reflects the baseline scenario of needing to build a single dedicated network.

    """
    backhaul_cost = get_backhaul_costs(backhaul, geotype, costs)

    cost_breakdown = {
        'single_sector_antenna': (
            discount_capex_and_opex(costs['single_sector_antenna'], parameters) *
            parameters['sectorization'] * sites_per_km2
        ),
        'single_remote_radio_unit': (
            discount_capex_and_opex(costs['single_remote_radio_unit'], parameters) *
            parameters['sectorization'] * sites_per_km2
        ),
        'single_baseband_unit': (
            discount_capex_and_opex(costs['single_baseband_unit'], parameters) *
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
            discount_opex(costs['site_rental'], parameters) * sites_per_km2
        ),
        'power_generator_battery_system': (
            discount_capex_and_opex(costs['power_generator_battery_system'], parameters) *
            sites_per_km2
        ),
        'high_speed_backhaul_hub': (
            discount_capex_and_opex(costs['high_speed_backhaul_hub'], parameters) *
            sites_per_km2
        ),
        'router': (
            discount_capex_and_opex(costs['router'], parameters) * sites_per_km2
        ),
        '{}_backhaul'.format(backhaul): (
            discount_capex_and_opex(backhaul_cost, parameters) * sites_per_km2
        )
    }

    return cost_breakdown


def passive(backhaul, geotype, costs, sites_per_km2, parameters):
    """
    Sharing of:
        - Mast
        - Site compound

    """
    backhaul_cost = get_backhaul_costs(backhaul, geotype, costs)

    cost_breakdown = {
        'single_sector_antenna': (
            discount(costs['single_sector_antenna'], parameters, 1) *
            parameters['sectorization'] * sites_per_km2
        ),
        'single_remote_radio_unit': (
            discount(costs['single_remote_radio_unit'], parameters, 1) *
            parameters['sectorization'] * sites_per_km2
        ),
        'single_baseband_unit': (
            discount(costs['single_baseband_unit'], parameters, 1) *
            sites_per_km2
        ),
        'tower': (
            costs['tower'] * sites_per_km2 / parameters['networks']
        ),
        'civil_materials': (
            costs['civil_materials'] * sites_per_km2 / parameters['networks']
        ),
        'transportation': (
            costs['transportation'] * sites_per_km2 / parameters['networks']
        ),
        'installation': (
            costs['installation'] * sites_per_km2 / parameters['networks']
        ),
        'site_rental': (
            discount(costs['site_rental'], parameters, 0) *
            sites_per_km2 / parameters['networks']
        ),
        'power_generator_battery_system': (
            discount(costs['power_generator_battery_system'], parameters, 1) *
            sites_per_km2 / parameters['networks']
        ),
        'high_speed_backhaul_hub': (
            discount(costs['high_speed_backhaul_hub'], parameters, 1) *
            sites_per_km2 / parameters['networks']
        ),
        'router': (
            discount(costs['router'], parameters, 1) *
            sites_per_km2 / parameters['networks']
        ),
        '{}_backhaul'.format(backhaul): (
            discount(backhaul_cost, parameters, 1) *
            sites_per_km2 / parameters['networks']
        )
    }

    return cost_breakdown


def active(backhaul, geotype, costs, sites_per_km2, parameters):
    """
    Sharing of:
        - RAN
        - Mast
        - Site compound

    """
    backhaul_cost = get_backhaul_costs(backhaul, geotype, costs)

    cost_breakdown = {
        'single_sector_antenna': (
            discount(costs['single_sector_antenna'], parameters, 1) *
            parameters['sectorization'] * sites_per_km2 /
            parameters['networks']
        ),
        'single_remote_radio_unit': (
            discount(costs['single_remote_radio_unit'], parameters, 1) *
            parameters['sectorization'] * sites_per_km2 /
            parameters['networks']
        ),
        'single_baseband_unit': (
            discount(costs['single_baseband_unit'], parameters, 1) *
            sites_per_km2 / parameters['networks']
        ),
        'tower': (
            costs['tower'] *
            sites_per_km2 / parameters['networks']
        ),
        'civil_materials': (
            costs['civil_materials'] *
            sites_per_km2 / parameters['networks']
        ),
        'transportation': (
            costs['transportation'] *
            sites_per_km2 / parameters['networks']
        ),
        'installation': (
            costs['installation'] *
            sites_per_km2 / parameters['networks']
        ),
        'site_rental': (
            discount(costs['site_rental'], parameters, 0) *
            sites_per_km2 / parameters['networks']
        ),
        'power_generator_battery_system': (
            discount(costs['power_generator_battery_system'], parameters, 1) *
            sites_per_km2 / parameters['networks']
        ),
        'high_speed_backhaul_hub': (
            discount(costs['high_speed_backhaul_hub'], parameters, 1) *
            sites_per_km2 / parameters['networks']
        ),
        'router': (
            discount(costs['router'], parameters, 1) *
            sites_per_km2 / parameters['networks']
        ),
        '{}_backhaul'.format(backhaul): (
            discount(backhaul_cost, parameters, 1) *
            sites_per_km2 / parameters['networks']
        )
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

    if backhaul == 'microwave':
        tech = '{}_backhaul_{}'.format(backhaul, geotype)
        cost = costs[tech]

    if backhaul == 'fiber':
        tech = '{}_backhaul_{}'.format(backhaul, geotype)
        cost = costs[tech]

    return cost
