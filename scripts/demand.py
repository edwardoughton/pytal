"""
Estimate demand

Written by Ed Oughton.

Winter 2020

"""
from utils import discount_revenue


def estimate_demand(regions, option, global_parameters, country_parameters):
    """
    Estimate the total revenue based on current demand.

    Parameters
    ----------
    regions : dataframe
        Geopandas dataframe of all regions.
    option : dict
        Contains the scenario and strategy information.
    global_parameters : dict
        All global model parameters.
    country_parameters : dict
        All country specific parameters.

    Returns
    -------
    regions : dataframe
        Geopandas dataframe of all regions.

    """
    #arpu : int
    #Average Revenue Per User for cellular per month.
    #economic demand
    #ARPU discounting really needs to be the same as the cost discounting
    regions['arpu'] = regions.apply(estimate_arpu, axis=1)

    #cell_penetration : float
    #Number of cell phones per member of the population.
    regions['population_with_phones'] = int(round(
        regions['population'] * country_parameters['penetration']))

    #phones : int
    #Total number of phones on the network being modeled.
    regions['phones_on_network'] =  int(round(
        regions['population_with_phones'] / country_parameters['networks']
        ))

    #phones : int
    #Total number of smartphones on the network being modeled.
    regions['population_with_smartphones'] = int(round(
        regions['population'] * country_parameters['smartphone_pen']))

    #phones : int
    #Total number of smartphones on the network being modeled.
    regions['smartphones_on_network'] = int(round(
        regions['population_with_smartphones'] / country_parameters['networks']))

    # demand_mbps_km2 : float
    # Total demand in mbps / km^2.
    regions['demand_mbps_km2'] = (
        regions['smartphones_on_network'] *
        int(option['scenario'].split('_')[1]) / #User demand in Mbps
        global_parameters['overbooking_factor'] /
        regions['area_km2']
        )

    regions['revenue'] = discount_revenue(
        (regions['arpu'] * regions['phones_on_network']).values[0],
        global_parameters
    )

    regions['revenue_km2'] = regions['revenue'] / regions['area_km2']

    return regions


def estimate_arpu(x):
    """
    Allocate consumption category given a specific luminosity.

    """
    if x['mean_luminosity_km2'] > 5:

        return 20

    elif x['mean_luminosity_km2'] > 1:

        return 5

    else:

        return 2


def estimate_phones(x):
    """
    Allocate consumption category given a specific luminosity.

    """
    if x['mean_luminosity_km2'] > 5:

        return 10

    elif x['mean_luminosity_km2'] > 1:

        return 5

    else:

        return 1
