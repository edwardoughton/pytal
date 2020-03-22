import pytest
from pytal.demand import estimate_demand
from pytal.supply import find_site_density


def test_optimize_network(
    setup_region,
    setup_option,
    setup_global_parameters,
    setup_country_parameters,
    setup_timesteps,
    setup_penetration_lut,
    setup_costs,
    setup_lookup,
    setup_ci
    ):
    #test demand being larger than max capacity
    answer = find_site_density(
        {'demand_mbps_km2': 100000,
        'geotype': 'urban'},
        setup_option,
        setup_country_parameters,
        setup_lookup,
        setup_ci
    )

    assert answer == 2

    answer = find_site_density(
        {'demand_mbps_km2': 0.005,
        'geotype': 'urban'},
        setup_option,
        setup_country_parameters,
        setup_lookup,
        setup_ci
    )

    assert answer == 0.01

    answer = find_site_density(
        {'demand_mbps_km2': 250,
        'geotype': 'urban'},
        setup_option,
        setup_country_parameters,
        setup_lookup,
        setup_ci
    )

    assert answer == 0.05

    answer = find_site_density(
        {'demand_mbps_km2': 120,
        'geotype': 'urban'},
        setup_option,
        setup_country_parameters,
        setup_lookup,
        setup_ci
    )

    assert answer == 0.02
