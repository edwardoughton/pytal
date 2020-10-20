import pytest
import math
from pytal.costs import (greenfield_4g, upgrade_to_4g, greenfield_5g_nsa,
    upgrade_to_5g_nsa, greenfield_5g_sa, upgrade_to_5g_sa,
    get_fronthaul_costs, get_backhaul_costs, local_net_costs,
    regional_net_costs, core_costs, discount_opex,
    discount_capex_and_opex, calc_costs, find_single_network_cost)

#test approach is to:
#integration test meta cost function
#unit test each function which returns the cost structure
#unit test the function which calculates quantities
#unit test infrastructure sharing strategies


def test_find_single_network_cost(setup_region, setup_costs,
    setup_global_parameters, setup_country_parameters,
    setup_core_lut):
    """
    Integration test for main function.

    """
    setup_region[0]['sites_4G'] = 0
    setup_region[0]['new_mno_sites'] = 1
    setup_region[0]['upgraded_mno_sites'] = 1
    setup_region[0]['network_site_density'] = 0.5
    setup_region[0]['backhaul_new'] = 0

    answer = find_single_network_cost(
        setup_region[0],
        {'strategy': '4G_epc_microwave_baseline_baseline_baseline_baseline'},
        setup_costs,
        setup_global_parameters,
        setup_country_parameters,
        setup_core_lut
    )

    assert answer['network_cost'] == 267480.4

    setup_region[0]['sites_4G'] = 0
    setup_region[0]['new_mno_sites'] = 1
    setup_region[0]['upgraded_mno_sites'] = 1
    setup_region[0]['sites_estimated_total'] = 1
    setup_region[0]['network_site_density'] = 0.5
    setup_region[0]['backhaul_new'] = 10

    answer = find_single_network_cost(
        setup_region[0],
        {'strategy': '4G_epc_microwave_baseline_baseline_baseline_baseline'},
        setup_costs,
        setup_global_parameters,
        setup_country_parameters,
        setup_core_lut
    )

    assert answer['network_cost'] == 320071.4

    setup_region[0]['sites_4G'] = 0
    setup_region[0]['new_mno_sites'] = 1
    setup_region[0]['upgraded_mno_sites'] = 1
    setup_region[0]['network_site_density'] = 0.5
    setup_region[0]['backhaul_new'] = 2

    answer = find_single_network_cost(
        setup_region[0],
        {'strategy': '4G_epc_microwave_baseline_baseline_baseline_baseline'},
        setup_costs,
        setup_global_parameters,
        setup_country_parameters,
        setup_core_lut
    )

    setup_region[0]['sites_4G'] = 0
    setup_region[0]['new_mno_sites'] = 1
    setup_region[0]['upgraded_mno_sites'] = 1
    setup_region[0]['network_site_density'] = 0.5
    setup_region[0]['backhaul_new'] = 2

    answer = find_single_network_cost(
        setup_region[0],
        {'strategy': '5G_nsa_microwave_baseline_baseline_baseline_baseline'},
        setup_costs,
        setup_global_parameters,
        setup_country_parameters,
        setup_core_lut
    )

    assert answer['network_cost'] == 601671.4

    setup_region[0]['new_mno_sites'] = 0
    setup_region[0]['upgraded_mno_sites'] = 1
    setup_region[0]['network_site_density'] = 0.5
    setup_region[0]['backhaul_new'] = 0

    answer = find_single_network_cost(
        setup_region[0],
        {'strategy': '5G_nsa_microwave_baseline_baseline_baseline_baseline'},
        setup_costs,
        setup_global_parameters,
        setup_country_parameters,
        setup_core_lut
    )

    assert round(answer['network_cost']) == round(473902)

    setup_region[0]['sites_4G'] = 0
    setup_region[0]['new_mno_sites'] = 1
    setup_region[0]['upgraded_mno_sites'] = 1
    setup_region[0]['network_site_density'] = 0.5
    setup_region[0]['backhaul_new'] = 2

    answer = find_single_network_cost(
        setup_region[0],
        {'strategy': '5G_sa_microwave_baseline_baseline_baseline_baseline'},
        setup_costs,
        setup_global_parameters,
        setup_country_parameters,
        setup_core_lut
    )

    assert answer['network_cost'] == 721499.9000000001#(110322 + 11952 + 11952 + 1027906)

    setup_region[0]['new_mno_sites'] = 0
    setup_region[0]['upgraded_mno_sites'] = 1
    setup_region[0]['network_site_density'] = 0.5
    setup_region[0]['backhaul_new'] = 0

    answer = find_single_network_cost(
        setup_region[0],
        {'strategy': '5G_sa_fiber_baseline_baseline_baseline_baseline'},
        setup_costs,
        setup_global_parameters,
        setup_country_parameters,
        setup_core_lut
    )

    assert answer['network_cost'] == 1155040.7#63357.0 + 1027906

    setup_region[0]['new_mno_sites'] = 0
    setup_region[0]['upgraded_mno_sites'] = 1
    setup_region[0]['network_site_density'] = 0.5
    setup_region[0]['backhaul_new'] = 1

    answer = find_single_network_cost(
        setup_region[0],
        {'strategy': '5G_sa_fiber_baseline_baseline_baseline_baseline'},
        setup_costs,
        setup_global_parameters,
        setup_country_parameters,
        setup_core_lut
    )

    assert answer['network_cost'] == 1155040.7#63357 + 1027906

    setup_region[0]['new_mno_sites'] = 1
    setup_region[0]['upgraded_mno_sites'] = 1
    setup_region[0]['network_site_density'] = 0.5
    setup_region[0]['backhaul_new'] = 2

    answer = find_single_network_cost(
        setup_region[0],
        {'strategy': '5G_sa_fiber_baseline_baseline_baseline_baseline'},
        setup_costs,
        setup_global_parameters,
        setup_country_parameters,
        setup_core_lut
    )

    assert answer['network_cost'] == 1237544.0000000002#152690 + 1027906

    setup_region[0]['new_mno_sites'] = 1
    setup_region[0]['upgraded_mno_sites'] = 0
    setup_region[0]['network_site_density'] = 0.001
    setup_region[0]['backhaul_new'] = 1

    answer = find_single_network_cost(
        setup_region[0],
        {'strategy': '5G_sa_fiber_baseline_baseline_baseline_baseline'},
        setup_costs,
        setup_global_parameters,
        setup_country_parameters,
        setup_core_lut
    )

    assert answer['network_cost'] == 1375624.7999999998#450398.0 + 1027906

    setup_region[0]['new_mno_sites'] = 10
    setup_region[0]['upgraded_mno_sites'] = 10
    setup_region[0]['network_site_density'] = 1
    setup_region[0]['backhaul_new'] = 20

    answer = find_single_network_cost(
        setup_region[0],
        {'strategy': '5G_sa_fiber_baseline_baseline_baseline_baseline'},
        setup_costs,
        setup_global_parameters,
        setup_country_parameters,
        setup_core_lut
    )

    assert answer['network_cost'] == 2674016.4000000004#1451800.0 + 1027906


def test_greenfield_4g(setup_region, setup_option, setup_costs,
    setup_global_parameters, setup_core_lut, setup_country_parameters):
    """
    Unit test.

    """
    setup_region[0]['upgraded_mno_sites'] = 0
    setup_region[0]['new_mno_sites'] = 1
    setup_region[0]['network_site_density'] = 1

    #test baseline infra sharing
    cost_structure = greenfield_4g(setup_region[0],
        '4G_epc_microwave_baseline_baseline_baseline_baseline',
        setup_costs, setup_global_parameters,
        setup_core_lut, setup_country_parameters)

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
        setup_core_lut, setup_country_parameters)

    assert cost_structure['tower'] == 10000 / setup_country_parameters['networks']['baseline_urban']
    assert cost_structure['civil_materials'] == 5000 / setup_country_parameters['networks']['baseline_urban']

    #test active infra sharing
    cost_structure = greenfield_4g(setup_region[0],
        '4G_epc_microwave_active_baseline_baseline_baseline',
        setup_costs, setup_global_parameters,
        setup_core_lut, setup_country_parameters)

    assert cost_structure['single_sector_antenna'] == 1500 / setup_country_parameters['networks']['baseline_urban']
    assert cost_structure['single_remote_radio_unit'] == 4000 / setup_country_parameters['networks']['baseline_urban']
    assert cost_structure['bbu_cabinet'] == 500 / setup_country_parameters['networks']['baseline_urban']
    assert cost_structure['civil_materials'] == 5000 / setup_country_parameters['networks']['baseline_urban']

    setup_region[0]['sites_estimated_total'] = 6
    setup_region[0]['upgraded_mno_sites'] = 3
    setup_region[0]['sites_3G'] = 3
    setup_region[0]['network_site_density'] = 2

    #test shared wholesale core network
    cost_structure = greenfield_4g(setup_region[0],
        '4G_epc_microwave_shared_baseline_baseline_baseline',
        setup_costs, setup_global_parameters,
        setup_core_lut, setup_country_parameters)

    assert cost_structure['core_node'] == (
        (setup_costs['core_node_epc'] * 2) /
         (setup_region[0]['new_mno_sites'] + setup_region[0]['upgraded_mno_sites']) /
        (setup_country_parameters['networks']['baseline_urban']))
    assert cost_structure['regional_node'] == (
        (setup_costs['regional_node_epc'] * 2) /
         (setup_region[0]['new_mno_sites'] + setup_region[0]['upgraded_mno_sites']) /
        (setup_country_parameters['networks']['baseline_urban']))


def test_upgrade_to_4g(setup_region, setup_option, setup_costs,
    setup_global_parameters, setup_core_lut, setup_country_parameters):
    """
    Unit test.

    """
    setup_region[0]['new_mno_sites'] = 0
    setup_region[0]['upgraded_mno_sites'] = 1
    setup_region[0]['sites_3G'] = 1
    setup_region[0]['network_site_density'] = 0.5

    cost_structure = upgrade_to_4g(setup_region[0],
        '4G_epc_microwave_baseline_baseline_baseline_baseline',
        setup_costs, setup_global_parameters,
        setup_core_lut, setup_country_parameters)

    assert cost_structure['single_sector_antenna'] == 1500
    assert cost_structure['single_remote_radio_unit'] == 4000
    assert cost_structure['installation'] == 5000
    assert cost_structure['site_rental'] == 9600
    assert cost_structure['router'] == 2000

    #test passive infra sharing
    cost_structure = upgrade_to_4g(setup_region[0],
        '4G_epc_microwave_passive_baseline_baseline_baseline',
        setup_costs, setup_global_parameters,
        setup_core_lut, setup_country_parameters)

    assert cost_structure['site_rental'] == 9600 / setup_country_parameters['networks']['baseline_urban']

    #test active infra sharing
    cost_structure = upgrade_to_4g(setup_region[0],
        '4G_epc_microwave_active_baseline_baseline_baseline',
        setup_costs, setup_global_parameters,
        setup_core_lut, setup_country_parameters)

    assert cost_structure['single_sector_antenna'] == 1500 / setup_country_parameters['networks']['baseline_urban']
    assert cost_structure['single_remote_radio_unit'] == 4000 / setup_country_parameters['networks']['baseline_urban']

    setup_region[0]['sites_estimated_total'] = 6
    setup_region[0]['upgraded_mno_sites'] = 3
    setup_region[0]['sites_3G'] = 3
    setup_region[0]['network_site_density'] = 2

    #test shared wholesale core network
    cost_structure = upgrade_to_4g(setup_region[0],
        '4G_epc_microwave_shared_baseline_baseline_baseline',
        setup_costs, setup_global_parameters,
        setup_core_lut, setup_country_parameters)

    assert cost_structure['regional_node'] == int(
        (setup_costs['regional_node_epc'] * 2) /
         (setup_region[0]['new_mno_sites'] + setup_region[0]['upgraded_mno_sites']) /
        (setup_country_parameters['networks']['baseline_urban']))


def test_greenfield_5g_nsa(setup_region, setup_option, setup_costs,
    setup_global_parameters, setup_core_lut, setup_country_parameters):
    """
    Unit test.

    """
    setup_region[0]['upgraded_mno_sites'] = 0
    setup_region[0]['new_mno_sites'] = 1
    setup_region[0]['network_site_density'] = 1

    #test baseline infra sharing
    cost_structure = greenfield_5g_nsa(setup_region[0],
        '5G_nsa_microwave_baseline_baseline_baseline_baseline',
        setup_costs, setup_global_parameters,
        setup_core_lut, setup_country_parameters)

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
        setup_core_lut, setup_country_parameters)

    assert cost_structure['tower'] == 10000 / setup_country_parameters['networks']['baseline_urban']
    assert cost_structure['civil_materials'] == 5000 / setup_country_parameters['networks']['baseline_urban']

    #test active infra sharing
    cost_structure = greenfield_5g_nsa(setup_region[0],
        '5G_nsa_microwave_active_baseline_baseline_baseline',
        setup_costs, setup_global_parameters,
        setup_core_lut, setup_country_parameters)

    assert cost_structure['single_sector_antenna'] == 1500 / setup_country_parameters['networks']['baseline_urban']
    assert cost_structure['single_remote_radio_unit'] == 4000 / setup_country_parameters['networks']['baseline_urban']
    assert cost_structure['civil_materials'] == 5000 / setup_country_parameters['networks']['baseline_urban']

    setup_region[0]['sites_estimated_total'] = 6
    setup_region[0]['upgraded_mno_sites'] = 3
    setup_region[0]['sites_3G'] = 3
    setup_region[0]['network_site_density'] = 2

    #test shared wholesale core network
    cost_structure = greenfield_5g_nsa(setup_region[0],
        '5G_nsa_microwave_shared_baseline_baseline_baseline',
        setup_costs, setup_global_parameters,
        setup_core_lut, setup_country_parameters)

    assert cost_structure['core_node'] == (
        (setup_costs['core_node_nsa'] * 2) /
        (setup_region[0]['new_mno_sites'] + setup_region[0]['upgraded_mno_sites']) /
        (setup_country_parameters['networks']['baseline_urban']))
    assert cost_structure['regional_node'] == (
        (setup_costs['regional_node_nsa'] * 2) /
         (setup_region[0]['new_mno_sites'] + setup_region[0]['upgraded_mno_sites']) /
        (setup_country_parameters['networks']['baseline_urban']))


def test_upgrade_to_5g_nsa(setup_region, setup_option, setup_costs,
    setup_global_parameters, setup_core_lut, setup_country_parameters):
    """
    Unit test.

    """
    setup_region[0]['new_mno_sites'] = 0
    setup_region[0]['upgraded_mno_sites'] = 1
    setup_region[0]['sites_3G'] = 1
    setup_region[0]['network_site_density'] = 0.5

    cost_structure = upgrade_to_5g_nsa(setup_region[0],
        '5G_nsa_microwave_baseline_baseline_baseline_baseline',
        setup_costs, setup_global_parameters,
        setup_core_lut, setup_country_parameters)

    assert cost_structure['single_sector_antenna'] == 1500
    assert cost_structure['single_remote_radio_unit'] == 4000
    assert cost_structure['installation'] == 5000
    assert cost_structure['site_rental'] == 9600
    assert cost_structure['router'] == 2000

    #test passive infra sharing
    cost_structure = upgrade_to_5g_nsa(setup_region[0],
        '5G_nsa_microwave_passive_baseline_baseline_baseline',
        setup_costs, setup_global_parameters,
        setup_core_lut, setup_country_parameters)

    assert cost_structure['site_rental'] == 9600 / setup_country_parameters['networks']['baseline_urban']

    #test active infra sharing
    cost_structure = upgrade_to_5g_nsa(setup_region[0],
        '5G_nsa_microwave_active_baseline_baseline_baseline',
        setup_costs, setup_global_parameters,
        setup_core_lut, setup_country_parameters)

    assert cost_structure['single_sector_antenna'] == 1500 / setup_country_parameters['networks']['baseline_urban']
    assert cost_structure['single_remote_radio_unit'] == 4000 / setup_country_parameters['networks']['baseline_urban']

    setup_region[0]['new_mno_sites'] = 3
    setup_region[0]['upgraded_mno_sites'] = 3
    setup_region[0]['sites_3G'] = 3
    setup_region[0]['network_site_density'] = 2

    #test shared wholesale core network
    cost_structure = upgrade_to_5g_nsa(setup_region[0],
        '5G_nsa_microwave_shared_baseline_baseline_baseline',
        setup_costs, setup_global_parameters,
        setup_core_lut, setup_country_parameters)

    assert cost_structure['core_node'] == ((setup_costs['core_node_nsa'] * 2) /
        (setup_region[0]['new_mno_sites'] + setup_region[0]['upgraded_mno_sites']) /
        (setup_country_parameters['networks']['baseline_urban']))

    assert cost_structure['regional_node'] == (
        (setup_costs['regional_node_nsa'] * 2) /
        (setup_region[0]['new_mno_sites'] + setup_region[0]['upgraded_mno_sites']) /
        (setup_country_parameters['networks']['baseline_urban']))


def test_greenfield_5g_sa(setup_region, setup_option, setup_costs,
    setup_global_parameters, setup_core_lut, setup_country_parameters):
    """
    Unit test.

    """
    setup_region[0]['upgraded_mno_sites'] = 1
    setup_region[0]['new_mno_sites'] = 1
    setup_region[0]['network_site_density'] = 1

    cost_structure = greenfield_5g_sa(setup_region[0],
        '5G_sa_microwave_baseline_baseline_baseline_baseline',
        setup_costs, setup_global_parameters,
        setup_core_lut, setup_country_parameters)

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
        setup_core_lut, setup_country_parameters)

    assert cost_structure['tower'] == 10000 / setup_country_parameters['networks']['baseline_urban']
    assert cost_structure['civil_materials'] == 5000 / setup_country_parameters['networks']['baseline_urban']

    #test active infra sharing
    cost_structure = greenfield_5g_sa(setup_region[0],
        '5g_sa_microwave_active_baseline_baseline_baseline',
        setup_costs, setup_global_parameters,
        setup_core_lut, setup_country_parameters)

    assert cost_structure['single_sector_antenna'] == 1500 / setup_country_parameters['networks']['baseline_urban']
    assert cost_structure['single_remote_radio_unit'] == 4000 / setup_country_parameters['networks']['baseline_urban']
    assert cost_structure['cloud_power_supply_converter'] == 1000 / setup_country_parameters['networks']['baseline_urban']
    assert cost_structure['civil_materials'] == 5000 / setup_country_parameters['networks']['baseline_urban']

    setup_region[0]['sites_estimated_total'] = 6
    setup_region[0]['upgraded_mno_sites'] = 3
    setup_region[0]['sites_3G'] = 3
    setup_region[0]['network_site_density'] = 2

    #test shared wholesale core network
    cost_structure = greenfield_5g_sa(setup_region[0],
        '5G_sa_microwave_shared_baseline_baseline_baseline',
        setup_costs, setup_global_parameters,
        setup_core_lut, setup_country_parameters)

    assert cost_structure['core_node'] == (
        (setup_costs['core_node_sa'] * 2) /
        (setup_region[0]['new_mno_sites'] + setup_region[0]['upgraded_mno_sites']) /
        (setup_country_parameters['networks']['baseline_urban']))
    assert cost_structure['regional_node'] == (
        (setup_costs['regional_node_sa'] * 2) /
        (setup_region[0]['new_mno_sites'] + setup_region[0]['upgraded_mno_sites']) /
        (setup_country_parameters['networks']['baseline_urban']))


def test_upgrade_to_5g_sa(setup_region, setup_option, setup_costs,
    setup_global_parameters, setup_core_lut, setup_country_parameters):
    """
    Unit test.

    """
    setup_region[0]['new_mno_sites'] = 1
    setup_region[0]['upgraded_mno_sites'] = 1
    setup_region[0]['sites_3G'] = 1
    setup_region[0]['network_site_density'] = 0.5

    cost_structure = upgrade_to_5g_sa(setup_region[0],
        '5G_sa_microwave_baseline_baseline_baseline_baseline',
        setup_costs, setup_global_parameters,
        setup_core_lut, setup_country_parameters)

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
        setup_core_lut, setup_country_parameters)

    assert cost_structure['site_rental'] == 9600 / setup_country_parameters['networks']['baseline_urban']

    #test active infra sharing
    cost_structure = upgrade_to_5g_sa(setup_region[0],
        '5g_sa_microwave_active_baseline_baseline_baseline',
        setup_costs, setup_global_parameters,
        setup_core_lut, setup_country_parameters)

    assert cost_structure['single_sector_antenna'] == int(1500 / setup_country_parameters['networks']['baseline_urban'])
    assert cost_structure['single_remote_radio_unit'] == int(4000 / setup_country_parameters['networks']['baseline_urban'])
    assert cost_structure['cloud_power_supply_converter'] == int(1000 / setup_country_parameters['networks']['baseline_urban'])

    setup_region[0]['new_mno_sites'] = 6
    setup_region[0]['upgraded_mno_sites'] = 3
    setup_region[0]['sites_3G'] = 3
    setup_region[0]['network_site_density'] = 2

    #test shared wholesale core network
    cost_structure = upgrade_to_5g_sa(setup_region[0],
        '5G_sa_microwave_shared_baseline_baseline_baseline',
        setup_costs, setup_global_parameters,
        setup_core_lut, setup_country_parameters)

    assert cost_structure['core_node'] == int(
        (setup_costs['core_node_sa'] * 2) /
        (setup_region[0]['new_mno_sites'] + setup_region[0]['upgraded_mno_sites']) /
        (setup_country_parameters['networks']['baseline_urban'])
        )
    assert cost_structure['regional_node'] == int(
        (setup_costs['regional_node_sa'] * 2) /
        (setup_region[0]['new_mno_sites'] + setup_region[0]['upgraded_mno_sites']) /
        (setup_country_parameters['networks']['baseline_urban']))


def test_get_fronthaul_costs(setup_region, setup_costs):
    """
    Unit test.

    """
    setup_region[0]['network_site_density'] = 1

    assert get_fronthaul_costs(setup_region[0], setup_costs) == int(
        setup_costs['fiber_urban_m'] *
        (math.sqrt(1/setup_region[0]['network_site_density']) / 2) * 1000)

    setup_region[0]['network_site_density'] = 4

    assert get_fronthaul_costs(setup_region[0], setup_costs) == int(
        setup_costs['fiber_urban_m'] *
        (math.sqrt(1/setup_region[0]['network_site_density']) / 2) * 1000)

    setup_region[0]['network_site_density'] = 0.5

    assert get_fronthaul_costs(setup_region[0], setup_costs) == int(
        setup_costs['fiber_urban_m'] *
        (math.sqrt(1/setup_region[0]['network_site_density']) / 2) * 1000)

    setup_region[0]['network_site_density'] = 0.00001

    assert get_fronthaul_costs(setup_region[0], setup_costs) == int(
        setup_costs['fiber_urban_m'] *
        (math.sqrt(1/setup_region[0]['network_site_density']) / 2) * 1000)


def test_get_backhaul_costs(setup_region, setup_costs, setup_core_lut):
    """
    Unit test.

    """
    assert get_backhaul_costs(setup_region[0], 'microwave',
        setup_costs, setup_core_lut) == (setup_costs['microwave_small'])

    setup_region[0]['area_km2'] = 5000

    assert get_backhaul_costs(setup_region[0], 'microwave',
        setup_costs, setup_core_lut) == (setup_costs['microwave_small'])

    setup_region[0]['area_km2'] = 100000

    assert get_backhaul_costs(setup_region[0], 'microwave',
        setup_costs, setup_core_lut) == (setup_costs['microwave_large'])

    setup_region[0]['area_km2'] = 2

    assert get_backhaul_costs(setup_region[0], 'fiber',
        setup_costs, setup_core_lut) == (setup_costs['fiber_urban_m'] * 250)

    setup_region[0]['area_km2'] = 8

    assert get_backhaul_costs(setup_region[0], 'fiber',
        setup_costs, setup_core_lut) == (setup_costs['fiber_urban_m'] * 500)

    assert get_backhaul_costs(setup_region[0], 'incorrect_backhaul_tech_name',
        setup_costs, setup_core_lut) == 0


def test_local_net_costs(setup_region, setup_option, setup_costs,
    setup_country_parameters, setup_global_parameters):
    """
    Unit test.

    """
    setup_region[0]['new_mno_sites'] = 2
    setup_region[0]['upgraded_mno_sites'] = 0
    setup_region[0]['area_km2'] = 40

    assert local_net_costs(setup_region[0], setup_costs, setup_option['strategy'],
        setup_country_parameters, setup_global_parameters) == (
            setup_costs['regional_node_lower_epc'] *
            (setup_region[0]['area_km2'] /
            setup_global_parameters['local_node_spacing_km2']) /
            (setup_region[0]['new_mno_sites'] + setup_region[0]['upgraded_mno_sites']))

    setup_region[0]['new_mno_sites'] = 0

    assert local_net_costs(setup_region[0], setup_costs, setup_option['strategy'],
        setup_country_parameters, setup_global_parameters) == 0


def test_regional_net_costs(setup_region, setup_option, setup_costs, setup_core_lut,
    setup_country_parameters):
    """
    Unit test.

    """
    setup_region[0]['new_mno_sites'] = 6
    setup_region[0]['upgraded_mno_sites'] = 0

    assert regional_net_costs(setup_region[0], 'regional_edge', setup_costs,
        setup_core_lut, setup_option['strategy'], setup_country_parameters) == int(
            (setup_costs['regional_edge'] * setup_core_lut['regional_edge']['MWI.1.1.1_1_new']) /
            (setup_region[0]['new_mno_sites'] + setup_region[0]['upgraded_mno_sites']))

    assert regional_net_costs(setup_region[0], 'regional_node', setup_costs,
        setup_core_lut, setup_option['strategy'], setup_country_parameters) == int(
            (setup_costs['regional_node_epc'] * setup_core_lut['regional_node']['MWI.1.1.1_1_new']) /
            (setup_region[0]['new_mno_sites'] + setup_region[0]['upgraded_mno_sites']))

    setup_region[0]['new_mno_sites'] = 10

    assert regional_net_costs(setup_region[0], 'regional_node', setup_costs,
        setup_core_lut, setup_option['strategy'], setup_country_parameters) == int(
            (setup_costs['regional_node_epc'] * setup_core_lut['regional_node']['MWI.1.1.1_1_new']) /
            (setup_region[0]['new_mno_sites'] + setup_region[0]['upgraded_mno_sites']))

    setup_core_lut['regional_node']['MWI.1.1.1_1'] = 10
    setup_region[0]['area_km2'] = 100

    assert regional_net_costs(setup_region[0], 'regional_node', setup_costs,
        setup_core_lut, setup_option['strategy'], setup_country_parameters) == int(
            (setup_costs['regional_node_epc'] * setup_core_lut['regional_node']['MWI.1.1.1_1_new']) /
            (setup_region[0]['new_mno_sites'] + setup_region[0]['upgraded_mno_sites']))

    assert regional_net_costs(setup_region[0], 'incorrrect_asset_name', setup_costs,
        setup_core_lut, setup_option['strategy'], setup_country_parameters) == 'Asset name not in lut'

    setup_region[0]['new_mno_sites'] = 0

    assert regional_net_costs(setup_region[0], 'regional_node', setup_costs,
        setup_core_lut, setup_option['strategy'], setup_country_parameters) == 0

    setup_region[0]['GID_id'] = 'unknown GID ID'

    assert regional_net_costs(setup_region[0], 'regional_node', setup_costs,
        setup_core_lut, setup_option['strategy'], setup_country_parameters) == 0


def test_core_costs(setup_region, setup_option, setup_costs, setup_core_lut, setup_country_parameters):
    """
    Unit test.

    """
    setup_region[0]['new_mno_sites'] = 2
    setup_region[0]['upgraded_mno_sites'] = 0
    setup_country_parameters['networks']['baseline_urban'] = 2

    assert core_costs(setup_region[0], 'core_edge', setup_costs,
        setup_core_lut, setup_option['strategy'], setup_country_parameters) == (
            (setup_costs['core_edge'] * 1000) /
            (setup_region[0]['new_mno_sites'] + setup_region[0]['upgraded_mno_sites']))

    assert core_costs(setup_region[0], 'core_node', setup_costs,
        setup_core_lut, setup_option['strategy'], setup_country_parameters) == (
            (setup_costs['core_node_{}'.format('epc')] * 2) /
            (setup_region[0]['new_mno_sites'] + setup_region[0]['upgraded_mno_sites']))

    assert core_costs(setup_region[0], 'incorrrect_asset_name', setup_costs,
        setup_core_lut, setup_option['strategy'], setup_country_parameters) == 0

    setup_region[0]['GID_id'] == 'unknown'

    assert core_costs(setup_region[0], 'core_edge', setup_costs,
        setup_core_lut, setup_option['strategy'], setup_country_parameters) == (
            (setup_costs['core_edge'] * setup_core_lut['core_edge']['MWI.1.1.1_1_new']) /
            (setup_region[0]['new_mno_sites'] + setup_region[0]['upgraded_mno_sites']))

    setup_core_lut['regional_node']['MWI.1.1.1_1'] = 3


def test_discount_capex_and_opex(setup_global_parameters, setup_country_parameters):
    """
    Unit test.

    """
    assert discount_capex_and_opex(1000, setup_global_parameters, setup_country_parameters) == (
        1195 * (1 + (setup_country_parameters['financials']['wacc'] / 100)))


def test_discount_opex(setup_global_parameters, setup_country_parameters):
    """
    Unit test.

    """
    assert discount_opex(1000, setup_global_parameters, setup_country_parameters) == (
        1952 * (1 + (setup_country_parameters['financials']['wacc'] / 100)))


def test_calc_costs(setup_region, setup_global_parameters, setup_country_parameters):
    """
    Unit test.

    """
    setup_region[0]['sites_4G'] = 0
    setup_region[0]['upgraded_mno_sites'] = 1
    setup_region[0]['new_mno_sites'] = 1

    answer, structure = calc_costs(
        setup_region[0],
        {'single_sector_antenna': 1500},
        'fiber',
        1,
        setup_global_parameters,
        setup_country_parameters)

    assert answer == 5917

    answer, structure = calc_costs(
        setup_region[0],
        {'single_baseband_unit': 4000},
        'fiber',
        1,
        setup_global_parameters,
        setup_country_parameters)

    assert answer == 5259

    answer, structure = calc_costs(
        setup_region[0],
        {'tower': 10000},
        'fiber',
        1,
        setup_global_parameters,
        setup_country_parameters)

    assert answer == 11000

    answer, structure = calc_costs(
        setup_region[0],
        {'site_rental': 9600},
        'fiber',
        1,
        setup_global_parameters,
        setup_country_parameters)

    assert answer == 20617 #two years' of rent

    answer, structure = calc_costs(setup_region[0],
        {'single_sector_antenna': 1500,
        'single_baseband_unit': 4000,
        'tower': 10000,
        'site_rental': 9600},
        'fiber',
        6,
        setup_global_parameters,
        setup_country_parameters)

    #answer = sum of antenna, bbu, tower, site_rental (5379 + 4781 + 10000 + 18743)
    assert answer == 42793

    answer, structure = calc_costs(
        setup_region[0],
        {'incorrect_name': 9600},
        'fiber',
        1,
        setup_global_parameters,
        setup_country_parameters)

    assert answer == 0 #two years' of rent

    answer, structure = calc_costs(setup_region[0],
        {'cots_processing': 6,
            'io_n2_n3': 6,
            'low_latency_switch': 6,
            'rack': 6,
            'cloud_power_supply_converter': 6,},
        'fiber',
        1,
        setup_global_parameters,
        setup_country_parameters)

    assert answer == round(sum([
        8.8, #cots_processing = capex + opex
        8.8, #io_n2_n3 = capex + opex
        8.8, #low_latency_switch = capex + opex
        6.6, #rack = capex
        8.8, #cloud_power_supply_converter = capex + opex
    ]))

    answer, structure = calc_costs(setup_region[0],
        {'backhaul': 100,},
        'fiber',
        1,
        setup_global_parameters,
        setup_country_parameters)

    assert answer == 132

    answer, structure = calc_costs(setup_region[0],
        {'backhaul': 100,},
        'fiber',
        0,
        setup_global_parameters,
        setup_country_parameters)

    assert answer == 0
