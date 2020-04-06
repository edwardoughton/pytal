import pytest
from pytal.assess import (get_spectrum_costs, calculate_tax, calculate_profit,
    calculate_benefit_cost_ratio, assess, estimate_subsidies)


def test_get_spectrum_costs(setup_region, setup_option, setup_country_parameters):

    setup_region[0]['new_sites'] = 1

    # 10000 people
    # 50000 = 0.5 * 10 * 10000 (cost = cost_mhz_pop * bw * pop )
    # 10000 = 0.1 * 10 * 10000 (cost = cost_mhz_pop * bw * pop )
    assert get_spectrum_costs(setup_region[0], setup_option['strategy'], setup_country_parameters) == 60000


def test_calculate_tax(setup_region, setup_option, setup_country_parameters):

    setup_region[0]['network_cost'] = 1e6

    assert calculate_tax(setup_region[0], setup_option['strategy'], setup_country_parameters) == 1e6 * (25/100)


def test_calculate_profit(setup_region, setup_country_parameters):

    setup_region[0]['network_cost'] = 1e6
    setup_region[0]['spectrum_cost'] = 6e4
    setup_region[0]['tax'] = 265e3

    assert calculate_profit(setup_region[0], setup_country_parameters) == 265e3


def test_calculate_benefit_cost_ratio(setup_region, setup_country_parameters):

    setup_region[0]['network_cost'] = 1e6
    setup_region[0]['spectrum_cost'] = 6e4
    setup_region[0]['tax'] = 265e3
    setup_region[0]['profit_margin'] = 265e3
    setup_region[0]['total_revenue'] = 159e4
    setup_region[0]['used_cross_subsidy'] = 0

    assert calculate_benefit_cost_ratio(setup_region[0], setup_country_parameters) == 1

    setup_region[0]['used_cross_subsidy'] = 159e4

    assert calculate_benefit_cost_ratio(setup_region[0], setup_country_parameters) == 2


def test_estimate_subsidies():

    region = {
            'GID_id': 'a',
            'total_revenue': 10000,
            'total_cost': 5000,
        }

    answer, available_cross_subsidy = estimate_subsidies(region, 0)

    assert answer['available_cross_subsidy'] == 5000
    assert answer['used_cross_subsidy'] == 0
    assert answer['required_state_subsidy'] == 0
    assert available_cross_subsidy == 5000

    region = {
            'GID_id': 'a',
            'total_revenue': 5000,
            'total_cost': 10000,
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
        }

    answer, available_cross_subsidy = estimate_subsidies(region, 2500)

    assert answer['available_cross_subsidy'] == 0
    assert answer['used_cross_subsidy'] == 2500
    assert answer['required_state_subsidy'] == 2500
    assert available_cross_subsidy == 0


def test_assess(setup_option, setup_global_parameters, setup_country_parameters):

    regions = [
        {
            'GID_id': 'a',
            'population': 1000,
            'population_km2': 500,
            'total_revenue': 20000,
            'network_cost': 5000,
        },
        {
            'GID_id': 'b',
            'population': 500,
            'population_km2': 250,
            'total_revenue': 12000,
            'network_cost': 8000,
        },
    ]

    answer = assess('MWI', regions, setup_option, setup_global_parameters,
        setup_country_parameters)

    assert answer[0]['total_revenue'] == 20000
    assert answer[0]['network_cost'] == 5000
    assert answer[0]['spectrum_cost'] == 6000
    assert answer[0]['tax'] == 1250 # 25% on total network cost of capital 5,000
    assert answer[0]['profit_margin'] == 2450 #20% of 12,250
    assert answer[0]['total_cost'] == 14700 #12,250 + 2,450
    assert answer[0]['available_cross_subsidy'] == 5300
    assert answer[0]['used_cross_subsidy'] == 0
    assert answer[0]['bcr'] == 1.3605442176870748
    assert answer[0]['required_state_subsidy'] == 0

    assert answer[1]['total_revenue'] == 12000
    assert answer[1]['network_cost'] == 8000
    assert answer[1]['spectrum_cost'] == 3000
    assert answer[1]['tax'] == 2000 # 25% on total network cost of capital 8,000
    assert answer[1]['profit_margin'] == 2600 #20% of 13,000
    assert answer[1]['total_cost'] == 15600 #13,000 + 2,600
    assert answer[1]['available_cross_subsidy'] == 0
    assert answer[1]['used_cross_subsidy'] == 3600
    assert answer[1]['bcr'] == 1
    assert answer[1]['required_state_subsidy'] == 0

    regions = [
        {
            'GID_id': 'a',
            'population': 1000,
            'population_km2': 500,
            'total_revenue': 20000,
            'network_cost': 5200,
        },
        {
            'GID_id': 'b',
            'population': 1000,
            'population_km2': 500,
            'total_revenue': 2500,
            'network_cost': 5200,
        },
    ]

    answer = assess('MWI', regions, setup_option, setup_global_parameters,
        setup_country_parameters)

    assert answer[0]['available_cross_subsidy'] == 5000
    assert answer[0]['used_cross_subsidy'] == 0
    assert answer[0]['required_state_subsidy'] == 0
    assert answer[1]['available_cross_subsidy'] == 0
    assert answer[1]['used_cross_subsidy'] == 5000
    assert answer[1]['required_state_subsidy'] == 7500
