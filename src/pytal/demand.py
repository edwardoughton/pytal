"""
Estimate demand

Written by Ed Oughton.

Winter 2020

"""


def estimate_demand(regions, option, global_parameters,
    country_parameters, timesteps, penetration_lut):
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
    timesteps : list
        All years for the assessment period.
    penetration_lut : list of dicts
        Contains annual penetration values.

    Returns
    -------
    regions : dataframe
        Geopandas dataframe of all regions.

    """
    output = []

    for region in regions:

        revenue = []
        demand_mbps_km2 = []

        for timestep in timesteps:

            penetration = penetration_lut[timestep]

            region['arpu'] = estimate_arpu(
                region,
                timestep,
                global_parameters,
                country_parameters
            )

            #cell_penetration : float
            #Number of cell phones per member of the population.
            region['population_with_phones'] = (
                region['population'] * (penetration / 100))

            #phones : int
            #Total number of phones on the network being modeled.
            region['phones_on_network'] = (
                region['population_with_phones'] /
                country_parameters['networks'])

            #phones : int
            #Total number of smartphones on the network being modeled.
            region['population_with_smartphones'] = (
               region['phones_on_network'] *
               country_parameters['smartphone_pen'])

            #phones : int
            #Total number of smartphones on the network being modeled.
            region['smartphones_on_network'] = (
                region['population_with_smartphones'] /
                country_parameters['networks'])

            # demand_mbps_km2 : float
            # Total demand in mbps / km^2.
            demand_mbps_km2.append(
                (region['smartphones_on_network'] *
                int(option['scenario'].split('_')[1]) / #User demand in Mbps
                global_parameters['overbooking_factor'] /
                region['area_km2']
                ))

            revenue.append(region['arpu'] * region['phones_on_network'])

        region['revenue'] = sum(revenue)
        region['revenue_km2'] = sum(revenue) / region['area_km2']
        region['demand_mbps_km2'] = sum(demand_mbps_km2) / len(demand_mbps_km2)

        output.append(region)

    return output


def estimate_arpu(region, timestep, global_parameters, country_parameters):
    """
    Allocate consumption category given a specific luminosity.

    """
    timestep = timestep - 2020

    if region['mean_luminosity_km2'] > country_parameters['luminosity']['high']:
        arpu = country_parameters['arpu']['high']
        return discount_arpu(arpu, timestep, global_parameters)

    elif region['mean_luminosity_km2'] > country_parameters['luminosity']['medium']:
        arpu = country_parameters['arpu']['medium']
        return discount_arpu(arpu, timestep, global_parameters)

    else:
        arpu = country_parameters['arpu']['low']
        return discount_arpu(arpu, timestep, global_parameters)


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


def discount_arpu(arpu, timestep, global_parameters):
    """
    Discount arpu based on return period.

    192,744 = 23,773 / (1 + 0.05) ** (0:9)

    Parameters
    ----------
    arpu : float
        Average revenue per user.
    timestep : int
        Time period (year) to discount against.
    global_parameters : dict
        All global model parameters.

    Returns
    -------
    discounted_arpu : float
        The discounted revenue over the desired time period.

    """
    discount_rate = global_parameters['discount_rate'] / 100

    discounted_arpu = arpu / (1 + discount_rate) ** timestep

    return discounted_arpu
