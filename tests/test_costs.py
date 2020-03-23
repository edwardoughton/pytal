import pytest
from pytal.costs import (baseline_new_site, baseline_upgrade, passive_new_site, active_new_site,
    get_backhaul_costs, get_core_costs, discount_capex_and_opex, discount_opex)


def test_baseline_new_site(setup_region, setup_option, setup_costs, setup_global_parameters,
    setup_backhaul_lut, setup_core_lut):

    setup_region[0]['new_sites'] = 1

    total_cost, cost_structure = baseline_new_site('MWI', setup_region[0], setup_option['strategy'],
        setup_costs, setup_global_parameters, setup_backhaul_lut, setup_core_lut)

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

    setup_region[0]['new_sites'] = 10

    total_cost, cost_structure = baseline_new_site('MWI', setup_region[0], setup_option['strategy'],
        setup_costs, setup_global_parameters, setup_backhaul_lut, setup_core_lut)

    assert total_cost == 6376170


def test_baseline_upgrade(setup_costs, setup_global_parameters):

    total_cost, cost_structure = baseline_upgrade(1, setup_costs, setup_global_parameters)

    assert cost_structure['antennas'] == 5379
    assert cost_structure['remote_radio_units'] == 14343
    assert cost_structure['single_baseband_unit'] == 11952
    assert cost_structure['installation'] == 5000

    assert total_cost == 36674

    total_cost, cost_structure = baseline_upgrade(10, setup_costs, setup_global_parameters)

    assert total_cost == 366740


def test_passive_new_site(setup_region, setup_option, setup_costs, setup_global_parameters,
    setup_backhaul_lut, setup_core_lut):

    setup_region[0]['new_sites'] = 1

    total_cost, cost_structure = passive_new_site('MWI', setup_region[0], setup_option['strategy'],
        setup_costs, setup_global_parameters, setup_backhaul_lut, setup_core_lut)

    assert cost_structure['antennas'] == 5379
    assert cost_structure['remote_radio_units'] == 14343
    assert cost_structure['single_baseband_unit'] == 11952
    assert cost_structure['tower'] == 5000
    assert cost_structure['civil_materials'] == 5000
    assert cost_structure['transportation'] == 5000
    assert cost_structure['installation'] == 2500
    assert cost_structure['site_rental'] == 9371.5
    assert cost_structure['power_generator_battery_system'] == 2988
    assert cost_structure['high_speed_backhaul_hub'] == 8964.5
    assert cost_structure['router'] == 1195
    assert cost_structure['microwave_backhaul'] == 5976

    assert total_cost == 591622.0

    setup_region[0]['new_sites'] = 10

    total_cost, cost_structure = passive_new_site('MWI', setup_region[0], setup_option['strategy'],
    setup_costs, setup_global_parameters, setup_backhaul_lut, setup_core_lut)

    assert total_cost == 5916220


def test_active_new_site(setup_region, setup_option, setup_costs, setup_global_parameters,
    setup_backhaul_lut, setup_core_lut):

    setup_region[0]['new_sites'] = 1

    total_cost, cost_structure = active_new_site('MWI', setup_region[0], setup_option['strategy'],
    setup_costs, setup_global_parameters, setup_backhaul_lut, setup_core_lut)

    assert cost_structure['antennas'] == 2689.5
    assert cost_structure['remote_radio_units'] == 7171.5
    assert cost_structure['single_baseband_unit'] == 5976
    assert cost_structure['tower'] == 5000
    assert cost_structure['civil_materials'] == 5000
    assert cost_structure['transportation'] == 5000
    assert cost_structure['installation'] == 2500
    assert cost_structure['site_rental'] == 9371.5
    assert cost_structure['power_generator_battery_system'] == 2988
    assert cost_structure['high_speed_backhaul_hub'] == 8964.5
    assert cost_structure['router'] == 1195
    assert cost_structure['microwave_backhaul'] == 5976

    assert total_cost == 318808.5

    setup_region[0]['new_sites'] = 10

    total_cost, cost_structure = active_new_site('MWI', setup_region[0], setup_option['strategy'],
        setup_costs, setup_global_parameters, setup_backhaul_lut, setup_core_lut)

    assert total_cost == 3188085


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
