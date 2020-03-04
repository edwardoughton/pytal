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
        Contains the scenario, strategy, and frequencies with bandwidths.
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
    #Number of cell phones per membeer of the population.
    regions['cell_pen'] = country_parameters['penetration']

    #phones : int
    #Total number of phones in a region.
    regions['phones'] =  (
        regions['population'] * regions['cell_pen'] / country_parameters['networks']
        )

    regions['revenue'] = discount_revenue(
        (regions['arpu'] * regions['phones']).values[0],
        global_parameters
    )

    regions['revenue_km2'] = regions['revenue'] / regions['area_km2']

    #data demand
    obf = global_parameters['overbooking_factor']
    user_demand = option['scenario'].split('_')[1]
    regions['smartphone_pen'] = country_parameters['smartphone_pen']

    # demand_mbps_km2 : float
    # Total demand in mbps / km^2.
    regions['demand_mbps_km2'] = (
        regions['population'] * regions['cell_pen'] * regions['smartphone_pen']
        / country_parameters['networks'] * int(user_demand) / obf / regions['area_km2']
        )

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
