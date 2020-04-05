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
    generation = strategy.split('_')[0]
    core = strategy.split('_')[1]

    new_sites = region['new_sites']
    upgraded_sites = region['upgraded_sites']
    existing_4g_sites = region['sites_4G']

    regional_cost = 0

    if new_sites > 0 and generation == '4G':

        cost_structure = greenfield_4g(country, region,
            strategy, costs, global_parameters, backhaul_lut, core_lut)

        total_cost = calc_costs(cost_structure, global_parameters)

        regional_cost += new_sites * total_cost


    if upgraded_sites > 0 and generation == '4G':

        upgraded_sites = upgraded_sites - existing_4g_sites

        cost_structure = upgrade_to_4g(country, region,
            strategy, costs, global_parameters, backhaul_lut, core_lut)

        total_cost = calc_costs(cost_structure, global_parameters)

        regional_cost += new_sites * total_cost


    if new_sites > 0 and generation == '5G' and core == 'nsa':

        cost_structure = greenfield_5g_nsa(country, region,
            strategy, costs, global_parameters, backhaul_lut, core_lut)

        total_cost = calc_costs(cost_structure, global_parameters)

        regional_cost += new_sites * total_cost


    if upgraded_sites > 0 and generation == '5G' and core == 'nsa':

        cost_structure = upgrade_to_5g_nsa(country, region,
            strategy, costs, global_parameters, backhaul_lut, core_lut)

        total_cost = calc_costs(cost_structure, global_parameters)

        regional_cost += new_sites * total_cost


    if new_sites > 0 and generation == '5G' and core == 'sa':

        cost_structure = greenfield_5g_sa(country, region,
            strategy, costs, global_parameters, backhaul_lut, core_lut)

        total_cost = calc_costs(cost_structure, global_parameters)

        regional_cost += new_sites * total_cost


    if upgraded_sites > 0 and generation == '5G' and core == 'sa':

        cost_structure = upgrade_to_5g_sa(country, region,
            strategy, costs, global_parameters, backhaul_lut, core_lut)

        total_cost = calc_costs(cost_structure, global_parameters)

        regional_cost += new_sites * total_cost

    return regional_cost


def greenfield_4g(country, region, strategy, costs,
    global_parameters, backhaul_lut, core_lut):
    """
    Build a greenfield 4G asset.

    """
    core = strategy.split('_')[1]
    backhaul = strategy.split('_')[2]
    sharing = strategy.split('_')[3]

    shared_assets = INFRA_SHARING_ASSETS[sharing]

    assets = {
        'single_sector_antenna': (
            costs['single_sector_antenna']
        ),
        'single_remote_radio_unit': (
            costs['single_remote_radio_unit']
        ),
        'single_baseband_unit': (
            costs['single_baseband_unit']
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
            costs['site_rental']
        ),
        'power_generator_battery_system': (
            costs['power_generator_battery_system']
        ),
        'high_speed_backhaul_hub': (
            costs['high_speed_backhaul_hub']
        ),
        'router': (
            costs['router']
        ),
        '{}_backhaul'.format(backhaul): (
            get_backhaul_costs(country, region, backhaul, costs, backhaul_lut)
        ),
        'core_edges': (
            get_core_costs(country, region, 'core_edges', costs, core_lut, core)
        ),
        'code_nodes': (
            get_core_costs(country, region, 'core_nodes', costs, core_lut, core)
        ),
        'regional_edges': (
            get_core_costs(country, region, 'regional_edges', costs, core_lut, core)
        ),
        'regional_nodes': (
            get_core_costs(country, region, 'regional_nodes', costs, core_lut, core)
        ),
    }

    cost_structure = {}

    for key, value in assets.items():
        if not key in shared_assets:
            cost_structure[key] = value
        else:
            value = value / global_parameters['networks']
            cost_structure[key] = value

    return cost_structure


def upgrade_to_4g(country, region, strategy, costs,
    global_parameters, backhaul_lut, core_lut):
    """
    Reflects the baseline scenario of needing to build a single dedicated
    network.

    """
    core = strategy.split('_')[1]
    backhaul = strategy.split('_')[2]
    sharing = strategy.split('_')[3]

    shared_assets = INFRA_SHARING_ASSETS[sharing]

    assets = {
        'single_sector_antenna': (
            costs['single_sector_antenna']
        ),
        'single_remote_radio_unit': (
            costs['single_remote_radio_unit']
        ),
        'single_baseband_unit': (
            costs['single_baseband_unit']
        ),
        'installation': (
            costs['installation']
        ),
        'site_rental': (
            costs['site_rental']
        ),
        'high_speed_backhaul_hub': (
            costs['high_speed_backhaul_hub']
        ),
        'router': (
            costs['router']
        ),
        '{}_backhaul'.format(backhaul): (
            get_backhaul_costs(country, region, backhaul, costs, backhaul_lut)
        ),
        'core_edges': (
            get_core_costs(country, region, 'core_edges', costs, core_lut, core)
        ),
        'code_nodes': (
            get_core_costs(country, region, 'core_nodes', costs, core_lut, core)
        ),
        'regional_edges': (
            get_core_costs(country, region, 'regional_edges', costs, core_lut, core)
        ),
        'regional_nodes': (
            get_core_costs(country, region, 'regional_nodes', costs, core_lut, core)
        ),
    }

    cost_structure = {}

    for key, value in assets.items():
        if not key in shared_assets:
            cost_structure[key] = value
        else:
            value = value / global_parameters['networks']
            cost_structure[key] = value

    return cost_structure


def greenfield_5g_nsa(country, region, strategy, costs,
    global_parameters, backhaul_lut, core_lut):
    """
    No sharing takes place.
    Reflects the baseline scenario of needing to build a single dedicated
    network.

    """
    core = strategy.split('_')[1]
    backhaul = strategy.split('_')[2]
    sharing = strategy.split('_')[3]

    shared_assets = INFRA_SHARING_ASSETS[sharing]

    assets = {
        'single_sector_antenna': (
            costs['single_sector_antenna']
        ),
        'single_remote_radio_unit': (
            costs['single_remote_radio_unit']
        ),
        'single_baseband_unit': (
            costs['single_baseband_unit']
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
            costs['site_rental']
        ),
        'power_generator_battery_system': (
            costs['power_generator_battery_system']
        ),
        'high_speed_backhaul_hub': (
            costs['high_speed_backhaul_hub']
        ),
        'router': (
            costs['router']
        ),
        '{}_backhaul'.format(backhaul): (
            get_backhaul_costs(country, region, backhaul, costs, backhaul_lut)
        ),
        'core_edges': (
            get_core_costs(country, region, 'core_edges', costs, core_lut, core)
        ),
        'code_nodes': (
            get_core_costs(country, region, 'core_nodes', costs, core_lut, core)
        ),
        'regional_edges': (
            get_core_costs(country, region, 'regional_edges', costs, core_lut, core)
        ),
        'regional_nodes': (
            get_core_costs(country, region, 'regional_nodes', costs, core_lut, core)
        ),
    }

    cost_structure = {}

    for key, value in assets.items():
        if not key in shared_assets:
            cost_structure[key] = value
        else:
            value = value / global_parameters['networks']
            cost_structure[key] = value

    return cost_structure


def upgrade_to_5g_nsa(country, region, strategy, costs,
    global_parameters, backhaul_lut, core_lut):
    """
    Reflects the baseline scenario of needing to build a single dedicated
    network.

    """
    core = strategy.split('_')[1]
    backhaul = strategy.split('_')[2]
    sharing = strategy.split('_')[3]

    shared_assets = INFRA_SHARING_ASSETS[sharing]

    assets = {
        'single_sector_antenna': (
            costs['single_sector_antenna']
        ),
        'single_remote_radio_unit': (
            costs['single_remote_radio_unit']
        ),
        'single_baseband_unit': (
            costs['single_baseband_unit']
        ),
        'installation': (
            costs['installation']
        ),
        'site_rental': (
            costs['site_rental']
        ),
        'power_generator_battery_system': (
            costs['power_generator_battery_system']
        ),
        'high_speed_backhaul_hub': (
            costs['high_speed_backhaul_hub']
        ),
        'router': (
            costs['router']
        ),
        '{}_backhaul'.format(backhaul): (
            get_backhaul_costs(country, region, backhaul, costs, backhaul_lut)
        ),
        'core_edges': (
            get_core_costs(country, region, 'core_edges', costs, core_lut, core)
        ),
        'code_nodes': (
            get_core_costs(country, region, 'core_nodes', costs, core_lut, core)
        ),
        'regional_edges': (
            get_core_costs(country, region, 'regional_edges', costs, core_lut, core)
        ),
        'regional_nodes': (
            get_core_costs(country, region, 'regional_nodes', costs, core_lut, core)
        ),
    }

    cost_structure = {}

    for key, value in assets.items():
        if not key in shared_assets:
            cost_structure[key] = value
        else:
            value = value / global_parameters['networks']
            cost_structure[key] = value

    return cost_structure


def greenfield_5g_sa(country, region, strategy, costs,
    global_parameters, backhaul_lut, core_lut):
    """
    No sharing takes place.
    Reflects the baseline scenario of needing to build a single dedicated
    network.

    """
    core = strategy.split('_')[1]
    backhaul = strategy.split('_')[2]
    sharing = strategy.split('_')[3]

    shared_assets = INFRA_SHARING_ASSETS[sharing]

    assets = {
        'single_sector_antenna': (
            costs['single_sector_antenna']
        ),
        'single_remote_radio_unit': (
            costs['single_remote_radio_unit']
        ),
        'single_baseband_unit': (
            costs['single_baseband_unit']
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
            costs['site_rental']
        ),
        'power_generator_battery_system': (
            costs['power_generator_battery_system']
        ),
        'high_speed_backhaul_hub': (
            costs['high_speed_backhaul_hub']
        ),
        'router': (
            costs['router']
        ),
        '{}_backhaul'.format(backhaul): (
            get_backhaul_costs(country, region, backhaul, costs, backhaul_lut)
        ),
        'core_edges': (
            get_core_costs(country, region, 'core_edges', costs, core_lut, core)
        ),
        'code_nodes': (
            get_core_costs(country, region, 'core_nodes', costs, core_lut, core)
        ),
        'regional_edges': (
            get_core_costs(country, region, 'regional_edges', costs, core_lut, core)
        ),
        'regional_nodes': (
            get_core_costs(country, region, 'regional_nodes', costs, core_lut, core)
        ),
    }

    cost_structure = {}

    for key, value in assets.items():
        if not key in shared_assets:
            cost_structure[key] = value
        else:
            value = value / global_parameters['networks']
            cost_structure[key] = value

    return cost_structure


def upgrade_to_5g_sa(country, region, strategy, costs,
    global_parameters, backhaul_lut, core_lut):
    """
    Reflects the baseline scenario of needing to build a single dedicated
    network.

    """
    core = strategy.split('_')[1]
    backhaul = strategy.split('_')[2]
    sharing = strategy.split('_')[3]

    shared_assets = INFRA_SHARING_ASSETS[sharing]

    assets = {
        'single_sector_antenna': (
            costs['single_sector_antenna']
        ),
        'single_remote_radio_unit': (
            costs['single_remote_radio_unit']
        ),
        'single_baseband_unit': (
            costs['single_baseband_unit']
        ),
        'installation': (
            costs['installation']
        ),
        'site_rental': (
            costs['site_rental']
        ),
        'power_generator_battery_system': (
            costs['power_generator_battery_system']
        ),
        'high_speed_backhaul_hub': (
            costs['high_speed_backhaul_hub']
        ),
        'router': (
            costs['router']
        ),
        '{}_backhaul'.format(backhaul): (
            get_backhaul_costs(country, region, backhaul, costs, backhaul_lut)
        ),
        'core_edges': (
            get_core_costs(country, region, 'core_edges', costs, core_lut, core)
        ),
        'code_nodes': (
            get_core_costs(country, region, 'core_nodes', costs, core_lut, core)
        ),
        'regional_edges': (
            get_core_costs(country, region, 'regional_edges', costs, core_lut, core)
        ),
        'regional_nodes': (
            get_core_costs(country, region, 'regional_nodes', costs, core_lut, core)
        ),
    }

    cost_structure = {}

    for key, value in assets.items():
        if not key in shared_assets:
            cost_structure[key] = value
        else:
            value = value / global_parameters['networks']
            cost_structure[key] = value

    return cost_structure


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


def calc_costs(cost_structure, global_parameters):
    """

    """
    total_cost = 0

    assets_counted = []

    for asset_name1, cost in cost_structure.items():
        for asset_name2, type_of_cost in COST_TYPE.items():
            if asset_name1 == asset_name2:

                if type_of_cost == 'capex_and_opex':
                    cost = discount_capex_and_opex(cost, global_parameters)
                    if asset_name1 == 'single_sector_antenna':
                        cost = cost * global_parameters['sectorization']
                    total_cost += cost
                    assets_counted.append(asset_name1)

                elif type_of_cost == 'capex':
                    total_cost += cost
                    assets_counted.append(asset_name1)

                elif type_of_cost == 'opex':
                    total_cost += discount_opex(cost, global_parameters)
                    assets_counted.append(asset_name1)

                else:
                    print('Did not recognize cost type')

    # if len(assets_counted) < len(cost_structure):
    #     print('Asset costs missing: Check names of assets in calc_cost function')
    # print(assets_counted, cost_structure)
    return total_cost


INFRA_SHARING_ASSETS = {
    'baseline': [],
    'passive': [
        'tower',
        'civil_materials',
        'transportation',
        'installation',
        'site_rental',
        'power_generator_battery_system',
    ],
    'active': [
        'single_sector_antenna',  ##these items need renaming
        'single_remote_radio_unit',
        'single_baseband_unit',
        'tower',
        'civil_materials',
        'transportation',
        'installation',
        'site_rental',
        'power_generator_battery_system',
        'high_speed_backhaul_hub',
        'router',
        'microwave_backhaul_small',
        'microwave_backhaul_medium',
        'microwave_backhaul_large',
        'fiber_backhaul_urban_m',
        'fiber_backhaul_suburban_m',
        'fiber_backhaul_rural_m',
    ]
}

COST_TYPE = {
    'single_sector_antenna': 'capex_and_opex',
    'single_remote_radio_unit': 'capex_and_opex',
    'single_baseband_unit': 'capex_and_opex',
    'tower': 'capex',
    'civil_materials': 'capex',
    'transportation': 'capex',
    'installation': 'capex',
    'site_rental': 'opex',
    'power_generator_battery_system': 'capex_and_opex',
    'high_speed_backhaul_hub': 'capex_and_opex',
    'router': 'capex_and_opex',
    'microwave_backhaul_small': 'capex_and_opex',
    'microwave_backhaul_medium': 'capex_and_opex',
    'microwave_backhaul_large': 'capex_and_opex',
    'fiber_backhaul_urban_m': 'capex_and_opex',
    'fiber_backhaul_suburban_m': 'capex_and_opex',
    'fiber_backhaul_rural_m': 'capex_and_opex',
}
