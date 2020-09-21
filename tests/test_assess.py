import pytest
from pytal.assess import (get_administration_cost,
    get_spectrum_costs, calculate_tax, calculate_profit,
    assess, estimate_subsidies, allocate_available_excess,
    calculate_total_market_costs, calc)


def test_assess(setup_option, setup_global_parameters, setup_country_parameters,
    setup_timesteps, setup_costs):
    """
    Integration test for main function.

    """
    regions = [
        {
            'GID_id': 'a',
            # 'GID_0': 'MEX',
            # 'scenario': 'test',
            # 'strategy': 'test',
            # 'confidence': 50,
            'geotype': 'rural 1',
            'population': 1000,
            'population_km2': 500,
            'total_mno_revenue': 20000,
            'network_cost': 5000,
            'smartphones_on_network': 250,
            'phones_on_network': 500,
        },
        {
            'GID_id': 'b',
            # 'GID_0': 'MEX',
            # 'scenario': 'test',
            # 'strategy': 'test',
            # 'confidence': 50,
            'geotype': 'rural 1',
            'population': 500,
            'population_km2': 250,
            'total_mno_revenue': 12000,
            'network_cost': 8000,
            'smartphones_on_network': 250,
            'phones_on_network': 500,
        },
    ]

    setup_country_parameters['financials']['spectrum_coverage_baseline_usd_mhz_pop'] = 0.125
    setup_country_parameters['financials']['spectrum_capacity_baseline_usd_mhz_pop'] = 0.025

    answer = assess('MWI', regions, setup_option, setup_global_parameters,
        setup_country_parameters, setup_timesteps, setup_costs)

    assert answer[0]['total_mno_revenue'] == 20000
    assert answer[0]['network_cost'] == 5000
    assert answer[0]['spectrum_cost'] == 3000
    assert answer[0]['tax'] == 1250
    assert answer[0]['profit_margin'] == 1000
    assert answer[0]['total_mno_cost'] == 11250.0
    assert answer[0]['available_cross_subsidy'] == 8750.0
    assert answer[0]['used_cross_subsidy'] == 0
    assert answer[0]['required_state_subsidy'] == 0

    assert answer[1]['total_mno_revenue'] == 12000
    assert answer[1]['network_cost'] == 8000
    assert answer[1]['spectrum_cost'] == 1500
    assert answer[1]['tax'] == 2000
    assert answer[1]['profit_margin'] == 1600.0
    assert answer[1]['total_mno_cost'] == 14700.0
    assert answer[1]['available_cross_subsidy'] == 0
    assert answer[1]['used_cross_subsidy'] == 2700.0
    assert answer[1]['required_state_subsidy'] == 0

    regions = [
        {
            'GID_id': 'a',
            # 'GID_0': 'MEX',
            # 'scenario': 'test',
            # 'strategy': 'test',
            # 'confidence': 50,
            'geotype': 'rural 1',
            'population': 1000,
            'population_km2': 500,
            'total_mno_revenue': 20000,
            'network_cost': 5200,
            'smartphones_on_network': 250,
            'phones_on_network': 500,
        },
        {
            'GID_id': 'b',
            # 'GID_0': 'MEX',
            # 'scenario': 'test',
            # 'strategy': 'test',
            # 'confidence': 50,
            'geotype': 'rural 1',
            'population': 1000,
            'population_km2': 500,
            'total_mno_revenue': 2500,
            'network_cost': 5200,
            'smartphones_on_network': 250,
            'phones_on_network': 500,
        },
    ]

    answer = assess('MWI', regions, setup_option, setup_global_parameters,
        setup_country_parameters, setup_timesteps, setup_costs)

    assert answer[0]['available_cross_subsidy'] == 8420.0
    assert answer[0]['used_cross_subsidy'] == 0
    assert answer[0]['required_state_subsidy'] == 0
    assert answer[1]['available_cross_subsidy'] == 0
    assert answer[1]['used_cross_subsidy'] == 8420.0
    assert answer[1]['required_state_subsidy'] == 660.0

    regions = [
        {
            'GID_id': 'a',
            # 'GID_0': 'MEX',
            # 'scenario': 'test',
            # 'strategy': 'test',
            # 'confidence': 50,
            'geotype': 'rural 1',
            'population': 0,
            'population_km2': 0,
            'total_mno_revenue': 0,
            'network_cost': 0,
            'smartphones_on_network': 0,
            'phones_on_network': 0,
        },
    ]

    answer = assess('MWI', regions, setup_option, setup_global_parameters,
        setup_country_parameters, setup_timesteps, setup_costs)

    assert answer[0]['cost_per_sp_user'] == 0


def test_get_administration_cost(setup_region, setup_country_parameters,
    setup_global_parameters, setup_timesteps):
    """
    Unit test.

    """
    setup_region[0]['network_cost'] = 100
    setup_timesteps = list(range(2020, 2030 + 1))

    answer = get_administration_cost(setup_region[0], setup_country_parameters,
        setup_global_parameters, setup_timesteps)

    assert round(answer['administration']) == 174


def test_get_spectrum_costs(setup_region, setup_option, setup_global_parameters, setup_country_parameters):
    """
    Unit test.

    """
    setup_region[0]['new_mno_sites'] = 1

    # 10000 people
    # 200000 = 1 * 20 * 10000 (cost = cost_mhz_pop * bw * pop )
    # 200000 = 1 * 20 * 10000 (cost = cost_mhz_pop * bw * pop )
    assert get_spectrum_costs(setup_region[0], setup_option['strategy'],
        setup_global_parameters, setup_country_parameters) == 400000

    setup_region[0]['new_mno_sites'] = 1

    # test high spectrum costs which are 50% higher
    assert get_spectrum_costs(setup_region[0], '4G_epc_microwave_baseline_baseline_high_baseline',
        setup_global_parameters, setup_country_parameters) == (
            400000 * (1 + (setup_country_parameters['financials']['spectrum_cost_high'] / 100)))

    # test low spectrum costs which are 50% lower
    assert get_spectrum_costs(setup_region[0], '4G_epc_microwave_baseline_baseline_low_baseline',
        setup_global_parameters, setup_country_parameters) == (
            400000 * (setup_country_parameters['financials']['spectrum_cost_low'] / 100))

    # test high spectrum costs which are 20% higher
    setup_country_parameters['financials']['spectrum_cost_high'] = 20
    assert get_spectrum_costs(setup_region[0], '4G_epc_microwave_baseline_baseline_high_baseline',
        setup_global_parameters, setup_country_parameters) == 400000 * (1 + (20 / 100))

    # test low spectrum costs which are 99% lower
    setup_country_parameters['financials']['spectrum_cost_low'] = 1
    assert get_spectrum_costs(setup_region[0], '4G_epc_microwave_baseline_baseline_low_baseline',
        setup_global_parameters, setup_country_parameters) == 400000 * (1 / 100)


def test_calculate_tax(setup_region, setup_option, setup_country_parameters):
    """
    Unit test.

    """
    setup_region[0]['total_mno_revenue'] = 1e7
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

    setup_region[0]['total_mno_revenue'] = 1e7
    setup_region[0]['network_cost'] = 1e9
    setup_region[0]['spectrum_cost'] = 1e1

    assert calculate_tax(setup_region[0], setup_option['strategy'], setup_country_parameters) == 1e8


def test_calculate_profit(setup_region, setup_country_parameters):
    """
    Unit test.

    """
    setup_region[0]['network_cost'] = 1e6
    setup_region[0]['spectrum_cost'] = 6e4
    setup_region[0]['tax'] = 265e3

    assert calculate_profit(setup_region[0], setup_country_parameters) == 200000.0


def test_estimate_subsidies():
    """
    Unit test.

    """
    region = {
            'GID_id': 'a',
            'total_mno_revenue': 10000,
            'total_mno_cost': 5000,
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
            'total_mno_revenue': 5000,
            'total_mno_cost': 10000,
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
            'total_mno_revenue': 5000,
            'total_mno_cost': 10000,
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
            'total_mno_revenue': 5000,
            'total_mno_cost': 10000,
            'available_cross_subsidy': 0,
            'deficit': 5000,
        }

    answer, available_cross_subsidy = estimate_subsidies(region, 2500)

    assert answer['available_cross_subsidy'] == 0
    assert answer['used_cross_subsidy'] == 2500
    assert answer['required_state_subsidy'] == 2500
    assert available_cross_subsidy == 0


def test_allocate_available_excess():
    """
    Unit test.

    """
    region = {
            'total_mno_revenue': 10000,
            'total_mno_cost': 5000,
        }

    answer = allocate_available_excess(region)

    assert answer['available_cross_subsidy'] == 5000
    assert answer['deficit'] == 0

    regions = {
            'total_mno_revenue': 5000,
            'total_mno_cost': 10000,
        }

    answer = allocate_available_excess(regions)

    assert answer['available_cross_subsidy'] == 0
    assert answer['deficit'] == 5000


def test_calculate_total_market_costs(setup_option, setup_country_parameters):
    """
    Unit test.

    """
    regions = [
        {
            'GID_id': 'a',
            # 'GID_0': 'MEX',
            # 'scenario': 'test',
            # 'strategy': 'test',
            # 'confidence': 50,
            'geotype': 'rural 1',
            'population': 0,
            'population_km2': 0,
            'total_mno_revenue': 33.3,
            'network_cost': 0,
            'smartphones_on_network': 0,
            'phones_on_network': 0,
            'administration': 33.3,
            'spectrum_cost': 33.3,
            'tax': 33.3,
            'profit_margin': 33.3,
            'cost': 33.3,
            'available_cross_subsidy': 33.3,
            'deficit': 33.3,
            'used_cross_subsidy': 33.3,
            'required_state_subsidy': 33.3,
            'total_mno_cost': 33.3
        },
    ]

    answer = calculate_total_market_costs(regions, setup_option, setup_country_parameters)

    assert answer[0]['total_market_revenue'] == 100
    assert answer[0]['total_administration'] == 100
    assert answer[0]['total_spectrum_cost'] == 100
    assert answer[0]['total_market_cost'] == 100
    assert answer[0]['total_available_cross_subsidy'] == 100
    assert answer[0]['total_used_cross_subsidy'] == 100


def test_calc():

    region = {
            'network_cost': 50,
            'smartphones_on_network': 33,
        }

    #$50 dollars
    metric = 'network_cost'

    #50% market share (2 MNOs)
    ms = 50

    #100 dollars for the whole market
    assert calc(region, metric, ms) == 100

    #$33 dollars
    metric = 'smartphones_on_network'

    #33% market share (3 MNOs)
    ms = 33

    #100 dollars for the whole market
    assert calc(region, metric, ms) == 100
