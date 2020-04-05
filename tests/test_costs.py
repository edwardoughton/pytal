import pytest
from pytal.costs import (greenfield_4g, upgrade_to_4g, greenfield_5g_nsa,
    upgrade_to_5g_nsa, greenfield_5g_sa, upgrade_to_5g_sa,
    get_backhaul_costs, get_core_costs, discount_opex, discount_capex_and_opex)


# def test_greenfield_4g(setup_region, setup_option, setup_costs,
#     setup_global_parameters, setup_backhaul_lut, setup_core_lut):

#     setup_region[0]['new_sites'] = 1

#     total_cost, cost_structure = greenfield_4g('MWI', setup_region[0],
#         '4G_epc_microwave_baseline_baseline_baseline_baseline',
#         setup_costs, setup_global_parameters,
#         setup_backhaul_lut, setup_core_lut)

#     assert cost_structure['antennas'] == 5379
#     assert cost_structure['remote_radio_units'] == 14343
#     assert cost_structure['single_baseband_unit'] == 11952
#     assert cost_structure['tower'] == 10000
#     assert cost_structure['civil_materials'] == 10000
#     assert cost_structure['transportation'] == 10000
#     assert cost_structure['installation'] == 5000
#     assert cost_structure['site_rental'] == 18743
#     assert cost_structure['power_generator_battery_system'] == 5976
#     assert cost_structure['high_speed_backhaul_hub'] == 17929
#     assert cost_structure['router'] == 2390
#     assert cost_structure['microwave_backhaul'] == 11952

#     assert total_cost == 637617

#     total_cost, cost_structure = greenfield_4g('MWI', setup_region[0],
#         '4G_epc_microwave_passive_baseline_baseline_baseline',
#         setup_costs, setup_global_parameters,
#         setup_backhaul_lut, setup_core_lut)

#     assert cost_structure['tower'] == 5000
#     assert cost_structure['civil_materials'] == 5000

#     assert total_cost == 607757.5

#     # total_cost, cost_structure = greenfield_4g('MWI', setup_region[0],
#     #     '4G_epc_microwave_active_baseline_baseline_baseline',
#     #     setup_costs, setup_global_parameters,
#     #     setup_backhaul_lut, setup_core_lut)

#     # assert cost_structure['antennas'] == (1500*3) / setup_global_parameters['networks']
#     # assert cost_structure['civil_materials'] == 5000

#     # assert total_cost == 607757.5


# def test_upgrade_to_4g(setup_region, setup_option, setup_costs,
#     setup_global_parameters, setup_backhaul_lut, setup_core_lut):

#     setup_region[0]['upgraded_sites'] = 1
#     setup_region[0]['sites_3G'] = 1

#     total_cost, cost_structure = upgrade_to_4g('MWI', setup_region[0],
#         '4G_epc_microwave_baseline_baseline_baseline_baseline',
#         setup_costs, setup_global_parameters,
#         setup_backhaul_lut, setup_core_lut)

#     assert cost_structure['antennas'] == 5379
#     assert cost_structure['remote_radio_units'] == 14343
#     assert cost_structure['single_baseband_unit'] == 11952
#     assert cost_structure['installation'] == 5000
#     assert cost_structure['high_speed_backhaul_hub'] == 17929
#     assert cost_structure['router'] == 2390
#     assert cost_structure['microwave_backhaul'] == 11952

#     assert total_cost == 582898


def test_greenfield_5g_nsa(setup_region, setup_option, setup_costs,
    setup_global_parameters, setup_backhaul_lut, setup_core_lut):

    setup_region[0]['new_sites'] = 1

    total_cost, cost_structure = greenfield_5g_nsa('MWI', setup_region[0],
        '5G_nsa_microwave_baseline_baseline_baseline_baseline',
        setup_costs, setup_global_parameters,
        setup_backhaul_lut, setup_core_lut)

    assert cost_structure['antennas'] == 5379
    assert cost_structure['remote_radio_units'] == 14343
    assert cost_structure['single_baseband_unit'] == 11952
    assert cost_structure['tower'] == 10000
    assert cost_structure['civil_materials'] == 10000
    assert cost_structure['transportation'] == 10000
    assert cost_structure['installation'] == 5000
    assert cost_structure['site_rental'] == 18743
    assert cost_structure['power_generator_battery_system'] == 5976
    assert cost_structure['high_speed_backhaul_hub'] == 17929
    assert cost_structure['router'] == 2390
    assert cost_structure['microwave_backhaul'] == 11952

    assert total_cost == 637617


# def test_upgrade_to_5g_nsa(setup_region, setup_option, setup_costs,
#     setup_global_parameters, setup_backhaul_lut, setup_core_lut):

#     setup_region[0]['upgraded_sites'] = 1
#     setup_region[0]['sites_3G'] = 1

#     total_cost, cost_structure = upgrade_to_5g_nsa('MWI', setup_region[0],
#         '5G_nsa_microwave_baseline_baseline_baseline_baseline',
#         setup_costs, setup_global_parameters,
#         setup_backhaul_lut, setup_core_lut)

#     assert cost_structure['antennas'] == 5379
#     assert cost_structure['remote_radio_units'] == 14343
#     assert cost_structure['single_baseband_unit'] == 11952
#     assert cost_structure['installation'] == 5000
#     assert cost_structure['high_speed_backhaul_hub'] == 17929
#     assert cost_structure['router'] == 2390
#     assert cost_structure['microwave_backhaul'] == 11952

#     assert total_cost == 582898


# def test_greenfield_5g_sa(setup_region, setup_option, setup_costs,
#     setup_global_parameters, setup_backhaul_lut, setup_core_lut):

#     setup_region[0]['new_sites'] = 1

#     total_cost, cost_structure = greenfield_5g_sa('MWI', setup_region[0],
#         '5G_sa_microwave_baseline_baseline_baseline_baseline',
#         setup_costs, setup_global_parameters,
#         setup_backhaul_lut, setup_core_lut)

#     assert cost_structure['antennas'] == 5379
#     assert cost_structure['remote_radio_units'] == 14343
#     assert cost_structure['single_baseband_unit'] == 11952
#     assert cost_structure['tower'] == 10000
#     assert cost_structure['civil_materials'] == 10000
#     assert cost_structure['transportation'] == 10000
#     assert cost_structure['installation'] == 5000
#     assert cost_structure['site_rental'] == 18743
#     assert cost_structure['power_generator_battery_system'] == 5976
#     assert cost_structure['high_speed_backhaul_hub'] == 17929
#     assert cost_structure['router'] == 2390
#     assert cost_structure['microwave_backhaul'] == 11952

#     assert total_cost == 637617


# def test_upgrade_to_5g_sa(setup_region, setup_option, setup_costs,
#     setup_global_parameters, setup_backhaul_lut, setup_core_lut):

#     setup_region[0]['upgraded_sites'] = 1
#     setup_region[0]['sites_3G'] = 1

#     total_cost, cost_structure = upgrade_to_5g_sa('MWI', setup_region[0],
#         '5G_sa_microwave_baseline_baseline_baseline_baseline',
#         setup_costs, setup_global_parameters,
#         setup_backhaul_lut, setup_core_lut)

#     assert cost_structure['antennas'] == 5379
#     assert cost_structure['remote_radio_units'] == 14343
#     assert cost_structure['single_baseband_unit'] == 11952
#     assert cost_structure['installation'] == 5000
#     assert cost_structure['high_speed_backhaul_hub'] == 17929
#     assert cost_structure['router'] == 2390
#     assert cost_structure['microwave_backhaul'] == 11952

#     assert total_cost == 582898


# def test_get_backhaul_costs(setup_region, setup_costs, setup_backhaul_lut):

#     assert get_backhaul_costs('MWI', setup_region[0], 'microwave',
#         setup_costs, {'MWI.1.1.1_1': 1000}) == (setup_costs['microwave_backhaul_small'])

#     assert get_backhaul_costs('MWI', setup_region[0], 'microwave',
#         setup_costs, {'MWI.1.1.1_1': 21000}) == (setup_costs['microwave_backhaul_medium'])

#     assert get_backhaul_costs('MWI', setup_region[0], 'microwave',
#         setup_costs, {'MWI.1.1.1_1': 41000}) == (setup_costs['microwave_backhaul_large'])

#     assert get_backhaul_costs('MWI', setup_region[0], 'fiber',
#         setup_costs, {'MWI.1.1.1_1': 1000}) == (setup_costs['fiber_backhaul_urban_m'] * 1000)


# def test_get_core_costs(setup_region, setup_costs, setup_core_lut):

#     assert get_core_costs('MWI', setup_region[0], 'core_edges', setup_costs,
#         setup_core_lut, 'epc') == (setup_costs['core_edges'] * 1000)

#     assert get_core_costs('MWI', setup_region[0], 'core_nodes', setup_costs,
#         setup_core_lut, 'epc') == (setup_costs['core_nodes_{}'.format('epc')] * 2)

#     assert get_core_costs('MWI', setup_region[0], 'regional_edges', setup_costs,
#         setup_core_lut, 'epc') == (setup_costs['regional_edges'] * 1000)

#     assert get_core_costs('MWI', setup_region[0], 'regional_nodes', setup_costs,
#         setup_core_lut, 'epc') == (setup_costs['regional_nodes_{}'.format('epc')] * 2)


# def test_discount_capex_and_opex(setup_global_parameters):

#     assert discount_capex_and_opex(1000, setup_global_parameters) == 1195


# def test_discount_opex(setup_global_parameters):

#     assert discount_opex(1000, setup_global_parameters) == 1952
