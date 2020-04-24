# import pytest
# import math
# from pytal.costs import (greenfield_4g, upgrade_to_4g, greenfield_5g_nsa,
#     upgrade_to_5g_nsa, greenfield_5g_sa, upgrade_to_5g_sa, get_fronthaul_costs,
#     get_backhaul_costs, discount_opex, discount_capex_and_opex,
#     calc_costs, find_single_network_cost, estimate_backhaul_length)

# #test approach is to:
# #test each function which returns the cost structure
# #test the function which calculates quantities
# #test infrastructure sharing strategies
# #test meta cost function

# def test_greenfield_4g(setup_region, setup_option, setup_costs,
#     setup_global_parameters, setup_backhaul_lut, setup_core_lut):

#     setup_region[0]['new_sites'] = 1
#     setup_region[0]['site_density'] = 0.5

#     #test baseline infra sharing
#     cost_structure = greenfield_4g(setup_region[0],
#         '4G_epc_microwave_baseline_baseline_baseline_baseline',
#         setup_costs, setup_global_parameters,
#         setup_backhaul_lut, setup_core_lut)

#     assert cost_structure['single_sector_antenna'] == 1500
#     assert cost_structure['single_remote_radio_unit'] == 4000
#     assert cost_structure['io_fronthaul'] ==1500
#     assert cost_structure['tower'] == 10000
#     assert cost_structure['civil_materials'] == 5000
#     assert cost_structure['transportation'] == 5000
#     assert cost_structure['installation'] == 5000
#     assert cost_structure['site_rental'] == 9600
#     assert cost_structure['power_generator_battery_system'] == 5000
#     assert cost_structure['io_s1_x2'] == 1500
#     assert cost_structure['router'] == 2000

#     #test passive infra sharing
#     cost_structure = greenfield_4g(setup_region[0],
#         '4G_epc_microwave_passive_baseline_baseline_baseline',
#         setup_costs, setup_global_parameters,
#         setup_backhaul_lut, setup_core_lut)

#     assert cost_structure['tower'] == 10000 / setup_global_parameters['networks']
#     assert cost_structure['civil_materials'] == 5000 / setup_global_parameters['networks']

#     #test active infra sharing
#     cost_structure = greenfield_4g(setup_region[0],
#         '4G_epc_microwave_active_baseline_baseline_baseline',
#         setup_costs, setup_global_parameters,
#         setup_backhaul_lut, setup_core_lut)

#     assert cost_structure['single_sector_antenna'] == 1500 / setup_global_parameters['networks']
#     assert cost_structure['single_remote_radio_unit'] == 4000 / setup_global_parameters['networks']
#     assert cost_structure['bbu_cabinet'] == 500 / setup_global_parameters['networks']
#     assert cost_structure['civil_materials'] == 5000 / setup_global_parameters['networks']


# def test_upgrade_to_4g(setup_region, setup_option, setup_costs,
#     setup_global_parameters, setup_backhaul_lut, setup_core_lut):

#     setup_region[0]['upgraded_sites'] = 1
#     setup_region[0]['sites_3G'] = 1
#     setup_region[0]['site_density'] = 0.5

#     cost_structure = upgrade_to_4g(setup_region[0],
#         '4G_epc_microwave_baseline_baseline_baseline_baseline',
#         setup_costs, setup_global_parameters,
#         setup_backhaul_lut, setup_core_lut)

#     assert cost_structure['single_sector_antenna'] == 1500
#     assert cost_structure['single_remote_radio_unit'] == 4000
#     assert cost_structure['installation'] == 5000
#     assert cost_structure['site_rental'] == 9600
#     assert cost_structure['router'] == 2000

#     #test passive infra sharing
#     cost_structure = upgrade_to_4g(setup_region[0],
#         '4G_epc_microwave_passive_baseline_baseline_baseline',
#         setup_costs, setup_global_parameters,
#         setup_backhaul_lut, setup_core_lut)

#     assert cost_structure['site_rental'] == 9600 / setup_global_parameters['networks']

#     #test active infra sharing
#     cost_structure = upgrade_to_4g(setup_region[0],
#         '4G_epc_microwave_active_baseline_baseline_baseline',
#         setup_costs, setup_global_parameters,
#         setup_backhaul_lut, setup_core_lut)

#     assert cost_structure['single_sector_antenna'] == 1500 / setup_global_parameters['networks']
#     assert cost_structure['single_remote_radio_unit'] == 4000 / setup_global_parameters['networks']


# def test_greenfield_5g_nsa(setup_region, setup_option, setup_costs,
#     setup_global_parameters, setup_backhaul_lut, setup_core_lut):

#     setup_region[0]['new_sites'] = 1
#     setup_region[0]['site_density'] = 0.5

#     #test baseline infra sharing
#     cost_structure = greenfield_5g_nsa(setup_region[0],
#         '5G_nsa_microwave_baseline_baseline_baseline_baseline',
#         setup_costs, setup_global_parameters,
#         setup_backhaul_lut, setup_core_lut)

#     assert cost_structure['single_sector_antenna'] == 1500
#     assert cost_structure['single_remote_radio_unit'] == 4000
#     assert cost_structure['tower'] == 10000
#     assert cost_structure['civil_materials'] == 5000
#     assert cost_structure['transportation'] == 5000
#     assert cost_structure['installation'] == 5000
#     assert cost_structure['site_rental'] == 9600
#     assert cost_structure['power_generator_battery_system'] == 5000
#     assert cost_structure['router'] == 2000

#     #test passive infra sharing
#     cost_structure = greenfield_5g_nsa(setup_region[0],
#         '5G_nsa_microwave_passive_baseline_baseline_baseline',
#         setup_costs, setup_global_parameters,
#         setup_backhaul_lut, setup_core_lut)

#     assert cost_structure['tower'] == 10000 / setup_global_parameters['networks']
#     assert cost_structure['civil_materials'] == 5000 / setup_global_parameters['networks']

#     #test active infra sharing
#     cost_structure = greenfield_5g_nsa(setup_region[0],
#         '5G_nsa_microwave_active_baseline_baseline_baseline',
#         setup_costs, setup_global_parameters,
#         setup_backhaul_lut, setup_core_lut)

#     assert cost_structure['single_sector_antenna'] == 1500 / setup_global_parameters['networks']
#     assert cost_structure['single_remote_radio_unit'] == 4000 / setup_global_parameters['networks']
#     assert cost_structure['civil_materials'] == 5000 / setup_global_parameters['networks']


# def test_upgrade_to_5g_nsa(setup_region, setup_option, setup_costs,
#     setup_global_parameters, setup_backhaul_lut, setup_core_lut):

#     setup_region[0]['upgraded_sites'] = 1
#     setup_region[0]['sites_3G'] = 1
#     setup_region[0]['site_density'] = 0.5

#     cost_structure = upgrade_to_5g_nsa(setup_region[0],
#         '5G_nsa_microwave_baseline_baseline_baseline_baseline',
#         setup_costs, setup_global_parameters,
#         setup_backhaul_lut, setup_core_lut)

#     assert cost_structure['single_sector_antenna'] == 1500
#     assert cost_structure['single_remote_radio_unit'] == 4000
#     assert cost_structure['installation'] == 5000
#     assert cost_structure['site_rental'] == 9600
#     assert cost_structure['router'] == 2000

#     #test passive infra sharing
#     cost_structure = upgrade_to_5g_nsa(setup_region[0],
#         '5G_nsa_microwave_passive_baseline_baseline_baseline',
#         setup_costs, setup_global_parameters,
#         setup_backhaul_lut, setup_core_lut)

#     assert cost_structure['site_rental'] == 9600 / setup_global_parameters['networks']

#     #test active infra sharing
#     cost_structure = upgrade_to_5g_nsa(setup_region[0],
#         '5G_nsa_microwave_active_baseline_baseline_baseline',
#         setup_costs, setup_global_parameters,
#         setup_backhaul_lut, setup_core_lut)

#     assert cost_structure['single_sector_antenna'] == 1500 / setup_global_parameters['networks']
#     assert cost_structure['single_remote_radio_unit'] == 4000 / setup_global_parameters['networks']



# def test_greenfield_5g_sa(setup_region, setup_option, setup_costs,
#     setup_global_parameters, setup_backhaul_lut, setup_core_lut):

#     setup_region[0]['new_sites'] = 1
#     setup_region[0]['site_density'] = 0.5

#     cost_structure = greenfield_5g_sa(setup_region[0],
#         '5G_sa_microwave_baseline_baseline_baseline_baseline',
#         setup_costs, setup_global_parameters,
#         setup_backhaul_lut, setup_core_lut)

#     assert cost_structure['single_sector_antenna'] == 1500
#     assert cost_structure['single_remote_radio_unit'] == 4000
#     assert cost_structure['cots_processing'] == 500
#     assert cost_structure['tower'] == 10000
#     assert cost_structure['civil_materials'] == 5000
#     assert cost_structure['transportation'] == 5000
#     assert cost_structure['installation'] == 5000
#     assert cost_structure['site_rental'] == 9600
#     assert cost_structure['power_generator_battery_system'] == 5000
#     assert cost_structure['router'] == 2000

#     #test passive infra sharing
#     cost_structure = greenfield_5g_sa(setup_region[0],
#         '5g_sa_microwave_passive_baseline_baseline_baseline',
#         setup_costs, setup_global_parameters,
#         setup_backhaul_lut, setup_core_lut)

#     assert cost_structure['tower'] == 10000 / setup_global_parameters['networks']
#     assert cost_structure['civil_materials'] == 5000 / setup_global_parameters['networks']

#     #test active infra sharing
#     cost_structure = greenfield_5g_sa(setup_region[0],
#         '5g_sa_microwave_active_baseline_baseline_baseline',
#         setup_costs, setup_global_parameters,
#         setup_backhaul_lut, setup_core_lut)

#     assert cost_structure['single_sector_antenna'] == 1500 / setup_global_parameters['networks']
#     assert cost_structure['single_remote_radio_unit'] == 4000 / setup_global_parameters['networks']
#     assert cost_structure['cloud_power_supply_converter'] == 1000 / setup_global_parameters['networks']
#     assert cost_structure['software'] == 50 / setup_global_parameters['networks']
#     assert cost_structure['civil_materials'] == 5000 / setup_global_parameters['networks']


# def test_upgrade_to_5g_sa(setup_region, setup_option, setup_costs,
#     setup_global_parameters, setup_backhaul_lut, setup_core_lut):

#     setup_region[0]['upgraded_sites'] = 1
#     setup_region[0]['sites_3G'] = 1
#     setup_region[0]['site_density'] = 0.5

#     cost_structure = upgrade_to_5g_sa(setup_region[0],
#         '5G_sa_microwave_baseline_baseline_baseline_baseline',
#         setup_costs, setup_global_parameters,
#         setup_backhaul_lut, setup_core_lut)

#     assert cost_structure['single_sector_antenna'] == 1500
#     assert cost_structure['single_remote_radio_unit'] == 4000
#     assert cost_structure['cots_processing'] == 500
#     assert cost_structure['installation'] == 5000
#     assert cost_structure['site_rental'] == 9600
#     assert cost_structure['low_latency_switch'] == 500
#     assert cost_structure['router'] == 2000

#     #test passive infra sharing
#     cost_structure = upgrade_to_5g_sa(setup_region[0],
#         '5g_sa_microwave_passive_baseline_baseline_baseline',
#         setup_costs, setup_global_parameters,
#         setup_backhaul_lut, setup_core_lut)

#     assert cost_structure['site_rental'] == 9600 / setup_global_parameters['networks']

#     #test active infra sharing
#     cost_structure = upgrade_to_5g_sa(setup_region[0],
#         '5g_sa_microwave_active_baseline_baseline_baseline',
#         setup_costs, setup_global_parameters,
#         setup_backhaul_lut, setup_core_lut)

#     assert cost_structure['single_sector_antenna'] == 1500 / setup_global_parameters['networks']
#     assert cost_structure['single_remote_radio_unit'] == 4000 / setup_global_parameters['networks']
#     assert cost_structure['cloud_power_supply_converter'] == 1000 / setup_global_parameters['networks']
#     assert cost_structure['software'] == 50 / setup_global_parameters['networks']


# def test_get_fronthaul_costs(setup_region, setup_costs):

#     setup_region[0]['site_density'] = 4

#     assert get_fronthaul_costs(setup_region[0], setup_costs) == (
#         setup_costs['fiber_fronthaul_urban_m'] * math.sqrt(1/setup_region[0]['site_density'])) * 1000

#     setup_region[0]['site_density'] = 0.5

#     assert get_fronthaul_costs(setup_region[0], setup_costs) == (
#         setup_costs['fiber_fronthaul_urban_m'] * math.sqrt(1/setup_region[0]['site_density'])) * 1000

#     setup_region[0]['site_density'] = 0.00001

#     assert get_fronthaul_costs(setup_region[0], setup_costs) == (
#         setup_costs['fiber_fronthaul_urban_m'] * math.sqrt(1/setup_region[0]['site_density'])) * 1000


# def test_get_backhaul_costs(setup_region, setup_costs, setup_backhaul_lut, setup_core_lut):

#     assert get_backhaul_costs(setup_region[0], 'microwave',
#         setup_costs, setup_backhaul_lut, setup_core_lut) == (setup_costs['microwave_backhaul_small'])

#     setup_region[0]['area_km2'] = 5000

#     assert get_backhaul_costs(setup_region[0], 'microwave',
#         setup_costs, setup_backhaul_lut, setup_core_lut) == (setup_costs['microwave_backhaul_medium'])

#     setup_region[0]['area_km2'] = 10000

#     assert get_backhaul_costs(setup_region[0], 'microwave',
#         setup_costs, setup_backhaul_lut, setup_core_lut) == (setup_costs['microwave_backhaul_large'])

#     setup_region[0]['area_km2'] = 2

#     assert get_backhaul_costs(setup_region[0], 'fiber',
#         setup_costs, setup_backhaul_lut, setup_core_lut) == (setup_costs['fiber_backhaul_urban_m'] * 500)

#     assert get_backhaul_costs(setup_region[0], 'incorrect_baclhaul_tech_name',
#         setup_costs, setup_backhaul_lut, setup_core_lut) == 'Did not recognise the backhaul technology'


# def test_estimate_backhaul_length(setup_backhaul_lut):

#     assert estimate_backhaul_length(1, setup_backhaul_lut) == 500

#     assert estimate_backhaul_length(0.1, setup_backhaul_lut) == 1500

#     assert estimate_backhaul_length(0.00000001, setup_backhaul_lut) == 5242880

#     assert estimate_backhaul_length(0.145, setup_backhaul_lut) == 1450

#     assert estimate_backhaul_length(0.000000001, setup_backhaul_lut) == 5242880

#     assert estimate_backhaul_length(2, setup_backhaul_lut) == 500


# # def test_get_core_costs(setup_region, setup_costs, setup_core_lut):

# #     assert get_core_costs(setup_region[0], 'core_edge', setup_costs,
# #         setup_core_lut, 'epc') == (setup_costs['core_edge'] * 1000)

# #     assert get_core_costs(setup_region[0], 'core_node', setup_costs,
# #         setup_core_lut, 'epc') == (setup_costs['core_node_{}'.format('epc')] * 2)

# #     assert get_core_costs(setup_region[0], 'regional_edge', setup_costs,
# #         setup_core_lut, 'epc') == (setup_costs['regional_edge'] * 1000)

# #     assert get_core_costs(setup_region[0], 'regional_node', setup_costs,
# #         setup_core_lut, 'epc') == 110000

# #     assert get_core_costs(setup_region[0], 'incorrrect_asset_name', setup_costs,
# #         setup_core_lut, 'epc') == 'Did not recognise core asset type'

# #     setup_region[0]['GID_id'] == 'unknown'

# #     assert get_core_costs(setup_region[0], 'core_edge', setup_costs,
# #         setup_core_lut, 'epc') == 20000

# #     assert get_core_costs(setup_region[0], 'regional_edge', setup_costs,
# #         setup_core_lut, 'epc') == 10000

# #     setup_core_lut['regional_node']['MWI.1.1.1_1'] = 3

# #     assert get_core_costs(setup_region[0], 'regional_node', setup_costs,
# #         setup_core_lut, 'epc') == 120000

# #     setup_core_lut['regional_node']['MWI.1.1.1_1'] = 10
# #     setup_region[0]['area_km2'] = 100

# #     assert get_core_costs(setup_region[0], 'regional_node', setup_costs,
# #         setup_core_lut, 'epc') == 370000

# def test_discount_capex_and_opex(setup_global_parameters):

#     assert discount_capex_and_opex(1000, setup_global_parameters) == 1195


# def test_discount_opex(setup_global_parameters):

#     assert discount_opex(1000, setup_global_parameters) == 1952


# # def test_calc_costs(setup_region, setup_global_parameters):

# #     setup_region[0]['sites_4G'] = 0
# #     setup_region[0]['upgraded_sites'] = 1
# #     setup_region[0]['new_sites'] = 1

# #     answer, structure = calc_costs(setup_region[0], {'single_sector_antenna': 1500}, 1, setup_global_parameters)

# #     assert answer == 5379

# #     answer, structure = calc_costs(setup_region[0], {'single_baseband_unit': 4000}, 1, setup_global_parameters)

# #     assert answer == 4781

# #     answer, structure = calc_costs(setup_region[0], {'tower': 10000}, 1, setup_global_parameters)

# #     assert answer == 10000

# #     answer, structure = calc_costs(setup_region[0], {'site_rental': 9600}, 1, setup_global_parameters)

# #     assert answer == 18743 #two years' of rent

# #     answer, structure = calc_costs(setup_region[0], {
# #         'single_sector_antenna': 1500,
# #         'single_baseband_unit': 4000,
# #         'tower': 10000,
# #         'site_rental': 9600
# #         }, 6, setup_global_parameters)

# #     #answer = sum of antenna, bbu, tower, site_rental (5379 + 4781 + 10000 + 18743)
# #     assert answer == 38903

# #     answer, structure = calc_costs(setup_region[0], {'incorrect_name': 9600}, 1, setup_global_parameters)

# #     assert answer == 0 #two years' of rent

# #     answer, structure = calc_costs(setup_region[0], {
# #         'cots_processing': 6,
# #         'io_n2_n3': 6,
# #         'low_latency_switch': 6,
# #         'rack': 6,
# #         'cloud_power_supply_converter': 6,
# #         'software': 6,
# #         }, 1, setup_global_parameters)

# #     assert answer == sum([
# #         8, #cots_processing = capex + opex
# #         8, #io_n2_n3 = capex + opex
# #         8, #low_latency_switch = capex + opex
# #         6, #rack = capex
# #         8, #cloud_power_supply_converter = capex + opex
# #         12,#software = opex
# #     ])

# #     answer, structure = calc_costs(setup_region[0], {
# #         'backhaul': 100,
# #         }, 1, setup_global_parameters)

# #     assert answer == 120

# #     answer, structure = calc_costs(setup_region[0], {
# #         'backhaul': 100,
# #         }, 0, setup_global_parameters)

# #     assert answer == 0


# # def test_find_single_network_cost(setup_region, setup_costs,
# #     setup_global_parameters, setup_country_parameters,
# #     setup_backhaul_lut, setup_core_lut):

# #     setup_region[0]['sites_4G'] = 0
# #     setup_region[0]['new_sites'] = 1
# #     setup_region[0]['upgraded_sites'] = 1
# #     setup_region[0]['site_density'] = 0.5
# #     setup_region[0]['backhaul_new'] = 0

# #     answer = find_single_network_cost(
# #         setup_region[0],
# #         {'strategy': '4G_epc_microwave_baseline_baseline_baseline_baseline'},
# #         setup_costs,
# #         setup_global_parameters,
# #         setup_country_parameters,
# #         setup_backhaul_lut,
# #         setup_core_lut
# #     )

# #     #~42k is a single 4G upgraded site
# #     #~68k is a single 4G greenfield site
# #     assert answer['network_cost'] == 1138228

# #     setup_region[0]['sites_4G'] = 0
# #     setup_region[0]['new_sites'] = 1
# #     setup_region[0]['upgraded_sites'] = 1
# #     setup_region[0]['site_density'] = 0.5
# #     setup_region[0]['backhaul_new'] = 1

# #     answer = find_single_network_cost(
# #         setup_region[0],
# #         {'strategy': '4G_epc_microwave_baseline_baseline_baseline_baseline'},
# #         setup_costs,
# #         setup_global_parameters,
# #         setup_country_parameters,
# #         setup_backhaul_lut,
# #         setup_core_lut
# #     )

# #     #42k is a single 4G upgraded site
# #     #68k is a single 4G greenfield site
# #     #11952 is a new backhaul (10k capex + opex of 1952)
# #     assert answer['network_cost'] == (110322 + 11952 + 1027906)

# #     setup_region[0]['sites_4G'] = 0
# #     setup_region[0]['new_sites'] = 1
# #     setup_region[0]['upgraded_sites'] = 1
# #     setup_region[0]['site_density'] = 0.5
# #     setup_region[0]['backhaul_new'] = 2

# #     answer = find_single_network_cost(
# #         setup_region[0],
# #         {'strategy': '4G_epc_microwave_baseline_baseline_baseline_baseline'},
# #         setup_costs,
# #         setup_global_parameters,
# #         setup_country_parameters,
# #         setup_backhaul_lut,
# #         setup_core_lut
# #     )

#     # #42189 is a single 4G upgraded site
#     # #68165 is a single 4G greenfield site
#     # #11952 is a new backhaul (10k capex + opex of 1952) * 2
#     # assert answer['network_cost'] == (110322 + 11952 + 11952 + 1027906)

#     # answer = find_single_network_cost(
#     #     setup_region[0],
#     #     {'strategy': '5G_sa_microwave_baseline_baseline_baseline_baseline'},
#     #     setup_costs,
#     #     setup_global_parameters,
#     #     setup_country_parameters,
#     #     setup_backhaul_lut,
#     #     setup_core_lut
#     # )

#     # assert answer['network_cost'] == (110322 + 11952 + 11952 + 1027906)

#     # setup_region[0]['new_sites'] = 0
#     # setup_region[0]['upgraded_sites'] = 1
#     # setup_region[0]['site_density'] = 0.5
#     # setup_region[0]['backhaul_new'] = 0

#     # answer = find_single_network_cost(
#     #     setup_region[0],
#     #     {'strategy': '5G_sa_fiber_baseline_baseline_baseline_baseline'},
#     #     setup_costs,
#     #     setup_global_parameters,
#     #     setup_country_parameters,
#     #     setup_backhaul_lut,
#     #     setup_core_lut
#     # )

#     # assert answer['network_cost'] == 63357.0 + 1027906

#     # setup_region[0]['new_sites'] = 0
#     # setup_region[0]['upgraded_sites'] = 1
#     # setup_region[0]['site_density'] = 0.5
#     # setup_region[0]['backhaul_new'] = 1

#     # answer = find_single_network_cost(
#     #     setup_region[0],
#     #     {'strategy': '5G_sa_fiber_baseline_baseline_baseline_baseline'},
#     #     setup_costs,
#     #     setup_global_parameters,
#     #     setup_country_parameters,
#     #     setup_backhaul_lut,
#     #     setup_core_lut
#     # )

#     # assert answer['network_cost'] == 63357 + 1027906

#     # setup_region[0]['new_sites'] = 1
#     # setup_region[0]['upgraded_sites'] = 1
#     # setup_region[0]['site_density'] = 0.5
#     # setup_region[0]['backhaul_new'] = 2

#     # answer = find_single_network_cost(
#     #     setup_region[0],
#     #     {'strategy': '5G_sa_fiber_baseline_baseline_baseline_baseline'},
#     #     setup_costs,
#     #     setup_global_parameters,
#     #     setup_country_parameters,
#     #     setup_backhaul_lut,
#     #     setup_core_lut
#     # )

#     # assert answer['network_cost'] == 152690 + 1027906

#     # setup_region[0]['new_sites'] = 1
#     # setup_region[0]['upgraded_sites'] = 0
#     # setup_region[0]['site_density'] = 0.001
#     # setup_region[0]['backhaul_new'] = 1

#     # answer = find_single_network_cost(
#     #     setup_region[0],
#     #     {'strategy': '5G_sa_fiber_baseline_baseline_baseline_baseline'},
#     #     setup_costs,
#     #     setup_global_parameters,
#     #     setup_country_parameters,
#     #     setup_backhaul_lut,
#     #     setup_core_lut
#     # )

#     # assert answer['network_cost'] == 450398.0 + 1027906

#     # setup_region[0]['new_sites'] = 10
#     # setup_region[0]['upgraded_sites'] = 10
#     # setup_region[0]['site_density'] = 1
#     # setup_region[0]['backhaul_new'] = 20

#     # answer = find_single_network_cost(
#     #     setup_region[0],
#     #     {'strategy': '5G_sa_fiber_baseline_baseline_baseline_baseline'},
#     #     setup_costs,
#     #     setup_global_parameters,
#     #     setup_country_parameters,
#     #     setup_backhaul_lut,
#     #     setup_core_lut
#     # )

#     # assert answer['network_cost'] == 1451800.0 + 1027906
