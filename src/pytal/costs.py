"""
Cost module
Author: Edward Oughton
Date: April 2019

Based off the repo pysim5g:
https://github.com/edwardoughton/pysim5g

"""
import math


def find_single_network_cost(country, region, strategy,
    costs, global_parameters, country_parameters, backhaul_lut, core_lut):
    """
    Calculates the annual total cost using capex and opex.

    Parameters
    ----------
    region : dict
        The region being assessed and all associated parameters.
    strategy : str
        Infrastructure sharing strategy.
    costs : dict
        Contains the costs of each necessary equipment item.
    global_parameters : dict
        Contains all global_parameters.
    country_parameters :
        ???
    backhaul_lut : dict
        Backhaul distance by region.

    Returns
    -------
    output : list of dicts
        Contains a list of costs, with affliated discounted capex and
        opex costs.

    """
    cost_results = get_costs(country, region, strategy, costs, global_parameters, backhaul_lut, core_lut
    )

    # total_network_cost = 0
    # for cost_result in cost_results:
    #     for key, value in cost_result.items():
    #         total_network_cost += value

    return cost_results#, total_network_cost


def get_costs(country, region, strategy, costs, global_parameters, backhaul_lut, core_lut):

    total_new_site_cost = 0
    total_upgrade_cost = 0

    sharing = strategy.split('_')[3]

    if sharing == 'baseline':
    #     if region['new_sites'] > 0:
        total_new_site_cost, cost_structure = baseline_new_site(country, region, strategy, costs,
            global_parameters, backhaul_lut, core_lut)

        # if region['upgraded_sites'] > 0:
        #     total_upgrade_cost, cost_structure = baseline_upgrade(region['upgraded_sites'], costs, global_parameters)

    if sharing == 'passive':
        total_new_site_cost, cost_structure = passive_new_site(country, region, strategy, costs,
            global_parameters, backhaul_lut, core_lut)

    if sharing == 'active':
        total_new_site_cost, cost_structure = active_new_site(country, region, strategy, costs,
            global_parameters, backhaul_lut, core_lut)
    #     costs = active(country, region, generation, core, backhaul, sharing,
    #     geotype, costs, global_parameters, country_parameters, backhaul_lut, core_lut)

    return total_new_site_cost + total_upgrade_cost


def baseline_new_site(country, region, strategy, costs,
    global_parameters, backhaul_lut, core_lut):
    """
    No sharing takes place.
    Reflects the baseline scenario of needing to build a single dedicated
    network.

    """
    core = strategy.split('_')[1]
    backhaul = strategy.split('_')[2]

    new_sites = region['new_sites']

    cost_structure = {
        'antennas': (
            discount_capex_and_opex(costs['single_sector_antenna'], global_parameters) *
            global_parameters['sectorization']
        ),
        'remote_radio_units': (
            discount_capex_and_opex(costs['single_remote_radio_unit'], global_parameters) * global_parameters['sectorization']
        ),
        'single_baseband_unit': (
            discount_capex_and_opex(costs['single_baseband_unit'], global_parameters)
        ),
        'tower': (
            costs['tower']
        ),
        'civil_materials': (
            costs['single_baseband_unit']
        ),
        'transportation': (
            costs['single_baseband_unit']
        ),
        'installation': (
            costs['installation']
        ),
        'site_rental': (
            discount_opex(costs['site_rental'], global_parameters)
        ),
        'power_generator_battery_system': (
            discount_capex_and_opex(costs['power_generator_battery_system'], global_parameters)
        ),
        'high_speed_backhaul_hub': (
            discount_capex_and_opex(costs['high_speed_backhaul_hub'], global_parameters)
        ),
        'router': (
            discount_capex_and_opex(costs['router'], global_parameters)
        ),
        '{}_backhaul'.format(backhaul): (
            discount_capex_and_opex(get_backhaul_costs(country, region, backhaul, costs, backhaul_lut), global_parameters)
        ),
        'core_edges': (
            discount_capex_and_opex(get_core_costs(country, region, 'core_edges', costs, core_lut, core), global_parameters)
        ),
        'code_nodes': (
            discount_capex_and_opex(get_core_costs(country, region, 'core_nodes', costs, core_lut, core), global_parameters)
        ),
        'regional_edges': (
            discount_capex_and_opex(get_core_costs(country, region, 'regional_edges', costs, core_lut, core), global_parameters)
        ),
        'regional_nodes': (
            discount_capex_and_opex(get_core_costs(country, region, 'regional_nodes', costs, core_lut, core), global_parameters)
        ),
    }

    total_new_site_cost = new_sites * sum(cost_structure.values())

    return total_new_site_cost, cost_structure


def baseline_upgrade(sites_to_upgrade, costs, global_parameters):
    """
    No sharing takes place.
    Reflects the baseline scenario of needing to build a single dedicated
    network.

    """
    cost_structure = {
        'antennas': (discount_capex_and_opex(costs['single_sector_antenna'], global_parameters) *
            global_parameters['sectorization']
        ),
        'remote_radio_units': (
            discount_capex_and_opex(costs['single_remote_radio_unit'], global_parameters) *
            global_parameters['sectorization']
        ),
        'single_baseband_unit': (
            discount_capex_and_opex(costs['single_baseband_unit'], global_parameters)
        ),
        'installation': (
            costs['installation']
        ),
    }

    total_upgrade_cost = sites_to_upgrade * sum(cost_structure.values())

    return total_upgrade_cost, cost_structure


def passive_new_site(country, region, strategy, costs,
    global_parameters, backhaul_lut, core_lut):
    """

    """
    core = strategy.split('_')[1]
    backhaul = strategy.split('_')[2]

    new_sites = region['new_sites']

    cost_structure = {
        'antennas': (
            discount_capex_and_opex(costs['single_sector_antenna'], global_parameters) *
            global_parameters['sectorization']
        ),
        'remote_radio_units': (
            discount_capex_and_opex(costs['single_remote_radio_unit'], global_parameters) *
            global_parameters['sectorization']
        ),
        'single_baseband_unit': (
            discount_capex_and_opex(costs['single_baseband_unit'], global_parameters)
        ),
        'tower': (
            costs['tower'] / global_parameters['networks']
        ),
        'civil_materials': (
            costs['single_baseband_unit'] / global_parameters['networks']
        ),
        'transportation': (
            costs['single_baseband_unit'] / global_parameters['networks']
        ),
        'installation': (
            costs['installation'] / global_parameters['networks']
        ),
        'site_rental': (
            discount_opex(costs['site_rental'], global_parameters) / global_parameters['networks']
        ),
        'power_generator_battery_system': (
            discount_capex_and_opex(costs['power_generator_battery_system'], global_parameters) / global_parameters['networks']
        ),
        'high_speed_backhaul_hub': (
            discount_capex_and_opex(costs['high_speed_backhaul_hub'], global_parameters) / global_parameters['networks']
        ),
        'router': (
            discount_capex_and_opex(costs['router'], global_parameters) / global_parameters['networks']
        ),
        '{}_backhaul'.format(backhaul): (
            discount_capex_and_opex(
                get_backhaul_costs(country, region, backhaul, costs, backhaul_lut), global_parameters) / global_parameters['networks']
        ),
        'core_edges': (
            discount_capex_and_opex(get_core_costs(country, region, 'core_edges', costs, core_lut, core), global_parameters)
        ),
        'code_nodes': (
            discount_capex_and_opex(get_core_costs(country, region, 'core_nodes', costs, core_lut, core), global_parameters)
        ),
        'regional_edges': (
            discount_capex_and_opex(get_core_costs(country, region, 'regional_edges', costs, core_lut, core), global_parameters)
        ),
        'regional_nodes': (
            discount_capex_and_opex(get_core_costs(country, region, 'regional_nodes', costs, core_lut, core), global_parameters)
        ),
    }

    total_new_site_cost = new_sites * sum(cost_structure.values())

    return total_new_site_cost, cost_structure


def active_new_site(country, region, strategy, costs,
    global_parameters, backhaul_lut, core_lut):
    """

    """
    core = strategy.split('_')[1]
    backhaul = strategy.split('_')[2]

    new_sites = region['new_sites']

    cost_structure = {
        'antennas': (
            discount_capex_and_opex(costs['single_sector_antenna'], global_parameters) *
            global_parameters['sectorization'] / global_parameters['networks']
        ),
        'remote_radio_units': (
            discount_capex_and_opex(costs['single_remote_radio_unit'], global_parameters) *
            global_parameters['sectorization'] / global_parameters['networks']
        ),
        'single_baseband_unit': (
            discount_capex_and_opex(costs['single_baseband_unit'], global_parameters) /
            global_parameters['networks']
        ),
        'tower': (
            costs['tower'] / global_parameters['networks']
        ),
        'civil_materials': (
            costs['single_baseband_unit'] / global_parameters['networks']
        ),
        'transportation': (
            costs['single_baseband_unit'] / global_parameters['networks']
        ),
        'installation': (
            costs['installation'] / global_parameters['networks']
        ),
        'site_rental': (
            discount_opex(costs['site_rental'], global_parameters) / global_parameters['networks']
        ),
        'power_generator_battery_system': (
            discount_capex_and_opex(costs['power_generator_battery_system'], global_parameters) / global_parameters['networks']
        ),
        'high_speed_backhaul_hub': (
            discount_capex_and_opex(costs['high_speed_backhaul_hub'], global_parameters) / global_parameters['networks']
        ),
        'router': (
            discount_capex_and_opex(costs['router'], global_parameters) / global_parameters['networks']
        ),
        '{}_backhaul'.format(backhaul): (
            discount_capex_and_opex(
                get_backhaul_costs(country, region, backhaul, costs, backhaul_lut), global_parameters) / global_parameters['networks']
        ),
        'core_edges': (
            discount_capex_and_opex(get_core_costs(country, region, 'core_edges', costs, core_lut, core), global_parameters) /
            global_parameters['networks']
        ),
        'code_nodes': (
            discount_capex_and_opex(get_core_costs(country, region, 'core_nodes', costs, core_lut, core), global_parameters) /
            global_parameters['networks']
        ),
        'regional_edges': (
            discount_capex_and_opex(get_core_costs(country, region, 'regional_edges', costs, core_lut, core), global_parameters) /
            global_parameters['networks']
        ),
        'regional_nodes': (
            discount_capex_and_opex(get_core_costs(country, region, 'regional_nodes', costs, core_lut, core), global_parameters) /
            global_parameters['networks']
        ),
    }

    total_new_site_cost = new_sites * sum(cost_structure.values())

    return total_new_site_cost, cost_structure


def get_backhaul_costs(country, region, backhaul, costs, backhaul_lut):
    """
    Calculate backhaul costs.

    """
    distance_m = backhaul_lut[region['GID_id']]

    if backhaul == 'microwave':
        if distance_m < 2e4:
            tech = '{}_backhaul_{}'.format(backhaul, 'small')
            cost = costs[tech]
        elif 2e4 < distance_m < 4e4:
            tech = '{}_backhaul_{}'.format(backhaul, 'medium')
            cost = costs[tech]
        else:
            tech = '{}_backhaul_{}'.format(backhaul, 'large')
            cost = costs[tech]

    elif backhaul == 'fiber':
        tech = '{}_backhaul_{}_m'.format(backhaul, region['geotype'].split(' ')[0])
        cost_per_meter = costs[tech]
        cost = cost_per_meter * distance_m

    else:
        print('Did not recognise the backhaul technology given')

    return cost


def get_core_costs(country, region, asset_type, costs, core_lut, core):
    """
    Return core asset costs.

    """

    if asset_type == 'core_edges':

        if region['GID_id'] in core_lut[asset_type]:
            distance_m = core_lut[asset_type][region['GID_id']]
            cost_m = costs['core_edges']
            cost = int(distance_m * cost_m)
        else:
            cost = 20000

        return cost

    elif asset_type == 'core_nodes':

        quantity = core_lut[asset_type][region['GID_id']]
        cost_each = costs['core_nodes_{}'.format(core)]

        return int(quantity * cost_each)

    elif asset_type == 'regional_edges':

        if 'regional_edges' in core_lut:
            if region['GID_id'] in core_lut[asset_type]:
                distance_m = core_lut[asset_type][region['GID_id']]
                cost_m = costs['regional_edges']
                cost = int(distance_m * cost_m)
            else:
                cost = 20000
        else:
            cost = 20000

        return cost

    elif asset_type == 'regional_nodes':

        if 'regional_nodes' in core_lut:
            if region['GID_id'] in core_lut[asset_type]:
                quantity = core_lut[asset_type][region['GID_id']]
                cost_each = costs['regional_nodes_{}'.format(core)]
                cost = int(quantity * cost_each)
            else:
                cost = 20000
        else:
            cost = 20000

        return cost

    else:
        print('Did not recognise core asset type')


def discount_capex_and_opex(capex, global_parameters):
    """
    Discount costs based on return period.

    Parameters
    ----------
    cost : float
        Financial cost.
    global_parameters : dict
        All global model parameters.

    Returns
    -------
    discounted_cost : float
        The discounted cost over the desired time period.

    """
    return_period = global_parameters['return_period']
    discount_rate = global_parameters['discount_rate'] / 100

    costs_over_time_period = []

    costs_over_time_period.append(capex)

    opex = round(capex * (global_parameters['opex_percentage_of_capex'] / 100))

    for i in range(0, return_period):
        costs_over_time_period.append(
            opex / (1 + discount_rate)**i
        )

    discounted_cost = round(sum(costs_over_time_period))

    return discounted_cost


def discount_opex(opex, global_parameters):
    """
    Discount opex based on return period.

    """
    return_period = global_parameters['return_period']
    discount_rate = global_parameters['discount_rate'] / 100

    costs_over_time_period = []

    for i in range(0, return_period):
        costs_over_time_period.append(
            opex / (1 + discount_rate)**i
        )

    discounted_cost = round(sum(costs_over_time_period))

    return discounted_cost
