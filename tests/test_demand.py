import pytest
from pytal.demand import estimate_demand


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

    answer = estimate_demand(
        setup_region,
        setup_option,
        setup_global_parameters,
        setup_country_parameters,
        setup_timesteps,
        setup_penetration_lut
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
    assert round(answer[0]['total_revenue']) == round(15 * 5000 / 3)

    # 1667 phones
    # arpu = 15
    # area = 2
    assert round(answer[0]['revenue_km2']) == round((15 * 5000 / 3) / 2)

    # 833 smartphones
    # scenario = 30
    # overbooking factor = 100
    # area = 2
    # demand_mbps_km2 = 125

    assert round(answer[0]['demand_mbps_km2']) == round(
        smartphones_on_network * 50 / 100 / 2
    )

    answer = estimate_demand(
        setup_region_rural,
        setup_option_high,
        setup_global_parameters,
        setup_country_parameters,
        setup_timesteps,
        setup_penetration_lut
    )

    # 1667 phones
    # arpu = 15
    # 40% subsidy
    assert round(answer[0]['total_revenue']) == round(15 * 5000 / 3 * 1.4)
