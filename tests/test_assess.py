import pytest
from pytal.assess import (get_administration_cost,
    get_spectrum_costs, calculate_tax, calculate_profit, calculate_benefit_cost_ratio,
    assess, estimate_subsidies, allocate_available_excess)



def test_get_administration_cost(setup_region, setup_country_parameters):

    setup_region[0]['network_cost'] = 100

    answer = get_administration_cost(setup_region[0], setup_country_parameters)

    answer['administration'] = (setup_region[0]['network_cost']
        * (setup_country_parameters['financials']['administration_percentage_of_network_cost']) / 100)


def test_get_spectrum_costs(setup_region, setup_option, setup_global_parameters, setup_country_parameters):

    setup_region[0]['new_sites'] = 1

    # 10000 people
    # 200000 = 1 * 20 * 10000 (cost = cost_mhz_pop * bw * pop )
    # 200000 = 1 * 20 * 10000 (cost = cost_mhz_pop * bw * pop )
    assert get_spectrum_costs(setup_region[0], setup_option['strategy'],
        setup_global_parameters, setup_country_parameters) == 400000

    setup_region[0]['new_sites'] = 1

    # test high spectrum costs which are 50% higher
    assert get_spectrum_costs(setup_region[0], '4G_epc_microwave_baseline_baseline_high_baseline',
        setup_global_parameters, setup_country_parameters) == (
            400000 * (1 + (setup_country_parameters['financials']['spectrum_cost_high'] / 100)))

    # test low spectrum costs which are 50% lower
    assert get_spectrum_costs(setup_region[0], '4G_epc_microwave_baseline_baseline_low_baseline',
        setup_global_parameters, setup_country_parameters) == (
            400000 * (setup_country_parameters['financials']['spectrum_cost_low'] / 100))


def test_calculate_tax(setup_region, setup_option, setup_country_parameters):

    setup_region[0]['total_revenue'] = 1e7
    setup_region[0]['network_cost'] = 1e6
    setup_region[0]['spectrum_cost'] = 1e1

    assert calculate_tax(setup_region[0], setup_option['strategy'], setup_country_parameters) == 1e6 * (25/100)

    setup_region[0]['network_cost'] = 1e6
    setup_option['strategy'] = '4G_epc_microwave_baseline_baseline_baseline_high'

    answer = calculate_tax(setup_region[0], setup_option['strategy'], setup_country_parameters)

    assert answer == 1e6 * (40/100)

    setup_region[0]['network_cost'] = 1e6
    setup_option['strategy'] = '4G_epc_microwave_baseline_baseline_baseline_low'

    answer = calculate_tax(setup_region[0], setup_option['strategy'], setup_country_parameters)

    assert answer == 1e6 * (10/100)

    setup_region[0]['total_revenue'] = 1e7
    setup_region[0]['network_cost'] = 1e9
    setup_region[0]['spectrum_cost'] = 1e1

    assert calculate_tax(setup_region[0], setup_option['strategy'], setup_country_parameters) == 1e8


def test_calculate_profit(setup_region, setup_country_parameters):

    setup_region[0]['network_cost'] = 1e6
    setup_region[0]['spectrum_cost'] = 6e4
    setup_region[0]['tax'] = 265e3

    assert calculate_profit(setup_region[0], setup_country_parameters) == 265e3


def test_estimate_subsidies():

    region = {
            'GID_id': 'a',
            'total_revenue': 10000,
            'total_cost': 5000,
            'available_cross_subsidy': 5000,
            'deficit': 0,
        }

    answer, available_cross_subsidy = estimate_subsidies(region, 0)

    assert answer['available_cross_subsidy'] == 5000
    assert answer['used_cross_subsidy'] == 0
    assert answer['required_state_subsidy'] == 0
    assert available_cross_subsidy == 0

    region = {
            'GID_id': 'a',
            'total_revenue': 5000,
            'total_cost': 10000,
            'available_cross_subsidy': 0,
            'deficit': 5000,
        }

    answer, available_cross_subsidy = estimate_subsidies(region, 5000)

    assert answer['available_cross_subsidy'] == 0
    assert answer['used_cross_subsidy'] == 5000
    assert answer['required_state_subsidy'] == 0
    assert available_cross_subsidy == 0

    region = {
            'GID_id': 'a',
            'total_revenue': 5000,
            'total_cost': 10000,
            'available_cross_subsidy': 0,
            'deficit': 5000,
        }

    answer, available_cross_subsidy = estimate_subsidies(region, 0)

    assert answer['available_cross_subsidy'] == 0
    assert answer['used_cross_subsidy'] == 0
    assert answer['required_state_subsidy'] == 5000
    assert available_cross_subsidy == 0

    region = {
            'GID_id': 'a',
            'total_revenue': 5000,
            'total_cost': 10000,
            'available_cross_subsidy': 0,
            'deficit': 5000,
        }

    answer, available_cross_subsidy = estimate_subsidies(region, 2500)

    assert answer['available_cross_subsidy'] == 0
    assert answer['used_cross_subsidy'] == 2500
    assert answer['required_state_subsidy'] == 2500
    assert available_cross_subsidy == 0


def test_assess(setup_option, setup_global_parameters, setup_country_parameters, setup_costs):

    regions = [
        {
            'GID_id': 'a',
            'population': 1000,
            'population_km2': 500,
            'total_revenue': 20000,
            'network_cost': 5000,
            'smartphones_on_network': 250,
            'phones_on_network': 500,
        },
        {
            'GID_id': 'b',
            'population': 500,
            'population_km2': 250,
            'total_revenue': 12000,
            'network_cost': 8000,
            'smartphones_on_network': 250,
            'phones_on_network': 500,
        },
    ]

    setup_country_parameters['financials']['spectrum_coverage_baseline_usd_mhz_pop'] = 0.125
    setup_country_parameters['financials']['spectrum_capacity_baseline_usd_mhz_pop'] = 0.025

    answer = assess('MWI', regions, setup_option, setup_global_parameters,
        setup_country_parameters, setup_costs)

    assert answer[0]['total_revenue'] == 20000
    assert answer[0]['network_cost'] == 5000
    # assert answer[0]['subs_acquisition'] == 500
    assert answer[0]['spectrum_cost'] == 3000
    assert answer[0]['tax'] == 1250
    assert answer[0]['profit_margin'] == 1850
    assert answer[0]['total_cost'] == 12100.0
    assert answer[0]['available_cross_subsidy'] == 7900.0
    assert answer[0]['used_cross_subsidy'] == 0
    assert answer[0]['bcr'] == 1.8018018018018018
    assert answer[0]['required_state_subsidy'] == 0

    assert answer[1]['total_revenue'] == 12000
    assert answer[1]['network_cost'] == 8000
    assert answer[1]['spectrum_cost'] == 1500
    assert answer[1]['tax'] == 2000
    assert answer[1]['profit_margin'] == 2300
    assert answer[1]['total_cost'] == 15400
    assert answer[1]['available_cross_subsidy'] == 0
    assert answer[1]['used_cross_subsidy'] == 3400.0
    assert answer[1]['bcr'] == 0.8695652173913043
    assert answer[1]['required_state_subsidy'] == 0

    regions = [
        {
            'GID_id': 'a',
            'population': 1000,
            'population_km2': 500,
            'total_revenue': 20000,
            'network_cost': 5200,
            'smartphones_on_network': 250,
            'phones_on_network': 500,
        },
        {
            'GID_id': 'b',
            'population': 1000,
            'population_km2': 500,
            'total_revenue': 2500,
            'network_cost': 5200,
            'smartphones_on_network': 250,
            'phones_on_network': 500,
        },
    ]

    answer = assess('MWI', regions, setup_option, setup_global_parameters,
        setup_country_parameters, setup_costs)

    assert answer[0]['available_cross_subsidy'] == 7560
    assert answer[0]['used_cross_subsidy'] == 0
    assert answer[0]['required_state_subsidy'] == 0
    assert answer[1]['available_cross_subsidy'] == 0
    assert answer[1]['used_cross_subsidy'] == 7560
    assert answer[1]['required_state_subsidy'] == 2380.0


def test_allocate_available_excess():

    region = {
            'total_revenue': 10000,
            'total_cost': 5000,
        }

    answer = allocate_available_excess(region)

    assert answer['available_cross_subsidy'] == 5000
    assert answer['deficit'] == 0

    regions = {
            'total_revenue': 5000,
            'total_cost': 10000,
        }

    answer = allocate_available_excess(regions)

    assert answer['available_cross_subsidy'] == 0
    assert answer['deficit'] == 5000
