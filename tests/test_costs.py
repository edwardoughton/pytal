import pytest
import math
from pytal.costs import (greenfield_4g, upgrade_to_4g, greenfield_5g_nsa,
    upgrade_to_5g_nsa, greenfield_5g_sa, upgrade_to_5g_sa, get_fronthaul_costs,
    get_backhaul_costs, get_core_costs, discount_opex, discount_capex_and_opex,
    calc_costs)

#test approach is to:
#test each function which returns the cost structure
#test the function which calculates quantities
#test infrastructure sharing strategies

def test_greenfield_4g(setup_region, setup_option, setup_costs,
    setup_global_parameters, setup_backhaul_lut, setup_core_lut):

    setup_region[0]['new_sites'] = 1
    setup_region[0]['site_density'] = 0.5

    #test baseline infra sharing
    cost_structure = greenfield_4g(setup_region[0],
        '4G_epc_microwave_baseline_baseline_baseline_baseline',
        setup_costs, setup_global_parameters,
        setup_backhaul_lut, setup_core_lut)

    assert cost_structure['single_sector_antenna'] == 1500
    assert cost_structure['single_remote_radio_unit'] == 4000
    assert cost_structure['io_fronthaul'] ==1500
    assert cost_structure['tower'] == 10000
    assert cost_structure['civil_materials'] == 5000
    assert cost_structure['transportation'] == 5000
    assert cost_structure['installation'] == 5000
    assert cost_structure['site_rental'] == 9600
    assert cost_structure['power_generator_battery_system'] == 5000
    assert cost_structure['io_s1_x2'] == 1500
    assert cost_structure['router'] == 2000

    #test passive infra sharing
    cost_structure = greenfield_4g(setup_region[0],
        '4G_epc_microwave_passive_baseline_baseline_baseline',
        setup_costs, setup_global_parameters,
        setup_backhaul_lut, setup_core_lut)

    assert cost_structure['tower'] == 10000 / setup_global_parameters['networks']
    assert cost_structure['civil_materials'] == 5000 / setup_global_parameters['networks']

    #test active infra sharing
    cost_structure = greenfield_4g(setup_region[0],
        '4G_epc_microwave_active_baseline_baseline_baseline',
        setup_costs, setup_global_parameters,
        setup_backhaul_lut, setup_core_lut)

    assert cost_structure['single_sector_antenna'] == 1500 / setup_global_parameters['networks']
    assert cost_structure['single_remote_radio_unit'] == 4000 / setup_global_parameters['networks']
    assert cost_structure['bbu_cabinet'] == 500 / setup_global_parameters['networks']
    assert cost_structure['civil_materials'] == 5000 / setup_global_parameters['networks']


def test_upgrade_to_4g(setup_region, setup_option, setup_costs,
    setup_global_parameters, setup_backhaul_lut, setup_core_lut):

    setup_region[0]['upgraded_sites'] = 1
    setup_region[0]['sites_3G'] = 1
    setup_region[0]['site_density'] = 0.5

    cost_structure = upgrade_to_4g(setup_region[0],
        '4G_epc_microwave_baseline_baseline_baseline_baseline',
        setup_costs, setup_global_parameters,
        setup_backhaul_lut, setup_core_lut)

    assert cost_structure['single_sector_antenna'] == 1500
    assert cost_structure['single_remote_radio_unit'] == 4000
    assert cost_structure['installation'] == 5000
    assert cost_structure['site_rental'] == 9600
    assert cost_structure['router'] == 2000

    #test passive infra sharing
    cost_structure = upgrade_to_4g(setup_region[0],
        '4G_epc_microwave_passive_baseline_baseline_baseline',
        setup_costs, setup_global_parameters,
        setup_backhaul_lut, setup_core_lut)

    assert cost_structure['site_rental'] == 9600 / setup_global_parameters['networks']

    #test active infra sharing
    cost_structure = upgrade_to_4g(setup_region[0],
        '4G_epc_microwave_active_baseline_baseline_baseline',
        setup_costs, setup_global_parameters,
        setup_backhaul_lut, setup_core_lut)

    assert cost_structure['single_sector_antenna'] == 1500 / setup_global_parameters['networks']
    assert cost_structure['single_remote_radio_unit'] == 4000 / setup_global_parameters['networks']


def test_greenfield_5g_nsa(setup_region, setup_option, setup_costs,
    setup_global_parameters, setup_backhaul_lut, setup_core_lut):

    setup_region[0]['new_sites'] = 1
    setup_region[0]['site_density'] = 0.5

    #test baseline infra sharing
    cost_structure = greenfield_5g_nsa(setup_region[0],
        '5G_nsa_microwave_baseline_baseline_baseline_baseline',
        setup_costs, setup_global_parameters,
        setup_backhaul_lut, setup_core_lut)

    assert cost_structure['single_sector_antenna'] == 1500
    assert cost_structure['single_remote_radio_unit'] == 4000
    assert cost_structure['tower'] == 10000
    assert cost_structure['civil_materials'] == 5000
    assert cost_structure['transportation'] == 5000
    assert cost_structure['installation'] == 5000
    assert cost_structure['site_rental'] == 9600
    assert cost_structure['power_generator_battery_system'] == 5000
    assert cost_structure['router'] == 2000

    #test passive infra sharing
    cost_structure = greenfield_5g_nsa(setup_region[0],
        '5G_nsa_microwave_passive_baseline_baseline_baseline',
        setup_costs, setup_global_parameters,
        setup_backhaul_lut, setup_core_lut)

    assert cost_structure['tower'] == 10000 / setup_global_parameters['networks']
    assert cost_structure['civil_materials'] == 5000 / setup_global_parameters['networks']

    #test active infra sharing
    cost_structure = greenfield_5g_nsa(setup_region[0],
        '5G_nsa_microwave_active_baseline_baseline_baseline',
        setup_costs, setup_global_parameters,
        setup_backhaul_lut, setup_core_lut)

    assert cost_structure['single_sector_antenna'] == 1500 / setup_global_parameters['networks']
    assert cost_structure['single_remote_radio_unit'] == 4000 / setup_global_parameters['networks']
    assert cost_structure['civil_materials'] == 5000 / setup_global_parameters['networks']


def test_upgrade_to_5g_nsa(setup_region, setup_option, setup_costs,
    setup_global_parameters, setup_backhaul_lut, setup_core_lut):

    setup_region[0]['upgraded_sites'] = 1
    setup_region[0]['sites_3G'] = 1
    setup_region[0]['site_density'] = 0.5

    cost_structure = upgrade_to_5g_nsa(setup_region[0],
        '5G_nsa_microwave_baseline_baseline_baseline_baseline',
        setup_costs, setup_global_parameters,
        setup_backhaul_lut, setup_core_lut)

    assert cost_structure['single_sector_antenna'] == 1500
    assert cost_structure['single_remote_radio_unit'] == 4000
    assert cost_structure['installation'] == 5000
    assert cost_structure['site_rental'] == 9600
    assert cost_structure['router'] == 2000

    #test passive infra sharing
    cost_structure = upgrade_to_5g_nsa(setup_region[0],
        '5G_nsa_microwave_passive_baseline_baseline_baseline',
        setup_costs, setup_global_parameters,
        setup_backhaul_lut, setup_core_lut)

    assert cost_structure['site_rental'] == 9600 / setup_global_parameters['networks']

    #test active infra sharing
    cost_structure = upgrade_to_5g_nsa(setup_region[0],
        '5G_nsa_microwave_active_baseline_baseline_baseline',
        setup_costs, setup_global_parameters,
        setup_backhaul_lut, setup_core_lut)

    assert cost_structure['single_sector_antenna'] == 1500 / setup_global_parameters['networks']
    assert cost_structure['single_remote_radio_unit'] == 4000 / setup_global_parameters['networks']



def test_greenfield_5g_sa(setup_region, setup_option, setup_costs,
    setup_global_parameters, setup_backhaul_lut, setup_core_lut):

    setup_region[0]['new_sites'] = 1
    setup_region[0]['site_density'] = 0.5

    cost_structure = greenfield_5g_sa(setup_region[0],
        '5G_sa_microwave_baseline_baseline_baseline_baseline',
        setup_costs, setup_global_parameters,
        setup_backhaul_lut, setup_core_lut)

    assert cost_structure['single_sector_antenna'] == 1500
    assert cost_structure['single_remote_radio_unit'] == 4000
    assert cost_structure['cots_processing'] == 500
    assert cost_structure['tower'] == 10000
    assert cost_structure['civil_materials'] == 5000
    assert cost_structure['transportation'] == 5000
    assert cost_structure['installation'] == 5000
    assert cost_structure['site_rental'] == 9600
    assert cost_structure['power_generator_battery_system'] == 5000
    assert cost_structure['router'] == 2000

    #test passive infra sharing
    cost_structure = greenfield_5g_sa(setup_region[0],
        '5g_sa_microwave_passive_baseline_baseline_baseline',
        setup_costs, setup_global_parameters,
        setup_backhaul_lut, setup_core_lut)

    assert cost_structure['tower'] == 10000 / setup_global_parameters['networks']
    assert cost_structure['civil_materials'] == 5000 / setup_global_parameters['networks']

    #test active infra sharing
    cost_structure = greenfield_5g_sa(setup_region[0],
        '5g_sa_microwave_active_baseline_baseline_baseline',
        setup_costs, setup_global_parameters,
        setup_backhaul_lut, setup_core_lut)

    assert cost_structure['single_sector_antenna'] == 1500 / setup_global_parameters['networks']
    assert cost_structure['single_remote_radio_unit'] == 4000 / setup_global_parameters['networks']
    assert cost_structure['cloud_power_supply_converter'] == 1000 / setup_global_parameters['networks']
    assert cost_structure['software'] == 50 / setup_global_parameters['networks']
    assert cost_structure['civil_materials'] == 5000 / setup_global_parameters['networks']


def test_upgrade_to_5g_sa(setup_region, setup_option, setup_costs,
    setup_global_parameters, setup_backhaul_lut, setup_core_lut):

    setup_region[0]['upgraded_sites'] = 1
    setup_region[0]['sites_3G'] = 1
    setup_region[0]['site_density'] = 0.5

    cost_structure = upgrade_to_5g_sa(setup_region[0],
        '5G_sa_microwave_baseline_baseline_baseline_baseline',
        setup_costs, setup_global_parameters,
        setup_backhaul_lut, setup_core_lut)

    assert cost_structure['single_sector_antenna'] == 1500
    assert cost_structure['single_remote_radio_unit'] == 4000
    assert cost_structure['cots_processing'] == 500
    assert cost_structure['installation'] == 5000
    assert cost_structure['site_rental'] == 9600
    assert cost_structure['low_latency_switch'] == 500
    assert cost_structure['router'] == 2000

    #test passive infra sharing
    cost_structure = upgrade_to_5g_sa(setup_region[0],
        '5g_sa_microwave_passive_baseline_baseline_baseline',
        setup_costs, setup_global_parameters,
        setup_backhaul_lut, setup_core_lut)

    assert cost_structure['site_rental'] == 9600 / setup_global_parameters['networks']

    #test active infra sharing
    cost_structure = upgrade_to_5g_sa(setup_region[0],
        '5g_sa_microwave_active_baseline_baseline_baseline',
        setup_costs, setup_global_parameters,
        setup_backhaul_lut, setup_core_lut)

    assert cost_structure['single_sector_antenna'] == 1500 / setup_global_parameters['networks']
    assert cost_structure['single_remote_radio_unit'] == 4000 / setup_global_parameters['networks']
    assert cost_structure['cloud_power_supply_converter'] == 1000 / setup_global_parameters['networks']
    assert cost_structure['software'] == 50 / setup_global_parameters['networks']


def test_get_fronthaul_costs(setup_region, setup_costs):

    setup_region[0]['site_density'] = 0.5

    assert get_fronthaul_costs(setup_region[0], setup_costs, ) == (
        setup_costs['fiber_fronthaul_urban_m'] * math.sqrt(1/setup_region[0]['site_density']))

    setup_region[0]['site_density'] = 4

    assert get_fronthaul_costs(setup_region[0], setup_costs, ) == (
        setup_costs['fiber_fronthaul_urban_m'] * math.sqrt(1/setup_region[0]['site_density']))


def test_get_backhaul_costs(setup_region, setup_costs, setup_backhaul_lut):

    assert get_backhaul_costs(setup_region[0], 'microwave',
        setup_costs, {'MWI.1.1.1_1': 1000}) == (setup_costs['microwave_backhaul_small'])

    assert get_backhaul_costs(setup_region[0], 'microwave',
        setup_costs, {'MWI.1.1.1_1': 21000}) == (setup_costs['microwave_backhaul_medium'])

    assert get_backhaul_costs(setup_region[0], 'microwave',
        setup_costs, {'MWI.1.1.1_1': 41000}) == (setup_costs['microwave_backhaul_large'])

    assert get_backhaul_costs(setup_region[0], 'fiber',
        setup_costs, {'MWI.1.1.1_1': 1000}) == (setup_costs['fiber_backhaul_urban_m'] * 1000)

    assert get_backhaul_costs(setup_region[0], 'incorrect_baclhaul_tech_name',
        setup_costs, {'MWI.1.1.1_1': 1000}) == 'Did not recognise the backhaul technology'


def test_get_core_costs(setup_region, setup_costs, setup_core_lut):

    assert get_core_costs(setup_region[0], 'core_edges', setup_costs,
        setup_core_lut, 'epc') == (setup_costs['core_edges'] * 1000)

    assert get_core_costs(setup_region[0], 'core_nodes', setup_costs,
        setup_core_lut, 'epc') == (setup_costs['core_nodes_{}'.format('epc')] * 2)

    assert get_core_costs(setup_region[0], 'regional_edges', setup_costs,
        setup_core_lut, 'epc') == (setup_costs['regional_edges'] * 1000)

    assert get_core_costs(setup_region[0], 'regional_nodes', setup_costs,
        setup_core_lut, 'epc') == (setup_costs['regional_nodes_{}'.format('epc')] * 2)

    assert get_core_costs(setup_region[0], 'incorrrect_asset_name', setup_costs,
        setup_core_lut, 'epc') == 'Did not recognise core asset type'

    setup_region[0]['GID_id'] == 'unknown'

    assert get_core_costs(setup_region[0], 'core_edges', setup_costs,
        setup_core_lut, 'epc') == 20000

    assert get_core_costs(setup_region[0], 'regional_edges', setup_costs,
        setup_core_lut, 'epc') == 10000

    assert get_core_costs(setup_region[0], 'regional_nodes', setup_costs,
        setup_core_lut, 'epc') == 200000


def test_discount_capex_and_opex(setup_global_parameters):

    assert discount_capex_and_opex(1000, setup_global_parameters) == 1195


def test_discount_opex(setup_global_parameters):

    assert discount_opex(1000, setup_global_parameters) == 1952


def test_calc_costs(setup_global_parameters):

    answer = calc_costs({'single_sector_antenna': 1500}, 6, setup_global_parameters)

    assert answer == 5379

    answer = calc_costs({'single_baseband_unit': 4000}, 6, setup_global_parameters)

    assert answer == 4781

    answer = calc_costs({'tower': 10000}, 6, setup_global_parameters)

    assert answer == 10000

    answer = calc_costs({'site_rental': 9600}, 6, setup_global_parameters)

    assert answer == 18743 #two years' of rent

    answer = calc_costs({
        'single_sector_antenna': 1500,
        'single_baseband_unit': 4000,
        'tower': 10000,
        'site_rental': 9600
        }, 6, setup_global_parameters)

    #answer = sum of antenna, bbu, tower, site_rental (5379 + 4781 + 10000 + 18743)
    assert answer == 38903

    answer = calc_costs({'incorrect_name': 9600}, 6, setup_global_parameters)

    assert answer == 0 #two years' of rent

    answer = calc_costs({
        'cots_processing': 6,
        'io_n2_n3': 6,
        'low_latency_switch': 6,
        'rack': 6,
        'cloud_power_supply_converter': 6,
        'software': 6,
        }, 6, setup_global_parameters)

    assert answer == sum([
        8, #cots_processing = capex + opex
        8, #io_n2_n3 = capex + opex
        8, #low_latency_switch = capex + opex
        6, #rack = capex
        8, #cloud_power_supply_converter = capex + opex
        12,#software = opex
    ])
