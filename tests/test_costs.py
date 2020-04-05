import pytest
from pytal.costs import (greenfield_4g, upgrade_to_4g, greenfield_5g_nsa,
    upgrade_to_5g_nsa, greenfield_5g_sa, upgrade_to_5g_sa,
    get_backhaul_costs, get_core_costs, discount_opex, discount_capex_and_opex, calc_costs)

#test approach is to:
#test each function which returns the cost structure
#test the function which calculates quantities
#test infrastructure sharing strategies

def test_greenfield_4g(setup_region, setup_option, setup_costs,
    setup_global_parameters, setup_backhaul_lut, setup_core_lut):

    setup_region[0]['new_sites'] = 1

    #test baseline infra sharing
    cost_structure = greenfield_4g('MWI', setup_region[0],
        '4G_epc_microwave_baseline_baseline_baseline_baseline',
        setup_costs, setup_global_parameters,
        setup_backhaul_lut, setup_core_lut)

    assert cost_structure['single_sector_antenna'] == 1500
    assert cost_structure['single_remote_radio_unit'] == 4000
    assert cost_structure['single_baseband_unit'] == 10000
    assert cost_structure['tower'] == 10000
    assert cost_structure['civil_materials'] == 10000
    assert cost_structure['transportation'] == 10000
    assert cost_structure['installation'] == 5000
    assert cost_structure['site_rental'] == 9600
    assert cost_structure['power_generator_battery_system'] == 5000
    assert cost_structure['high_speed_backhaul_hub'] == 15000
    assert cost_structure['router'] == 2000

    #test passive infra sharing
    cost_structure = greenfield_4g('MWI', setup_region[0],
        '4G_epc_microwave_passive_baseline_baseline_baseline',
        setup_costs, setup_global_parameters,
        setup_backhaul_lut, setup_core_lut)

    assert cost_structure['tower'] == 10000 / setup_global_parameters['networks']
    assert cost_structure['civil_materials'] == 10000 / setup_global_parameters['networks']

    #test active infra sharing
    cost_structure = greenfield_4g('MWI', setup_region[0],
        '4G_epc_microwave_active_baseline_baseline_baseline',
        setup_costs, setup_global_parameters,
        setup_backhaul_lut, setup_core_lut)

    assert cost_structure['single_sector_antenna'] == 1500 / setup_global_parameters['networks']
    assert cost_structure['single_remote_radio_unit'] == 4000 / setup_global_parameters['networks']
    assert cost_structure['single_baseband_unit'] == 10000 / setup_global_parameters['networks']
    assert cost_structure['civil_materials'] == 10000 / setup_global_parameters['networks']


def test_upgrade_to_4g(setup_region, setup_option, setup_costs,
    setup_global_parameters, setup_backhaul_lut, setup_core_lut):

    setup_region[0]['upgraded_sites'] = 1
    setup_region[0]['sites_3G'] = 1

    cost_structure = upgrade_to_4g('MWI', setup_region[0],
        '4G_epc_microwave_baseline_baseline_baseline_baseline',
        setup_costs, setup_global_parameters,
        setup_backhaul_lut, setup_core_lut)

    assert cost_structure['single_sector_antenna'] == 1500
    assert cost_structure['single_remote_radio_unit'] == 4000
    assert cost_structure['single_baseband_unit'] == 10000
    assert cost_structure['installation'] == 5000
    assert cost_structure['site_rental'] == 9600
    assert cost_structure['high_speed_backhaul_hub'] == 15000
    assert cost_structure['router'] == 2000

    #test passive infra sharing
    cost_structure = upgrade_to_4g('MWI', setup_region[0],
        '4G_epc_microwave_passive_baseline_baseline_baseline',
        setup_costs, setup_global_parameters,
        setup_backhaul_lut, setup_core_lut)

    assert cost_structure['site_rental'] == 9600 / setup_global_parameters['networks']

    #test active infra sharing
    cost_structure = upgrade_to_4g('MWI', setup_region[0],
        '4G_epc_microwave_active_baseline_baseline_baseline',
        setup_costs, setup_global_parameters,
        setup_backhaul_lut, setup_core_lut)

    assert cost_structure['single_sector_antenna'] == 1500 / setup_global_parameters['networks']
    assert cost_structure['single_remote_radio_unit'] == 4000 / setup_global_parameters['networks']
    assert cost_structure['single_baseband_unit'] == 10000 / setup_global_parameters['networks']


def test_greenfield_5g_nsa(setup_region, setup_option, setup_costs,
    setup_global_parameters, setup_backhaul_lut, setup_core_lut):

    setup_region[0]['new_sites'] = 1

    #test baseline infra sharing
    cost_structure = greenfield_5g_nsa('MWI', setup_region[0],
        '4G_epc_microwave_baseline_baseline_baseline_baseline',
        setup_costs, setup_global_parameters,
        setup_backhaul_lut, setup_core_lut)

    # TODO: assert total_cost == 522100
    assert cost_structure['single_sector_antenna'] == 1500
    assert cost_structure['single_remote_radio_unit'] == 4000
    assert cost_structure['single_baseband_unit'] == 10000
    assert cost_structure['tower'] == 10000
    assert cost_structure['civil_materials'] == 10000
    assert cost_structure['transportation'] == 10000
    assert cost_structure['installation'] == 5000
    assert cost_structure['site_rental'] == 9600
    assert cost_structure['power_generator_battery_system'] == 5000
    assert cost_structure['high_speed_backhaul_hub'] == 15000
    assert cost_structure['router'] == 2000

    #test passive infra sharing
    cost_structure = greenfield_5g_nsa('MWI', setup_region[0],
        '4G_epc_microwave_passive_baseline_baseline_baseline',
        setup_costs, setup_global_parameters,
        setup_backhaul_lut, setup_core_lut)

    assert cost_structure['tower'] == 10000 / setup_global_parameters['networks']
    assert cost_structure['civil_materials'] == 10000 / setup_global_parameters['networks']

    #test active infra sharing
    cost_structure = greenfield_5g_nsa('MWI', setup_region[0],
        '4G_epc_microwave_active_baseline_baseline_baseline',
        setup_costs, setup_global_parameters,
        setup_backhaul_lut, setup_core_lut)

    assert cost_structure['single_sector_antenna'] == 1500 / setup_global_parameters['networks']
    assert cost_structure['single_remote_radio_unit'] == 4000 / setup_global_parameters['networks']
    assert cost_structure['single_baseband_unit'] == 10000 / setup_global_parameters['networks']
    assert cost_structure['civil_materials'] == 10000 / setup_global_parameters['networks']


def test_upgrade_to_5g_nsa(setup_region, setup_option, setup_costs,
    setup_global_parameters, setup_backhaul_lut, setup_core_lut):

    setup_region[0]['upgraded_sites'] = 1
    setup_region[0]['sites_3G'] = 1

    cost_structure = upgrade_to_5g_nsa('MWI', setup_region[0],
        '5G_nsa_microwave_baseline_baseline_baseline_baseline',
        setup_costs, setup_global_parameters,
        setup_backhaul_lut, setup_core_lut)

    #TODO: assert total_cost == 692100
    assert cost_structure['single_sector_antenna'] == 1500
    assert cost_structure['single_remote_radio_unit'] == 4000
    assert cost_structure['single_baseband_unit'] == 10000
    assert cost_structure['installation'] == 5000
    assert cost_structure['site_rental'] == 9600
    assert cost_structure['high_speed_backhaul_hub'] == 15000
    assert cost_structure['router'] == 2000

    #test passive infra sharing
    cost_structure = upgrade_to_5g_nsa('MWI', setup_region[0],
        '4G_epc_microwave_passive_baseline_baseline_baseline',
        setup_costs, setup_global_parameters,
        setup_backhaul_lut, setup_core_lut)

    assert cost_structure['site_rental'] == 9600 / setup_global_parameters['networks']

    #test active infra sharing
    cost_structure = upgrade_to_5g_nsa('MWI', setup_region[0],
        '4G_epc_microwave_active_baseline_baseline_baseline',
        setup_costs, setup_global_parameters,
        setup_backhaul_lut, setup_core_lut)

    assert cost_structure['single_sector_antenna'] == 1500 / setup_global_parameters['networks']
    assert cost_structure['single_remote_radio_unit'] == 4000 / setup_global_parameters['networks']
    assert cost_structure['single_baseband_unit'] == 10000 / setup_global_parameters['networks']


def test_greenfield_5g_sa(setup_region, setup_option, setup_costs,
    setup_global_parameters, setup_backhaul_lut, setup_core_lut):

    setup_region[0]['new_sites'] = 1

    cost_structure = greenfield_5g_sa('MWI', setup_region[0],
        '5G_sa_microwave_baseline_baseline_baseline_baseline',
        setup_costs, setup_global_parameters,
        setup_backhaul_lut, setup_core_lut)

    #TODO assert total_cost == 522100
    assert cost_structure['single_sector_antenna'] == 1500
    assert cost_structure['single_remote_radio_unit'] == 4000
    assert cost_structure['single_baseband_unit'] == 10000
    assert cost_structure['tower'] == 10000
    assert cost_structure['civil_materials'] == 10000
    assert cost_structure['transportation'] == 10000
    assert cost_structure['installation'] == 5000
    assert cost_structure['site_rental'] == 9600
    assert cost_structure['power_generator_battery_system'] == 5000
    assert cost_structure['high_speed_backhaul_hub'] == 15000
    assert cost_structure['router'] == 2000

    #test passive infra sharing
    cost_structure = greenfield_5g_sa('MWI', setup_region[0],
        '4G_epc_microwave_passive_baseline_baseline_baseline',
        setup_costs, setup_global_parameters,
        setup_backhaul_lut, setup_core_lut)

    assert cost_structure['tower'] == 10000 / setup_global_parameters['networks']
    assert cost_structure['civil_materials'] == 10000 / setup_global_parameters['networks']

    #test active infra sharing
    cost_structure = greenfield_5g_sa('MWI', setup_region[0],
        '4G_epc_microwave_active_baseline_baseline_baseline',
        setup_costs, setup_global_parameters,
        setup_backhaul_lut, setup_core_lut)

    assert cost_structure['single_sector_antenna'] == 1500 / setup_global_parameters['networks']
    assert cost_structure['single_remote_radio_unit'] == 4000 / setup_global_parameters['networks']
    assert cost_structure['single_baseband_unit'] == 10000 / setup_global_parameters['networks']
    assert cost_structure['civil_materials'] == 10000 / setup_global_parameters['networks']



def test_upgrade_to_5g_sa(setup_region, setup_option, setup_costs,
    setup_global_parameters, setup_backhaul_lut, setup_core_lut):

    setup_region[0]['upgraded_sites'] = 1
    setup_region[0]['sites_3G'] = 1

    cost_structure = upgrade_to_5g_sa('MWI', setup_region[0],
        '5G_sa_microwave_baseline_baseline_baseline_baseline',
        setup_costs, setup_global_parameters,
        setup_backhaul_lut, setup_core_lut)

    #TODO: assert total_cost == 692100
    assert cost_structure['single_sector_antenna'] == 1500
    assert cost_structure['single_remote_radio_unit'] == 4000
    assert cost_structure['single_baseband_unit'] == 10000
    assert cost_structure['installation'] == 5000
    assert cost_structure['site_rental'] == 9600
    assert cost_structure['high_speed_backhaul_hub'] == 15000
    assert cost_structure['router'] == 2000

    #test passive infra sharing
    cost_structure = upgrade_to_5g_sa('MWI', setup_region[0],
        '4G_epc_microwave_passive_baseline_baseline_baseline',
        setup_costs, setup_global_parameters,
        setup_backhaul_lut, setup_core_lut)

    assert cost_structure['site_rental'] == 9600 / setup_global_parameters['networks']

    #test active infra sharing
    cost_structure = upgrade_to_5g_sa('MWI', setup_region[0],
        '4G_epc_microwave_active_baseline_baseline_baseline',
        setup_costs, setup_global_parameters,
        setup_backhaul_lut, setup_core_lut)

    assert cost_structure['single_sector_antenna'] == 1500 / setup_global_parameters['networks']
    assert cost_structure['single_remote_radio_unit'] == 4000 / setup_global_parameters['networks']
    assert cost_structure['single_baseband_unit'] == 10000 / setup_global_parameters['networks']


def test_get_backhaul_costs(setup_region, setup_costs, setup_backhaul_lut):

    assert get_backhaul_costs('MWI', setup_region[0], 'microwave',
        setup_costs, {'MWI.1.1.1_1': 1000}) == (setup_costs['microwave_backhaul_small'])

    assert get_backhaul_costs('MWI', setup_region[0], 'microwave',
        setup_costs, {'MWI.1.1.1_1': 21000}) == (setup_costs['microwave_backhaul_medium'])

    assert get_backhaul_costs('MWI', setup_region[0], 'microwave',
        setup_costs, {'MWI.1.1.1_1': 41000}) == (setup_costs['microwave_backhaul_large'])

    assert get_backhaul_costs('MWI', setup_region[0], 'fiber',
        setup_costs, {'MWI.1.1.1_1': 1000}) == (setup_costs['fiber_backhaul_urban_m'] * 1000)


def test_get_core_costs(setup_region, setup_costs, setup_core_lut):

    assert get_core_costs('MWI', setup_region[0], 'core_edges', setup_costs,
        setup_core_lut, 'epc') == (setup_costs['core_edges'] * 1000)

    assert get_core_costs('MWI', setup_region[0], 'core_nodes', setup_costs,
        setup_core_lut, 'epc') == (setup_costs['core_nodes_{}'.format('epc')] * 2)

    assert get_core_costs('MWI', setup_region[0], 'regional_edges', setup_costs,
        setup_core_lut, 'epc') == (setup_costs['regional_edges'] * 1000)

    assert get_core_costs('MWI', setup_region[0], 'regional_nodes', setup_costs,
        setup_core_lut, 'epc') == (setup_costs['regional_nodes_{}'.format('epc')] * 2)


def test_discount_capex_and_opex(setup_global_parameters):

    assert discount_capex_and_opex(1000, setup_global_parameters) == 1195


def test_discount_opex(setup_global_parameters):

    assert discount_opex(1000, setup_global_parameters) == 1952


def test_calc_costs(setup_global_parameters):

    answer = calc_costs({'single_sector_antenna': 1500}, setup_global_parameters)

    assert answer == 5379

    answer = calc_costs({'single_baseband_unit': 4000}, setup_global_parameters)

    assert answer == 4781

    answer = calc_costs({'tower': 10000}, setup_global_parameters)

    assert answer == 10000

    answer = calc_costs({'site_rental': 9600}, setup_global_parameters)

    assert answer == 18743 #two years' of rent

    answer = calc_costs({
        'single_sector_antenna': 1500,
        'single_baseband_unit': 4000,
        'tower': 10000,
        'site_rental': 9600
        }, setup_global_parameters)

    #answer = sum of antenna, bbu, tower, site_rental (5379 + 4781 + 10000 + 18743)
    assert answer == 38903

    answer = calc_costs({'incorrect_name': 9600}, setup_global_parameters)

    assert answer == 0 #two years' of rent
