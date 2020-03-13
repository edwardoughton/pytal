import pytest
from pytal.demand import estimate_demand


def test_estimate_demand(
    setup_region,
    setup_option,
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

    print(answer)

    assert answer == 0
