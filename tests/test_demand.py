# import pytest
# from pytal.demand import estimate_demand, get_per_user_capacity, estimate_arpu



# def test_estimate_demand(
#     setup_region,
#     setup_region_rural,
#     setup_option,
#     setup_option_high,
#     setup_global_parameters,
#     setup_country_parameters,
#     setup_timesteps,
#     setup_penetration_lut
#     ):

#     answer = estimate_demand(
#         setup_region,
#         setup_option,
#         setup_global_parameters,
#         setup_country_parameters,
#         setup_timesteps,
#         setup_penetration_lut,
#         {'urban': {'smartphone': 0.5}}
#     )

#     # pop = 10000
#     # pen = 50%
#     # = 5000 phones
#     assert answer[0]['population_with_phones'] == 5000

#     # 5000 phones
#     # 3 networks
#     # = 1667 phones
#     assert round(answer[0]['phones_on_network']) == round(5000 / 3)

#     # 5000 phones
#     # 3 networks
#     # 50% smartphones
#     # = 833 smartphones
#     smartphones_on_network = round(5000 / 3 * (50 / 100))
#     assert round(answer[0]['smartphones_on_network']) == smartphones_on_network

#     # 1667 phones
#     # arpu = 15
#     assert round(answer[0]['total_revenue']) == round(15 * 5000 / 3)

#     # 1667 phones
#     # arpu = 15
#     # area = 2
#     assert round(answer[0]['revenue_km2']) == round((15 * 5000 / 3) / 2)

#     # 833 smartphones
#     # scenario = 30
#     # overbooking factor = 100
#     # area = 2
#     # demand_mbps_km2 = 125

#     assert round(answer[0]['demand_mbps_km2']) == round(
#         smartphones_on_network * 50 / 100 / 2
#     )

#     answer = estimate_demand(
#         setup_region_rural,
#         setup_option_high,
#         setup_global_parameters,
#         setup_country_parameters,
#         setup_timesteps,
#         setup_penetration_lut,
#         {'rural': {'smartphone': 0.5}}
#     )

#     # 1667 phones on network
#     # arpu = 15
#     # 40% subsidy
#     assert round(answer[0]['total_revenue']) == round(5000 * 15 / 3)


# def test_get_per_user_capacity():

#     answer = get_per_user_capacity('urban', {'scenario': 'S1_25_5_1'})

#     assert answer == 25

#     answer = get_per_user_capacity('suburban', {'scenario': 'S1_25_5_1'})

#     assert answer == 5

#     answer = get_per_user_capacity('rural', {'scenario': 'S1_25_5_1'})

#     assert answer == 1

#     answer = get_per_user_capacity('made up geotype', {'scenario': 'S1_25_5_1'})

#     assert answer == 'Did not recognise geotype'


# def test_estimate_arpu(setup_region, setup_timesteps, setup_global_parameters,
#     setup_country_parameters):

#     answer = estimate_arpu({'mean_luminosity_km2': 10}, 2020, setup_global_parameters,
#         setup_country_parameters)

#     assert answer == 15

#     answer = estimate_arpu({'mean_luminosity_km2': 2}, 2020, setup_global_parameters,
#         setup_country_parameters)

#     assert answer == 5

#     answer = estimate_arpu({'mean_luminosity_km2': 0}, 2020, setup_global_parameters,
#         setup_country_parameters)

#     assert answer == 2
