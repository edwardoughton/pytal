import pytest
from pytal.assess import (get_spectrum_costs, calculate_tax, calculate_profit,
    calculate_benefit_cost_ratio, assess)


def test_get_spectrum_costs(setup_region, setup_option, setup_country_parameters):

    setup_region[0]['new_sites'] = 1

    # 10000 people
    # 50000 = 0.5 * 10 * 10000 (cost = cost_mhz_pop * bw * pop )
    # 10000 = 0.1 * 10 * 10000 (cost = cost_mhz_pop * bw * pop )
    assert get_spectrum_costs(setup_region[0], setup_option['strategy'], setup_country_parameters) == 60000


def test_calculate_tax(setup_region, setup_option, setup_country_parameters):

    setup_region[0]['total_network_cost'] = 1e6
    setup_region[0]['total_spectrum_cost'] = 6e4

    assert calculate_tax(setup_region[0], setup_option['strategy'], setup_country_parameters) == 265000


def test_calculate_profit(setup_region, setup_country_parameters):

    setup_region[0]['total_network_cost'] = 1e6
    setup_region[0]['total_spectrum_cost'] = 6e4
    setup_region[0]['total_tax'] = 265e3

    assert calculate_profit(setup_region[0], setup_country_parameters) == 265e3


def test_calculate_benefit_cost_ratio(setup_region, setup_country_parameters):

    setup_region[0]['total_network_cost'] = 1e6
    setup_region[0]['total_spectrum_cost'] = 6e4
    setup_region[0]['total_tax'] = 265e3
    setup_region[0]['total_profit'] = 265e3

    setup_region[0]['total_revenue'] = 159e4

    assert calculate_benefit_cost_ratio(setup_region[0], setup_country_parameters) == 1


def test_assess(setup_region, setup_option, setup_global_parameters, setup_country_parameters):

    setup_region[0]['total_network_cost'] = 10000
    setup_region[0]['total_revenue'] = 12000

    answer = assess('MWI', setup_region, setup_option, setup_global_parameters, setup_country_parameters)

    assert answer[0]['total_cost'] == 105000
