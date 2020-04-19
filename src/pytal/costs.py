"""
Cost module
Author: Edward Oughton
Date: April 2019

Based off the repo pysim5g:
https://github.com/edwardoughton/pysim5g

"""
import math
from itertools import tee

def find_single_network_cost(region, strategy, costs, global_parameters,
    country_parameters, backhaul_lut, core_lut):
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
    all_sites = new_sites + upgraded_sites

    new_backhaul = region['backhaul_new']

    regional_cost = []

    for i in range(1, int(all_sites) + 1):

        if i <= upgraded_sites and generation == '4G':

            cost_structure = upgrade_to_4g(region,strategy, costs,
                global_parameters, backhaul_lut, core_lut)

            backhaul_quant = backhaul_quantity(i, new_backhaul)

            total_cost = calc_costs(region, cost_structure, backhaul_quant, global_parameters)

            regional_cost.append(total_cost)


        if i <= upgraded_sites and generation == '5G' and core == 'nsa':

            cost_structure = upgrade_to_5g_nsa(region, strategy, costs,
                global_parameters, backhaul_lut, core_lut)

            backhaul_quant = backhaul_quantity(i, new_backhaul)

            total_cost = calc_costs(region, cost_structure, backhaul_quant, global_parameters)

            regional_cost.append(total_cost)


        if i <= upgraded_sites and generation == '5G' and core == 'sa':

            cost_structure = upgrade_to_5g_sa(region, strategy, costs,
                global_parameters, backhaul_lut, core_lut)

            backhaul_quant = backhaul_quantity(i, new_backhaul)

            total_cost = calc_costs(region, cost_structure, backhaul_quant, global_parameters)

            regional_cost.append(total_cost)


        if i > upgraded_sites and generation == '4G':

            cost_structure = greenfield_4g(region, strategy, costs,
                global_parameters, backhaul_lut, core_lut)

            backhaul_quant = backhaul_quantity(i, new_backhaul)

            total_cost = calc_costs(region, cost_structure, backhaul_quant, global_parameters)

            regional_cost.append(total_cost)


        if i > upgraded_sites and generation == '5G' and core == 'nsa':

            cost_structure = greenfield_5g_nsa(region, strategy, costs,
                global_parameters, backhaul_lut, core_lut)

            backhaul_quant = backhaul_quantity(i, new_backhaul)

            total_cost = calc_costs(region, cost_structure, backhaul_quant, global_parameters)

            regional_cost.append(total_cost)


        if i > upgraded_sites and generation == '5G' and core == 'sa':

            cost_structure = greenfield_5g_sa(region, strategy, costs,
                global_parameters, backhaul_lut, core_lut)

            backhaul_quant = backhaul_quantity(i, new_backhaul)

            total_cost = calc_costs(region, cost_structure, backhaul_quant, global_parameters)

            regional_cost.append(total_cost)

    return sum(regional_cost)


def backhaul_quantity(i, new_backhaul):
    if i <= new_backhaul:
        return 1
    else:
        return 0


def greenfield_4g(region, strategy, costs, global_parameters,
    backhaul_lut, core_lut):
    """
    Build a greenfield 4G asset.

    """
    core = strategy.split('_')[1]
    backhaul = '{}_backhaul'.format(strategy.split('_')[2])
    sharing = strategy.split('_')[3]
    geotype = region['geotype'].split(' ')[0]

    shared_assets = INFRA_SHARING_ASSETS[sharing]

    assets = {
        'single_sector_antenna': costs['single_sector_antenna'],
        'single_remote_radio_unit': costs['single_remote_radio_unit'],
        'io_fronthaul': costs['io_fronthaul'],
        'processing': costs['processing'],
        'io_s1_x2': costs['io_s1_x2'],
        'control_unit': costs['control_unit'],
        'cooling_fans': costs['cooling_fans'],
        'distributed_power_supply_converter': costs['distributed_power_supply_converter'],
        'power_generator_battery_system': costs['power_generator_battery_system'],
        'bbu_cabinet': costs['bbu_cabinet'],
        'tower': costs['tower'],
        'civil_materials': costs['civil_materials'],
        'transportation': costs['transportation'],
        'installation': costs['installation'],
        'site_rental': costs['site_rental_{}'.format(geotype)],
        'router': costs['router'],
        'backhaul': get_backhaul_costs(region, backhaul, costs, backhaul_lut, core_lut),
        'core_edges': get_core_costs(region, 'core_edge', costs, core_lut, core),
        'code_nodes': get_core_costs(region, 'core_node', costs, core_lut, core),
        'regional_edges': get_core_costs(region, 'regional_edge', costs, core_lut, core),
        'regional_nodes': get_core_costs(region, 'regional_node', costs, core_lut, core),
    }

    cost_structure = {}

    for key, value in assets.items():
        if not key in shared_assets:
            cost_structure[key] = value
        else:
            value = value / global_parameters['networks']
            cost_structure[key] = value

    return cost_structure


def upgrade_to_4g(region, strategy, costs, global_parameters,
    backhaul_lut, core_lut):
    """
    Reflects the baseline scenario of needing to build a single dedicated
    network.

    """
    core = strategy.split('_')[1]
    backhaul = strategy.split('_')[2]
    sharing = strategy.split('_')[3]
    geotype = region['geotype'].split(' ')[0]

    shared_assets = INFRA_SHARING_ASSETS[sharing]

    assets = {
        'single_sector_antenna': costs['single_sector_antenna'],
        'single_remote_radio_unit': costs['single_remote_radio_unit'],
        'io_fronthaul': costs['io_fronthaul'],
        'processing': costs['processing'],
        'io_s1_x2': costs['io_s1_x2'],
        'control_unit': costs['control_unit'],
        'cooling_fans': costs['cooling_fans'],
        'distributed_power_supply_converter': costs['distributed_power_supply_converter'],
        'bbu_cabinet': costs['bbu_cabinet'],
        'installation': costs['installation'],
        'site_rental': costs['site_rental_{}'.format(geotype)],
        'router': costs['router'],
        'backhaul': get_backhaul_costs(region, backhaul, costs, backhaul_lut, core_lut),
        'core_edges': get_core_costs(region, 'core_edge', costs, core_lut, core),
        'code_nodes': get_core_costs(region, 'core_node', costs, core_lut, core),
        'regional_edges': get_core_costs(region, 'regional_edge', costs, core_lut, core),
        'regional_nodes': get_core_costs(region, 'regional_node', costs, core_lut, core),
    }

    cost_structure = {}

    for key, value in assets.items():
        if not key in shared_assets:
            cost_structure[key] = value
        else:
            value = value / global_parameters['networks']
            cost_structure[key] = value

    return cost_structure


def greenfield_5g_nsa(region, strategy, costs,
    global_parameters, backhaul_lut, core_lut):
    """
    No sharing takes place.
    Reflects the baseline scenario of needing to build a single dedicated
    network.

    """
    core = strategy.split('_')[1]
    backhaul = strategy.split('_')[2]
    sharing = strategy.split('_')[3]
    geotype = region['geotype'].split(' ')[0]

    shared_assets = INFRA_SHARING_ASSETS[sharing]

    assets = {
        'single_sector_antenna': costs['single_sector_antenna'],
        'single_remote_radio_unit': costs['single_remote_radio_unit'],
        'io_fronthaul': costs['io_fronthaul'],
        'processing': costs['processing'],
        'io_s1_x2': costs['io_s1_x2'],
        'control_unit': costs['control_unit'],
        'cooling_fans': costs['cooling_fans'],
        'distributed_power_supply_converter': costs['distributed_power_supply_converter'],
        'power_generator_battery_system': costs['power_generator_battery_system'],
        'bbu_cabinet': costs['bbu_cabinet'],
        'tower': costs['tower'],
        'civil_materials': costs['civil_materials'],
        'transportation': costs['transportation'],
        'installation': costs['installation'],
        'site_rental': costs['site_rental_{}'.format(geotype)],
        'router': costs['router'],
        'backhaul': get_backhaul_costs(region, backhaul, costs, backhaul_lut, core_lut),
        'core_edges': get_core_costs(region, 'core_edge', costs, core_lut, core),
        'code_nodes': get_core_costs(region, 'core_node', costs, core_lut, core),
        'regional_edges': get_core_costs(region, 'regional_edge', costs, core_lut, core),
        'regional_nodes': get_core_costs(region, 'regional_node', costs, core_lut, core),
    }

    cost_structure = {}

    for key, value in assets.items():
        if not key in shared_assets:
            cost_structure[key] = value
        else:
            value = value / global_parameters['networks']
            cost_structure[key] = value

    return cost_structure


def upgrade_to_5g_nsa(region, strategy, costs,
    global_parameters, backhaul_lut, core_lut):
    """
    Reflects the baseline scenario of needing to build a single dedicated
    network.

    """
    core = strategy.split('_')[1]
    backhaul = strategy.split('_')[2]
    sharing = strategy.split('_')[3]
    geotype = region['geotype'].split(' ')[0]

    shared_assets = INFRA_SHARING_ASSETS[sharing]

    assets = {
        'single_sector_antenna': costs['single_sector_antenna'],
        'single_remote_radio_unit': costs['single_remote_radio_unit'],
        'io_fronthaul': costs['io_fronthaul'],
        'processing': costs['processing'],
        'io_s1_x2': costs['io_s1_x2'],
        'control_unit': costs['control_unit'],
        'cooling_fans': costs['cooling_fans'],
        'distributed_power_supply_converter': costs['distributed_power_supply_converter'],
        'bbu_cabinet': costs['bbu_cabinet'],
        'installation': costs['installation'],
        'site_rental': costs['site_rental_{}'.format(geotype)],
        'router': costs['router'],
        'backhaul': get_backhaul_costs(region, backhaul, costs, backhaul_lut, core_lut),
        'core_edges': get_core_costs(region, 'core_edge', costs, core_lut, core),
        'code_nodes': get_core_costs(region, 'core_node', costs, core_lut, core),
        'regional_edges': get_core_costs(region, 'regional_edge', costs, core_lut, core),
        'regional_nodes': get_core_costs(region, 'regional_node', costs, core_lut, core),
    }

    cost_structure = {}

    for key, value in assets.items():
        if not key in shared_assets:
            cost_structure[key] = value
        else:
            value = value / global_parameters['networks']
            cost_structure[key] = value

    return cost_structure


def greenfield_5g_sa(region, strategy, costs,
    global_parameters, backhaul_lut, core_lut):
    """
    No sharing takes place.
    Reflects the baseline scenario of needing to build a single dedicated
    network.

    """
    core = strategy.split('_')[1]
    backhaul = strategy.split('_')[2]
    sharing = strategy.split('_')[3]
    geotype = region['geotype'].split(' ')[0]

    shared_assets = INFRA_SHARING_ASSETS[sharing]

    assets = {
        'single_sector_antenna': costs['single_sector_antenna'],
        'single_remote_radio_unit': costs['single_remote_radio_unit'],
        'io_fronthaul': costs['io_fronthaul'],
        'cots_processing': costs['cots_processing'],
        'io_n2_n3': costs['io_n2_n3'],
        'low_latency_switch': costs['low_latency_switch'],
        'rack': costs['rack'],
        'cloud_power_supply_converter': costs['cloud_power_supply_converter'],
        'software': costs['software'],
        'power_generator_battery_system': costs['power_generator_battery_system'],
        'fronthaul': get_fronthaul_costs(region, costs),
        'cloud_backhaul': get_backhaul_costs(region, backhaul, costs, backhaul_lut, core_lut),
        'tower': costs['tower'],
        'civil_materials': costs['civil_materials'],
        'transportation': costs['transportation'],
        'installation': costs['installation'],
        'site_rental': costs['site_rental_{}'.format(geotype)],
        'router': costs['router'],
        'core_edges': get_core_costs(region, 'core_edge', costs, core_lut, core),
        'code_nodes': get_core_costs(region, 'core_node', costs, core_lut, core),
        'regional_edges': get_core_costs(region, 'regional_edge', costs, core_lut, core),
        'regional_nodes': get_core_costs(region, 'regional_node', costs, core_lut, core),
    }

    cost_structure = {}

    for key, value in assets.items():
        if not key in shared_assets:
            cost_structure[key] = value
        else:
            value = value / global_parameters['networks']
            cost_structure[key] = value

    return cost_structure


def upgrade_to_5g_sa(region, strategy, costs,
    global_parameters, backhaul_lut, core_lut):
    """
    Reflects the baseline scenario of needing to build a single dedicated
    network.

    """
    core = strategy.split('_')[1]
    backhaul = strategy.split('_')[2]
    sharing = strategy.split('_')[3]
    geotype = region['geotype'].split(' ')[0]

    shared_assets = INFRA_SHARING_ASSETS[sharing]

    assets = {
        'single_sector_antenna': costs['single_sector_antenna'],
        'single_remote_radio_unit': costs['single_remote_radio_unit'],
        'io_fronthaul': costs['io_fronthaul'],
        'cots_processing': costs['cots_processing'],
        'io_n2_n3': costs['io_n2_n3'],
        'low_latency_switch': costs['low_latency_switch'],
        'rack': costs['rack'],
        'cloud_power_supply_converter': costs['cloud_power_supply_converter'],
        'software': costs['software'],
        'fronthaul': get_fronthaul_costs(region, costs),
        'cloud_backhaul': get_backhaul_costs(region, backhaul, costs, backhaul_lut, core_lut),
        'installation': costs['installation'],
        'site_rental': costs['site_rental_{}'.format(geotype)],
        'router': costs['router'],
        'core_edges': get_core_costs(region, 'core_edge', costs, core_lut, core),
        'code_nodes': get_core_costs(region, 'core_node', costs, core_lut, core),
        'regional_edges': get_core_costs(region, 'regional_edge', costs, core_lut, core),
        'regional_nodes': get_core_costs(region, 'regional_node', costs, core_lut, core),
    }

    cost_structure = {}

    for key, value in assets.items():
        if not key in shared_assets:
            cost_structure[key] = value
        else:
            value = value / global_parameters['networks']
            cost_structure[key] = value

    return cost_structure


def get_fronthaul_costs(region, costs):
    """
    Calculate fronthaul costs.

    """
    average_cell_spacing_km = math.sqrt(1/region['site_density'])
    average_cell_spacing_m = average_cell_spacing_km * 1000 #convert km to m

    tech = 'fiber_fronthaul_{}_m'.format(region['geotype'].split(' ')[0])
    cost_per_meter = costs[tech]
    cost = cost_per_meter * average_cell_spacing_m

    return cost


def get_backhaul_costs(region, backhaul, costs, backhaul_lut, core_lut):
    """
    Calculate backhaul costs.

    # backhaul_fiber backhaul_copper backhaul_microwave	backhaul_satellite

    """
    backhaul_tech = backhaul.split('_')[0]
    geotype = region['geotype'].split(' ')[0]

    regional_nodes = core_lut['regional_node'][region['GID_id']]
    node_density_km2 = regional_nodes / region['area_km2']
    distance_m = estimate_backhaul_length(node_density_km2, backhaul_lut)

    if backhaul_tech == 'microwave':
        if distance_m < 2e4:
            tech = '{}_backhaul_{}'.format(backhaul_tech, 'small')
            cost = costs[tech]
        elif 2e4 < distance_m < 4e4:
            tech = '{}_backhaul_{}'.format(backhaul_tech, 'medium')
            cost = costs[tech]
        else:
            tech = '{}_backhaul_{}'.format(backhaul_tech, 'large')
            cost = costs[tech]

    elif backhaul_tech == 'fiber':
        tech = '{}_backhaul_{}_m'.format(backhaul_tech, geotype)
        cost_per_meter = costs[tech]
        cost = cost_per_meter * distance_m

    else:
        return 'Did not recognise the backhaul technology'

    return cost


def estimate_backhaul_length(node_density_km2, backhaul_lut):
    """
    Estimate backhaul length given a certain regional node density.

    """
    backhaul_lut = sorted(backhaul_lut, key=lambda item: item['node_density_km2'])

    max_density = backhaul_lut[-1]
    min_density = backhaul_lut[0]

    if node_density_km2 >= max_density['node_density_km2']:

        return max_density['average_distance_m']

    elif node_density_km2 < min_density['node_density_km2']:
        return min_density['average_distance_m']

    else:

        for item in pairwise(backhaul_lut):
            lower, upper  = item
            if lower['node_density_km2'] <= node_density_km2 < upper['node_density_km2']:
                distance_m = interpolate(
                    lower['node_density_km2'], lower['average_distance_m'],
                    upper['node_density_km2'], upper['average_distance_m'],
                    node_density_km2
                )

                return distance_m


def pairwise(iterable):
    """
    Return iterable of 2-tuples in a sliding window.
    >>> list(pairwise([1,2,3,4]))
    [(1,2),(2,3),(3,4)]
    """
    a, b = tee(iterable)
    next(b, None)

    return zip(a, b)


def interpolate(x0, y0, x1, y1, x):
    """
    Linear interpolation between two values.

    """
    y = (y0 * (x1 - x) + y1 * (x - x0)) / (x1 - x0)

    return y


def get_core_costs(region, asset_type, costs, core_lut, core):
    """
    Return core asset costs.

    """
    if asset_type == 'core_edge':

        if region['GID_id'] in core_lut[asset_type]:
            distance_m = core_lut[asset_type][region['GID_id']]
            cost_m = costs['core_edge']
            cost = int(distance_m * cost_m)
        else:
            cost = 20000

        return cost

    elif asset_type == 'core_node':

        quantity = core_lut[asset_type][region['GID_id']]
        cost_each = costs['core_node_{}'.format(core)]

        return int(quantity * cost_each)

    elif asset_type == 'regional_edge':

        if 'regional_edge' in core_lut:
            if region['GID_id'] in core_lut[asset_type]:
                distance_m = core_lut[asset_type][region['GID_id']]
                cost_m = costs['regional_edge']
                cost = int(distance_m * cost_m)
            else:
                cost = 20000
        else:
            cost = 20000

        return cost

    elif asset_type == 'regional_node':

        if 'regional_node' in core_lut:
            if region['GID_id'] in core_lut[asset_type]:
                quantity = core_lut[asset_type][region['GID_id']]
                cost_each = costs['regional_node_{}'.format(core)]
                cost = int(quantity * cost_each)
            else:
                cost = 20000
        else:
            cost = 20000

        return cost

    return 'Did not recognise core asset type'


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


def calc_costs(region, cost_structure, backhaul_quantity, global_parameters):
    """

    """
    all_sites = region['upgraded_sites'] + region['new_sites']
    geotype = region['geotype'].split(' ')[0]

    total_cost = 0

    for asset_name1, cost in cost_structure.items():
        for asset_name2, type_of_cost in COST_TYPE.items():
            if asset_name1 == asset_name2:

                if asset_name1 == 'backhaul' and backhaul_quantity == 0:
                    continue

                if region['sites_4G'] > 0 and asset_name1 in [
                    'core_edge',
                    'core_node',
                    'regional_edge',
                    'regional_node',
                    'cloud_backhaul',
                    ]:
                    continue

                if type_of_cost == 'capex_and_opex':

                    cost = discount_capex_and_opex(cost, global_parameters)

                    if asset_name1 == 'single_sector_antenna':
                        cost = cost * global_parameters['sectorization']

                    if asset_name1 == 'cots_processing':

                        split = 'cots_processing_split_{}'.format(geotype)
                        quantity = all_sites / global_parameters[split]
                        cost = cost * (quantity // 5 + (21 % 5 > 0)) #last part rounds up

                    if asset_name1 == 'low_latency_switch':
                        quantity = all_sites / global_parameters['low_latency_switch_split']
                        cost = cost * (quantity // 5 + (21 % 5 > 0)) #last part rounds up

                    if asset_name1 == 'rack':
                        quantity = all_sites / global_parameters['rack_split']
                        cost = cost * (quantity // 5 + (21 % 5 > 0)) #last part rounds up

                    if asset_name1 == 'cloud_power_supply_converter':
                        quantity = all_sites / global_parameters['cloud_power_supply_converter_split']
                        cost = cost * (quantity // 5 + (21 % 5 > 0)) #last part rounds up

                    if asset_name1 == 'software':
                        quantity = all_sites / global_parameters['software']
                        cost = cost * (quantity // 5 + (21 % 5 > 0)) #last part rounds up

                    if asset_name1 == 'cloud_backhaul':
                        quantity = all_sites / global_parameters['cloud_backhaul_split']
                        cost = cost * (quantity // 5 + (21 % 5 > 0)) #last part rounds up

                    total_cost += cost

                elif type_of_cost == 'capex':
                    total_cost += cost

                elif type_of_cost == 'opex':
                    total_cost += discount_opex(cost, global_parameters)

                else:
                    return 'Did not recognize cost type'

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
        'io_fronthaul',
        'processing',
        'io_s1_x2',
        'control_unit',
        'cooling_fans',
        'distributed_power_supply_converter',
        'bbu_cabinet',
        'fronthaul',
        'cots_processing',
        'io_n2_n3',
        'low_latency_switch',
        'rack',
        'cloud_power_supply_converter',
        'software',
        'tower',
        'civil_materials',
        'transportation',
        'installation',
        'site_rental',
        'power_generator_battery_system',
        'backhaul',
        'cloud_backhaul',
    ]
}


COST_TYPE = {
    'single_sector_antenna': 'capex_and_opex',
    'single_remote_radio_unit': 'capex_and_opex',
    'single_baseband_unit': 'capex_and_opex',
    'io_fronthaul': 'capex_and_opex',
    'processing': 'capex_and_opex',
    'io_s1_x2': 'capex_and_opex',
    'control_unit': 'capex_and_opex',
    'cooling_fans': 'capex_and_opex',
    'distributed_power_supply_converter': 'capex_and_opex',
    'bbu_cabinet': 'capex',
    'fronthaul': 'capex_and_opex',
    'cots_processing': 'capex_and_opex',
    'io_n2_n3': 'capex_and_opex',
    'low_latency_switch': 'capex_and_opex',
    'rack': 'capex',
    'cloud_power_supply_converter': 'capex_and_opex',
    'software': 'opex',
    'tower': 'capex',
    'civil_materials': 'capex',
    'transportation': 'capex',
    'installation': 'capex',
    'site_rental': 'opex',
    'power_generator_battery_system': 'capex_and_opex',
    'backhaul': 'capex_and_opex',
    'cloud_backhaul': 'capex_and_opex',

}
