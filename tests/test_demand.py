import pytest
from pytal.demand import estimate_demand, get_per_user_capacity, estimate_arpu


def test_estimate_demand(
    setup_region,
    setup_region_rural,
    setup_option,
    setup_option_high,
    setup_global_parameters,
    setup_country_parameters,
    setup_timesteps,
    setup_penetration_lut
    ):
    """
    Integration test.

    """
    answer, annual_answer = estimate_demand(
        setup_region,
        setup_option,
        setup_global_parameters,
        setup_country_parameters,
        setup_timesteps,
        setup_penetration_lut,
        {'urban': {2020: 50}}
    )

    # pop = 10000
    # pen = 50%
    # = 5000 phones
    assert answer[0]['population_with_phones'] == 5000

    # 5000 phones
    # 3 networks
    # = 1667 phones
    assert round(answer[0]['phones_on_network']) == round(5000 / 3)

    # 5000 phones
    # 3 networks
    # 50% smartphones
    # = 833 smartphones
    smartphones_on_network = round(5000 / 3 * (50 / 100))
    assert round(answer[0]['smartphones_on_network']) == smartphones_on_network

    # 1667 phones
    # arpu = 15
    assert round(answer[0]['total_mno_revenue']) == round(15 * 5000 * 12 / 3)

    # 1667 phones
    # arpu = 15
    # area = 2
    assert round(answer[0]['revenue_km2']) == round((15 * 5000 * 12 / 3) / 2)

    # 833 smartphones
    # scenario = 30
    # overbooking factor = 100
    # area = 2
    # demand_mbps_km2 = 125

    assert round(answer[0]['demand_mbps_km2']) == round(
        smartphones_on_network * 50 / 100 / 2
    )

    #Check suburban geotype uses urban in the smartphone lut
    setup_region[0]['geotype'] = 'suburban'
    answer, annual_answer = estimate_demand(
        setup_region,
        setup_option,
        setup_global_parameters,
        setup_country_parameters,
        setup_timesteps,
        setup_penetration_lut,
        {'urban': {2020: 50}}
    )

    # pop = 10000
    # pen = 50%
    # = 5000 phones
    assert answer[0]['population_with_phones'] == 5000

    # 5000 phones
    # 3 networks
    # = 1667 phones
    assert round(answer[0]['phones_on_network']) == round(5000 / 3)

    # 5000 phones
    # 3 networks
    # 50% smartphones
    # = 833 smartphones
    smartphones_on_network = round(5000 / 3 * (50 / 100))
    assert round(answer[0]['smartphones_on_network']) == smartphones_on_network

    answer, annual_answer = estimate_demand(
        setup_region_rural,
        setup_option_high,
        setup_global_parameters,
        setup_country_parameters,
        setup_timesteps,
        setup_penetration_lut,
        {'rural': {2020: 50}}
    )

    # 1667 phones on network
    # arpu = 15
    # 40% subsidy
    assert round(answer[0]['total_mno_revenue']) == round(5000 * 15 * 12 / 3)

    setup_region[0]['geotype'] = 'rural'
    setup_region[0]['mean_luminosity_km2'] = 2
    setup_option['strategy'] = '4G_epc_microwave_baseline_shared_baseline_baseline'
    setup_country_parameters['arpu']['medium'] = 7

    #iterate through years to create annual lookup
    setup_timesteps = list(range(2020, 2030 + 1))
    setup_penetration_lut = {}
    intermediate = {}
    for i in setup_timesteps:
        setup_penetration_lut[i] = 50
        intermediate[i] = 50

    setup_smartphone_lut = {}
    setup_smartphone_lut['rural'] = intermediate

    answer, annual_answer = estimate_demand(
        setup_region,
        setup_option,
        setup_global_parameters,
        setup_country_parameters,
        setup_timesteps,
        setup_penetration_lut,
        setup_smartphone_lut
    )

    # pop = 10000
    # pen = 50%
    # = 5000 phones
    assert answer[0]['population_with_phones'] == 5000

    # 5000 phones
    # 1 network
    # = 5000 phones
    assert round(answer[0]['phones_on_network']) == round(5000)

    # 5000 phones
    # 1 network
    # 50% smartphones
    # = 833 smartphones
    smartphones_on_network = round(5000 * (50 / 100))
    assert round(answer[0]['smartphones_on_network']) == smartphones_on_network

    # 5000 phones
    # arpu = 7 # monthly
    # discounted arpur over 10 years @ 5% = 242
    #[35000.0, 33333.33333333333, 31746.031746031746, 30234.31594860166,
    # 28794.586617715864, 27423.41582639606, 26117.538882281962, 24873.846554554246,
    # 23689.377671004044, 22561.312067622897, 21486.963873926572]
    # multplied by 12 months per year
    assert round(answer[0]['total_mno_revenue']) == round(3663129)

    # 2500 smartphones
    # scenario = 50
    # overbooking factor = 100
    # area = 2
    # demand_mbps_km2 = 125
    #sum [625.0, 625.0, 625.0, 625.0, 625.0, 625.0, 625.0, 625.0, 625.0, 625.0, 625.0] / 11
    assert round(answer[0]['demand_mbps_km2']) == round(
        ((smartphones_on_network * 50 / 100 / 2) * 11) / 11
    )

    setup_region[0]['population'] = 0
    setup_region[0]['population_km2'] = 0

    answer, annual_answer = estimate_demand(
        setup_region,
        setup_option,
        setup_global_parameters,
        setup_country_parameters,
        setup_timesteps,
        setup_penetration_lut,
        setup_smartphone_lut
    )

    assert answer[0]['population_with_phones'] == 0


def test_get_per_user_capacity():
    """
    Unit test.

    """
    answer = get_per_user_capacity('urban', {'scenario': 'S1_25_5_1'})

    assert answer == 25

    answer = get_per_user_capacity('suburban', {'scenario': 'S1_25_5_1'})

    assert answer == 5

    answer = get_per_user_capacity('rural', {'scenario': 'S1_25_5_1'})

    assert answer == 1

    answer = get_per_user_capacity('made up geotype', {'scenario': 'S1_25_5_1'})

    assert answer == 'Did not recognise geotype'


def test_estimate_arpu(setup_region, setup_timesteps, setup_global_parameters,
    setup_country_parameters):
    """
    Unit test.

    """
    answer = estimate_arpu({'mean_luminosity_km2': 10}, 2020, setup_global_parameters,
        setup_country_parameters)

    assert answer == 15

    answer = estimate_arpu({'mean_luminosity_km2': 2}, 2020, setup_global_parameters,
        setup_country_parameters)

    assert answer == 5

    answer = estimate_arpu({'mean_luminosity_km2': 0}, 2020, setup_global_parameters,
        setup_country_parameters)

    assert answer == 2
